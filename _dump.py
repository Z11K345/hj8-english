# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')

def get_text(pdf):
    doc = fitz.open(pdf); t="\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t

samples = [
    ('一课一练','Unit 1 Section 1 Reading（分层练习）.pdf'),
    ('专项练习','【沪教】八上英语完形填空17篇.pdf'),
    ('专项练习','【沪教】八上英语单项选择100题.pdf'),
]

out=[]
for cat,fn in samples:
    p=os.path.join(RES,cat,fn); text=get_text(p)
    out.append("="*60)
    out.append(f"{cat}/{fn}  len={len(text)}")
    # first 【答案】 offset
    first = text.find('【答案】')
    out.append(f"first 【答案】 at offset {first} ({100*first//max(1,len(text))}% of text)")
    out.append("--- HEAD (first 1800 chars, question part) ---")
    out.append(text[:1800])
    out.append("--- around first 【答案】 (±900) ---")
    if first>=0:
        out.append(text[max(0,first-600):first+900])
    out.append("")

with open(os.path.join(BASE,'_dump.txt'),'w',encoding='utf-8') as fh:
    fh.write("\n".join(out))
print("done")
