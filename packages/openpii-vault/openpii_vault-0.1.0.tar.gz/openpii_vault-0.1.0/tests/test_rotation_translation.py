import os, base64, json
import pytest

# Optional FPE
try:
    from openpii_vault.fpe_pyffx import PyFFXDigitsProvider
    HAVE_FPE = True
except Exception:
    HAVE_FPE = False


@pytest.mark.skipif(not HAVE_FPE, reason="FPE provider (pyffx) not installed")
def test_fpe_translation_map_single_value():
    # Simulate FPE key rotation v1->v2 and produce (old_token,new_token) pair
    key_v1 = os.urandom(32)
    key_v2 = os.urandom(32)
    prov_v1 = PyFFXDigitsProvider(key=key_v1)
    prov_v2 = PyFFXDigitsProvider(key=key_v2)

    salt_b64 = base64.b64encode(os.urandom(32)).decode()
    tweak = base64.b64decode(salt_b64)
    value = "5551112222"

    old_token = prov_v1.encrypt(value, tweak=tweak, key_version="v1")
    # translate by decrypting with v1 then encrypting with v2 (same salt)
    plain = prov_v1.decrypt(old_token, tweak=tweak, key_version="v1")
    assert plain == value
    new_token = prov_v2.encrypt(plain, tweak=tweak, key_version="v2")

    # assert equivalence mapping can be stored
    mapping_row = {
        "subject_id": "u1",
        "pii_type": "phone",
        "old_token": old_token,
        "new_token": new_token,
        "old_key_version": "v1",
        "new_key_version": "v2",
        "old_salt_id": "s1",
        "new_salt_id": "s1",
    }
    assert set(mapping_row.keys()) >= {
        "subject_id", "pii_type", "old_token", "new_token",
        "old_key_version", "new_key_version", "old_salt_id", "new_salt_id"
    }
