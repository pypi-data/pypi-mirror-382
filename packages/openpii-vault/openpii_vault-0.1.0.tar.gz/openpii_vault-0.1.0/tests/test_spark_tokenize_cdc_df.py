import json, os, base64
import pytest

pyspark = pytest.importorskip("pyspark")
from pyspark.sql import SparkSession, Row, functions as F

from openpii_vault.tokenize_cdc_df import tokenize_cdc_df
from openpii_vault.salt_provider import InMemorySaltProvider

# Optional FPE
try:
    from openpii_vault.fpe_pyffx import PyFFXDigitsProvider
    HAVE_FPE = True
except Exception:
    HAVE_FPE = False


@pytest.fixture(scope="session")
def spark():
    spark = (SparkSession.builder
             .master("local[2]")
             .appName("openpii-vault-tests")
             .getOrCreate())
    yield spark
    spark.stop()


def test_spark_hmac_vaulted_flow(spark):
    rows = [
        Row(subject_id="u1", payload=json.dumps({"customer": {"ssn": "123-45-6789"}})),
        Row(subject_id="u2", payload=json.dumps({"customer": {"ssn": "987-65-4321"}})),
    ]
    df = spark.createDataFrame(rows)

    pii_specs = [{"path": "$.customer.ssn", "type": "ssn", "mode": "hmac_vaulted"}]
    hmac_secret_b64 = base64.b64encode(os.urandom(32)).decode()

    facts, vault = tokenize_cdc_df(
        df=df,
        subject_col="subject_id",
        payload_col="payload",
        event_ts_col=None,
        product_id="checkout",
        pii_specs=pii_specs,
        token_mode=None,
        hmac_secret_b64=hmac_secret_b64,
        salt_provider=InMemorySaltProvider(),
    )

    # Tokenized payload present
    out_col = "payload_tokenized"
    assert out_col in facts.columns
    sample = json.loads(facts.select(out_col).first()[0])
    assert len(sample["customer"]["ssn"]) == 64  # HMAC(hex)

    # Vault rows present (exploded)
    assert vault.count() == 2


@pytest.mark.skipif(not HAVE_FPE, reason="FPE provider (pyffx) not installed")
def test_spark_fpe_with_salts_join(spark):
    rows = [
        Row(subject_id="u1", payload=json.dumps({"user": {"phone": "+1-555-111-2222"}})),
        Row(subject_id="u2", payload=json.dumps({"user": {"phone": "+1-222-333-4444"}})),
    ]
    df = spark.createDataFrame(rows)

    salts = [Row(subject_id="u1", salt_b64=base64.b64encode(os.urandom(32)).decode()),
             Row(subject_id="u2", salt_b64=base64.b64encode(os.urandom(32)).decode())]
    salts_df = spark.createDataFrame(salts)

    pii_specs = [{"path": "$.user.phone", "type": "phone", "mode": "fpe"}]
    prov = PyFFXDigitsProvider(key=os.urandom(32))

    facts, vault = tokenize_cdc_df(
        df=df,
        subject_col="subject_id",
        payload_col="payload",
        event_ts_col=None,
        product_id="checkout",
        pii_specs=pii_specs,
        token_mode=None,
        fpe_provider=prov,
        fpe_key_version="v1",
        salts_df=salts_df,             # salts provided via join
    )

    out_col = "payload_tokenized"
    assert out_col in facts.columns
    sample_tok = json.loads(facts.select(out_col).first()[0])["user"]["phone"]
    # digits-only provider: output should be digits of same length, not equal to original digits
    assert sample_tok.isdigit()
    assert len(sample_tok) == 10
    assert vault.count() == 0  # FPE only => no raw-PII vault rows
