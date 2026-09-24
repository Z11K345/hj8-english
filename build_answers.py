# -*- coding: utf-8 -*-
"""从「解析版」PDF 提取每题答案，生成 <卷>.answers.json，并写入 manifest 的 answers 字段。

答案来源优先级：
  1) 行内 【答案】X  / 【答案】N．X  （X 为单个字母=选择题；X 为单词/短语=填空/任务型）
  2) 选择题详解中的 故选X / 答案为X / 答案是X  （解析版常把答案写在解析里）
按键：题号 -> 答案文本。选择题答案为单个大写字母；填空/任务型为参考词（含首字母提示）。

仅对带有「正式答题卡」(card) 的试卷生成 answers（前端在 cardmode 下做自动批改）。

解析策略：
  - parse_answers_per_block：按「题号．」切块，处理常见单答案/解析内答案（覆盖绝大多数选择题）。
  - scan_consolidated：全局扫描【答案】段，对「连续编号答案块」（任务型阅读、完成句子、单词填空等
    多题共用一个【答案】标签）做整体拆分，避免逐块解析时只抓到首题而漏掉后续题号。
  - 题号分隔符统一用全角「．」，避免把 "1903." "3.5" 等小数/年份误判为下一题号。
"""

import os, re, json

BASE = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app"
OUT = os.path.join(BASE, "exam-data", "manifest.json")

# 解析版常见页脚/水印行：页码、公众号、卷名、年级标识；答案提取时整行丢弃
FOOTER_RE = re.compile(
    r'第\s*\d+\s*页\s*共\s*\d+\s*页|微信公众号[:：]|UNIT\s+\d+.*（解析版）'
    r'|初中英语.*八年级|沪教.*八年级', re.I)

try:
    import fitz
except Exception as e:
    print("需要 PyMuPDF：", e)
    raise SystemExit(1)


def clean_answer(a):
    """清洗单条答案：去首尾空白、去句尾标点、首字母填空 (P)erhaps -> Perhaps。"""
    a = a.strip()
    # 整行丢弃页脚/水印
    lines = [l for l in a.splitlines() if not FOOTER_RE.search(l.strip())]
    a = "\n".join(lines).strip()
    a = re.sub(r'[\s。．，,]+$', '', a)               # 句尾标点
    a = re.sub(r'^\(([A-Za-z])\)', r'\1', a)          # (P)erhaps -> Perhaps
    a = re.sub(r'^[(（]([A-Za-z])[)）]', r'\1', a)    # 兼容半角/全角括号
    return a.strip()


def split_numbered(text):
    """把 '41．Flight.\n42．On 17 December, 1903.\n43．12 seconds.' 拆成 [(41,'Flight.'),(42,'On...'),...]。
    仅以全角「．」为分隔符，且数字前不能是数字/小数点（避免 1903. / 3.5 被误拆）。多行答案按内容自然合并。"""
    parts = re.split(r'(?<![\d．])(?<![\d])\b(\d{1,3})\s*[．]\s*', text)
    res = []
    i = 1
    while i + 1 < len(parts):
        try:
            no = int(parts[i])
        except ValueError:
            i += 2
            continue
        content = parts[i + 1]
        res.append((no, content))
        i += 2
    return res


def scan_consolidated(text):
    """全局扫描所有【答案】段，找出「连续编号的多题答案块」并整体拆分。
    单字母段（无编号）与单题段交回逐块解析处理；只有 ≥2 个编号的整块才在此统一拆出。"""
    qans = {}
    for mm in re.finditer(r'【答案】', text):
        start = mm.end()
        rest = text[start:]
        nxt = re.search(r'【|书面表达|七、作文|八、作文', rest)
        seg = rest[:nxt.start()] if nxt else rest
        pairs = [(no, clean_answer(ans)) for no, ans in split_numbered(seg)]
        pairs = [(no, ans) for no, ans in pairs if ans]
        if len(pairs) >= 2:
            for no, ans in pairs:
                qans[str(no)] = ans
        elif len(pairs) == 1:
            # 单题带编号：仍记录，但逐块解析大概率已处理，这里仅作补充
            qans.setdefault(str(pairs[0][0]), pairs[0][1])
    return qans


def parse_answers_per_block(text):
    """原有逐块解析：按「题号．」切块，提取【答案】或解析内 故选X 等。覆盖绝大多数选择题。"""
    lines = text.splitlines()
    blocks = []
    cur_no = None
    buf = []
    for line in lines:
        if '书面表达' in line or '七、作文' in line or '八、作文' in line:
            if cur_no is not None:
                blocks.append((cur_no, "\n".join(buf)))
            break
        m = re.match(r'^\s*(\d{1,3})\s*[．.]\s*', line)
        if m:
            if cur_no is not None:
                blocks.append((cur_no, "\n".join(buf)))
            cur_no = int(m.group(1))
            buf = [line]
        elif cur_no is not None:
            buf.append(line)
    if cur_no is not None:
        blocks.append((cur_no, "\n".join(buf)))

    qans = {}
    for no, blk in blocks:
        ans = None
        ma = re.search(r'【答案】\s*(.*?)(?=\s*【|\s*$)', blk, re.S)
        if ma:
            ans_blob = ma.group(1).strip()
            # 单条（可能是字母或单词）；若内含编号交给 consolidated 处理，这里只取无编号情形
            if not re.search(r'\d{1,3}\s*[．]', ans_blob):
                ans = clean_answer(ans_blob)
        if ans is None:
            mm = re.search(r'故选\s*([A-Fa-f])', blk)
            if not mm:
                mm = re.search(r'答案为\s*([A-Fa-f])', blk)
            if not mm:
                mm = re.search(r'答案是\s*([A-Fa-f])', blk)
            if not mm:
                mm = re.search(r'答案选\s*([A-Fa-f])', blk)
            if not mm:
                mm = re.search(r'答案\s*[：:]\s*([A-Fa-f])', blk)
            if not mm:
                mm = re.search(r'正确答案[为是]?\s*([A-Fa-f])', blk)
            if mm:
                ans = mm.group(1).upper()
        if ans is not None and ans != '':
            qans[str(no)] = ans
    return qans


def parse_answers(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    pb = parse_answers_per_block(text)
    g = scan_consolidated(text)
    # 逐块结果优先（已验证覆盖率高且题号上下文准确）；consolidated 仅补充缺失项
    merged = dict(pb)
    for k, v in g.items():
        if k not in merged or not merged[k]:
            merged[k] = v
    return merged


def fix_card_types(card_path, qans):
    """根据解析版答案的数据特征校正 card.json 的题型：某大题若绝大多数答案为单个字母(A-F)则定为 mc，
    否则为 blank（填空/完成句子/阅读还原/句子翻译等均为单词或短语作答）。避免把单词填空题误判为选择题。"""
    try:
        cj = json.load(open(card_path, encoding='utf-8'))
    except Exception:
        return
    changed = 0
    for sec in cj.get('sections', []):
        nos = sec.get('nos') or []
        if not nos:
            continue
        letters = sum(1 for no in nos if re.fullmatch(
            r'[A-F]', str(qans.get(str(no), qans.get(no, ''))).strip().upper()))
        ratio = letters / len(nos)
        if sec['type'] == 'mc' and ratio < 0.6:
            sec['type'] = 'blank'
            changed += 1
        elif sec['type'] == 'blank' and ratio >= 0.8:
            sec['type'] = 'mc'
            changed += 1
    if changed:
        json.dump(cj, open(card_path, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
    return changed


def extract_positions(pdf_path, keys):
    """从「学生版」PDF 抓取每个题号在试卷上的位置 [页码(1起), 纵向比例 0-1]，供前端点击题号跳转。
    学生版无答案插入、题号布局最干净。两遍：先匹配「N．/N.」标号（最准），再回退裸数字词（完形/单词填空等无句号标号）。"""
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

    # 第一遍：优先「N．/N.」标号的题号（最准确，题号出现早于答案）
    scan(lambda no, word: re.match(r'%d[．.]' % no, word) is not None)
    # 第二遍：仅对仍未定位的题号，回退到裸数字词（完形/单词填空等无句号标号；取首个命中，个别数字可能偏前，属可接受误差）
    scan(lambda no, word: word == str(no))
    return {str(k): v for k, v in pos.items()}


def main():
    manifest = json.load(open(OUT, encoding='utf-8'))
    gen = 0
    for cat in manifest['cats']:
        for p in cat['papers']:
            if not p.get('card') or not p.get('answerPdf'):
                continue
            pdf_abs = os.path.join(BASE, p['answerPdf'].replace('/', os.sep))
            if not os.path.isfile(pdf_abs):
                print("缺失解析版：", p['answerPdf'])
                continue
            qans = parse_answers(pdf_abs)
            # 题号位置取自学生版（布局干净），与解析版题号位置一致，两种 PDF 均可跳转
            stu_abs = os.path.join(BASE, p.get('pdf', '').replace('/', os.sep)) if p.get('pdf') else None
            positions = extract_positions(stu_abs, list(qans.keys())) if stu_abs else {}
            ans_path = p['card'].replace('.card.json', '.answers.json')
            ans_abs = os.path.join(BASE, ans_path.replace('/', os.sep))
            json.dump({'answers': qans, 'positions': positions}, open(ans_abs, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=1)
            card_abs = os.path.join(BASE, p['card'].replace('/', os.sep))
            fixed = fix_card_types(card_abs, qans)
            p['answers'] = ans_path
            gen += 1
            mc = sum(1 for v in qans.values()
                     if re.fullmatch(r'[A-F]', v.strip()))
            fixmsg = f"（校正题型 {fixed} 处）" if fixed else ""
            print(f"  {p['label']}: 提取 {len(qans)} 题答案（其中选择题 {mc} 题）{fixmsg}")
    json.dump(manifest, open(OUT, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print("生成 answers 完成，共", gen, "套")


if __name__ == '__main__':
    main()
