from openpii_vault.json_path_utils import parse_json_path

def test_parse_basic():
    assert parse_json_path('$.a.b[0].c') == ['a','b',0,'c']

def test_parse_wildcard():
    assert parse_json_path('$.a[*].b') == ['a','*','b']
