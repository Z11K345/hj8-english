# -*- coding: utf-8 -*-
import os, re, json, fitz, traceback
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')

def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs)
    t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return t

HEADER_RE = re.compile(r'(?m)^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')
DELIM_LS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
DELIM_ANY = re.compile(r'(\d{1,3})\s*[.．.]\s*')

def _extract_numbered(text, expected):
    matches = []
    for m in DELIM_LS.finditer(text): matches.append((m.start(), m.end()))
    for m in DELIM_ANY.finditer(text): matches.append((m.start(), m.end()))
    matches.sort()
    dedup = []
    for s, e in matches:
        if dedup and s <= dedup[-1][0] + 3:
            if s < dedup[-1][0]:
                dedup[-1] = (s, e)
            continue
        dedup.append((s, e))
    items = []
    n = len(dedup)
    for i, (s, e) in enumerate(dedup):
        nxt = dedup[i+1][0] if i+1 < n else len(text)
        seg = text[e:nxt]
        seg = re.sub(r'【解析】[\s\S]*$', '', seg)
        seg = HEADER_RE.sub('', seg).strip()
        items.append(seg)
    if len(items) < expected:
        raise ValueError('题数不足: %d < %d' % (len(items), expected))
    return items[:expected], [], len(items)

out = []
try:
    for label, markers, expected in [
        ('【沪教】八上英语期末完成句子119题.pdf', ['解析版）','解析版)'], 119),
        ('【沪教】八上英语期末用单词的适当形式填空70题.pdf', ['答案版）','答案版)'], 70),
    ]:
        pdf = os.path.join(BASE, 'resources/专项练习', label)
        text = pdf_text(pdf)
        pos = -1
        for mk in markers:
            idx = text.find(mk)
            if idx >= 0 and (pos < 0 or idx < pos): pos = idx
        out.append('%s marker_pos=%s' % (label, pos))
        if pos < 0:
            out.append('  !! marker not found'); continue
        tail = text[pos:]
        items, missing, nb = _extract_numbered(tail, expected)
        out.append('  extracted_total=%d returned=%d' % (nb, len(items)))
        if expected == 119:
            out.append('  sample 33=%r 34=%r 35=%r 98=%r 100=%r 119=%r' % (
                items[32] if len(items)>32 else '', items[33] if len(items)>33 else '',
                items[34] if len(items)>34 else '', items[97] if len(items)>97 else '',
                items[99] if len(items)>99 else '', items[118] if len(items)>118 else ''))
        else:
            out.append('  sample 21=%r 22=%r 23=%r 24=%r 25=%r 26=%r' % (
                items[20] if len(items)>20 else '', items[21] if len(items)>21 else '',
                items[22] if len(items)>22 else '', items[23] if len(items)>23 else '',
                items[24] if len(items)>24 else '', items[25] if len(items)>25 else ''))
except Exception:
    out.append('EXCEPTION:\n' + traceback.format_exc())

with open(os.path.join(BASE,'_dbg119h.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
