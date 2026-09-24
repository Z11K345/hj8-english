# -*- coding: utf-8 -*-
"""
生成知识类 PDF 的结构化 knowledgeData，并把 manifest 全部接上。
- 单词表 / 不规则动词表（含默写版）= 复用已有 JSON
- 短语归纳 / 词性转换 = 结构化 generic/vocab JSON（背一背 + 测一测）
- 词汇拓展 / 必背范文 / 知识梳理 = text 型（阅读 + 抽背 + AI）
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "exam-data", "manifest.json")
RES = os.path.join(ROOT, "resources")
KD = os.path.join(ROOT, "knowledge-data")

CJK = r"[一-鿿]"
def has_cjk(s): return re.search(CJK, s) is not None

def resolve(p):
    if os.path.exists(p): return p
    if os.path.exists(p.strip()): return p.strip()
    return p

def pdf_lines(pdf_path):
    import pdfplumber
    out=[]
    with pdfplumber.open(resolve(pdf_path)) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            for ln in t.split("\n"):
                s = ln.strip()
                if not s: continue
                if re.search(r"微信公众号|瑾言教育|第\s*\d+\s*页\s*共", s): continue
                out.append(s)
    return out

# ---------- text 型：按章节分组（知识梳理）----------
SEC_RE = re.compile(r"^[一二三四五六七八九十]+、")
def text_sectioned(pdf_path, title):
    lines = pdf_lines(pdf_path)
    blocks=[]; cur=None
    for s in lines:
        if SEC_RE.match(s):
            if cur and (cur["text"].strip() or cur["title"]):
                blocks.append(cur)
            cur={"title":s, "text":""}
        else:
            if cur is None:
                cur={"title":"", "text":""}
            cur["text"] += s + "\n"
    if cur and (cur["text"].strip() or cur["title"]):
        blocks.append(cur)
    if not blocks:
        blocks=[{"title":"", "text":"\n".join(lines)}]
    return {"title":title, "type":"text", "blocks":blocks}

# ---------- text 型：按页（必背范文）----------
def text_perpage(pdf_path, title):
    import pdfplumber
    blocks=[]
    with pdfplumber.open(resolve(pdf_path)) as pdf:
        for i,page in enumerate(pdf.pages):
            t=page.extract_text() or ""
            body=[]
            for ln in t.split("\n"):
                s=ln.strip()
                if not s: continue
                if re.search(r"微信公众号|瑾言教育|第\s*\d+\s*页\s*共", s): continue
                body.append(s)
            if body:
                blocks.append({"title":f"第 {i+1} 篇", "text":"\n".join(body)})
    return {"title":title, "type":"text", "blocks":blocks}

# ---------- text 型：按空行分块（词汇拓展）----------
def text_byblank(pdf_path, title):
    import pdfplumber
    lines=[]
    with pdfplumber.open(resolve(pdf_path)) as pdf:
        for page in pdf.pages:
            t=page.extract_text() or ""
            for ln in t.split("\n"):
                lines.append(ln.rstrip())
    # 合并：连续非空行归一块，空行分隔
    blocks=[]; buf=[]
    for ln in lines:
        if ln.strip()=="":
            if buf:
                blocks.append({"title":"", "text":"\n".join(buf)}); buf=[]
        else:
            buf.append(ln.strip())
    if buf:
        blocks.append({"title":"", "text":"\n".join(buf)})
    # 去掉页脚/页眉干扰块（过短且含公众号）
    blocks=[b for b in blocks if not re.search(r"微信公众号|瑾言教育|第\s*\d+\s*页", b["text"])]
    if not blocks:
        blocks=[{"title":"", "text":"\n".join(l for l in lines if l.strip())}]
    return {"title":title, "type":"text", "blocks":blocks}

# ---------- 结构化：短语归纳 ----------
def generic_phrases(pdf_path, title):
    lines = pdf_lines(pdf_path)
    items=[]
    for s in lines:
        # 一行可能含多个词条：按「数字+英文」切分
        for part in re.split(r"(?=\d+[a-zA-Z])", s):
            part=part.strip()
            if not part: continue
            part=re.sub(r"^\d+\s*", "", part)
            m=re.search(CJK, part)
            if not m: continue
            en=re.sub(r"\s{2,}", " ", part[:m.start()]).strip()
            cn=part[m.start():].strip()
            if not re.search(r"[A-Za-z]", en): continue   # 跳过标题/页眉等非词条
            if not cn: continue
            items.append({"英文":en, "中文":cn})
    return {"title":title, "type":"vocab",
            "columns":["英文","中文"],
            "items":items,
            "quizModes":[{"id":"cn2en","name":"看中文，写英文","prompt":"中文","answerKeys":["英文"]},
                         {"id":"en2cn","name":"看英文，写中文","prompt":"英文","answerKeys":["中文"]}]}

def fix_space(s):
    return re.sub(r"([a-zA-Z])(n\.|adj\.|adv\.)", r"\1 \2", s)

# ---------- 结构化：词性转换 ----------
def generic_wordform(pdf_path, title):
    lines = pdf_lines(pdf_path)
    items=[]
    for s in lines:
        s=re.sub(r"^\d+\.\s*", "", s).strip()
        if "→" not in s: continue
        base, rest = s.split("→", 1)
        base=fix_space(base.strip())
        derived=fix_space(rest.replace("→"," / ").strip())
        if not base or not derived: continue
        items.append({"原词":base, "转化":derived})
    return {"title":title, "type":"generic",
            "columns":["原词","转化"],
            "items":items,
            "quizModes":[{"id":"w2d","name":"看原词，写转化","prompt":"原词","answerKeys":["转化"]}]}

def save_json(relpath, obj):
    full=os.path.join(KD, relpath)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    json.dump(obj, open(full,"w",encoding="utf-8"), ensure_ascii=False, indent=1)
    return full

# 复用映射（默写版等指向已有 JSON）
REUSE = {
    "不规则动词表（默写版）": "知识点总结/【沪教】八上英语不规则动词表（背诵版）.json",
    "单词表默写": "知识点总结/【沪教】八上英语单词表.json",
    "单词表（汉译英默写，不带音标）": "知识点总结/【沪教】八上英语单词表.json",
    "单词表（背诵版，带音标）": "知识点总结/【沪教】八上英语单词表.json",
    "单词表（英译汉默写，带音标）": "知识点总结/【沪教】八上英语单词表.json",
}

def handler_for(label):
    if "短语归纳" in label: return "phrase"
    if "词性转换（背诵版）" in label or "词性转换（默写版）" in label: return "wordform"
    if "必背范文" in label: return "essay"
    if "词汇拓展" in label: return "vocexp"
    if "知识梳理" in label or "核心知识" in label: return "core"
    return None

def main():
    m=json.load(open(MANIFEST,encoding="utf-8"))
    log=[]
    wf_json_rel=None  # 词性转换 JSON（背诵/默写共用）
    for cat in m["cats"]:
        if cat["name"] not in ("知识梳理","知识点总结"): continue
        for p in cat["papers"]:
            label=p.get("label","")
            pdf=resolve(os.path.join(ROOT, p["pdf"]))
            base=os.path.basename(p["pdf"]).replace(".pdf","")
            matched=[v for k,v in REUSE.items() if k in label]
            if matched:
                rel=matched[0]
                p["knowledgeData"]= "knowledge-data/"+rel
                log.append(("REUSE", label, rel, 0))
                continue
            h=handler_for(label)
            if h=="phrase":
                obj=generic_phrases(pdf, base)
                rel="知识点总结/"+base+".json"; save_json(rel,obj)
                p["knowledgeData"]="knowledge-data/"+rel
                log.append(("GEN", label, rel, len(obj["items"])))
            elif h=="wordform":
                if wf_json_rel is None:
                    obj=generic_wordform(pdf, "【沪教】八上英语词性转换")
                    wf_json_rel="知识点总结/【沪教】八上英语词性转换.json"
                    save_json(wf_json_rel, obj)
                p["knowledgeData"]="knowledge-data/"+wf_json_rel
                log.append(("WORDCLASS", label, wf_json_rel, len(obj["items"])))
            elif h=="essay":
                obj=text_perpage(pdf, base); rel="知识点总结/"+base+".json"; save_json(rel,obj)
                p["knowledgeData"]="knowledge-data/"+rel
                log.append(("GEN", label, rel, len(obj["blocks"])))
            elif h=="vocexp":
                obj=text_perpage(pdf, base); rel="知识点总结/"+base+".json"; save_json(rel,obj)
                p["knowledgeData"]="knowledge-data/"+rel
                log.append(("GEN", label, rel, len(obj["blocks"])))
            elif h=="core":
                obj=text_sectioned(pdf, base); rel="知识梳理/"+base+".json"; save_json(rel,obj)
                p["knowledgeData"]="knowledge-data/"+rel
                log.append(("GEN", label, rel, len(obj["blocks"])))
            else:
                log.append(("SKIP", label, "", 0))
    json.dump(m, open(MANIFEST,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print("=== 处理结果 ===")
    for row in log: print(row)
    print("manifest 已更新；knowledgeData 字段总数：", sum(1 for c in m["cats"] if c["name"] in ("知识梳理","知识点总结") for p in c["papers"] if p.get("knowledgeData")))

if __name__=="__main__":
    main()
