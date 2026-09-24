# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
cat = next(c for c in man['cats'] if c['name'] == '一课一练')
paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')
pabs = os.path.join(BASE, paper['pdf'].replace('/', os.sep))  # 学生版
doc = fitz.open(pabs); text = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close()

positions = [m.start() for m in CN_SEC.finditer(text)]
segs = []
prev = 0
for pos in positions:
    segs.append(text[prev:pos]); prev = pos
segs.append(text[prev:])

card = json.load(open(os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（学生版）.card.json'), encoding='utf-8'))

out = []
for i in [4,5,9]:
    seg = segs[i] if i < len(segs) else ''
    ctitle = card['sections'][i]['title']
    ccount = card['sections'][i]['nos'][-1]
    out.append('############ student seg %d | %s | cardcount=%s ############' % (i, ctitle, ccount))
    out.append('  len=%d ; first 600 chars:' % len(seg))
    out.append('  ' + seg[:600].replace('\n','\\n'))
    # rough blank/question count: count of ____ or 题号 patterns
    blanks = len(re.findall(r'_+', seg))
    out.append('  underscore-runs=%d' % blanks)

open(os.path.join(BASE, '_diag_student.txt'), 'w', encoding='utf-8').write("\n".join(out))
