# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs)
    t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close(); return t
text = pdf_text(os.path.join(BASE,'resources/专项练习','【沪教】八上英语期末用单词的适当形式填空70题.pdf'))
pos = text.find('答案版）')
tail = text[pos:]
out = []
# show all LS/ANY matches with num 18..26
DELIM_LS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
DELIM_ANY = re.compile(r'(\d{1,3})\s*[.．.]\s*')
for m in DELIM_LS.finditer(tail):
    if 18 <= int(m.group(1)) <= 26:
        out.append('LS num=%s @%d ctx=%r' % (m.group(1), m.start(), tail[m.start()-3:m.start()+20]))
out.append('---- raw around 22 in tail ----')
i = tail.find('22')
while i >= 0 and i < len(tail):
    seg = tail[i-10:i+60]
    if '22' in seg:
        out.append('@%d repr=%r' % (i, seg))
    i = tail.find('22', i+1)
    if i > 4000: break
with open(os.path.join(BASE,'_dbg119k.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
