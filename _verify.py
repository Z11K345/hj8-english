# -*- coding: utf-8 -*-
import os, re, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
out = []

# 1. manifest checks
man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
def find_paper(label):
    for cat in man['cats']:
        for p in cat['papers']:
            if p.get('label') == label:
                return p
    return None

checks = [
 'Unit 1 Section 1 Reading（原卷·完整版）',
 '期末单句首字母填空70题.pdf',
 '期末完成句子119题.pdf',
 '期末用单词的适当形式填空70题.pdf',
 '期末复习重点短语及句型.pdf',
 '期末复习重点词汇及词性转换.pdf',
]
for lbl in checks:
    p = find_paper(lbl)
    if p is None:
        out.append('MISSING paper: %s' % lbl); continue
    out.append('%s -> has card=%s answers=%s' % (lbl, 'card' in p, 'answers' in p))

# 2. answer counts
def cnt_ans(rel):
    d = json.load(open(os.path.join(BASE, rel), encoding='utf-8'))
    return len(d['answers'])
out.append('--- answers counts ---')
out.append('Unit1 解析版: %d (expect 119)' % cnt_ans('exam-data/一课一练/Unit 1 Section 1 Reading（解析版）.answers.json'))
out.append('首字母70: %d (expect 70)' % cnt_ans('exam-data/专项练习/【沪教】八上英语期末单句首字母填空70题.answers.json'))
out.append('完成句子119: %d (expect 119)' % cnt_ans('exam-data/专项练习/【沪教】八上英语期末完成句子119题.answers.json'))
out.append('适当形式70: %d (expect 70)' % cnt_ans('exam-data/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.answers.json'))

# 3. card fixes
card = json.load(open(os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（学生版）.card.json'), encoding='utf-8'))
secs = card['sections']
out.append('--- Unit1 card sections ---')
for i,s in enumerate(secs):
    out.append('  %d: %s type=%s nos=%d opts=%s' % (i, s['title'], s['type'], len(s['nos']), s.get('opts','-')))

# 4. spot-check a few Unit1 answers
ua = json.load(open(os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（解析版）.answers.json'), encoding='utf-8'))['answers']
out.append('--- Unit1 spot checks ---')
out.append('0_1=%s' % ua.get('0_1'))
out.append('5_16=%s' % ua.get('5_16'))
out.append('6_5=%s' % ua.get('6_5'))
out.append('9_8=%s' % ua.get('9_8'))

open(os.path.join(BASE, '_verify.txt'), 'w', encoding='utf-8').write("\n".join(out))
