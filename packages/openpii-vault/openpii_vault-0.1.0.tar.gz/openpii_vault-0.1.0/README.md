# OpenPII Vault

> **Privacy-first tokenization and vaulting for modern data pipelines.**  
> OpenPII Vault makes it easy to de-identify, tokenize, and vault PII *at ingestion* — not at the end of your data lifecycle — so analytics, AI, and compliance teams can safely collaborate on secure, privacy-preserving datasets.

[![CI](https://github.com/logicoflife/openpii-vault/actions/workflows/ci.yml/badge.svg)](https://github.com/logicoflife/openpii-vault/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)]()
[![PyPI](https://img.shields.io/pypi/v/openpii-vault.svg)](https://pypi.org/project/openpii-vault/)


**Author:** Shobha Sethuraman ([shobha.sethuraman@gmail.com](mailto:shobha.sethuraman@gmail.com))

---

## 💡 Why OpenPII Vault?

**OpenPII Vault** helps data teams handle *Personally Identifiable Information (PII)* responsibly — without slowing down analytics or product velocity.

Instead of keeping sensitive data in its raw form until the end of its lifecycle, OpenPII Vault lets you **de-identify at the source**, ensuring:

- 🔒 **Privacy by design** — PII is tokenized or vaulted immediately upon collection.
- ⚡ **Analytics-ready** — Deterministic tokenization preserves joins, counts, and correlations.
- 🧠 **LLM-safe data sharing** — large datasets can be scanned and trained on without privacy risk.
- 🧩 **Vaulted reversibility** — selectively re-identify authorized data for operations or compliance.
- 🧰 **Plug-and-play integration** — works with AWS Glue, PySpark, and Iceberg tables.
- 🪶 **Lightweight** — pure Python, easy to deploy in ETL or streaming contexts.

---

## 🚀 Quickstart

Install:

```bash
pip install openpii-vault
```

Tokenize a JSON record (for example, from a DynamoDB CDC event):

```python
from openpii_vault.tokenize_cdc_df import tokenize_json_str

json_record = {
    "subject_id": "user123",
    "email": "alice@example.com",
    "phones": ["+1-555-111-2222"],
    "address": {"street": "123 Main St", "city": "Denver"},
}

pii_paths = {
    "email": "$.email",
    "phone": "$.phones[*]",
    "address": "$.address.street",
}

tokenized, vault_rows = tokenize_json_str(
    json_str=json_record,
    pii_paths=pii_paths,
    subject_id="user123",
    product_id="checkout",
)

print(tokenized)
print(vault_rows)
```

---

## 🧩 Example: AWS Glue / Iceberg Integration

Below is an example AWS Glue job that reads DynamoDB CDC JSONs from S3, tokenizes PII in-place, and writes to Iceberg for long-term analytics storage:

```python
from pyspark.sql import SparkSession
from openpii_vault.spark_udf import tokenize_pii_udf

spark = SparkSession.builder.appName("tokenize-cdc").getOrCreate()

raw_df = spark.read.json("s3://my-landing-zone/dynamodb/checkout_events/")

pii_config = {
    "email": "$.contact.email",
    "phone": "$.contact.phones[*]",
    "name": "$.user.name",
}

tokenized_df = raw_df.withColumn("data", tokenize_pii_udf("data", pii_config))

(
    tokenized_df.writeTo("glue_catalog.raw_persistent.checkout_events")
    .option("partitioning", "date, subject_id")
    .tableProperty("format", "iceberg")
    .append()
)
```

---

## 🧱 Architecture (at a glance)
```
[ Ingestion (CDC from DynamoDB) ]
           ↓
 [ Tokenization + Vaulting (Glue Job) ]
           ↓
 [ Iceberg  (PII-free) Zone ]
           ↓
 [ Analytics & AI Use Cases ]
           ↓
 [ Optional Vault (for reversible lookups) ]
```

---

## 📜 License

```
Copyright (c) 2025 Shobha Sethuraman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0
```

---

## 🌍 Roadmap

- ✅ In-place tokenization for JSON / nested PII paths  
- 🚧 KMS envelope encryption adapter  
- 🚧 Multi-product subject-level consent management  
- 🧪 Spark streaming and Kafka integration  
- 🧩 dbt / Cube.js metric store plugin  

---

## 🤝 Contributing

Contributions are welcome!  
See [`CONTRIBUTING.md`](CONTRIBUTING.md) for setup, testing, and PR guidelines.  
If you discover a security issue, please see [`SECURITY.md`](SECURITY.md).

---

## 🌐 Links

- [Documentation](https://github.com/logicoflife/openpii-vault#readme)
- [Issues](https://github.com/logicoflife/openpii-vault/issues)
- [PyPI](https://pypi.org/project/openpii-vault/)

## License

Licensed under the Apache License, Version 2.0 (Apache-2.0).

- Copyright (c) 2025 Shobha Sethuraman  
- SPDX-License-Identifier: Apache-2.0

See the [LICENSE](./LICENSE) file for the full text of the license.
