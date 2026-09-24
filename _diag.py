# -*- coding: utf-8 -*-
import os, re, json, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')
ED = os.path.join(BASE, 'exam-data')

CN_SEC   = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$')
QNO_START = re.compile(r'(?m)^\s*(\d+)\s*[.．、)）]')
QNO_MID   = re.compile(r'(\d+)\s*[.．、)）]\s*(?=[\u4e00-\u9fff_])')
OPT_A = re.compile(r'(?m)^\s*A\s*[\.．、]')

def get_text(pdf):
    doc = fitz.open(pdf)
    t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return t

def card_sections(text, title):
    lines = text.split('\n')
    sections = []; cur_title=None; cur_body=[]; has_sec=False
    for ln in lines:
        m=CN_SEC.match(ln)
        if m:
            if cur_title is not None: sections.append((cur_title,cur_body))
            cur_title=m.group(2).strip() or ('第'+m.group(1)+'部分'); cur_body=[]; has_sec=True
        else:
            if cur_title is not None: cur_body.append(ln)
    if cur_title is not None: sections.append((cur_title,cur_body))
    if not has_sec: sections=[('全卷',lines)]
    out=[]
    for st,body in sections:
        joined='\n'.join(body)
        opt_a=len(OPT_A.findall(joined))
        if opt_a>0 or re.search(r'选择|阅读|匹配|还原|五选五|六选五|七选五|信息|完形|单选|语法选择',st):
            nums={int(x) for x in QNO_START.findall(joined)}; nums={n for n in nums if 1<=n<=400}
            nq=len(nums) or len(OPT_A.findall(joined)); typ='mc'
        else:
            nums={int(x) for x in QNO_START.findall(joined)}|{int(x) for x in QNO_MID.findall(joined)}
            nums={n for n in nums if 1<=n<=400}; nq=len(nums); typ='blank'
        if nq==0: continue
        out.append((st,typ,nq))
    return out

def answer_blocks(text):
    # 返回所有【答案】段里的 (局部编号列表) 及总题数，按文档顺序
    blocks=[]
    for mm in re.finditer(r'【答案】', text):
        start=mm.end(); rest=text[start:]
        nxt=re.search(r'【|书面表达|七、作文|八、作文', rest)
        seg=rest[:nxt.start()] if nxt else rest
        # 提取局部编号
        pairs=re.findall(r'(\d{1,3})\s*[．.]\s*', seg)
        nums=[int(x) for x in pairs]
        blocks.append(nums)
    total=sum(len(b) for b in blocks)
    return blocks,total

samples = [
    ('专项练习','【沪教】八上英语单项选择100题.pdf'),
    ('专项练习','【沪教】八上英语阅读理解之记叙文18篇.pdf'),
    ('专项练习','【沪教】八上英语完形填空17篇.pdf'),
    ('专项练习','【沪教】八上英语完成句子37题.pdf'),
    ('一课一练','Unit 1 Section 2 Grammar（分层练习）.pdf'),
    ('一课一练','Unit 1 Section 1 Reading（分层练习）.pdf'),
]

lines=[]
for cat,fn in samples:
    p=os.path.join(RES,cat,fn)
    text=get_text(p)
    secs=card_sections(text,fn)
    blocks,total=answer_blocks(text)
    card_total=sum(n for _,_,n in secs)
    lines.append(f"\n### {cat}/{fn}")
    lines.append(f"  card sections: {len(secs)} | card total Q={card_total} | answer blocks={len(blocks)} | answer total={total}")
    for i,(st,typ,nq) in enumerate(secs):
        lines.append(f"    sec{i+1}: [{typ}] {st[:24]} nq={nq}")
    lines.append(f"    answer block sizes: {[len(b) for b in blocks]}")
lines.append("\nNOTE: if card_total != answer total, or block sizes reset per passage, numbered alignment fails.")

with open(os.path.join(BASE,'_diag.txt'),'w',encoding='utf-8') as fh:
    fh.write("\n".join(lines))
print("done")
