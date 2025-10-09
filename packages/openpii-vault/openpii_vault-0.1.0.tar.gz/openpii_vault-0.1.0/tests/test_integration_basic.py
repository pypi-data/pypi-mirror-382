from openpii_vault.tokenize_cdc_df import tokenize_json_str

def test_email_domain_preserved():
    jj = '{"customer":{"email":"User@Example.com"}}'
    out, rows = tokenize_json_str(jj, 'u1', 'c2FsdDE=', 'A', [{"path":"$.customer.email","type":"email","preserve_domain":True}])
    assert "@example.com" in out and rows and rows[0]['pii_type']=='email'
