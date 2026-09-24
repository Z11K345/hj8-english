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

def count_qnums(s):
    # question numbers at line start like '1.' '2.'
    return re.findall(r'(?m)^\s*(\d{1,3})\s*[.．.]\s', s)

# card 4 = 完成句子 = 学生版 segs[5]; card 9 = 阅读理解 = segs[10]
out = []
for ci, si, name in [(4,5,'完成句子'), (9,10,'阅读理解')]:
    seg = segs[si]
    nums = count_qnums(seg)
    # unique sorted
    uniq = sorted(set(int(n) for n in nums))
    out.append('SECTION %d (%s): line-start question numbers found=%s ; unique=%s ; max=%s' % (ci, name, nums, uniq, max(uniq) if uniq else 'NA'))
    out.append('  first 300: ' + seg[:300].replace('\n','\\n'))
    out.append('  last 300: ' + seg[-300:].replace('\n','\\n'))
open(os.path.join(BASE, '_diag_count49.txt'), 'w', encoding='utf-8').write("\n".join(out))
