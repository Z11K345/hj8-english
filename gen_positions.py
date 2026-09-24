# -*- coding: utf-8 -*-
"""为所有试卷（含无答题卡的纯浏览卷）生成「题号 -> [页码, 纵向比例]」位置表，
输出 exam-data/positions.json，供前端点击题号跳转到试卷对应题目。

- 有答题卡的卷：题号取自 card.json 的 nos（最准）。
- 无答题卡的卷：从学生版 PDF 文本用（数字+句号）与（独占一行的孤立数字）两路探测题号。
位置始终取自学生版 PDF（布局干净）。
"""
import os, re, json, fitz

BASE = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app"
EXAM = os.path.join(BASE, "exam-data")
manifest = json.load(open(os.path.join(EXAM, "manifest.json"), encoding="utf-8"))

NUM_A = re.compile(r"(\d{1,3})\s*[．.](?!\d)")          # 数字 + 句号（排除小数）
NUM_B = re.compile(r"(?:^|\n)[ \t]*(\d{1,3})[ \t]*(?:\n|$)")  # 独占一行的孤立数字（完形/填空空号）
# 行首题号：行首出现「数字 + 句号/顿号/括号/空格/行尾」，排除句中数字（年份、年龄等）与超大值
LINE_NO = re.compile(r'^\s*[（(]?\s*(\d{1,3})(?:[\．.、）)\s]|$)')

def extract_positions(pdf_path, keys):
    if not os.path.isfile(pdf_path):
        return {}
    try:
        doc = fitz.open(pdf_path)
    except Exception:
        return {}
    pos = {}
    want = set(int(k) for k in keys if str(k).isdigit())

    def scan(matchfn):
        for pi in range(doc.page_count):
            if not (want - set(pos.keys())):
                break
            try:
                words = doc[pi].get_text("words")
            except Exception:
                continue
            ph = doc[pi].rect.height or 1
            for w in words:
                word = w[4]
                for no in list(want):
                    if no in pos:
                        continue
                    if matchfn(no, word):
                        pos[no] = [pi + 1, round(min(max(w[1] / ph, 0), 1), 4)]
                        break
    # 第一遍：数字后紧跟非数字分隔符（句号/顿号/括号/空格/行尾），最贴近题号写法
    scan(lambda no, word: re.match(r'^%d(?:\D|$)' % no, word) is not None)
    # 第二遍：孤立整词（兜底，捕捉"独占一行"的填空空号）
    scan(lambda no, word: word == str(no))
    doc.close()
    return {str(k): v for k, v in pos.items()}

def detect_numbers(text):
    out = set()
    for ln in text.splitlines():
        m = LINE_NO.match(ln)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 300:   # 过滤页码/题号序号等异常大值（如 847/955）
                out.add(n)
    return sorted(out)

def paper_numbers(p):
    if p.get('card'):
        card_path = os.path.join(BASE, p['card'].replace('/', os.sep))
        try:
            card = json.load(open(card_path, encoding='utf-8'))
            nos = []
            for sec in card.get('sections', []):
                nos += list(sec.get('nos', []))
            if nos:
                return sorted(set(nos))
        except Exception:
            pass
    pdf = p.get('pdf')
    if pdf:
        stu = os.path.join(BASE, pdf.replace('/', os.sep))
        if os.path.isfile(stu):
            try:
                doc = fitz.open(stu)
                text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
                doc.close()
                return detect_numbers(text)
            except Exception:
                pass
    return []

out = {}
for cat in manifest['cats']:
    for p in cat['papers']:
        pdf = p.get('pdf')
        if not pdf:
            continue
        stu = os.path.join(BASE, pdf.replace('/', os.sep))
        if not os.path.isfile(stu):
            continue
        keys = paper_numbers(p)
        if not keys:
            continue
        positions = extract_positions(stu, keys)
        if positions:
            out[(p.get('cat') or cat.get('name') or '') + '||' + p['label']] = positions

json.dump(out, open(os.path.join(EXAM, "positions.json"), "w", encoding="utf-8"),
         ensure_ascii=False)
total_keys = sum(len(v) for v in out.values())
print("generated positions for", len(out), "papers; total 题号 entries:", total_keys)
