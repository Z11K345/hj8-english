# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
pdf = os.path.join(BASE, 'resources/专项练习/【沪教】八上英语期末完形填空20篇.pdf')
doc = fitz.open(pdf)
text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
doc.close()
ans_start = text.find('【答案】')
atext = text[ans_start:]
positions = [m.start() for m in re.finditer(r'【答案】', atext)]
out = []
for k, pos in enumerate(positions[:6]):
    rest = atext[pos+len('【答案】'):]
    # block_end replica
    m_b = re.search(r'【', rest); m_j = re.search(r'解析', rest)
    m_q = re.search(r'(?m)^\s*\d+\s*[.．、)）]\s*\S.{9,}', rest)
    cands = [x.start() for x in (m_b, m_j, m_q) if x]
    end = min(cands) if cands else len(rest)
    seg = rest[:end]
    seg = re.split(r'【解析】', seg)[0]; seg = re.split(r'解析', seg)[0]
    out.append('--- block %d ---' % k)
    out.append('raw seg (first 200): %r' % seg[:200])
    out.append('seg len=%d' % len(seg))
open(os.path.join(BASE, '_diag3.txt'), 'w', encoding='utf-8').write("\n".join(out))
print('done')
