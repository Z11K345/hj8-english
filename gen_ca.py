# -*- coding: utf-8 -*-
"""为一课一练 / 专项练习 重新生成结构化答题卡(card.json) + 参考答案(answers.json)。

版式关键事实（已用 PDF 文本核验）：
  这些「分层练习 / 专项」PDF 是「学生版 + 解析版」合并文件：
    前半 = 学生版（只有题目，无答案）；后半 = 解析版（把题目再列一遍，附【答案】【解析】）。
  因此首个【答案】一定出现在解析版里；其之前是纯题目区，之后是带答案的解析区。

  答案键一律采用「板块下标_题号」(si_no)，避免一课一练多板块同名“第1题”在前端互相覆盖；
  前端 exam.html 同步改成优先查 si_no，再回退旧版 no（兼容单元检测全局编号）。

  本题设计：直接从解析版(atext)抽取答案，并以「答案条数」作为该题板块的题目数，
  因此 卡题数 == 答案条数 天然一致，彻底规避“数题号”带来的漏数/重数。

  - 一课一练：解析版用「一、二、三…」(CN_SEC) 分板块；板块内答案为「逐题行内【答案】X」
    或「 consolidated 1. A 2. B」两种形态，统一按【答案】标记抽取。
  - 专项：解析版没有 CN_SEC，改为按【答案】块切分（每篇/每篇短文 = 一个【答案】块），
    块内即「1. B 2. A … 10. C」式答案，块数 = 篇数。

用法：
  python gen_ca.py --dry            # 写 _ca_report.txt，不写盘
  python gen_ca.py                  # 正式生成并写 manifest
"""
import os, re, json, argparse, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CATS = ['一课一练', '专项练习']

CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)
ESSAY_KW = ['作文', '写作', '书面表达', '书面']
FOOTER_RE = re.compile(
    r'第\s*\d+\s*页\s*共\s*\d+\s*页|微信公众号[:：]|（解析版）|初中英语.*八年级|沪教.*八年级',
    re.I)


def clean_answer(a):
    lines = [l for l in a.splitlines() if not FOOTER_RE.search(l.strip())]
    a = "\n".join(lines).strip()
    a = re.sub(r'[\s。．，,]+$', '', a)
    a = re.sub(r'^[(（]([A-Za-z])[)）]', r'\1', a)
    return a.strip()


def block_end(rest):
    """答案块结束位置：下一个【 或 解析 或 下一个“行首数字+长文本”（新题）"""
    m_b = re.search(r'【', rest)
    m_j = re.search(r'解析', rest)
    m_q = re.search(r'(?m)^\s*\d+\s*[.．、)）]\s*\S.{9,}', rest)
    cands = [x.start() for x in (m_b, m_j, m_q) if x]
    return min(cands) if cands else len(rest)


def parse_one_block(rest):
    """解析单个【答案】标记后的答案文本，返回有序答案列表。"""
    end = block_end(rest)
    seg = rest[:end]
    seg = re.split(r'【解析】', seg)[0]
    seg = re.split(r'解析', seg)[0]
    nums = re.findall(r'\d{1,3}\s*[.．.]\s*', seg)
    items = []
    if nums:
        parts = re.split(r'\d{1,3}\s*[.．.]\s*', seg)
        for p in parts[1:]:
            a = clean_answer(p)
            if a:
                items.append(a)
    else:
        a = clean_answer(seg)
        if a:
            # 无编号答案串：解析版常把完形/语法选择的选项写成
            #   "B A C D E F G H I J"（空格/逗号分隔）、"BACDEFGHIJ"（连续拼接）
            #   或 "BACCB\nDDCAA"（每行 5 个、跨行拼接）。统一拆成多个单字母答案。
            if re.match(r'^[A-Fa-f](?:[\s,]+[A-Fa-f])+$', a):
                items.extend(re.split(r'[\s,]+', a))
            else:
                a_compact = re.sub(r'\s+', '', a)
                if re.match(r'^[A-Fa-f]{4,}$', a_compact):
                    items.extend(list(a_compact))
                else:
                    items.append(a)
    return items


def parse_answers_in(sec_text):
    items = []
    for mm in re.finditer(r'【答案】', sec_text):
        items.extend(parse_one_block(sec_text[mm.end():]))
    return items


def sectionize(text):
    """按 CN_SEC 拆分；无则返回 [('全卷', text)]。"""
    lines = text.split('\n')
    raw = []; cur_title = None; cur_body = []; has = False
    for ln in lines:
        m = CN_SEC.match(ln)
        if m:
            if cur_title is not None:
                raw.append((cur_title, '\n'.join(cur_body)))
            cur_title = m.group(2).strip() or ('第' + m.group(1) + '部分')
            cur_body = []; has = True
        else:
            if cur_title is not None:
                cur_body.append(ln)
    if cur_title is not None:
        raw.append((cur_title, '\n'.join(cur_body)))
    if not has:
        raw = [('全卷', text)]
    return raw


def classify(title, items):
    if any(k in title for k in ESSAY_KW):
        return 'essay', 0
    if not items:
        return 'blank', 0
    letters = [a for a in items if re.match(r'^[A-Fa-f]$', a.strip())]
    if len(letters) >= max(1, int(len(items) * 0.6)):
        maxL = max(ord(x.upper()) - 64 for x in letters)
        return 'mc', max(4, maxL)
    return 'blank', 0


def build_sections_from_atext(atext):
    """返回 [(title, items, type, opts)]。"""
    out = []
    secs = sectionize(atext)
    if len(secs) == 1 and secs[0][0] == '全卷':
        # 专项：按【答案】块切分（每篇一个块）
        positions = [m.start() for m in re.finditer(r'【答案】', atext)]
        for i, pos in enumerate(positions):
            rest = atext[pos + len('【答案】'):]
            items = parse_one_block(rest)
            if not items:
                continue
            title = '第%d篇' % (i + 1)
            typ, opts = classify(title, items)
            out.append((title, items, typ, opts))
    else:
        for title, body in secs:
            items = parse_answers_in(body)
            if not items:
                continue
            typ, opts = classify(title, items)
            out.append((title, items, typ, opts))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    args = ap.parse_args()
    man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
    report = []
    total_card = 0
    written = 0
    skipped = 0
    problems = []
    for cat in man['cats']:
        name = cat['name']
        if name not in CATS:
            continue
        for pp in cat['papers']:
            pdf = pp.get('pdf') or ''
            if not pdf:
                continue
            pabs = os.path.join(BASE, pdf.replace('/', os.sep))
            if not os.path.isfile(pabs):
                report.append('缺失PDF: ' + pdf)
                skipped += 1
                continue
            doc = fitz.open(pabs)
            text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
            doc.close()
            ans_start = text.find('【答案】')
            if ans_start < 0:
                report.append('[SKIP 无【答案】] ' + name + ' | ' + pp.get('label'))
                skipped += 1
                continue
            atext = text[ans_start:]
            title = pp.get('label', '') or name + ' ' + os.path.basename(pdf)
            secs = build_sections_from_atext(atext)
            total_q = sum(len(s[1]) for s in secs)
            if total_q == 0:
                report.append('[SKIP 抽不到答案] ' + name + ' | ' + pp.get('label'))
                skipped += 1
                continue
            if args.dry:
                report.append('### %s | %s' % (name, pp.get('label')))
                report.append('   板块=%d 总题数=%d' % (len(secs), total_q))
                for i, (t, items, typ, opts) in enumerate(secs):
                    report.append('     [%d/%s/opts=%s] %s nq=%d' % (
                        i, typ, opts, t[:20], len(items)))
                continue
            # 写 card.json
            card_secs = []
            ans = {}
            for si, (t, items, typ, opts) in enumerate(secs):
                nos = list(range(1, len(items) + 1))
                sec = {'title': t, 'type': typ, 'nos': nos}
                if typ == 'mc':
                    sec['opts'] = opts
                card_secs.append(sec)
                for j, no in enumerate(nos):
                    ans['%d_%d' % (si, no)] = items[j]
            base = os.path.splitext(os.path.basename(pdf))[0]
            card_path = os.path.join(ED, name, base + '.card.json')
            json.dump({'title': title, 'sections': card_secs},
                      open(card_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            ans_path = os.path.join(ED, name, base + '.answers.json')
            json.dump({'answers': ans, 'positions': {}},
                      open(ans_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            pp['card'] = 'exam-data/' + name + '/' + base + '.card.json'
            pp['answers'] = 'exam-data/' + name + '/' + base + '.answers.json'
            written += 1
            total_card += 1
    if not args.dry:
        json.dump(man, open(os.path.join(ED, 'manifest.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        report.append('written cards+answers: ' + str(written) + '  skipped: ' + str(skipped))
    with open(os.path.join(BASE, '_ca_report.txt'), 'w', encoding='utf-8') as fh:
        fh.write("\n".join(report))
    print("done")


if __name__ == '__main__':
    main()
