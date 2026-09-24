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
# 学生版 card-section 5 -> segs[6]
seg5 = segs[6]
# split into A and B by 'B 语法填空'
a_part = seg5.split('B 语法填空')[0]
b_part = seg5.split('B 语法填空')[1] if 'B 语法填空' in seg5 else ''
def count_blanks(s):
    # count numbered blank cues like 1._____ or 1._______(x) or 1. P________
    nums = re.findall(r'(?m)^\s*(\d+)\s*\.', s)
    # also underscore runs
    us = len(re.findall(r'_+', s))
    return len(nums), us, nums
na, ua, nsa = count_blanks(a_part)
nb, ub, nsb = count_blanks(b_part)
out.append('SECTION5 A: numbered=%d underscores=%d nums=%s' % (na, ua, nsa))
out.append('SECTION5 B: numbered=%d underscores=%d nums=%s' % (nb, ub, nsb))
out.append('A last 200: ' + a_part[-200:].replace('\n','\\n'))
out.append('B full (%d): ' % len(b_part) + b_part.replace('\n','\\n'))

# 阅读还原 card-section 6 -> segs[7]
seg6 = segs[7]
# gaps are positions between paragraphs; count occurrences of the 1..5 standalone numbers
gaps = re.findall(r'(?m)^\s*([1-5])\s*$', seg6)
out.append('SECTION6 gap-standalone-numbers: %s (count=%d)' % (gaps, len(gaps)))
# option lines A. B. C. D. E.
opts = re.findall(r'(?m)^\s*([A-E])\.\s', seg6)
out.append('SECTION6 option-lines: %s' % opts)

open(os.path.join(BASE, '_diag_count59.txt'), 'w', encoding='utf-8').write("\n".join(out))
