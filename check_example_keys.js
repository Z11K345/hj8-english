const fs = require('fs');
const APP = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app/';
const KD = APP + 'knowledge-data/';

const html = fs.readFileSync(APP + 'exam.html', 'utf8');
function grab(name) {
  const re = new RegExp('function ' + name + '\\s*\\([^)]*\\)\\s*\\{[\\s\\S]*?\\n\\}', 'm');
  const m = html.match(re);
  if (!m) throw new Error('cannot extract ' + name);
  return m[0];
}
const names = ['kbEnOnly', 'kbPosFix', 'kbCode', 'knowExtendKeyItem'];
const src = names.map(grab).join('\n');
console.log('extracted:', names.join(', '), '(' + src.length + ' bytes)');

const knowCfg = {};
const factory = new Function('knowCfg', src + '\nreturn knowExtendKeyItem;');
const keyFn = factory(knowCfg);

const kb = JSON.parse(fs.readFileSync(KD + '例句库.json', 'utf8'));
const E = kb.entries;

const SRC = [
  ['知识点总结/【沪教】八上英语不规则动词表（背诵版）.json', 'verb'],
  ['知识点总结/【沪教】八上英语单词表.json', 'vocab'],
  ['知识点总结/【沪教】八上英语短语归纳.json', 'vocab'],
  ['知识点总结/【沪教】八上英语词性转换.json', 'generic']
];
let T = 0, H = 0;
SRC.forEach(([f, kind]) => {
  const j = JSON.parse(fs.readFileSync(KD + f, 'utf8'));
  knowCfg.kind = kind;
  knowCfg.promptKey = j.columns[0];
  let h = 0;
  j.items.forEach(it => { const k = keyFn(it); if (k && E[k]) h++; });
  T += j.items.length; H += h;
  console.log('  ' + f.split('/').pop().slice(0, 26) + '  ' + h + '/' + j.items.length);
});
console.log('TOTAL ' + H + '/' + T + ' (' + Math.round(H / T * 100) + '%)');
console.log(H / T > 0.98 ? 'PASS: exam.html 的键函数与例句库一致' : 'FAIL: 键函数不一致，需修正');
