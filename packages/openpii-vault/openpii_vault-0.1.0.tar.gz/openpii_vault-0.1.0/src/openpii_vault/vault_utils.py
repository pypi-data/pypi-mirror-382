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
openpii_vault.vault_utils
=========================

Helper utilities for creating vault rows and (future) envelope encryption.
This module intentionally keeps crypto minimal; a production deployment should
replace `encrypt_envelope` with a KMS-backed envelope encryption adapter.
"""
from __future__ import annotations

import base64
import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def encrypt_envelope(raw: str) -> str:
    """Stub for envelope encryption.

    Args:
        raw: The plaintext/raw value to protect (e.g., original PII).

    Returns:
        A base64-encoded UTF-8 representation. This is a placeholder;
        substitute with a proper KMS envelope encryption implementation.
    """
    return base64.b64encode((raw or "").encode("utf-8")).decode("utf-8")


def make_vault_row(
    product_id: str,
    subject_id: str,
    pii_type: str,
    token: str,
    raw_value: str,
    key_version: str = "v1",
    token_mode: Optional[str] = None,
) -> Dict:
    """Build a dictionary representing a vault record.

    The vault stores a mapping from a deterministic token to the protected
    original value (encrypted), plus minimal metadata for auditing.

    Args:
        product_id: Logical product identifier (e.g., "checkout").
        subject_id: Subject identifier (e.g., user id).
        pii_type: Type/category of the PII field (e.g., "ssn", "email").
        token: The deterministic token value produced by the tokenizer.
        raw_value: The raw/original value (will be envelope-encrypted).
        key_version: Version label for the encryption key/process.
        token_mode: Optional tokenization mode annotation (e.g., "hmac").

    Returns:
        Dict with fields suitable for turning into a Spark/DataFrame row.
    """
    ts = int(time.time())
    row = {
        "product_id": product_id,
        "subject_id": subject_id,
        "pii_type": pii_type,
        "token": token,
        "raw_value_enc": encrypt_envelope(raw_value),
        "key_version": key_version,
        "created_at": ts,
        "last_seen_at": ts,
    }
    if token_mode:
        row["token_mode"] = token_mode
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Vault row created for %s/%s (%s)", product_id, subject_id, pii_type)
    return row
