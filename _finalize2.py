# -*- coding: utf-8 -*-
"""Finalize answers for 期末完成句子119题 and 期末用单词的适当形式填空70题.
- Robust numbered-answer parser: handles line-start "N.", line-start "N " (space),
  and mid-line "N." (e.g. "help 34. be") forms; strips page-header/footer lines;
  removes 【解析】 blocks before splitting.
- Fix 完成句子119 card: gen_ca dropped Q118/Q119 (page-footer bug) -> nos 1..119.
"""
import os, re, json, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')

def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs)
    t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return t

HEADER_RE = re.compile(r'(?m)^【沪教】|^第\s*\d+\s*页\s*共\s*\d+\s*页|^微信公众号')

# Line-start item number in either "N." or "N " (space) form.
DELIM_LS = re.compile(r'(?m)(?:^|\n)\s*(\d{1,3})(?:[.．.]\s*|\s+(?=\S))')
# Mid-line "N." form (e.g. "help 34. be"); deduped against LS.
DELIM_ANY = re.compile(r'(\d{1,3})\s*[.．.]\s*')

def _extract_numbered(text, expected):
    """Extract `expected` answer items in DOCUMENT ORDER. Answers are keyed by
    position (not printed number) so source typos like '44' for '22' still land
    on the right blank. LS captures line-start items; ANY captures mid-line ones
    (e.g. 'help 34.'). Each item's own 【解析】 tail is stripped per segment."""
    matches = []
    for m in DELIM_LS.finditer(text):
        matches.append((m.start(), m.end()))
    for m in DELIM_ANY.finditer(text):
        matches.append((m.start(), m.end()))
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
        nxt = dedup[i + 1][0] if i + 1 < n else len(text)
        seg = text[e:nxt]
        seg = re.sub(r'【解析】[\s\S]*$', '', seg)   # drop this item's 解析 tail
        seg = HEADER_RE.sub('', seg).strip()
        items.append(seg)
    if len(items) < expected:
        raise ValueError('题数不足: %d < %d' % (len(items), expected))
    return items[:expected]

def _find_answer_section(text, markers):
    search_start = 0
    while True:
        pos = -1; fm = None
        for mk in markers:
            idx = text.find(mk, search_start)
            if idx >= 0 and (pos < 0 or idx < pos):
                pos = idx; fm = mk
        if pos < 0:
            return None
        tail = text[pos:]
        if re.search(r'(?m)^\s*\d{1,3}\s*[.．.]\s*\S', tail[:3000]):
            return tail
        search_start = pos + len(fm)

def build_answers(man, label, markers, expected, log):
    cat = next(c for c in man['cats'] if c['name'] == '专项练习')
    paper = next(p for p in cat['papers'] if p.get('label') == label)
    text = pdf_text(paper['pdf'])
    tail = _find_answer_section(text, markers)
    if tail is None:
        raise ValueError('%s 未找到答案标记' % label)
    items = _extract_numbered(tail, expected)
    base = os.path.splitext(os.path.basename(paper['pdf']))[0]
    ans_path = os.path.join(ED, '专项练习', base + '.answers.json')
    ans = {'0_%d' % (i + 1): items[i] for i in range(expected)}
    with open(ans_path, 'w', encoding='utf-8') as f:
        json.dump({'answers': ans, 'positions': {}}, f, ensure_ascii=False, indent=1)
    paper['answers'] = 'exam-data/专项练习/' + base + '.answers.json'
    log.append('%s：写入 %d 条答案 -> %s' % (label, len(ans), os.path.basename(ans_path)))

def fix_card_nos(man, label, expected, log):
    cat = next(c for c in man['cats'] if c['name'] == '专项练习')
    paper = next(p for p in cat['papers'] if p.get('label') == label)
    card_path = os.path.join(ED, paper['card'].replace('exam-data/', '', 1))
    with open(card_path, 'r', encoding='utf-8') as f:
        card = json.load(f)
    old = card['sections'][0]['nos']
    card['sections'][0]['nos'] = list(range(1, expected + 1))
    with open(card_path, 'w', encoding='utf-8') as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    log.append('%s：卡片 nos 由 %d 项修正为 1..%d' % (label, len(old), expected))

if __name__ == '__main__':
    import traceback
    man_path = os.path.join(ED, 'manifest.json')
    with open(man_path, 'r', encoding='utf-8') as f:
        man = json.load(f)
    log = []
    try:
        build_answers(man, '期末完成句子119题.pdf', ['解析版）', '解析版)'], 119, log)
        fix_card_nos(man, '期末完成句子119题.pdf', 119, log)
        build_answers(man, '期末用单词的适当形式填空70题.pdf', ['答案版）', '答案版)'], 70, log)
        with open(man_path, 'w', encoding='utf-8') as f:
            json.dump(man, f, ensure_ascii=False, indent=1)
        log.append('manifest 已更新')
    except Exception:
        log.append('EXCEPTION:\n' + traceback.format_exc())
    with open(os.path.join(BASE, '_finalize2.log'), 'w', encoding='utf-8') as f:
        f.write("\n".join(log))
