# -*- coding: utf-8 -*-
import os, re, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')

CN_SEC = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$', re.M)

FILES = [
    'resources/一课一练/Unit 1 Section 2 Grammar（分层练习）.pdf',
    'resources/专项练习/【沪教】八上英语完形填空17篇.pdf',
    'resources/专项练习/【沪教】八上英语期末短文填空36篇.pdf',
    'resources/专项练习/【沪教】八上英语短文语法填空21篇.pdf',
    'resources/专项练习/【沪教】八上英语阅读还原五选五14篇.pdf',
]

def dump(pdf):
    cat = pdf.split('/')[1]
    base = os.path.basename(pdf)
    p = os.path.join(BASE, pdf.replace('/', os.sep))
    doc = fitz.open(p)
    text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    ans_start = text.find('【答案】')
    qtext = text[:ans_start]; atext = text[ans_start:]
    out = []
    out.append('='*70)
    out.append('%s | %s' % (cat, base))
    out.append('qtext_len=%d atext_len=%d' % (len(qtext), len(atext)))
    csec_q = CN_SEC.findall(qtext)
    csec_a = CN_SEC.findall(atext)
    out.append('CN_SEC in qtext=%d  in atext=%d' % (len(csec_q), len(csec_a)))
    out.append('CN_SEC atext headers: ' + str([h[1][:14] for h in csec_a][:30]))
    # answer blocks
    blocks = []
    for mm in re.finditer(r'【答案】', atext):
        start = mm.end(); rest = atext[start:]
        nxt = re.search(r'【', rest)
        seg = rest[:nxt.start()] if nxt else rest
        seg0 = re.split(r'【解析】', seg)[0]
        blocks.append(seg0)
    out.append('【答案】blocks=%d' % len(blocks))
    # show first 3 and any block with many items
    for i, b in enumerate(blocks[:3]):
        nums = re.findall(r'\d{1,3}\s*[.．.]\s*', b)
        parts = re.split(r'\d{1,3}\s*[.．.]\s*', b)
        items = [x for x in parts[1:] if x.strip()]
        out.append('  block[%d] len=%d numnums=%d items=%d' % (i, len(b), len(nums), len(items)))
        out.append('     raw[:160]=%r' % b[:160])
    # a 'passage' heuristic: lines starting with 数字. at line start in qtext (cloze options?)
    opt_lines = re.findall(r'(?m)^\s*\d+\s*[.．、)）]\s*[A-Za-z]', qtext)
    out.append('qtext lines "N. letter" (cloze options?)=%d' % len(opt_lines))
    # look for passage markers like Passage or （  ）or blank markers ___N___
    blank_marks = re.findall(r'_{2,}\s*(\d+)\s*_{2,}', qtext)
    out.append('qtext blank markers ___N___ =%d' % len(blank_marks))
    with open(os.path.join(BASE, '_diag2.txt'), 'a', encoding='utf-8') as fh:
        fh.write("\n".join(out) + "\n")

if __name__ == '__main__':
    try:
        fh = open(os.path.join(BASE, '_diag2.txt'), 'w', encoding='utf-8')
        for pdf in FILES:
            dump(pdf)
        fh.close()
        print('done')
    except Exception as e:
        import traceback
        with open(os.path.join(BASE, '_diag2.txt'), 'a', encoding='utf-8') as fe:
            fe.write('ERROR: ' + repr(e) + '\n' + traceback.format_exc())
