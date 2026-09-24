# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
cat = next(c for c in man['cats'] if c['name'] == '一课一练')
paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')

# 学生版
doc = fitz.open(os.path.join(BASE, paper['pdf'].replace('/', os.sep)))
stu = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close()
stu_hdrs = [(m.group(1), m.group(2).strip()) for m in CN_SEC.finditer(stu)]

# 解析版
doc = fitz.open(os.path.join(BASE, paper['answerPdf'].replace('/', os.sep)))
res = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close()
res_hdrs = [(m.group(1), m.group(2).strip()) for m in CN_SEC.finditer(res)]

card = json.load(open(os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（学生版）.card.json'), encoding='utf-8'))
card_titles = [s['title'] for s in card['sections']]

out = []
out.append('=== 学生版 CN_SEC headers (%d) ===' % len(stu_hdrs))
for i,(r,t) in enumerate(stu_hdrs):
    out.append('  %d: %s %s' % (i, r, t))
out.append('=== 解析版 CN_SEC headers (%d) ===' % len(res_hdrs))
for i,(r,t) in enumerate(res_hdrs):
    out.append('  %d: %s %s' % (i, r, t))
out.append('=== card sections (%d) ===' % len(card_titles))
for i,t in enumerate(card_titles):
    out.append('  %d: %s' % (i, t))

open(os.path.join(BASE, '_diag_align.txt'), 'w', encoding='utf-8').write("\n".join(out))
