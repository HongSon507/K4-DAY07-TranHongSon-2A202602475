#!/usr/bin/env python3
"""Kiểm tra Checkpoint 2 (CP2) theo chuẩn docs/DATA_COLLECTION.md."""

import csv
import re
from pathlib import Path

D = Path('data/hoc-bong-chon-loc')
REQ = ['doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience']

mds = sorted(D.glob('*.md'))
rows = list(csv.DictReader(open(D / 'sources.csv', encoding='utf-8')))
ids, auds = [], {}

for p in mds:
    raw_fm = p.read_text(encoding='utf-8').split('---')[1]
    fm = dict(re.findall(r'^(\w+):\s*["\']?(.*?)["\']?\s*$', raw_fm, re.M))
    ids.append(fm.get('doc_id'))
    aud = fm.get('audience')
    auds[aud] = auds.get(aud, 0) + 1
    is_ok = all(k in fm for k in REQ) and fm.get('doc_id') == p.stem
    print(f"{p.name:45} {'OK' if is_ok else 'THIEU METADATA'}")

print('so file :', len(mds), '(can 5-10)')
print('csv     :', 'khop' if sorted(r['doc_id'] for r in rows) == sorted(ids) else 'LECH')
print('audience:', auds)
