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

HEADER_RE = re.compile(r'(?m)^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')
def _remove_jiexi(body):
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', body)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    return body
DELIM_LS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
DELIM_ANY = re.compile(r'(\d{1,3})\s*[.．.]\s*')

out = []
text = pdf_text(os.path.join(BASE, 'resources/专项练习', '【沪教】八上英语期末完成句子119题.pdf'))
pos = text.find('解析版）')
tail = text[pos:]
out.append('tail len=%d' % len(tail))
for stage, fn in [('raw', lambda x: x), ('jiexi', _remove_jiexi), ('header', lambda x: HEADER_RE.sub('', x))]:
    b = fn(tail) if stage!='raw' else tail
    for n in ['98','100']:
        out.append('%s: contains %s? %s' % (stage, n, n in b))
body = HEADER_RE.sub('', _remove_jiexi(tail))
out.append('body len=%d' % len(body))
ls = [(m.group(1), m.start()) for m in DELIM_LS.finditer(body)]
anym = [(m.group(1), m.start()) for m in DELIM_ANY.finditer(body)]
out.append('DELIM_LS count=%d, has 98? %s has 100? %s' % (len(ls), ('98',0) in [(x,0) for x in ls] , any(x=='100' for x,__ in ls)))
out.append('DELIM_ANY count=%d, has 98? %s has 100? %s' % (len(anym), any(x=='98' for x,__ in anym), any(x=='100' for x,__ in anym)))
# find indices of 98 100 in body
for n in ['98','100']:
    i = body.find(n)
    out.append('body find %s at %s ctx=%r' % (n, i, body[i-3:i+12] if i>=0 else 'NONE'))

with open(os.path.join(BASE,'_dbg119j.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
