# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, '_dbg119c.txt')
out = []
CN_NUM = re.compile(r'(\d{1,3})\s*[.．.]\s*')
HEADER_RE = re.compile(r'^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')
def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs); t="\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t
def _remove_jiexi(body):
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', body)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    return body
def _strip_headers(tail):
    lines = tail.splitlines()
    kept = [ln for ln in lines if not HEADER_RE.match(ln.strip())]
    return "\n".join(kept)
def _extract_numbered(text, expected):
    body = _remove_jiexi(text)
    parts = re.split(CN_NUM, body)
    items = []
    for k in range(1, len(parts)-1, 2):
        t = parts[k+1].strip()
        if t: items.append(t)
    return items[:expected]
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
# search for 118./119. in raw tail
out.append('has 118. : %s' % ('118.' in tail or '118．' in tail))
out.append('has 119. : %s' % ('119.' in tail or '119．' in tail))
# count occurrences of line-start 118 / 119
out.append('line 118 count: %d' % len(re.findall(r'(?m)^\s*118\s*[.．.]', tail)))
out.append('line 119 count: %d' % len(re.findall(r'(?m)^\s*119\s*[.．.]', tail)))
# strip headers then extract
clean = _strip_headers(tail)
items = _extract_numbered(clean, 119)
out.append('after header-strip count: %d' % len(items))
out.append('item 64 = %r' % (items[63] if len(items)>63 else 'NA'))
with open(LOG,'w',encoding='utf-8') as f:
    f.write("\n".join(out))
