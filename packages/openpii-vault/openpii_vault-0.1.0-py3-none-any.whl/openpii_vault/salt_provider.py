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
from __future__ import annotations
from typing import Protocol
import os, base64
from datetime import datetime, timezone

class SaltProvider(Protocol):
    def get_salt_b64(self, subject_id: str) -> str: ...
    def set_salt_b64(self, subject_id: str, salt_b64: str) -> None: ...
    def delete_salt(self, subject_id: str) -> None: ...
    def status(self, subject_id: str) -> str: ...

def new_subject_salt_b64() -> str:
    return base64.b64encode(os.urandom(32)).decode("ascii")

class InMemorySaltProvider:
    def __init__(self): self._store = {}
    def get_salt_b64(self, subject_id: str) -> str:
        row = self._store.get(subject_id)
        if row and row["status"] == "active":
            return row["salt_b64"]
        salt_b64 = new_subject_salt_b64()
        self._store[subject_id] = {"salt_b64": salt_b64, "status": "active",
                                   "created_at": datetime.now(timezone.utc).isoformat()}
        return salt_b64
    def set_salt_b64(self, subject_id: str, salt_b64: str) -> None:
        self._store[subject_id] = {"salt_b64": salt_b64, "status": "active",
                                   "created_at": datetime.now(timezone.utc).isoformat()}
    def delete_salt(self, subject_id: str) -> None:
        if subject_id in self._store:
            self._store[subject_id]["status"] = "erased"
            self._store[subject_id]["erased_at"] = datetime.now(timezone.utc).isoformat()
    def status(self, subject_id: str) -> str:
        return self._store.get(subject_id, {}).get("status", "missing")
