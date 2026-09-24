# -*- coding: utf-8 -*-
"""Inspect papers without answers to see if answer keys exist in pdf/answerPdf."""
import os, re, json, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')

man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))

def extract_text(path):
    pabs = os.path.join(BASE, path.replace('/', os.sep))
    if not os.path.isfile(pabs):
        return None, 'FILE_NOT_FOUND'
    doc = fitz.open(pabs)
    text = "\n".join(doc[i].get_text() for i in range(doc.page_count))
    doc.close()
    return text, 'OK'

# Collect target papers: card but no answers, plus Writing papers
targets = []
for cat in man['cats']:
    name = cat['name']
    for pp in cat['papers']:
        label = pp.get('label','')
        has_card = bool(pp.get('card'))
        has_ans = bool(pp.get('answers'))
        if has_card and not has_ans:
            targets.append((name, pp))
        elif 'Writing' in label and has_card:
            targets.append((name, pp))

report = []
report.append('目标卷数量: %d' % len(targets))
for name, pp in targets:
    label = pp.get('label','')
    pdf = pp.get('pdf','')
    ans_pdf = pp.get('answerPdf','')
    report.append('')
    report.append('## %s | %s' % (name, label))
    report.append('  pdf: %s' % pdf)
    report.append('  answerPdf: %s' % (ans_pdf or '无'))
    for field in ['pdf','answerPdf']:
        path = pp.get(field,'')
        if not path:
            continue
        text, status = extract_text(path)
        report.append('  [%s] status=%s chars=%s' % (field, status, len(text) if text else 0))
        if not text:
            continue
        # Search answer markers
        markers = ['【答案】','【解析】','参考答案','答案','范文','Keys','KEY','key','解析版']
        for mk in markers:
            idx = text.find(mk)
            if idx >= 0:
                snippet = text[idx:idx+500].replace('\n',' | ')
                report.append('    命中 "%s" at %d: %s...' % (mk, idx, snippet[:300]))
        # If no markers, dump first 600 chars and last 600 chars
        if all(text.find(mk) < 0 for mk in markers):
            first = text[:600].replace('\n',' | ')
            last = text[-600:].replace('\n',' | ')
            report.append('    无答案类标记。开头: %s' % first)
            report.append('    结尾: %s' % last)

out_path = os.path.join(BASE, '_inspect_report.txt')
with open(out_path, 'w', encoding='utf-8') as fh:
    fh.write("\n".join(report))
print('done ->', out_path)
