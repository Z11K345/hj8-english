# -*- coding: utf-8 -*-
"""从文字版 PDF 试卷提取单选题题干、选项、答案与解析。

统一对齐策略（覆盖三类试卷，单遍扫描）：
- 一课一练类：练习区给出题干+选项；卷末"解析版"按局部编号逐题给出【答案】+【解析】
  （解析里含"句意：…"作为题干回放）。→ 题干来自练习区，答案按"最早未作答题"顺序对齐。
- 单元检测类：卷末"解析版"整段重述每道题（题干+选项+【答案】+【详解】），全局编号 1–N。
  重述的题干与练习区相同 → 按"题干文本"去重，答案就近/按编号对齐；完形/阅读的"句意："
  解析无标记，单独按编号回填。
- 专项练习类：单一大题、答案集中在卷末（1B2C / 1．B 2．C）→ 按局部编号对齐。

要点：
- 不按页切分，整篇单遍扫描。
- 选项支持同行多选项拆分（如 "B．x C．y"）。
- 完形填空题干以"编号+选项同行"(11．A．form) 形式出现 → 记为"第N题"标签（缺篇章语境，作参考）。
- 仅保留带 >=2 个选项的题为单选题。
输出 JSON：{title,cat,pages,questions:[{no,stem,opts,answer,expl}],matched,total}
"""
import os, re, json, sys, fitz

BASE = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources"
OUT = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\exam-data"

NUM_RE = re.compile(r'^\s*(\d{1,3})\s*[．.、]\s*(.*)$')
OPT_RE = re.compile(r'^\s*([A-E])[\.．、]\s*(.*)$')
NUMOPT_RE = re.compile(r'^\s*(\d{1,3})\s*[．.、]\s*([A-E])\s*[．.、]\s*(.*)$')
ANS_PAIR_RE = re.compile(r'(\d{1,3})\s*[．.、]?\s*([A-E])')
ANS_RANGE_RE = re.compile(r'(\d{1,3})\s*[-—~]\s*(\d{1,3})\s*[:：]?\s*([A-E]{2,})')
BLOCK_MARKS = ('【答案】', '【解析】', '【详解】', '【导语】')
SECTION_RE = re.compile(r'^[一二三四五六七八九十]+、')
# 解析块：以"N．【题型/句意/根据】……故选X。"形式出现；用题型关键词锚定，避免误吞题干句
EXPL_KEYWORDS = r'(?:句意|细节|推理|主旨|最佳|篇章|词义|代词|写作|态度|观点|语篇|标题|排序|段落|猜测|归纳|判断|目的|结构|含义|根据)'
EXPL_RE = re.compile(
    r'(\d{1,3})\s*[．.、]\s*' + EXPL_KEYWORDS +
    r'([^\n]*?[\s\S]*?故选[ABCDE]。)'
)

def clean_line(s):
    return s.replace('（', '(').replace('）', ')').strip()

def norm_stem(stem):
    return re.sub(r'\s+', '', stem).strip()

def clean_text(s):
    """清理页脚水印/章节尾注等噪声：解析版、微信公众号、第N页共M页、Unit 章节标题碎片。"""
    if not s:
        return s
    # 截断第一个噪声锚点之后的内容（噪声通常出现在行尾，由分页导致）
    cut = len(s)
    for a in (r'解析版', r'微信公众号', r'第\s*\d+\s*页\s*共'):
        m = re.search(a, s)
        if m and m.start() < cut:
            cut = m.start()
    s = s[:cut]
    # 去除被拼到题干/解析末尾的章节标题碎片（如 "Unit 1 Section 1 Reading 分层练习("）
    s = re.sub(r'Unit\s*\d+[\s\S]*$', '', s)
    s = re.sub(r'分层练习', '', s)
    s = re.sub(r'[ \t]{2,}', ' ', s)
    s = re.sub(r'\s+([.,;:!?])', r'\1', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def split_inline_options(line):
    parts = re.split(r'(?=\s[A-E][\.．、])', line)
    out = []
    for p in parts:
        m = OPT_RE.match(p.strip())
        if m:
            out.append((m.group(1), m.group(2).strip()))
    return out

def capture_block(lines, i):
    buf = [lines[i]]
    j = i + 1
    while j < len(lines):
        ln = lines[j]
        if any(mk in ln for mk in BLOCK_MARKS):
            break
        # 仅当"编号后有实质题干"(长度>1)才视为下一题起点；
        # 避免把批量答案续行(如 "12．D")误判为题号而截断答案块
        mm = NUM_RE.match(ln)
        if mm and OPT_RE.match(ln) is None and len(mm.group(2).strip()) > 1:
            break
        buf.append(ln)
        j += 1
    return '\n'.join(buf), j

def parse_answer_pairs(block):
    ans = {}
    for m in re.finditer(ANS_RANGE_RE, block):
        a, b, letters = int(m.group(1)), int(m.group(2)), m.group(3)
        for k, ch in enumerate(letters):
            if a + k <= b:
                ans[a + k] = ch
    for num, letter in ANS_PAIR_RE.findall(block):
        ans[int(num)] = letter
    if not ans:
        sm = re.search(r'【答案】\s*([A-E])', block)
        if sm:
            return sm.group(1)
    return ans

def extract_pdf(cat, fname):
    path = os.path.join(BASE, cat, fname)
    doc = fitz.open(path)
    raw_pages = [doc[i].get_text() for i in range(doc.page_count)]
    doc.close()
    lines = [clean_line(l) for l in '\n'.join(raw_pages).split('\n')]
    lines = [l for l in lines if l]

    # 解析版处理策略：若"解析版"区域会重述题干（单元检测类），则只解析解析版区域，
    # 避免与练习区题干因措辞微差被当成两题而错位；若解析版只给答案（一课一练类），整篇解析。
    marker = -1
    for idx, l in enumerate(lines):
        if '解析版' in l:
            marker = idx
            break
    if marker >= 0:
        probe = lines[marker:marker + 250]
        restates = False
        for l in probe:
            if any(k in l for k in ('答案', '解析', '详解', '导语')):
                continue
            mm = NUM_RE.match(l)
            if mm and OPT_RE.match(l) is None and len(mm.group(2).strip()) > 1:
                restates = True
                break
        if restates:
            lines = lines[marker:]
            full_text = '\n'.join(lines)

    questions = []          # 真实单选题
    seen_stems = set()      # 已用归一化题干（去重重述）
    cur = None
    cur_is_real = False
    last_answered = None
    current_section = ''
    full_text = '\n'.join(lines)

    def flush_cur():
        nonlocal cur, cur_is_real
        if cur is None:
            return
        if cur_is_real:
            cur['stem'] = clean_text(cur['stem'])
            if len(cur['opts']) >= 2 and norm_stem(cur['stem']):
                questions.append(cur)
                seen_stems.add(norm_stem(cur['stem']))
        cur = None
        cur_is_real = False

    def earliest_unmatched():
        for q in questions:
            if q['answer'] is None:
                return q
        return None

    i = 0
    N = len(lines)
    while i < N:
        l = lines[i]
        if SECTION_RE.match(l):
            current_section = l
            i += 1
            continue
        m = NUM_RE.match(l)
        if m and OPT_RE.match(l) is None:
            no = int(m.group(1))
            stem = m.group(2).strip()
            # 解析/解释性文字（"句意：…""细节理解题。…"等）不是题目，跳过避免误建题
            if ('题。' in stem[:15]) or re.match(
                    r'^(句意|解析|详解|导语|答案|考点|考查|分析|主旨|说明|任务|阅读表达|书面表达|完成句子|根据|回答|译文|翻译|细节|推理|最佳|篇章|词义|代词|写作|态度|观点|语篇|标题|排序|段落|猜测|归纳|判断|目的|结构|含义)',
                    stem):
                i += 1
                continue
            nk = norm_stem(stem)
            if nk in seen_stems:
                # 解析版重述（与练习区题干相同）→ 不作为新题，仅作答案落点占位
                cur = {'no': no, 'stem': stem, 'opts': [], 'answer': None,
                       'expl': None, '_dup': True}
                cur_is_real = False
                i += 1
                continue
            flush_cur()
            cur = {'no': no, 'stem': stem, 'opts': [], 'answer': None,
                   'expl': None, '_dup': False}
            cur_is_real = True
            i += 1
            continue
        nm = NUMOPT_RE.match(l)
        if nm and cur is not None:
            no = int(nm.group(1))
            if cur is None or cur.get('_dup') or len(cur['opts']) >= 2:
                flush_cur()
                label = (current_section.split('（')[0].strip() + ' ' if current_section else '') + f'第{no}题'
                cur = {'no': no, 'stem': label, 'opts': [], 'answer': None,
                       'expl': None, '_dup': False}
                cur_is_real = True
            cur['opts'].append(nm.group(3).strip())
            i += 1
            continue
        om = OPT_RE.match(l)
        if om and cur is not None and not cur.get('_dup'):
            for _, text in split_inline_options(l):
                cur['opts'].append(text)
            i += 1
            continue
        if cur is not None and not cur.get('_dup') and len(cur['opts']) == 0 and cur['stem']:
            cur['stem'] += l
            i += 1
            continue
        if '【答案】' in l:
            flush_cur()  # 先把当前题纳入 questions，避免内嵌答案错位
            block, i = capture_block(lines, i)
            res = parse_answer_pairs(block)
            if isinstance(res, str):
                q = earliest_unmatched()
                if q is not None:
                    q['answer'] = res
                    last_answered = q
            else:
                flush_cur()
                for num, letter in res.items():
                    for q in reversed(questions):
                        if q['no'] == num and q['answer'] is None:
                            q['answer'] = letter
                            last_answered = q
                            break
            continue
        if '【解析】' in l or '【详解】' in l:
            block, i = capture_block(lines, i)
            whole = re.sub(r'^【(?:解析|详解)】\s*', '', block).strip()
            if last_answered is not None:
                last_answered['expl'] = clean_text(whole)
            continue
        i += 1
    flush_cur()

    # 解析兜底：单元检测完形/阅读解析无【详解】标记（"N．…故选X。"形式），按编号回填缺解析的题
    for num, seg in EXPL_RE.findall(full_text):
        n = int(num)
        for q in questions:
            if q['no'] == n and not q.get('expl'):
                q['expl'] = clean_text(seg.strip())
                break

    # 仅保留带 >=2 选项且有答案的单选题（无答案的多为解析/解释性误建行）
    questions = [q for q in questions if len(q['opts']) >= 2 and q['answer']]
    matched = len(questions)
    return {
        'title': fname,
        'cat': cat,
        'pages': len(raw_pages),
        'questions': questions,
        'matched': matched,
        'total': len(questions),
    }

if __name__ == '__main__':
    MODE = sys.argv[1] if len(sys.argv) > 1 else 'samples'
    if MODE == 'samples':
        targets = [
            ("一课一练", "Unit 1 Section 2 Grammar（分层练习）.pdf"),
            ("单元检测", "Unit 1（基础卷）.pdf"),
            ("专项练习", "【沪教】八上英语单项选择100题.pdf"),
        ]
    else:
        targets = []
        for cat in ("一课一练", "单元检测", "专项练习"):
            d = os.path.join(BASE, cat)
            for f in sorted(os.listdir(d)):
                if f.lower().endswith('.pdf'):
                    targets.append((cat, f))
    if not os.path.exists(OUT):
        os.makedirs(OUT)
    for cat, f in targets:
        try:
            r = extract_pdf(cat, f)
        except Exception as e:
            print(f"!! ERROR {cat}|{f}: {e}")
            continue
        print("=" * 70)
        print(f"{cat} | {f}")
        print(f"  页数 {r['pages']} | 抽取MC题 {r['total']} | 答案匹配 {r['matched']}")
        with_ans = [q['no'] for q in r['questions'] if q['answer']]
        print(f"  有答案题号(前40): {with_ans[:40]}")
        with_expl = sum(1 for q in r['questions'] if q.get('expl'))
        print(f"  带解析 {with_expl}")
        outp = os.path.join(OUT, cat)
        if not os.path.exists(outp):
            os.makedirs(outp)
        with open(os.path.join(outp, f + '.json'), 'w', encoding='utf-8') as fh:
            json.dump(r, fh, ensure_ascii=False, indent=1)
