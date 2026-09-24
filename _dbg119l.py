# -*- coding: utf-8 -*-
import os, re, json, fitz, traceback
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
out = []
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location('fin2', os.path.join(BASE, '_finalize2.py'))
    # can't import (runs main). Instead replicate build_answers.
    HEADER_RE = re.compile(r'(?m)^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')
    DELIM_LS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
    DELIM_ANY = re.compile(r'(\d{1,3})\s*[.．.]\s*')
    def pdf_text(path):
        pabs = os.path.join(BASE, path.replace('/', os.sep))
        doc = fitz.open(pabs); t = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close(); return t
    def _find_answer_section(text, markers):
        s0 = 0
        while True:
            pos=-1; fm=None
            for mk in markers:
                idx=text.find(mk, s0)
                if idx>=0 and (pos<0 or idx<pos): pos=idx; fm=mk
            if pos<0: return None
            tail=text[pos:]
            if re.search(r'(?m)^\s*\d{1,3}\s*[.．.]\s*\S', tail[:3000]): return tail
            s0=pos+len(fm)
    def _extract_numbered(text, expected):
        matches=[]
        for m in DELIM_LS.finditer(text): matches.append((m.start(),m.end()))
        for m in DELIM_ANY.finditer(text): matches.append((m.start(),m.end()))
        matches.sort(); dedup=[]
        for s,e in matches:
            if dedup and s<=dedup[-1][0]+3:
                if s<dedup[-1][0]: dedup[-1]=(s,e)
                continue
            dedup.append((s,e))
        items=[]; n=len(dedup)
        for i,(s,e) in enumerate(dedup):
            nxt=dedup[i+1][0] if i+1<n else len(text)
            seg=text[e:nxt]; seg=re.sub(r'【解析】[\s\S]*$','',seg); seg=HEADER_RE.sub('',seg).strip()
            items.append(seg)
        if len(items)<expected: raise ValueError('题数不足 %d<%d'%(len(items),expected))
        return items[:expected]
    pdf = os.path.join(BASE,'resources/专项练习','【沪教】八上英语期末用单词的适当形式填空70题.pdf')
    text = pdf_text(pdf)
    tail = _find_answer_section(text, ['答案版）','答案版)'])
    out.append('tail found: %s' % (tail is not None))
    items = _extract_numbered(tail, 70)
    out.append('items=%d' % len(items))
    base = '【沪教】八上英语期末用单词的适当形式填空70题'
    ans_path = os.path.join(ED, '专项练习', base + '.answers.json')
    with open(ans_path, 'w', encoding='utf-8') as f:
        json.dump({'answers': {'0_%d'%(i+1): items[i] for i in range(70)}, 'positions': {}}, f, ensure_ascii=False, indent=1)
    out.append('WROTE %s' % ans_path)
except Exception:
    out.append('EXCEPTION:\n'+traceback.format_exc())
with open(os.path.join(BASE,'_dbg119l.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
