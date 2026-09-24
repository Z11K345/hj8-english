# -*- coding: utf-8 -*-
import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CATS = ['一课一练', '专项练习']
man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
problems = []
total_sections = 0
total_q = 0
covered_q = 0
checked = 0
for cat in man['cats']:
    if cat['name'] not in CATS:
        continue
    for pp in cat['papers']:
        card = pp.get('card'); ans = pp.get('answers')
        if not card or not ans:
            continue
        checked += 1
        cpath = os.path.join(BASE, card)
        apath = os.path.join(BASE, ans)
        if not os.path.isfile(cpath) or not os.path.isfile(apath):
            problems.append('missing file: ' + card); continue
        cj = json.load(open(cpath, encoding='utf-8'))
        aj = json.load(open(apath, encoding='utf-8'))
        amap = aj.get('answers', {})
        for si, sec in enumerate(cj.get('sections', [])):
            total_sections += 1
            for no in sec.get('nos', []):
                total_q += 1
                key = '%d_%d' % (si, no)
                if key in amap and str(amap[key]).strip():
                    covered_q += 1
                else:
                    problems.append('%s : %s[%d] q%d 缺答案' % (cat['name'], sec.get('title',''), si, no))
lines = []
lines.append('checked papers=%d  sections=%d  questions=%d  covered=%d' % (checked, total_sections, total_q, covered_q))
if problems:
    lines.append('PROBLEMS (%d):' % len(problems))
    for p in problems[:50]:
        lines.append('  ' + p)
else:
    lines.append('ALL ANSWERS COVERED')
open(os.path.join(BASE, '_validate_report.txt'), 'w', encoding='utf-8').write("\n".join(lines))
