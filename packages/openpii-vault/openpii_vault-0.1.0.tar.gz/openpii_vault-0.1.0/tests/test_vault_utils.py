from openpii_vault.vault_utils import make_vault_row

def test_vault_row_shape():
    r = make_vault_row('A','u1','email','tok','raw')
    assert r['product_id']=='A' and r['pii_type']=='email' and 'raw_value_enc' in r
