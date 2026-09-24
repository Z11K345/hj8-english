# -*- coding: utf-8 -*-
import os, re, json, traceback
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
LOG = os.path.join(BASE, '_finalize.log')

def safe_write_card():
    card_path = os.path.join(ED, '一课一练', 'Unit 1 Section 1 Reading（学生版）.card.json')
    card = json.load(open(card_path, encoding='utf-8'))
    card['sections'][5]['nos'] = list(range(1, 17))   # 短文填空 9 -> 16
    card['sections'][6]['nos'] = list(range(1, 6))     # 阅读还原 1 -> 5
    card['sections'][6]['opts'] = 5                    # A-E
    card['sections'][9]['nos'] = list(range(1, 9))     # 阅读理解 4 -> 8
    with open(card_path, 'w', encoding='utf-8') as f:
        json.dump(card, f, ensure_ascii=False, indent=1)

def safe_write_manifest():
    man_path = os.path.join(ED, 'manifest.json')
    man = json.load(open(man_path, encoding='utf-8'))
    def set_ans(label, rel):
        for cat in man['cats']:
            for p in cat['papers']:
                if p.get('label') == label:
                    p['answers'] = rel
                    return
        raise ValueError('not found: ' + label)
    set_ans('Unit 1 Section 1 Reading（原卷·完整版）',
            'exam-data/一课一练/Unit 1 Section 1 Reading（解析版）.answers.json')
    set_ans('期末单句首字母填空70题.pdf',
            'exam-data/专项练习/【沪教】八上英语期末单句首字母填空70题.answers.json')
    set_ans('期末完成句子119题.pdf',
            'exam-data/专项练习/【沪教】八上英语期末完成句子119题.answers.json')
    set_ans('期末用单词的适当形式填空70题.pdf',
            'exam-data/专项练习/【沪教】八上英语期末用单词的适当形式填空70题.answers.json')
    for lbl in ['期末复习重点短语及句型.pdf', '期末复习重点词汇及词性转换.pdf']:
        for cat in man['cats']:
            for p in cat['papers']:
                if p.get('label') == lbl:
                    p.pop('card', None); p.pop('answers', None)
    with open(man_path, 'w', encoding='utf-8') as f:
        json.dump(man, f, ensure_ascii=False, indent=1)

out = []
try:
    safe_write_card()
    out.append('card fixed OK')
except Exception as e:
    out.append('CARD ERROR: ' + traceback.format_exc())
try:
    safe_write_manifest()
    out.append('manifest fixed OK')
except Exception as e:
    out.append('MANIFEST ERROR: ' + traceback.format_exc())

with open(LOG, 'w', encoding='utf-8') as f:
    f.write("\n".join(out))
print("\n".join(out))
