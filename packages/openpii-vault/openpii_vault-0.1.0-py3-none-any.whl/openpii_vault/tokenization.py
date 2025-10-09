
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
"""openpii_vault.tokenization
==============================

Core tokenization primitives for OpenPII Vault.

This module provides:

- `hmac_token(subject_salt_b64, value, hex_len=32)`: legacy helper used by tests;
  returns a deterministic HMAC-SHA256 **hex** digest truncated to 32 chars by default.
- `TokenizationConfig`: configuration dataclass for the tokenizer.
- `tokenize_value(value, subject_salt_b64, cfg)`: main primitive that supports
  both HMAC and FPE (via a provider interface). In HMAC mode it returns a
  **64-char** hex digest. If `cfg.hmac_secret` is missing, it **falls back** to
  the provided `subject_salt_b64` for compatibility with simple test flows.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
from dataclasses import dataclass
from typing import Optional, Protocol, Literal, Any

logger = logging.getLogger(__name__)

TokenMode = Literal["hmac", "fpe"]


class FPEProvider(Protocol):
    """Pluggable FPE provider interface.

    Methods:
        encrypt: Encrypt a plaintext string using a tweak and key version.
        decrypt: Optional reverse transform; not used by current tests.
    """

    def encrypt(self, plaintext: str, *, tweak: bytes, key_version: str) -> str: ...
    def decrypt(self, ciphertext: str, *, tweak: bytes, key_version: str) -> str: ...  # pragma: no cover


@dataclass
class TokenizationConfig:
    """Configuration for tokenization operations.

    Attributes:
        mode: Tokenization mode: "hmac" or "fpe".
        hmac_secret: Raw key bytes for HMAC. If None, will fall back to subject_salt_b64.
        fpe_provider: Optional FPE provider instance implementing `FPEProvider`.
        fpe_key_version: Version label for the FPE key material.
    """
    mode: TokenMode = "hmac"
    hmac_secret: Optional[bytes] = None
    fpe_provider: Optional[FPEProvider] = None
    fpe_key_version: str = "v1"


def hmac_token(subject_salt_b64: str, value: str, hex_len: int = 32) -> str:
    """Legacy deterministic HMAC helper (used by unit tests).

    Args:
        subject_salt_b64: Base64-encoded per-subject salt/key.
        value: Input string.
        hex_len: Length to truncate the hex digest (defaults to 32).

    Returns:
        str: Deterministic hex digest string truncated to `hex_len`.
    """
    if value is None:
        return None  # type: ignore[return-value]
    key = base64.b64decode(subject_salt_b64 or "")
    digest = hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:hex_len]


def tokenize_value(value, subject_salt_b64, cfg: TokenizationConfig) -> str:
    """Tokenize a scalar string using HMAC or FPE.

    This function accepts **positional arguments** for compatibility with tests:
        tokenize_value("alice@example.com", "c2FsdDE=", cfg)

    HMAC mode:
        - Uses `cfg.hmac_secret` if provided; otherwise **falls back** to the
          decoded `subject_salt_b64` to preserve legacy/simple call behavior.
        - Returns the full **64-char** hex digest from SHA-256.

    FPE mode:
        - Delegates to `cfg.fpe_provider.encrypt(...)` and returns its result.
        - Requires `cfg.fpe_provider` to be non-None.

    Args:
        value: Input string to tokenize.
        subject_salt_b64: Base64-encoded per-subject salt (tweak and/or fallback key).
        cfg: TokenizationConfig selecting "hmac" or "fpe".

    Returns:
        str: Tokenized output string.
    """
    if value is None:
        return None  # type: ignore[return-value]

    if cfg.mode == "hmac":
        # Decode the per-subject salt ("tweak")
        tweak = base64.b64decode(subject_salt_b64 or "")
        if cfg.hmac_secret:
            # Derive a per-subject key from the library secret and subject salt
            per_subject_key = hmac.new(cfg.hmac_secret, tweak, hashlib.sha256).digest()
            key = per_subject_key
        else:
            # Legacy fallback: use the subject salt directly as the HMAC key
            key = tweak
        return hmac.new(key, value.encode("utf-8"), hashlib.sha256).hexdigest()

    if cfg.mode == "fpe":
        if not cfg.fpe_provider:
            raise ValueError("FPE mode selected but no fpe_provider configured")
        tweak = base64.b64decode(subject_salt_b64 or "")
        return cfg.fpe_provider.encrypt(value, tweak=tweak, key_version=cfg.fpe_key_version)

    raise ValueError(f"Unknown tokenization mode: {cfg.mode}")


__all__ = ["TokenizationConfig", "hmac_token", "tokenize_value"]
