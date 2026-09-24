# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
cat = next(c for c in man['cats'] if c['name'] == '一课一练')
paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')
doc = fitz.open(os.path.join(BASE, paper['pdf'].replace('/', os.sep)))
stu = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close()

positions = [m.start() for m in CN_SEC.finditer(stu)]
segs = []
prev = 0
for pos in positions:
    segs.append(stu[prev:pos]); prev = pos
segs.append(stu[prev:])

out = []
# 学生版 card-section 5 -> segs[6]; 6 -> segs[7]
for ci, si in [(5,6),(6,7)]:
    seg = segs[si]
    # count blank-like tokens: runs of _ or (xxx) cues
    underscores = len(re.findall(r'_+', seg))
    # also count lines starting with option letters A-E (for 阅读还原)
    out.append('############ card-section %d | total len=%d | underscore-runs=%d ############' % (ci, len(seg), underscores))
    out.append(seg.replace('\n','\\n'))
open(os.path.join(BASE, '_diag_full59.txt'), 'w', encoding='utf-8').write("\n".join(out))
