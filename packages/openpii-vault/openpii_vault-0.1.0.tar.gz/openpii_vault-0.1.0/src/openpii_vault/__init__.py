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
"""
OpenPII Vault package initialization.

This file intentionally avoids importing submodules to prevent circular imports
and to keep `import openpii_vault` lightweight during test collection.
Import submodules explicitly, e.g.:
    from openpii_vault.tokenize_cdc_df import tokenize_json_str, tokenize_cdc_df
"""
from __future__ import annotations

__all__ = ["__version__", "__author__", "__license__"]

__version__ = "0.2.0"
__author__ = "Shobha Sethuraman"
__license__ = "Apache-2.0"
