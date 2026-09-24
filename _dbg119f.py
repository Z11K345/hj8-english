# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
pdf = os.path.join(BASE, 'resources/专项练习/【沪教】八上英语期末完成句子119题.pdf')
doc = fitz.open(pdf)
text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
doc.close()

# find answer section marker
markers = ['解析版）','解析版)']
pos = -1
for mk in markers:
    idx = text.find(mk)
    if idx >= 0 and (pos < 0 or idx < pos):
        pos = idx
tail = text[pos:]

out = []
out.append("tail length=%d, pos=%d" % (len(tail), pos))

# print ALL digit-leading matches in tail with context
CN = re.compile(r'(\d{1,3})\s*[.．.、]')
for m in CN.finditer(tail):
    num = int(m.group(1))
    if 30 <= num <= 105:
        s = max(0, m.start()-15); e = min(len(tail), m.end()+25)
        ctx = tail[s:e].replace('\n','\\n')
        out.append("num=%d @%d : ...%s..." % (num, m.start(), ctx))

# specifically find any '98' or '100' substring
out.append("---- raw search for 98 / 100 ----")
for needle in ['98','100','34']:
    for m in re.finditer(re.escape(needle), tail):
        s = max(0, m.start()-25); e = min(len(tail), m.end()+25)
        ctx = tail[s:e].replace('\n','\\n')
        out.append("%s @%d : ...%s..." % (needle, m.start(), ctx))

with open(os.path.join(BASE,'_dbg119f.txt'),'w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("written", len(out), "lines")
