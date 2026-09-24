# -*- coding: utf-8 -*-
import os, re, fitz, json

BASE = os.path.dirname(os.path.abspath(__file__))

def pdf_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    doc = fitz.open(pabs)
    text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return text

# Unit 1 answerPdf
text = pdf_text('resources/一课一练/Unit 1 Section 1 Reading（解析版）.pdf')
idx = text.find('【答案】')
print('=== Unit 1 解析版 answers section ===')
print(text[idx:idx+4000])
print('\n\n')

# 3 专项 papers
targets = [
    'resources/专项练习/【沪教】八上英语期末单句首字母填空70题.pdf',
    'resources/专项练习/【沪教】八上英语期末完成句子119题.pdf',
    'resources/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.pdf',
]
for t in targets:
    text = pdf_text(t)
    # find 答案版 or 解析版 section start (look for footer-like)
    for marker in ['答案版）', '解析版）', '参考答案', '【答案】']:
        idx = text.find(marker)
        if idx >= 0:
            print('===', t, 'marker:', marker, 'at', idx, '===')
            print(text[idx-200:idx+4000])
            print('\n\n')
            break
    else:
        print('===', t, 'NO MARKER ===')
        print(text[-2000:])
        print('\n\n')
