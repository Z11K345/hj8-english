# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
LOG = os.path.join(BASE, '_dbg119.txt')
out = []

CN_NUM = re.compile(r'(\d{1,3})\s*[.．.]\s*')

def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs); t = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t

def _remove_jiexi(body):
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', body)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    return body

def _extract_numbered(text, expected):
    body = _remove_jiexi(text)
    parts = re.split(CN_NUM, body)
    items = []
    for k in range(1, len(parts)-1, 2):
        t = parts[k+1].strip()
        if t:
            items.append(t)
    return items[:expected]

def _find_answer_section(text, markers):
    search_start = 0
    while True:
        pos = -1; fm = None
        for mk in markers:
            idx = text.find(mk, search_start)
            if idx >= 0 and (pos < 0 or idx < pos):
                pos = idx; fm = mk
        if pos < 0: return None
        tail = text[pos:]
        if re.search(r'(?m)^\s*\d{1,3}\s*[.．.]\s*\S', tail[:3000]):
            return tail
        search_start = pos + len(fm)

text = pdf_text('resources/专项练习/【沪教】八上英语期末完成句子119题.pdf')
tail = _find_answer_section(text, ['解析版）','解析版)'])
out.append('tail found: %s' % (tail is not None))
if tail:
    out.append('tail first 120: ' + tail[:120].replace('\n','\\n'))
    items = _extract_numbered(tail, 119)
    out.append('item count: %d' % len(items))
    out.append('first 5: ' + ' | '.join(items[:5]))
    out.append('last 5: ' + ' | '.join(items[-5:]))
    # show items around 30-34 to inspect embedded numbers
    out.append('items 30-35: ' + ' || '.join('%d:%s' % (i+1, items[i]) for i in range(30, min(36,len(items)))))
with open(LOG,'w',encoding='utf-8') as f:
    f.write("\n".join(out))
