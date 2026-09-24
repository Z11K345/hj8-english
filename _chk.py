# -*- coding: utf-8 -*-
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
Z = '专项练习'
f119 = os.path.join(ED, Z, '【沪教】八上英语期末完成句子119题.answers.json')
f70 = os.path.join(ED, Z, '【沪教】八上英语期末用单词的适当形式填空70题.answers.json')
log = os.path.join(BASE, '_finalize2.log')

def info(p):
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        n = len(d.get('answers', {}))
        return 'EXISTS keys=%d' % n
    return 'MISSING'

print('119:', info(f119))
print('70 :', info(f70))
print('log:', 'EXISTS' if os.path.exists(log) else 'MISSING')
