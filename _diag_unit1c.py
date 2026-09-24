# -*- coding: utf-8 -*-
import os, re, json, fitz
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
cat = next(c for c in man['cats'] if c['name'] == '一课一练')
paper = next(p for p in cat['papers'] if p.get('label') == 'Unit 1 Section 1 Reading（原卷·完整版）')
pabs = os.path.join(BASE, paper['answerPdf'].replace('/', os.sep))
doc = fitz.open(pabs); text = "\n".join(doc[i].get_text() for i in range(doc.page_count)); doc.close()
atext = text[text.find('【答案】'):]

positions = [m.start() for m in CN_SEC.finditer(atext)]
segs = []
prev = 0
for pos in positions:
    segs.append(atext[prev:pos]); prev = pos
segs.append(atext[prev:])

card = json.load(open(os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（学生版）.card.json'), encoding='utf-8'))

out = []
for i, seg in enumerate(segs):
    ctitle = card['sections'][i]['title']
    ccount = card['sections'][i]['nos'][-1]
    ctype = card['sections'][i]['type']
    out.append('############ seg %d | %s | count=%s type=%s ############' % (i, ctitle, ccount, ctype))
    # extract each 【答案】 block
    for m in re.finditer(r'【答案】', seg):
        block = seg[m.end():]
        # cut at next 【 or end
        nxt = re.search(r'【', block)
        if nxt: block = block[:nxt.start()]
        block = block.strip()
        out.append('  -- block[%d]: %s' % (len(block), block[:400].replace('\n','\\n')))

open(os.path.join(BASE, '_diag_unit1c.txt'), 'w', encoding='utf-8').write("\n".join(out))
