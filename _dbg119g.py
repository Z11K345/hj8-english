# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
def check(pdf, marker, label):
    doc = fitz.open(pdf)
    text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    pos = text.find(marker)
    q = text[:pos]
    # line-start numbers
    nums = [int(m.group(1)) for m in re.finditer(r'(?m)^\s*(\d{1,3})\s*[.．.]\s*', q)]
    distinct = sorted(set(nums))
    out = "%s : qregion_len=%d marker_pos=%d  distinct_q_nums=%s  max=%s count=%d" % (
        label, len(q), pos, distinct[:5], distinct[-5:] if distinct else [], len(distinct))
    return out

r1 = check(os.path.join(BASE,'resources/专项练习/【沪教】八上英语期末完成句子119题.pdf'), '解析版）', '完成句子119')
r2 = check(os.path.join(BASE,'resources/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.pdf'), '答案版）', '适当形式70')
with open(os.path.join(BASE,'_dbg119g.txt'),'w',encoding='utf-8') as f:
    f.write(r1+"\n"+r2)
print(r1)
print(r2)
