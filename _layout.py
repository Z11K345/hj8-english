# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$')

def get_text(pdf):
    doc = fitz.open(pdf); t="\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t

samples = [
    ('一课一练','Unit 1 Section 2 Grammar（分层练习）.pdf'),
    ('一课一练','Unit 1 Section 1 Reading（分层练习）.pdf'),
    ('专项练习','【沪教】八上英语完形填空17篇.pdf'),
]

out=[]
for cat,fn in samples:
    p=os.path.join(RES,cat,fn); text=get_text(p)
    # 找 板块 header 与 【答案】 的相对顺序（用字符偏移）
    events=[]
    for m in CN_SEC.finditer(text):
        events.append((m.start(), 'SEC', m.group(2).strip()[:16]))
    for m in re.finditer(r'【答案】', text):
        events.append((m.start(), 'ANS', ''))
    events.sort()
    out.append(f"\n### {cat}/{fn}")
    cur=None
    for off,kind,val in events:
        if kind=='SEC':
            out.append(f"  [板块] {val}")
        else:
            out.append(f"         ↑【答案】")
    # 统计：每个板块header后到下一个板块header之间的【答案】数量
    out.append("  --- 各板块区间内的【答案】数（若末尾板块含大量答案则偏末尾）---")
    secs=[(m.start(), m.group(2).strip()[:14]) for m in CN_SEC.finditer(text)]
    if not secs:
        secs=[(0,'全卷')]
    secs.append((len(text),'END'))
    for i in range(len(secs)-1):
        s,e=secs[i][0],secs[i+1][0]
        cnt=len(re.findall(r'【答案】', text[s:e]))
        if cnt: out.append(f"    板块[{secs[i][1]}]: {cnt} 个答案块")
    tot=len(re.findall(r'【答案】',text)); out.append(f"  总计【答案】块={tot}")

with open(os.path.join(BASE,'_layout.txt'),'w',encoding='utf-8') as fh:
    fh.write("\n".join(out))
print("done")
