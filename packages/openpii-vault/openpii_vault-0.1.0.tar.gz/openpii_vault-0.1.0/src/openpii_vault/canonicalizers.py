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
import re
def canon_email(v: str):
    if v is None: return None, None
    v = v.strip().lower()
    if '@' not in v: return v, None
    local, domain = v.split('@', 1)
    return f"{local}@{domain}", domain
def canon_phone(v: str):
    if v is None: return None
    digits = re.sub(r'\D','', v)
    if digits.startswith('1') and len(digits)==11: digits = digits[1:]
    return digits
def canon_name(v: str): return ' '.join((v or '').split()).lower() or None
def canon_address(v: str): return ' '.join((v or '').split()).lower() or None
def canon_dob(v: str): return (v or '').strip() or None
