import os, base64
import pytest

from openpii_vault.tokenization import TokenizationConfig, tokenize_value

# FPE provider is optional; skip tests if not available
try:
    from openpii_vault.fpe_pyffx import PyFFXDigitsProvider
    HAVE_FPE = True
except Exception:
    HAVE_FPE = False


def _b64(n=32) -> str:
    return base64.b64encode(os.urandom(n)).decode("ascii")


def test_hmac_per_subject_isolation_and_determinism():
    secret = os.urandom(32)
    cfg = TokenizationConfig(mode="hmac", hmac_secret=secret)
    s1 = _b64()
    s2 = _b64()

    # Same subject salt + same value => identical token
    t1a = tokenize_value("alice@example.com", s1, cfg)
    t1b = tokenize_value("alice@example.com", s1, cfg)
    assert t1a == t1b

    # Different subject salt => different token
    t2 = tokenize_value("alice@example.com", s2, cfg)
    assert t2 != t1a


@pytest.mark.skipif(not HAVE_FPE, reason="FPE provider (pyffx) not installed")
def test_fpe_roundtrip_digits():
    key = os.urandom(32)
    prov = PyFFXDigitsProvider(key=key)
    cfg = TokenizationConfig(mode="fpe", fpe_provider=prov, fpe_key_version="v1")
    salt = _b64()

    token = tokenize_value("5551112222", salt, cfg)
    plain = prov.decrypt(token, tweak=base64.b64decode(salt), key_version="v1")
    assert plain == "5551112222"
