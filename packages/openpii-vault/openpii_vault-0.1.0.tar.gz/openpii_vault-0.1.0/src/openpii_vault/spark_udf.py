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
from pyspark.sql import types as T
def build_udf(process_fn):
    vault_row_schema = T.ArrayType(T.StructType([
        T.StructField('product_id', T.StringType()),
        T.StructField('subject_id', T.StringType()),
        T.StructField('pii_type', T.StringType()),
        T.StructField('token', T.StringType()),
        T.StructField('raw_value_enc', T.BinaryType()),
        T.StructField('key_version', T.StringType()),
        T.StructField('created_at', T.LongType()),
        T.StructField('last_seen_at', T.LongType()),
    ]))
    ret_schema = T.StructType([
        T.StructField('json_out', T.StringType()),
        T.StructField('vault_rows', vault_row_schema)
    ])
    from pyspark.sql import functions as F
    return F.udf(process_fn, ret_schema)
