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

# card sections
card = json.load(open(os.path.join(ED, '一课一练', os.path.basename(paper['card']) if False else 'Unit 1 Section 1 Reading（学生版）.card.json'), encoding='utf-8'))
card_secs = card['sections']

out = []
for i, seg in enumerate(segs):
    cnt_ans = seg.count('【答案】')
    # sample markers
    mc_letters = re.findall(r'【答案】\s*([A-Fa-f])', seg)
    # try plain numbered extraction
    body = re.sub(r'【解析】[\s\S]*?(?=\n\d{1,3}\s*[.．.])', '', seg)
    body = re.sub(r'【解析】[\s\S]*$', '', body)
    parts = re.split(r'(\d{1,3})\s*[.．.]\s*', body)
    plain_items = []
    for k in range(1, len(parts)-1, 2):
        t = parts[k+1].strip()
        if t: plain_items.append(t)
    ctitle = card_secs[i]['title'] if i < len(card_secs) else '?'
    ccount = card_secs[i]['nos'][-1] if i < len(card_secs) else '?'
    ctype = card_secs[i]['type'] if i < len(card_secs) else '?'
    out.append('seg %d | card=%s(%s,type=%s) | 【答案】=%d | mc_letters=%d | plain_items=%d' % (
        i, ctitle, ccount, ctype, cnt_ans, len(mc_letters), len(plain_items)))
    # show a few plain items
    out.append('   plain sample: ' + ' || '.join(plain_items[:3]))

open(os.path.join(BASE, '_diag_unit1b.txt'), 'w', encoding='utf-8').write("\n".join(out))
