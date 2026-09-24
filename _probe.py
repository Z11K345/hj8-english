import os, json
BASE = os.path.dirname(os.path.abspath(__file__))
ED = os.path.join(BASE, 'exam-data')
out=[]
for cat in ['单元检测','一课一练','专项练习']:
    d = os.path.join(ED, cat)
    if not os.path.isdir(d):
        out.append(f"=== {cat}: NO DIR"); continue
    cards = sorted(f for f in os.listdir(d) if f.endswith('.card.json'))
    out.append(f"=== {cat}: cards={len(cards)}")
    if cards:
        cj = json.load(open(os.path.join(d, cards[0]), encoding='utf-8'))
        out.append("  sample card: " + cards[0])
        out.append("  sections: " + str([(s['title'][:14], s['type'], len(s['nos']), s['nos'][:3]) for s in cj['sections']]))
        ansf = cards[0].replace('.card.json', '.answers.json')
        if os.path.exists(os.path.join(d, ansf)):
            aj = json.load(open(os.path.join(d, ansf), encoding='utf-8'))
            ks = list(aj['answers'].keys())[:12]
            out.append("  answers keys sample: " + str(ks) + " total=" + str(len(aj['answers'])))
        else:
            out.append("  NO answers.json")
with open(os.path.join(BASE, '_probe.txt'), 'w', encoding='utf-8') as fh:
    fh.write("\n".join(out))
print("done")
