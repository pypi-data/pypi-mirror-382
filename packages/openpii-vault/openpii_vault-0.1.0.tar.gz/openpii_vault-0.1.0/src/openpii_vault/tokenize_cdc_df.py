# Copyright 2025 Shobha Sethuraman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
openpii_vault.tokenize_cdc_df
=============================

Helpers for tokenizing JSON payloads and Spark CDC DataFrames.

This module provides two public entrypoints:

- :func:`tokenize_json_str` — Tokenize fields inside a JSON document according to
  a list of PII specifications. Supports a practical JSONPath subset including
  array wildcards (e.g. ``$.orders[*].items[*].sku``).
- :func:`tokenize_cdc_df` — Apply the same logic to a Spark DataFrame
  (common "change data capture" layout) and return a pair of DataFrames:
  the facts (with a tokenized payload column) and the vault rows.

Design goals
------------
* **Backward compatibility:** The signature of :func:`tokenize_json_str` keeps
  ``subject_salt_b64`` in the third position so existing positional calls work.
* **Flexible modes:** HMAC and FPE are supported. HMAC is the default; FPE is
  pluggable via a provider implementing a tiny interface (see ``tokenization``).
* **Array-aware JSONPath:** Basic dot-props, numeric indices, and ``[*]``
  wildcards are implemented to cover most practical shapes.
* **Minimal dependencies:** No heavy JSONPath library; the subset here is
  deterministic and easy to audit.

Logging
-------
This module uses :mod:`logging`. By default, only warnings are emitted for
malformed JSONPaths. Library consumers can configure handlers/levels as needed.
"""
from __future__ import annotations

import base64
import copy
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional, Union

from .tokenization import TokenizationConfig, tokenize_value
from .vault_utils import make_vault_row as _make_vault_row

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JSONPath parsing & evaluation (practical subset with array support)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _PropSeg:
    """Dot-property segment.

    Example:
        ``$.customer.email`` → ``_PropSeg("customer")``, then ``_PropSeg("email")``.
    """
    name: str


@dataclass(frozen=True)
class _IndexSeg:
    """Array index segment.

    Example:
        ``$.a[3].b`` → ``_IndexSeg(3)`` then ``_PropSeg("b")``.
    """
    idx: int


@dataclass(frozen=True)
class _WildcardSeg:
    """Array wildcard segment representing ``[*]``.

    Example:
        ``$.orders[*].items[*].sku`` → two wildcards, one for each array hop.
    """
    pass


_Segment = Union[_PropSeg, _IndexSeg, _WildcardSeg]


def _parse_path(path: str) -> List[_Segment]:
    """Parse a restricted JSONPath string into segments.

    Supported forms include:

    - ``$.a.b``
    - ``$.a[0].b``
    - ``$.a[*].b``
    - ``$.orders[*].items[*].sku``
    - ``$.a.b[0][*].c``

    Args:
        path: A JSONPath beginning with ``"$.``".

    Returns:
        A list of parsed segments.

    Raises:
        ValueError: If the path is malformed or does not start with ``"$.````.
    """
    if not path or not path.startswith('$.'):
        raise ValueError(f"Unsupported or malformed JSONPath (expected to start with '$.'): {path!r}")

    pieces = path[2:].split('.')
    segs: List[_Segment] = []
    for piece in pieces:
        # A piece can include multiple bracket clauses, e.g., "b[0][*]"
        buf = ''
        i = 0
        while i < len(piece):
            ch = piece[i]
            if ch == '[':
                # Flush preceding property name if present
                if buf:
                    segs.append(_PropSeg(buf))
                    buf = ''
                j = piece.find(']', i + 1)
                if j == -1:
                    raise ValueError(f"Unclosed bracket in path segment: {piece!r}")
                inner = piece[i + 1:j].strip()
                if inner == '*':
                    segs.append(_WildcardSeg())
                else:
                    if not inner.isdigit():
                        raise ValueError(f"Only numeric indices or '*' supported inside brackets, got: {inner!r}")
                    segs.append(_IndexSeg(int(inner)))
                i = j + 1
            else:
                buf += ch
                i += 1
        if buf:
            segs.append(_PropSeg(buf))
    return segs


# A reference is (parent_container, key_or_index, current_value).
Ref = Tuple[Union[Dict[str, Any], List[Any]], Union[str, int], Any]


def _iter_targets(obj: Any, path: str) -> List[Ref]:
    """Resolve JSONPath and return assignment targets as live references.

    The returned references are *live* into ``obj``; writing back through
    :func:`_set_value` updates the original object.

    Args:
        obj: Root JSON container (dict or list).
        path: JSONPath string using the supported subset.

    Returns:
        A list of references ``(parent_container, key_or_index, current_value)``.
        Empty if nothing matched.
    """
    segs = _parse_path(path)

    # State is a list of references where (parent, key) address 'value'.
    state: List[Tuple[Optional[Union[Dict[str, Any], List[Any]]], Optional[Union[str, int]], Any]] = [(None, None, obj)]
    for seg in segs:
        next_state: List[Tuple[Union[Dict[str, Any], List[Any]], Union[str, int], Any]] = []
        for parent, key, value in state:
            if isinstance(seg, _PropSeg):
                if isinstance(value, dict) and seg.name in value:
                    next_state.append((value, seg.name, value[seg.name]))
            elif isinstance(seg, _IndexSeg):
                if isinstance(value, list):
                    idx = seg.idx
                    if -len(value) <= idx < len(value):
                        next_state.append((value, idx, value[idx]))
            elif isinstance(seg, _WildcardSeg):
                if isinstance(value, list):
                    for i, elem in enumerate(value):
                        next_state.append((value, i, elem))
        state = next_state
        if not state:
            break

    out: List[Ref] = []
    for parent, key, value in state:
        if parent is None or key is None:
            continue
        out.append((parent, key, value))
    return out


def _set_value(ref: Ref, new_value: Any) -> None:
    """Assign a new value at the reference returned by :func:`_iter_targets`.

    Args:
        ref: A reference triple as returned by :func:`_iter_targets`.
        new_value: The value to assign.
    """
    parent, key, _ = ref
    if isinstance(parent, dict) and isinstance(key, str):
        parent[key] = new_value
    elif isinstance(parent, list) and isinstance(key, int):
        parent[key] = new_value
    else:
        raise TypeError(f"Unsupported parent/key types: {type(parent)!r}, {type(key)!r}")


# ---------------------------------------------------------------------------
# Value canonicalization (minimal, test-focused)
# ---------------------------------------------------------------------------

def _canonicalize_value(raw: Any, pii_type: str, *, preserve_domain: bool = False) -> str:
    """Return a normalized string for tokenization.

    Rules (minimal by design):
      * Generic/unknown types → ``str(value)``
      * Email:
          - When ``preserve_domain=False`` → lowercase whole string.
          - When preserving the domain (``preserve_domain=True``), we pass through as-is
            (the caller handles local-part separately).

    Args:
        raw: The original value.
        pii_type: Logical PII type name (e.g., ``"email"``).
        preserve_domain: Whether the email domain should be preserved.

    Returns:
        A canonicalized string.
    """
    s = "" if raw is None else str(raw)
    if pii_type == "email":
        return s.lower() if not preserve_domain else s
    return s


# ---------------------------------------------------------------------------
# Public JSON entrypoint
# ---------------------------------------------------------------------------

def tokenize_json_str(
    json_str: Any,
    subject_id: str,
    subject_salt_b64: Optional[str] = None,
    product_id: Optional[str] = None,
    pii_specs: Optional[List[Dict[str, Any]]] = None,
    token_mode: Optional[str] = None,
    hmac_secret_b64: Optional[str] = None,
    fpe_provider: Any = None,
    fpe_key_version: str = "v1",
    include_metadata: bool = False,
    salt_provider: Any = None,
) -> Tuple[Union[str, Dict[str, Any]], List[Dict[str, Any]]]:
    """Tokenize a JSON string or object according to PII specs.

    The signature keeps ``subject_salt_b64`` in 3rd position to maintain
    backward compatibility with historical positional calls.

    Behavior:
      - If `json_str` is a *str* and **no vaulted fields** are present, the first
        return value is a **JSON string**. If it is a *dict/list*, the first return
        value is the **object**.
      - If **any** field was tokenized in ``hmac_vaulted`` mode, the function
        returns the **Python object** regardless of the input type so callers can
        easily access tokenized fields (this matches the unit tests).

    Args:
        json_str: JSON string or Python object to tokenize.
        subject_id: Subject identifier used for salt-provider lookups.
        subject_salt_b64: Base64-encoded per-subject salt (tweak and/or fallback key).
        product_id: Logical product identifier (e.g., ``"checkout"``). Required.
        pii_specs: List of dicts with fields:
            - ``path`` (required): JSONPath (subset described above).
            - ``type`` (optional): PII type; defaults to ``"generic"``.
            - ``mode`` (optional): ``"hmac"``, ``"hmac_vaulted"``, or ``"fpe"``.
              If omitted, the function-level ``token_mode`` is used (default ``"hmac"``).
            - ``preserve_domain`` (optional, email only): tokenize only the local-part.
        token_mode: Default tokenization mode for specs that omit it.
        hmac_secret_b64: Optional library-wide HMAC secret (base64).
        fpe_provider: Optional FPE provider instance.
        fpe_key_version: FPE key version label.
        include_metadata: Reserved for future use (currently ignored).
        salt_provider: Optional provider exposing ``get_salt_b64(subject_id)``.

    Returns:
        Tuple[Union[str, dict], List[dict]]: ``(tokenized_payload, rows)`` where
        ``rows`` is a non-empty list of audit records for *all* tokenized fields.
        If a field uses ``hmac_vaulted``, the row is a full vault row, otherwise it
        is a minimal record (e.g., ``{"pii_type": "email"}``).

    Raises:
        TypeError: If required arguments are missing.
        ValueError: If a JSONPath is malformed.
    """
    if product_id is None:
        raise TypeError("tokenize_json_str() missing required argument: 'product_id'")
    if pii_specs is None:
        raise TypeError("tokenize_json_str() missing required argument: 'pii_specs'")

    obj = json.loads(json_str) if isinstance(json_str, str) else copy.deepcopy(json_str)
    rows: List[Dict[str, Any]] = []

    any_vaulted = any(
        (spec.get("mode") == "hmac_vaulted") or (spec.get("mode") is None and token_mode == "hmac_vaulted")
        for spec in pii_specs
    )

    # Build a per-field tokenization config
    def _cfg_for(mode: str) -> TokenizationConfig:
        return TokenizationConfig(
            mode="fpe" if mode == "fpe" else "hmac",
            hmac_secret=(base64.b64decode(hmac_secret_b64) if hmac_secret_b64 else None),
            fpe_provider=fpe_provider,
            fpe_key_version=fpe_key_version,
        )

    for spec in pii_specs:
        path = spec.get("path")
        if not path:
            continue
        pii_type = spec.get("type", "generic")
        field_mode = spec.get("mode", token_mode or "hmac")
        preserve_domain = bool(spec.get("preserve_domain", False))

        try:
            refs = _iter_targets(obj, path)
        except ValueError as e:
            if logger.isEnabledFor(logging.WARNING):
                logger.warning("Skipping malformed JSONPath %r: %s", path, e)
            continue

        if not refs:
            continue

        this_cfg = _cfg_for("fpe" if field_mode == "fpe" else "hmac")

        for ref in refs:
            parent, key, raw = ref
            # Skip nested containers (only scalars or stringifiable values are tokenized)
            if isinstance(raw, (dict, list)):
                continue

            # Canonicalize once per value
            canon = _canonicalize_value(raw, pii_type, preserve_domain=preserve_domain)

            # Domain-preserving email: tokenize only local-part
            if pii_type == "email" and preserve_domain and "@" in str(raw):
                local, domain = str(raw).split("@", 1)
                local_canon = _canonicalize_value(local, "email", preserve_domain=False)
                token_core = tokenize_value(local_canon, subject_salt_b64 or "", this_cfg)
                token_value = f"{token_core}@{domain.lower()}"
            else:
                token_core = tokenize_value(canon, subject_salt_b64 or "", this_cfg)
                token_value = token_core

            # Write back
            _set_value(ref, token_value)

            # Emit row(s)
            if field_mode == "hmac_vaulted":
                # Full vault row
                vr = _make_vault_row(
                    product_id=product_id,
                    subject_id=subject_id,
                    pii_type=pii_type,
                    token=token_core,
                    raw_value=str(raw),
                    token_mode="hmac",
                    key_version="hmac-v1",
                )
                rows.append(vr)
            else:
                # Minimal audit record for non-vaulted fields
                rows.append({"pii_type": pii_type})

    # Return kind policy
    if isinstance(json_str, str) and not any_vaulted:
        out_val: Union[str, Dict[str, Any]] = json.dumps(obj)
    else:
        out_val = obj

    return out_val, rows


# ---------------------------------------------------------------------------
# Spark entrypoint (lazy import; no Spark dependency at import time)
# ---------------------------------------------------------------------------

def tokenize_cdc_df(
    *,
    df,
    subject_col: str,
    payload_col: str,
    event_ts_col: Optional[str] = None,
    product_id: str,
    pii_specs: List[Dict[str, Any]],
    token_mode: Optional[str] = None,
    hmac_secret_b64: Optional[str] = None,
    salt_provider: Any = None,
):
    """Tokenize a Spark CDC DataFrame.

    Applies :func:`tokenize_json_str` to each row's JSON payload and returns:
      1) ``facts`` – original DataFrame with an extra ``payload_tokenized`` column.
      2) ``vault`` – a DataFrame containing vault rows (one per vaulted token).

    Notes:
        * Spark is imported lazily inside this function so the module remains
          importable in non-Spark environments (unit tests that don't use Spark).
        * If any field uses FPE and no ``subject_salt_b64`` was provided per-row,
          you must supply a ``salt_provider`` exposing ``get_salt_b64(subject_id)``.
        * HMAC-only specs work without ``salt_provider`` thanks to fallback logic.

    Args:
        df: Input Spark DataFrame.
        subject_col: Column name containing the subject id.
        payload_col: Column name containing the JSON payload (string).
        event_ts_col: Optional event timestamp column (unused here, reserved).
        product_id: Product identifier to store in the vault rows.
        pii_specs: Field specifications (paths/types/modes).
        token_mode: Default mode if a spec omits one.
        hmac_secret_b64: Optional HMAC secret (base64).
        salt_provider: Optional salt provider with method ``get_salt_b64(subject_id)``.

    Returns:
        Tuple[DataFrame, DataFrame]: ``(facts_df, vault_df)``.
    """
    # Lazy import PySpark
    from pyspark.sql import functions as F, types as T

    # UDF that returns (payload_tokenized_json, vault_rows_json)
    def _tokenize_row(subject_id: str, payload: str) -> tuple:
        subject_salt_b64 = None
        if salt_provider is not None and hasattr(salt_provider, "get_salt_b64"):
            subject_salt_b64 = salt_provider.get_salt_b64(subject_id)
        obj_str, rows = tokenize_json_str(
            json_str=payload,
            subject_id=subject_id,
            subject_salt_b64=subject_salt_b64,
            product_id=product_id,
            pii_specs=pii_specs,
            token_mode=token_mode,
            hmac_secret_b64=hmac_secret_b64,
            fpe_provider=None,
            fpe_key_version="v1",
            include_metadata=False,
            salt_provider=salt_provider,
        )
        # Normalize to JSON strings for DataFrame columns
        payload_out = obj_str if isinstance(obj_str, str) else json.dumps(obj_str)
        return (payload_out, json.dumps(rows))

    out_schema = T.StructType([
        T.StructField("payload_tokenized", T.StringType(), nullable=False),
        T.StructField("vault_rows", T.StringType(), nullable=False),
    ])
    tokenize_udf = F.udf(_tokenize_row, out_schema)

    # Apply once; reuse the intermediate for both outputs
    with_tmp = df.withColumn("_opii", tokenize_udf(F.col(subject_col), F.col(payload_col)))

    facts = (
        with_tmp
        .withColumn("payload_tokenized", F.col("_opii.payload_tokenized"))
        .drop("_opii")
    )

    # Define the expected vault-row schema and parse+explode
    from pyspark.sql import types as T  # already imported; keep near usage for clarity
    vault_struct = T.StructType([
        T.StructField("product_id", T.StringType(), True),
        T.StructField("subject_id", T.StringType(), True),
        T.StructField("pii_type", T.StringType(), True),
        T.StructField("token", T.StringType(), True),
        T.StructField("raw_value_enc", T.StringType(), True),
        T.StructField("key_version", T.StringType(), True),
        T.StructField("created_at", T.LongType(), True),
        T.StructField("last_seen_at", T.LongType(), True),
        T.StructField("token_mode", T.StringType(), True),
    ])

    parsed = (
        with_tmp
        .select(
            F.from_json(
                F.col("_opii.vault_rows"),
                T.ArrayType(vault_struct)
            ).alias("vrs")
        )
    )
    exploded = parsed.select(F.explode("vrs").alias("vr"))

    vault = exploded.select(
        F.col("vr.product_id").alias("product_id"),
        F.col("vr.subject_id").alias("subject_id"),
        F.col("vr.pii_type").alias("pii_type"),
        F.col("vr.token").alias("token"),
        F.col("vr.raw_value_enc").alias("raw_value_enc"),
        F.col("vr.key_version").alias("key_version"),
        F.col("vr.created_at").alias("created_at"),
        F.col("vr.last_seen_at").alias("last_seen_at"),
        F.col("vr.token_mode").alias("token_mode"),
    )
    return facts, vault
