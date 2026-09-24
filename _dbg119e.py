# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, '_dbg119e.txt')
out = []
HEADER_RE = re.compile(r'^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')
def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs); t="\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t
def _remove_jiexi(body):
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', body)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    return body
def _strip_headers(tail):
    return "\n".join(ln for ln in tail.splitlines() if not HEADER_RE.match(ln.strip()))
def _find_answer_section(text, markers):
    s=0
    while True:
        pos=-1; fm=None
        for mk in markers:
            idx=text.find(mk,s)
            if idx>=0 and (pos<0 or idx<pos): pos=idx; fm=mk
        if pos<0: return None
        tail=text[pos:]
        if re.search(r'(?m)^\s*\d{1,3}\s*[.．.]\s*\S', tail[:3000]): return tail
        s=pos+len(fm)
text = pdf_text('resources/专项练习/【沪教】八上英语期末完成句子119题.pdf')
tail = _find_answer_section(text, ['解析版）','解析版)'])
clean = _strip_headers(tail)
body = _remove_jiexi(clean)
idx = body.find('97.')
out.append('region 97-119 raw:')
out.append(body[idx:idx+500].replace('\n','\\n'))
with open(LOG,'w',encoding='utf-8') as f:
    f.write("\n".join(out))
