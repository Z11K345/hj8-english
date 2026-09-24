# -*- coding: utf-8 -*-
# 为一课一练 / 专项练习 这种只有 PDF、没有 card.json 的试卷，
# 从 PDF 文本层自动识别「大题 → 题号 → 题型(单选/填空/作文)」，生成结构化答题卡 card.json。
# 用法：
#   python gen_cards.py --dry            # 只检测打印，不写盘
#   python gen_cards.py --dry --only 单项选择
#   python gen_cards.py                  # 正式生成并写入 manifest
import os, re, sys, json, argparse, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
RES = os.path.join(BASE, 'resources')
CATS_WITH_CARD = ['一课一练', '专项练习']          # 这两类需要结构化答题卡
CATS_SKIP     = ['知识梳理', '知识点总结']         # 无题目，不生成

# 大题分隔：一二三四…、 或 一二三四…．
CN_SEC   = re.compile(r'^\s*([一二三四五六七八九十]+)\s*[、.．]\s*(.+)$')
# 题号：行首数字 + 标点（覆盖大多数题，含英文题干）
QNO_START = re.compile(r'(?m)^\s*(\d+)\s*[.．、)）]')
# 题号：行中数字 + 标点 + 紧跟中文/下划线（覆盖「1.… 2.出生…」这种挤在一行的填空）
QNO_MID   = re.compile(r'(\d+)\s*[.．、)）]\s*(?=[\u4e00-\u9fff_])')
# 选项行：行首 A. / B. …（用于数单选题数量，每个单选恰好一个 A 选项）
OPT_A = re.compile(r'(?m)^\s*A\s*[\.．、]')
# 题目类关键字：文件名或板块标题命中其一，即判定为「习题卷」，才生成答题卡。
#  deliberately 不含 篇/表达/写作/范文/书面 —— 这些属于写作指导/范文背诵，不是习题。
EX_KW = ['填空','选择','完成','翻译','首字母','适当形式','语法','完形','阅读','听力',
         '语音','默写','词组','单词','语篇','匹配','还原','听选','补全','短文','短语',
         '词汇','句型','单项','题','阅读配对','阅读填空','语法填空']
def is_exercise(title, sections):
    if any(s['type'] == 'mc' for s in sections):
        return True
    # 文件名/卷名（专项卷多为中文卷名，如「单项选择100题」）命中即习题卷
    if any(k in title for k in EX_KW):
        return True
    # 板块标题须是「短小干净」的题型名（≤24字）才认作习题，避免写作指导里的长句标题误判
    for s in sections:
        t = s['title']
        if len(t) <= 24 and any(k in t for k in EX_KW):
            return True
    return False

def classify(title, body):
    if re.search(r'表达|作文|写作|书面', title):
        return 'essay', 0
    opt_a = len(OPT_A.findall(body))
    if opt_a > 0 or re.search(r'选择|阅读|匹配|还原|五选五|六选五|七选五|信息|完形|单选|语法选择', title):
        return 'mc', 4
    return 'blank', 0

def detect_card(text, title):
    sections = _raw_card(text)
    if not is_exercise(title, sections):
        return []          # 写作指导/范文背诵等非习题卷，不生成答题卡
    return sections

def _raw_card(text):
    lines = text.split('\n')
    sections = []
    cur_title = None
    cur_body = []
    has_sec = False
    for ln in lines:
        m = CN_SEC.match(ln)
        if m:
            if cur_title is not None:
                sections.append((cur_title, cur_body))
            cur_title = m.group(2).strip() or ('第' + m.group(1) + '部分')
            cur_body = []
            has_sec = True
        else:
            if cur_title is not None:
                cur_body.append(ln)
    if cur_title is not None:
        sections.append((cur_title, cur_body))
    if not has_sec:
        sections = [('全卷', lines)]
    out = []
    for st, body in sections:
        joined = '\n'.join(body)
        typ, opts = classify(st, joined)
        if typ == 'mc':
            # 单选题干以「1. 2. …」行首数字开头，直接数题干即可（选项行以字母开头，不会被计入）
            nums = {int(x) for x in QNO_START.findall(joined)}
            nums = {n for n in nums if 1 <= n <= 400}
            nq = len(nums) or len(OPT_A.findall(joined))
        elif typ == 'blank':
            nums = {int(x) for x in QNO_START.findall(joined)} | \
                   {int(x) for x in QNO_MID.findall(joined)}
            nums = {n for n in nums if 1 <= n <= 400}
            nq = len(nums)
        else:
            nq = 0
        if nq == 0 and typ != 'essay':
            continue
        sec = {'title': st, 'type': typ, 'nos': list(range(1, nq + 1))}
        if typ == 'mc':
            sec['opts'] = opts
        out.append(sec)
    return out

# PDF 文本抽取放在独立子进程里执行：pdfminer 的底层 C 扩展在个别 PDF 上会偶发段错误（SIGSEGV），
# 若在主进程抽取会直接中断整批生成；子进程崩了只跳过该卷，不影响其余。
_EXTRACT_WORKER = (
    "import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8');"
    "from pdfminer.high_level import extract_text;"
    "print(extract_text(sys.argv[1]))"
)
def extract_safe(pdf):
    p = os.path.join(BASE, pdf)
    if not os.path.exists(p):
        return None
    try:
        r = subprocess.run([sys.executable, '-c', _EXTRACT_WORKER, p],
                           capture_output=True, timeout=120)
        if r.returncode != 0:
            print('  !! extract fail', pdf, (r.stderr or b'')[-200:].decode('utf-8','ignore'))
            return None
        return r.stdout.decode('utf-8', 'ignore')
    except subprocess.TimeoutExpired:
        print('  !! extract timeout', pdf); return None
    except Exception as e:
        print('  !! extract err', pdf, e); return None

def gen_for_paper(pdf, title):
    text = extract_safe(pdf)
    if text is None:
        return None
    return detect_card(text, title)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry', action='store_true')
    ap.add_argument('--only', default='')
    args = ap.parse_args()
    man = json.load(open(os.path.join(ED, 'manifest.json'), encoding='utf-8'))
    total_written = 0
    for cat in man['cats']:
        name = cat['name']
        if name not in CATS_WITH_CARD:
            continue
        for pp in cat['papers']:
            if args.only and args.only not in (pp.get('label', '')):
                continue
            pdf = pp.get('pdf') or ''
            if not pdf:
                continue
            card = gen_for_paper(pdf, pp.get('label', '') or name + ' ' + (pp.get('pdf','')))
            if not card:
                if args.dry:
                    print('[SKIP no-card]', name, pp.get('label'))
                continue
            if args.dry:
                print('###', name, '|', pp.get('label'))
                for s in card:
                    print('   ', s['type'], '|', s.get('opts', ''), '|', s['title'][:30],
                          '| nos', s['nos'][:12], ('...' + str(len(s['nos'])) if len(s['nos']) > 12 else ''))
                continue
            base = os.path.splitext(os.path.basename(pdf))[0]
            card_path = os.path.join(ED, name, base + '.card.json')
            json.dump({'title': pp.get('label', ''), 'sections': card},
                      open(card_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            pp['card'] = 'exam-data/' + name + '/' + base + '.card.json'
            total_written += 1
    if not args.dry:
        json.dump(man, open(os.path.join(ED, 'manifest.json'), 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print('written cards:', total_written)

if __name__ == '__main__':
    main()
