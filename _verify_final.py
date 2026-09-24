# -*- coding: utf-8 -*-
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
out = []
# 119 card nos
p119 = os.path.join(ED, '专项练习', '【沪教】八上英语期末完成句子119题.card.json')
c119 = json.load(open(p119, encoding='utf-8'))
nos119 = c119['sections'][0]['nos']
out.append('119 card nos: min=%d max=%d count=%d' % (min(nos119), max(nos119), len(nos119)))
# answer files exist + count (search both dirs)
def find_ans(fname):
    for d in ['专项练习', '一课一练']:
        fp = os.path.join(ED, d, fname)
        if os.path.exists(fp):
            d2 = json.load(open(fp, encoding='utf-8'))
            return '%s: %d keys' % (os.path.join(d, fname), len(d2['answers']))
    return '%s: MISSING' % fname
for f in ['【沪教】八上英语期末完成句子119题.answers.json',
          '【沪教】八上英语期末用单词的适当形式填空70题.answers.json',
          '【沪教】八上英语期末单句首字母填空70题.answers.json',
          'Unit 1 Section 1 Reading（解析版）.answers.json']:
    out.append(find_ans(f))
# manifest references resolve to existing files (a is relative to BASE, already has exam-data/)
man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
def check(label):
    for cat in man['cats']:
        for p in cat['papers']:
            if p.get('label') == label:
                a = p.get('answers')
                if not a: return '%s: NO answers' % label
                fp = os.path.join(BASE, a)   # a already includes exam-data/
                return '%s: %s -> %s' % (label, os.path.basename(a), 'OK' if os.path.exists(fp) else 'MISSING')
    return '%s: not found' % label
for lbl in ['期末完成句子119题.pdf','期末用单词的适当形式填空70题.pdf','期末单句首字母填空70题.pdf',
            'Unit 1 Section 1 Reading（原卷·完整版）','期末复习重点短语及句型.pdf','期末复习重点词汇及词性转换.pdf']:
    out.append(check(lbl))
with open(os.path.join(BASE,'_verify_final.txt'),'w',encoding='utf-8') as f:
    f.write('\n'.join(out))
