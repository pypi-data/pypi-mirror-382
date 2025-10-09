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
# Minimal JSON path helpers with wildcard support: $.a.b[*].c
def parse_json_path(path: str):
    assert path.startswith('$.')
    parts = []
    token = path[2:]
    buf = ''
    i = 0
    while i < len(token):
        c = token[i]
        if c == '.':
            if buf: parts.append(buf); buf=''
            i+=1; continue
        if c == '[':
            if buf: parts.append(buf); buf=''
            j = token.find(']', i)
            idx = token[i+1:j]
            parts.append('*' if idx=='*' else int(idx))
            i = j+1; continue
        buf += c; i+=1
    if buf: parts.append(buf)
    return parts

def walk_set(doc, parts, on_value):
    def _rec(parent, key, node, idx):
        if idx == len(parts):
            on_value(parent, key, node); return
        seg = parts[idx]
        if isinstance(seg, str):
            if isinstance(node, dict) and seg in node:
                _rec(node, seg, node[seg], idx+1)
        elif seg == '*':
            if isinstance(node, list):
                for i, el in enumerate(node):
                    _rec(node, i, el, idx+1)
        elif isinstance(seg, int):
            if isinstance(node, list) and 0 <= seg < len(node):
                _rec(node, seg, node[seg], idx+1)
    _rec(None, None, doc, 0)
