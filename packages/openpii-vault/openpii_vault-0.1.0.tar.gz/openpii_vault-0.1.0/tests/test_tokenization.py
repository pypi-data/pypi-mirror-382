from openpii_vault.tokenization import hmac_token

def test_hmac_deterministic():
    t1 = hmac_token('c2FsdDE=', 'value'); t2 = hmac_token('c2FsdDE=', 'value')
    assert t1 == t2 and len(t1)==32
