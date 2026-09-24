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
# 学生版 header i -> segs[i+1]; card index i == header i. So 学生版 content for card i is segs[i+1].
idx_map = {5:6, 6:7, 9:10}
out = []
for ci, si in idx_map.items():
    out.append('############ 学生版 card-section %d (segs[%d]) ############' % (ci, si))
    out.append(segs[si][:1400].replace('\n','\\n'))
open(os.path.join(BASE, '_diag_stu59.txt'), 'w', encoding='utf-8').write("\n".join(out))
