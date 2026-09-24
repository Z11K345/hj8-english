import os, sys, json, glob

BASE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(BASE, 'resources')

out = []
out.append("=== fitz check ===")
try:
    import fitz
    out.append("fitz OK: " + str(fitz.VersionBind))
except Exception as e:
    out.append("fitz MISSING: " + repr(e))

out.append("")
out.append("=== PDF inventory by category ===")
for cat in sorted(os.listdir(RES)):
    d = os.path.join(RES, cat)
    if not os.path.isdir(d):
        continue
    files = sorted(os.listdir(d))
    jiexi = [f for f in files if '解析' in f]
    out.append(f"\n[{cat}] total={len(files)} 解析版={len(jiexi)}")
    for f in files:
        tag = '  <-- 解析版' if '解析' in f else ''
        out.append("   " + f + tag)

with open(os.path.join(BASE, '_investigate.txt'), 'w', encoding='utf-8') as fh:
    fh.write("\n".join(out))
print("done")
