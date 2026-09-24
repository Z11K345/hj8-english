# -*- coding: utf-8 -*-
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
LOG = os.path.join(BASE, '_countcheck.txt')
out = []
def cnt(rel):
    d = json.load(open(os.path.join(BASE, rel), encoding='utf-8'))
    return len(d['answers'])
out.append('Unit1 解析版: %d (expect 119)' % cnt('exam-data/一课一练/Unit 1 Section 1 Reading（解析版）.answers.json'))
out.append('首字母70: %d (expect 70)' % cnt('exam-data/专项练习/【沪教】八上英语期末单句首字母填空70题.answers.json'))
out.append('完成句子119: %d (expect 119)' % cnt('exam-data/专项练习/【沪教】八上英语期末完成句子119题.answers.json'))
out.append('适当形式70: %d (expect 70)' % cnt('exam-data/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.answers.json'))
# spot checks
u = json.load(open(os.path.join(ED,'一课一练','Unit 1 Section 1 Reading（解析版）.answers.json'),encoding='utf-8'))['answers']
out.append('Unit1 0_1=%r 5_16=%r 6_5=%r 9_8=%r' % (u.get('0_1'), u.get('5_16'), u.get('6_5'), u.get('9_8')))
zc = json.load(open(os.path.join(ED,'专项练习','【沪教】八上英语期末完成句子119题.answers.json'),encoding='utf-8'))['answers']
out.append('完成句子 0_1=%r 0_119=%r' % (zc.get('0_1'), zc.get('0_119')))
with open(LOG,'w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("\n".join(out))
