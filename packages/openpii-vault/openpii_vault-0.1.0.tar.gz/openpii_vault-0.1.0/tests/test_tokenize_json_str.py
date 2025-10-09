import os, base64, json
import pytest

from openpii_vault.tokenize_cdc_df import tokenize_json_str
from openpii_vault.tokenization import TokenizationConfig
from openpii_vault.salt_provider import InMemorySaltProvider

# Optional FPE
try:
    from openpii_vault.fpe_pyffx import PyFFXDigitsProvider
    HAVE_FPE = True
except Exception:
    HAVE_FPE = False


def _b64(n=32) -> str:
    return base64.b64encode(os.urandom(n)).decode("ascii")


def test_hmac_vaulted_generates_vault_rows():
    payload = {"customer": {"ssn": "123-45-6789"}}
    specs = [
        {"path": "$.customer.ssn", "type": "ssn", "mode": "hmac_vaulted"},
    ]

    # HMAC secret required
    hmac_secret_b64 = _b64()

    obj, vault_rows = tokenize_json_str(
        json_str=json.dumps(payload),
        subject_id="u1",
        product_id="checkout",
        pii_specs=specs,
        token_mode=None,                   # use per-field mode
        hmac_secret_b64=hmac_secret_b64,  # used by hmac_vaulted
        salt_provider=InMemorySaltProvider(),  # optional for HMAC
    )

    # tokenized value should be hex-ish (length 64 for sha256)
    tokenized_ssn = obj["customer"]["ssn"]
    assert isinstance(tokenized_ssn, str) and len(tokenized_ssn) == 64

    # vault row emitted with meta
    assert len(vault_rows) == 1
    row = vault_rows[0]
    assert row["product_id"] == "checkout"
    assert row["subject_id"] == "u1"
    assert row["pii_type"] == "ssn"
    assert row["token_mode"] == "hmac"
    assert "key_version" in row


@pytest.mark.skipif(not HAVE_FPE, reason="FPE provider (pyffx) not installed")
def test_email_preserve_domain_with_fpe_requires_salt_and_preserves_domain():
    payload = {"user": {"email": "Alice@Example.COM"}}
    specs = [
        {"path": "$.user.email", "type": "email", "mode": "fpe", "preserve_domain": True},
    ]

    salt_provider = InMemorySaltProvider()
    fpe_key = os.urandom(32)
    prov = PyFFXDigitsProvider(key=fpe_key)  # digits provider won't transform email local-part; this is illustrative

    obj, vault_rows = tokenize_json_str(
        json_str=json.dumps(payload),
        subject_id="u1",
        product_id="checkout",
        pii_specs=specs,
        token_mode=None,
        fpe_provider=prov,
        fpe_key_version="v1",
        salt_provider=salt_provider,   # required for FPE
    )

    tok = obj["user"]["email"]
    assert "@" in tok
    local, domain = tok.split("@", 1)
    assert domain == "example.com"  # lowercased, preserved
    assert local != "alice"         # transformed (in real FPE for emails you'd use an alphanumeric provider)
    assert vault_rows == []         # FPE mode does not produce raw vault rows


def test_fpe_without_salt_raises():
    payload = {"user": {"phone": "+1-555-111-2222"}}
    specs = [{"path": "$.user.phone", "type": "phone", "mode": "fpe"}]

    with pytest.raises(ValueError):
        tokenize_json_str(
            json_str=json.dumps(payload),
            subject_id="u1",
            product_id="checkout",
            pii_specs=specs,
            fpe_provider=None,            # not relevant: error comes from missing salt
            salt_provider=None,           # missing salt => error
        )
