# -*- coding: utf-8 -*-
"""Add missing answers.json + fix under-counted card sections for Unit 1 原卷,
and build answers for the three 专项 papers whose keys live in a tail section.

Targets:
- Unit 1 Section 1 Reading（原卷·完整版）: answers from its answerPdf（解析版）.
  Card had 3 under-counted sections (短文填空 9->16, 阅读还原 1->5, 阅读理解 4->8)
  caused by gen_ca's page-footer split bug; fixed here and answers aligned.
- 专项练习 期末单句首字母填空70题: 答案版 tail
- 专项练习 期末完成句子119题: 解析版 tail
- 专项练习 期末用单词的适当形式填空70题: 答案版 tail
Also removes the answer-card from two pure vocab reference sheets.
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

# ===== Unit 1 原卷 answers (verified against 解析版, aligned to card sections 0-9) =====
UNIT1 = {
 0: ["was unusually talented in","was born","in the countryside","showed great intelligence",
     "think about","be related to","come from","come in different sizes","as small as",
     "more than","die out","either….or"],
 1: ["B","D","D","A","C","A","A","D","C","B","A","B"],
 2: ["Dinosaurs","Perhaps","notebook","intelligent","talented","artistic","vehicles","relate",
     "completely","genius","includes","rules"],
 3: ["musical musician","inventor invention to invent","intelligence intelligent","talent talented",
     "artist art","scientist science","Carefully","to paint painting","include including",
     "completed completely"],
 4: ["is talented in playing","shows great intelligence in","is related to","Either or has checked",
     "changed the way","was born in the countryside","die out","look it up","as heavy as"],
 5: ["invention","Perhaps","completely","included","talent","Genius","knowledge","them","in",
     "countries","traditional","is discovered","will appear","carefully","to check","amazing"],
 6: ["C","D","E","A","B"],
 7: ["C","D","B","C","B","C","A","B","D","D","B","B","A","B","D"],
 8: ["B","A","C","C","B","D","D","B","A","C"],
 9: ["C","D","B","D","D","D","A","D"],
}

EXPECTED_UNIT1 = {0:12,1:12,2:12,3:10,4:9,5:16,6:5,7:15,8:10,9:8}

def fix_unit1(man, log):
    cat = next(c for c in man['cats'] if c['name'] == '一课一练')
    paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')
    # verify + build answers
    answers = {}
    for si, items in UNIT1.items():
        if len(items) != EXPECTED_UNIT1[si]:
            raise ValueError('Unit1 sec %d 答案数%s!=%s' % (si, len(items), EXPECTED_UNIT1[si]))
        for j, a in enumerate(items):
            answers['%d_%d' % (si, j+1)] = a
    base = os.path.splitext(os.path.basename(paper['answerPdf']))[0]
    ans_path = os.path.join(ED, '一课一练', base + '.answers.json')
    json.dump({'answers': answers, 'positions': {}}, open(ans_path, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    paper['answers'] = 'exam-data/一课一练/' + base + '.answers.json'
    # fix under-counted card sections
    card_path = os.path.join(BASE, paper['card'].replace('exam-data/', '', 1))
    card = json.load(open(card_path, encoding='utf-8'))
    card['sections'][5]['nos'] = list(range(1, 17))           # 短文填空 9 -> 16
    card['sections'][6]['nos'] = list(range(1, 6))            # 阅读还原 1 -> 5
    card['sections'][6]['opts'] = 5                           # options A-E
    card['sections'][9]['nos'] = list(range(1, 9))            # 阅读理解 4 -> 8
    json.dump(card, open(card_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log.append('Unit 1 原卷：写入 %d 条答案；修正卡片 短文填空->16, 阅读还原->5, 阅读理解->8' % len(answers))

# ===== 专项 papers: robust global-split parser (handles embedded numbers & 解析 blocks) =====
CN_NUM = re.compile(r'(\d{1,3})\s*[.．.]\s*')

def _remove_jiexi(body):
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', body)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    return body

def _extract_numbered(text, expected):
    body = _remove_jiexi(text)
    parts = re.split(CN_NUM, body)
    items = []
    for k in range(1, len(parts)-1, 2):
        t = parts[k+1].strip()
        if t:
            items.append(t)
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

def fix_zhuanxiang(man, label, markers, expected, ans_name, log):
    cat = next(c for c in man['cats'] if c['name'] == '专项练习')
    paper = next(p for p in cat['papers'] if p.get('label') == label)
    text = pdf_text(paper['pdf'])
    tail = _find_answer_section(text, markers)
    if tail is None:
        raise ValueError('%s 未找到标记 %s' % (ans_name, markers))
    items = _extract_numbered(tail, expected)
    if len(items) != expected:
        raise ValueError('%s 答案数不是%d: %d' % (ans_name, expected, len(items)))
    base = os.path.splitext(os.path.basename(paper['pdf']))[0]
    ans_path = os.path.join(ED, '专项练习', base + '.answers.json')
    os.makedirs(os.path.dirname(ans_path), exist_ok=True)
    ans = {'0_%d' % (i+1): items[i] for i in range(expected)}
    json.dump({'answers': ans, 'positions': {}}, open(ans_path, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    paper['answers'] = 'exam-data/专项练习/' + base + '.answers.json'
    log.append('%s：写入 %d 条答案' % (ans_name, len(ans)))

def remove_card_from_reference(man, label, log):
    for cat in man['cats']:
        for p in cat['papers']:
            if p.get('label') == label:
                p.pop('card', None)
                p.pop('answers', None)
                log.append('移除答题卡：%s' % label)
                return
    log.append('未找到参考表：%s' % label)

if __name__ == '__main__':
    man_path = os.path.join(ED, 'manifest.json')
    man = json.load(open(man_path, encoding='utf-8'))
    log = []
    fix_unit1(man, log)
    fix_zhuanxiang(man, '期末单句首字母填空70题.pdf', ['答案版）','答案版)'], 70, '首字母填空70题', log)
    fix_zhuanxiang(man, '期末完成句子119题.pdf', ['解析版）','解析版)'], 119, '完成句子119题', log)
    fix_zhuanxiang(man, '期末用单词的适当形式填空70题.pdf', ['答案版）','答案版)'], 70, '适当形式填空70题', log)
    remove_card_from_reference(man, '期末复习重点短语及句型.pdf', log)
    remove_card_from_reference(man, '期末复习重点词汇及词性转换.pdf', log)
    json.dump(man, open(man_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(BASE, '_fix_missing_answers.log'), 'w', encoding='utf-8').write("\n".join(log))
    print("\n".join(log))
