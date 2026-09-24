# -*- coding: utf-8 -*-
"""从单元检测「学生版」PDF 解析出正式答题卡结构（v3，稳健版）。

只提取「可靠」信息：章节标题、作答类型、题号列表、选择题选项个数。
题干/选项原文不提取（段落会串入选项，易错）——题目在左侧 PDF 中阅读，
右侧答题卡只负责「作答」，完全对应真实考试的答题卡模型。

作答类型：
  mc    —— 选字母（单项选择 / 阅读理解 / 阅读还原 / 阅读匹配 / 词汇等）
  blank —— 写词/短语（完形填空 / 短文填空 / 语篇填词 / 选词填空 / 任务型阅读 / 首字母）
  essay —— 作文（书面表达）

题号识别（对所有非作文章节统一）：
  (A) 数字 + 全角/半角句号（N． / N.），排除小数 N.N
  (B) 独占一行的孤立数字（完形/短文填空/语篇填词的空号）
两路取并集、去重、排序。

输出：exam-data/单元检测/<卷名>.card.json
{
  "title":"Unit 1（基础卷）",
  "sections":[
    {"title":"一、单项选择（…）","type":"mc","nos":[1..10],"opts":4},
    {"title":"二、完形填空（…）","type":"blank","nos":[11..20]},
    {"title":"三、阅读（…）","type":"mc","nos":[21..40],"opts":4},
    {"title":"五、短文填空（…）","type":"blank","nos":[45..54]},
    {"title":"七、书面表达（15 分）","type":"essay","nos":[]}
  ]
}
"""
import os, re, json, fitz

RES = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources\单元检测"
OUT = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\exam-data\单元检测"

# (A) 题号：数字 + 句号（全/半角），句号后不能是数字（排除 1.5 这类小数）
NUM_A = re.compile(r"(\d{1,3})\s*[．.](?!\d)")
# (B) 空号：独占一行的孤立数字
NUM_B = re.compile(r"(?:^|\n)[ \t]*(\d{1,3})[ \t]*(?:\n|$)")
# 选择题选项字母（行首 A-F + 句号），用于推断选项个数（4 或 5）
OPT_LET = re.compile(r"(?m)^[ \t]*([A-F])\s*[．.]")

def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    pages = [doc[i].get_text() for i in range(doc.page_count)]
    doc.close()
    return "\n".join(pages)

def clean(s):
    s = s.replace("\u3000", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def split_sections(text):
    text = re.sub(r"Unit\s+\d+.*?学生版\)", " ", text)
    text = re.sub(r"第\d+\s*页共\d+\s*页", " ", text)
    text = re.sub(r"微信公众号[：:].*", " ", text)
    parts = re.split(r"((?<=\n)[一二三四五六七八九十]+\s*、[^\n]+)", text)
    secs = []
    i = 1
    while i + 1 < len(parts):
        secs.append((clean(parts[i]), parts[i + 1]))
        i += 2
    if not secs and parts:
        secs = [("", parts[0])]
    return secs

def classify(title):
    t = title
    if "表达" in t or "作文" in t:
        return "essay"
    if "还原" in t or "匹配" in t:          # 阅读还原 / 阅读匹配 = 选字母
        return "mc"
    # 完形填空 = 选字母（cloze with A/B/C/D）
    if "完形填空" in t or "完型填空" in t:
        return "mc"
    # 需要写词的题型
    if ("短文填空" in t or "语篇填词" in t or "选词填空" in t or "首字母" in t
            or "任务型" in t or "归纳" in t or "回答问题" in t):
        return "blank"
    # 兜底：只出现“填空”二字（无完形/短文/语篇/选词/首字母等限定）→ 视为写词
    if "填空" in t or "填词" in t:
        return "blank"
    return "mc"                              # 单项选择/阅读理解/词汇/句型 等默认选字母

def detect_numbers(body):
    cand = [int(x) for x in NUM_A.findall(body)] + [int(x) for x in NUM_B.findall(body)]
    cand = [n for n in cand if 1 <= n <= 200]
    seen = set(); uni = []
    for n in cand:
        if n not in seen:
            seen.add(n); uni.append(n)
    if not uni:
        return uni
    uni_sorted = sorted(uni)
    # 取最长连续区间（剔除孤立噪点，如段落里的年份/页码）
    best = (0, 1)  # (start_idx, end_idx) 左闭右开
    s = 0
    for i in range(1, len(uni_sorted)):
        if uni_sorted[i] != uni_sorted[i - 1] + 1:
            if i - s > best[1] - best[0]:
                best = (s, i)
            s = i
    if len(uni_sorted) - s > best[1] - best[0]:
        best = (s, len(uni_sorted))
    lo, hi = uni_sorted[best[0]], uni_sorted[best[1] - 1]
    run = list(range(lo, hi + 1))
    # 仅当最长区间覆盖 >=80% 的候选时才用它（否则保留去重后的全部，避免误删有间隔的真实题号）
    if len(run) >= 0.8 * len(uni_sorted):
        return run
    return uni_sorted

def detect_opts(body):
    letters = sorted(set(OPT_LET.findall(body)))
    # 选项个数：默认 4（A-D）；若明确检出 5/6 个行首选项字母则用之；绝不低至 3
    return min(6, max(4, len(letters)))

def build_one(student_pdf):
    base = os.path.basename(student_pdf)            # Unit 1（基础卷）（学生版）.pdf
    name = base[:-len("（学生版）.pdf")]             # Unit 1（基础卷）
    text = extract_text(student_pdf)
    secs = split_sections(text)
    out = []
    for title, body in secs:
        typ = classify(title)
        if typ == "essay":
            out.append({"title": title or "书面表达", "type": "essay", "nos": []})
        elif typ == "blank":
            out.append({"title": title or "填空", "type": "blank",
                        "nos": detect_numbers(body)})
        else:  # mc
            out.append({"title": title or "选择题", "type": "mc",
                        "nos": detect_numbers(body), "opts": detect_opts(body)})
    card = {"title": name, "sections": out}
    return name, card

def main():
    files = [f for f in os.listdir(RES) if "学生" in f and f.endswith(".pdf")]
    ok = 0
    for f in sorted(files):
        try:
            name, card = build_one(os.path.join(RES, f))
        except Exception as e:
            print("FAIL", f, e); continue
        out_name = name + ".card.json"
        with open(os.path.join(OUT, out_name), "w", encoding="utf-8") as fh:
            json.dump(card, fh, ensure_ascii=False, indent=1)
        summ = ", ".join(
            f"{s['type']}:{len(s['nos'])}" + (f"(opt{s.get('opts')})" if s.get("opts") else "")
            for s in card["sections"])
        print(f"{out_name}: {summ}")
        ok += 1
    print("完成", ok, "套")

if __name__ == "__main__":
    main()