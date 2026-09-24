# -*- coding: utf-8 -*-
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(BASE, '_countcheck2.txt')
out = []
files = {
 'Unit1': 'exam-data/一课一练/Unit 1 Section 1 Reading（解析版）.answers.json',
 '首字母70': 'exam-data/专项练习/【沪教】八上英语期末单句首字母填空70题.answers.json',
 '完成句子119': 'exam-data/专项练习/【沪教】八上英语期末完成句子119题.answers.json',
 '适当形式70': 'exam-data/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.answers.json',
}
for name, rel in files.items():
    p = os.path.join(BASE, rel)
    if not os.path.exists(p):
        out.append('%s: FILE MISSING' % name); continue
    try:
        d = json.load(open(p, encoding='utf-8'))
        out.append('%s: keys=%d' % (name, len(d.get('answers', {}))))
    except Exception as e:
        out.append('%s: LOAD ERROR %s' % (name, repr(e)))
with open(LOG, 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
