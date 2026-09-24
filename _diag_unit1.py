# -*- coding: utf-8 -*-
"""Diagnostic: inspect Unit 1 解析版 answer layout for robust section parsing."""
import os, re, json, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
cat = next(c for c in man['cats'] if c['name'] == '一课一练')
paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')
pabs = os.path.join(BASE, paper['answerPdf'].replace('/', os.sep))
doc = fitz.open(pabs)
text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
doc.close()

ans_start = text.find('【答案】')
atext = text[ans_start:]

out = []
out.append('=== total 【答案】 count in atext: %d' % atext.count('【答案】'))
out.append('=== CN_SEC headers (pos, roman, title) ===')
for m in CN_SEC.finditer(atext):
    out.append('%d | %s | %s' % (m.start(), m.group(1), m.group(2).strip()))

# split by headers, show first 120 chars of each segment
positions = [m.start() for m in CN_SEC.finditer(atext)]
segments = []
prev = 0
for pos in positions:
    segments.append(atext[prev:pos])
    prev = pos
segments.append(atext[prev:])
out.append('=== %d segments (incl leading pre-header) ===' % len(segments))
for i, seg in enumerate(segments):
    snippet = seg[:140].replace('\n', '\\n')
    out.append('--- seg %d (len=%d): %s' % (i, len(seg), snippet))

out_path = os.path.join(BASE, '_diag_unit1.txt')
open(out_path, 'w', encoding='utf-8').write("\n".join(out))
