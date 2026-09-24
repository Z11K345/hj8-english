# -*- coding: utf-8 -*-
import os, re, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')

def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs)
    t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return t

out = []
for fname, needles in [
    ('【沪教】八上英语期末完成句子119题.pdf', ['98', '100']),
    ('【沪教】八上英语期末用单词的适当形式填空70题.pdf', ['22']),
]:
    text = pdf_text(os.path.join(BASE, 'resources/专项练习', fname))
    for n in needles:
        idx = text.find(n)
        seg = text[idx-5:idx+15]
        out.append('%s find %r -> repr=%r' % (fname, n, seg))
        # try matching a number at idx
        m = re.match(r'\d{1,3}(?:[.．.]\s*|\s+(?=\S))', text[idx:])
        out.append('   match-from-idx: %r' % (m.group(0) if m else None))

# test DELIM_LS on a crafted line-start space case
DLS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
test = "\nabc\n98 Either\nor"
mm = list(DLS.finditer(test))
out.append('TEST crafted: matches=%r' % [(m.group(1), m.start()) for m in mm])

with open(os.path.join(BASE,'_dbg119i.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
