# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')

def get_text(pdf):
    doc = fitz.open(pdf); t="\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t

samples = [
    ('一课一练','Unit 1 Section 2 Grammar（分层练习）.pdf'),
    ('专项练习','【沪教】八上英语完形填空17篇.pdf'),
    ('专项练习','【沪教】八上英语期末短文填空36篇.pdf'),
]
out=[]
for cat,fn in samples:
    p=os.path.join(RES,cat,fn); text=get_text(p)
    ans_start=text.find('【答案】')
    atext=text[ans_start:]
    # count 【答案】 occurrences
    nblocks=len(re.findall(r'【答案】', atext))
    out.append('='*50)
    out.append('%s/%s  atext len=%d  【答案】blocks=%d' % (cat,fn,len(atext),nblocks))
    out.append('--- TAIL of atext (last 1500 chars) ---')
    out.append(atext[-1500:])
out.append('')
out.append('NOTE: if tail shows a compact list of many 答案 with no 解析 => consolidated key exists.')
with open(os.path.join(BASE,'_tail.txt'),'w',encoding='utf-8') as fh:
    fh.write("\n".join(out))
print('done')
