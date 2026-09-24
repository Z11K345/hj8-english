# -*- coding: utf-8 -*-
"""扫描 exam-data/ 与 resources/ 生成 manifest.json，供 exam.html 选择试卷使用。

- JSON 试卷（extract.py 产物）按原分类归入对应类别。
- resources/<分类>/ 下成对的 （学生版）.pdf / （解析版）.pdf 会按原分类追加，
  做到 1 字不差地完美呈现原卷。
"""
import os, re, json, datetime

BASE = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\exam-data"
RES = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources"
OUT = os.path.join(BASE, "manifest.json")

CAT_META = [
    ("一课一练", "一课一练（分层练习）"),
    ("单元检测", "单元检测（基础/提升卷）"),
    ("专项练习", "专项练习（题型专练）"),
    ("知识梳理", "知识梳理（单元核心）"),
    ("知识点总结", "知识点总结（背诵）"),
]
CAT_LABELS = dict(CAT_META)

def clean_label(name):
    base = re.sub(r'\.pdf\.json$', '', name)
    base = re.sub(r'^【沪教】八上英语', '', base)
    return base.strip()

# 预建分类，保持固定顺序
cats = [{'name': cat, 'label': label, 'papers': []} for cat, label in CAT_META]
cat_map = {c['name']: i for i, c in enumerate(cats)}
extra_cats = []  # 仅有原卷 PDF 而无 JSON 的分类兜底
total_q = 0
total_papers = 0

# 1) JSON 扫描
def scan_json(cat):
    global total_q, total_papers
    d = os.path.join(BASE, cat)
    if not os.path.isdir(d):
        return
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'):
            continue
        fp = os.path.join(d, f)
        try:
            j = json.load(open(fp, encoding='utf-8'))
        except Exception:
            continue
        n = len(j.get('questions', []))
        if n == 0:
            continue
        cats[cat_map[cat]]['papers'].append({
            'file': f'{cat}/{f}'.replace('\\', '/'),
            'label': clean_label(f),
            'count': n,
        })
        total_q += n
        total_papers += 1

for cat, _ in CAT_META:
    scan_json(cat)

# 1.5) 听力音频索引：resources/听力音频/ 下的 mp3，按「Unit N Section 1-3」前缀归属对应听力试卷。
#      文件名形如：Unit 1 Section 1-3 四 听选信息 听力音频.mp3（同一份听力卷含多条音频，按题干序号 四/五/六 排序）
AUD_DIR = os.path.join(RES, '听力音频')
CN_NUM = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
def _cn2num(s):
    m = re.match(r'\s*([一二三四五六七八九十]+)', s or '')
    if not m:
        return 99
    t = m.group(1)
    if len(t) == 1:
        return CN_NUM.get(t, 99)
    if '十' in t:
        a, _, b = t.partition('十')
        return (CN_NUM.get(a, 1) if a else 1) * 10 + (CN_NUM.get(b, 0) if b else 0)
    return 99

audio_index = {}   # 'unit 1 section 1-3' -> [ {label, src, order}, ... ]
if os.path.isdir(AUD_DIR):
    for f in sorted(os.listdir(AUD_DIR)):
        if not f.lower().endswith('.mp3'):
            continue
        m = re.match(r'(Unit\s*\d+\s*Section\s*1-3)\s*(.*?)听力音频', f, re.I)
        if not m:
            continue
        key = re.sub(r'\s+', ' ', m.group(1)).strip().lower()
        tail = m.group(2).strip()
        audio_index.setdefault(key, []).append({
            'label': tail or f,
            'src': 'resources/听力音频/' + f,
            'order': _cn2num(tail),
        })
for k in audio_index:
    audio_index[k].sort(key=lambda a: a['order'])

def attach_audio(paper):
    m = re.search(r'(Unit\s*\d+\s*Section\s*1-3)', paper.get('label') or '', re.I)
    if not m:
        return
    key = re.sub(r'\s+', ' ', m.group(1)).strip().lower()
    lst = audio_index.get(key)
    if lst:
        paper['audio'] = [{'label': a['label'], 'src': a['src']} for a in lst]

# 2) 原卷 PDF（学生版+解析版）按分类追加
for cat in ("一课一练", "单元检测", "专项练习", "知识梳理", "知识点总结"):
    res_dir = os.path.join(RES, cat)
    if not os.path.isdir(res_dir):
        continue
    for f in sorted(os.listdir(res_dir)):
        if not f.endswith('（学生版）.pdf'):
            continue
        base = f[:-len('（学生版）.pdf')]
        ans = base + '（解析版）.pdf'
        if not os.path.isfile(os.path.join(res_dir, ans)):
            continue
        pdf_paper = {
            'pdf': 'resources/' + cat + '/' + f,
            'answerPdf': 'resources/' + cat + '/' + ans,
            'label': base + '（原卷·完整版）',
            'count': '原卷',
            'cat': cat,
        }
        # 若存在对应的答题卡结构（build_answercard.py 产物），挂上 card 字段，
        # 前端据此渲染「正式答题卡」替代自由文本框。
        card_file = os.path.join(BASE, cat, base + '.card.json')
        if os.path.isfile(card_file):
            pdf_paper['card'] = ('exam-data/' + cat + '/' + base + '.card.json').replace('\\', '/')
        # 若存在对应的标准答案（build_answers.py 产物），挂上 answers 字段，
        # 前端 buildCard 据此加载标准答案，交卷后才能自动批改（打 ✓/✗）。
        ans_file = os.path.join(BASE, cat, base + '.answers.json')
        if os.path.isfile(ans_file):
            pdf_paper['answers'] = ('exam-data/' + cat + '/' + base + '.answers.json').replace('\\', '/')
        attach_audio(pdf_paper)
        if cat in cat_map:
            cats[cat_map[cat]]['papers'].append(pdf_paper)
        else:
            extra_cats.append({'name': cat, 'label': CAT_LABELS.get(cat, cat+'（原卷PDF）'), 'papers': [pdf_paper]})
        total_papers += 1

# 3) 扁平原卷 PDF（未拆分成 学生版/解析版，直接作为可浏览原卷）：
#    多为 一课一练 / 专项练习 / 知识梳理 / 知识点总结。标记 readOnly，前端打开即显示 PDF，不进入计时/交卷考试流。
for cat in ("一课一练", "单元检测", "专项练习", "知识梳理", "知识点总结"):
    res_dir = os.path.join(RES, cat)
    if not os.path.isdir(res_dir):
        continue
    for f in sorted(os.listdir(res_dir)):
        if not f.lower().endswith('.pdf'):
            continue
        if f.endswith('（学生版）.pdf') or f.endswith('（解析版）.pdf'):
            continue  # 已由第 2 步作为 学生版/解析版 配对处理
        pdf_paper = {
            'pdf': 'resources/' + cat + '/' + f,
            'label': clean_label(f),
            'count': None,
            'readOnly': True,
            'cat': cat,
        }
        attach_audio(pdf_paper)
        if cat in cat_map:
            cats[cat_map[cat]]['papers'].append(pdf_paper)
        else:
            ex = next((c for c in extra_cats if c['name'] == cat), None)
            if ex: ex['papers'].append(pdf_paper)
            else: extra_cats.append({'name': cat, 'label': CAT_LABELS.get(cat, cat + '（原卷PDF）'), 'papers': [pdf_paper]})
        total_papers += 1

cats = [c for c in cats if c['papers']] + extra_cats

manifest = {
    'generated': datetime.date.today().isoformat(),
    'totalPapers': total_papers,
    'totalQuestions': total_q,
    'cats': cats,
}

with open(OUT, 'w', encoding='utf-8') as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=1)
print('生成 manifest.json 完成')
print('试卷数:', total_papers, '题目总数:', total_q)
for c in cats:
    print(f"  {c['label']}: {len(c['papers'])} 套")
