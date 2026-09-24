import os, fitz

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')

# sample files to scan
samples = [
    ('专项练习', '【沪教】八上英语单项选择100题.pdf'),
    ('专项练习', '【沪教】八上英语完形填空17篇.pdf'),
    ('专项练习', '【沪教】八上英语完成句子37题.pdf'),
    ('专项练习', '【沪教】八上英语阅读理解之记叙文18篇.pdf'),
    ('一课一练', 'Unit 1 Section 2 Grammar（分层练习）.pdf'),
    ('一课一练', 'Unit 1 Section 1 Reading（分层练习）.pdf'),
    ('一课一练', 'Unit 1 Section 1 Reading（解析版）.pdf'),
]

MARKERS = ['参考答案', '答案', 'Keys', 'Key', 'Answer', '解析', '参考答案与解析']

def scan(path):
    doc = fitz.open(path)
    full = []
    for pg in doc:
        full.append(pg.get_text())
    text = "\n".join(full)
    doc.close()
    lower = text.lower()
    found = {}
    for m in MARKERS:
        idx = lower.rfind(m.lower())
        found[m] = idx
    # report last marker position in characters
    last_pos = max((v for v in found.values() if v >= 0), default=-1)
    return text, found, last_pos, len(text)

lines = []
for cat, fn in samples:
    p = os.path.join(RES, cat, fn)
    if not os.path.exists(p):
        lines.append(f"\n### MISSING: {cat}/{fn}")
        continue
    text, found, last_pos, tlen = scan(p)
    lines.append(f"\n### {cat}/{fn}")
    lines.append(f"  text length={tlen}, last answer-marker pos={last_pos} ({'near end' if last_pos>tlen*0.6 else 'not near end'})")
    lines.append(f"  markers found: " + ", ".join(f"{k}@{v}" for k,v in found.items() if v>=0))
    if last_pos >= 0:
        snippet = text[max(0,last_pos-200):last_pos+400]
        lines.append("  --- snippet around last marker ---")
        for sl in snippet.splitlines():
            if sl.strip():
                lines.append("    " + sl.strip()[:120])

with open(os.path.join(BASE, '_scan_answers.txt'), 'w', encoding='utf-8') as fh:
    fh.write("\n".join(lines))
print("done")
