// 生成 英文修正.json —— 只收录「高置信度」粘连词，零误伤
const fs = require('fs');
const BASE = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app';
process.chdir(BASE);
const dir = 'knowledge-data';

function walk(d, out) {
  for (const f of fs.readdirSync(d)) {
    const p = d + '/' + f, st = fs.statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (f.endsWith('.json')) out.push(p);
  }
  return out;
}
const all = walk(dir, []);

// ---------- 1. 功能词（闭集合，绝不含内容词） ----------
const FUNC_STR = 'a an the and or but nor so yet for of to in on at by with from into onto upon over under above below ' +
  'between among during before after since until till unless though although because whether while when where why how ' +
  'who whom whose which what that this these those there here then than as if is am are was were be been being ' +
  'do does did done have has had having will would shall should can could may might must not no all any some each every ' +
  'both few many much more most other another such own same too very just only also still even ever never always ' +
  'often sometimes again back out up down off away along around about across against without within behind beside beyond ' +
  'near inside outside toward towards per via he she it they we you me him her them us my your his its our their ' +
  'myself yourself himself herself itself ourselves yourselves themselves something nothing anything everything ' +
  'someone anyone everyone somebody anybody everybody nobody one two three';
const FUNC = new Set(FUNC_STR.split(/\s+/).filter(Boolean));

// ---------- 2. 可信词表（例句库 + 词性标注词 + 音标标注词） ----------
const CLEAN = new Set(FUNC);
function harvestRuns(v, depth) {
  if (depth > 8 || v == null) return;
  if (typeof v === 'string') {
    (v.match(/[A-Za-z][A-Za-z'’-]*/g) || []).forEach(w => CLEAN.add(w.toLowerCase().replace(/[’']/g, '')));
    return;
  }
  if (Array.isArray(v)) { v.forEach(x => harvestRuns(x, depth + 1)); return; }
  if (typeof v === 'object') { for (const k in v) harvestRuns(v[k], depth + 1); }
}
try {
  const ex = JSON.parse(fs.readFileSync(dir + '/例句库.json', 'utf8'));
  harvestRuns(ex.entries || {}, 0);
} catch (e) { console.log('例句库 fail', e.message); }

// 词性标注 / 音标标注 → 确定是「独立单词」
const POS_RE = /([A-Za-z][A-Za-z'’-]{1,})[\s\u3000]+(?=(?:n|v|adj|adv|prep|conj|pron|num|int|vt|vi|aux|art)\.)/g;
const PHO_RE = /([A-Za-z][A-Za-z'’-]{1,})[\s\u3000]+\/[^\/\n]{2,60}\//g;

const KNOW_FILES = all.filter(p => !/例句库\.json$|出题库\.json$|英文修正\.json$/.test(p));
for (const fp of KNOW_FILES) {
  const raw = fs.readFileSync(fp, 'utf8');
  let m;
  POS_RE.lastIndex = 0; while ((m = POS_RE.exec(raw)) !== null) CLEAN.add(m[1].toLowerCase());
  PHO_RE.lastIndex = 0; while ((m = PHO_RE.exec(raw)) !== null) CLEAN.add(m[1].toLowerCase());
}
// 人工兜底：确定是真单词、绝不能被拆的（防止词表遗漏）
// 注意：整段拼接必须先用括号包住再 .split()，否则 + 的优先级会让 .split() 只作用于最后一段字符串
('banknote banknotes birthplace artwork understand understood becoming forgetting forgotten independent independence ' +
  'outdoors otherwise overnight upstairs downstairs homework housework weekend notebook newspaper classroom playground ' +
  'football basketball bookshop birthday daylight daytime gentleman gentlemanly grandparent grandchild nothing anyone ' +
  'someone nobody everybody everything anything everyone everywhere anywhere somewhere nowhere somehow sometime sometimes ' +
  'meanwhile moreover furthermore nevertheless therefore however whatever whenever wherever whichever ' +
  'included include includes increased decrease although another everyday ' +
  'overcome percentage password highway manage operate attend snow rest slow ' +
  'chessboard afternoon morning evening birthday classmate housework teamwork ' +
  'whenever whatever whichever whoever whomever whatever storyline notebook workbook ' +
  'brightly happily quickly clearly suddenly finally usually carefully easily ' +
  'writing reading drawing playing running swimming hiking shopping fishing ' +
  'traveling travelling dancing singing painting cooking cleaning washing ' +
  'forward backward butterfly dragonfly forty fifty sixty seventy eighty ninety ' +
  'plant plants fly flies flying weekday weekdays traveler travelers traveller travellers ' +
  'himself herself yourself myself ourselves yourselves itself themselves themselves').split(/\s+/).filter(Boolean).forEach(w => CLEAN.add(w));
if (process.env.GLUE_DEBUG) console.log('  [after 兜底1] size=' + CLEAN.size + ' housework=' + CLEAN.has('housework') + ' daytime=' + CLEAN.has('daytime'));

// 常见词兜底（提升切分质量，避免 flower+is 被切成 flow+er+is）
('flower flowers faster slower needed needs farming farmer farmers sick art artist heart healthy health surprise surprised ' +
  'challenge challenges choice choices record records idea ideas prize notebook notebooks soldier soldiers classmate classmates ' +
  'coffee teacher teachers family families wing wings candle candles train trains city cities math business cooking rules exam ' +
  'project class tour tours king hero victory freedom doubt stress parents parent students student children child').split(/\s+/)
  .filter(Boolean).forEach(w => CLEAN.add(w));

// 碎片黑名单：这些永远不能当作独立词片
const BAD_PART = new Set(('er est ed ing es s ly nt mi al ic ous ion tion sion ation ction ity ify ise ize ness ance ence ' +
  'ist ism ard ent ant ite ual ial cy ty ry ny my py gh ph sh ch th wh ck qu st nd rd ld mp nk sk sp tr dr br cr fr gr pr ' +
  'bl cl fl gl pl sl sm sn sw tw ss').split(/\s+/).filter(Boolean));
// 允许的两字母词片
const GOOD2 = new Set('am an as at be by do go he hi if in is it me my no of on or so to up us we ok'.split(/\s+/).filter(Boolean));

// ---------- 3b. 派生形态扩充（hike -> hiking/hiked，run -> running …） ----------
const PRIME = new Set(CLEAN);       // grow() 之前的「原生词表」，用于打分
(function grow() {
  const seed = [...CLEAN];
  const add = x => { if (x && x.length >= 3) CLEAN.add(x); };
  for (const w of seed) {
    if (FUNC.has(w)) continue;      // 虚词不生成形态，否则会出现 thes / ofs / ins 这类假词
    add(w + 's'); add(w + 'es'); add(w + 'ed'); add(w + 'ing'); add(w + 'er'); add(w + 'est');
    add(w + 'ly'); add(w + 'd'); add(w + 'r'); add(w + 'ies'); add(w + 'ied');
    if (/e$/.test(w)) { const b = w.slice(0, -1); add(b + 'ing'); add(b + 'ed'); add(b + 'er'); add(b + 'est'); }
    if (/[^aeiou][aeiou][^aeiou]$/.test(w)) { const c = w.slice(-1); add(w + c + 'ing'); add(w + c + 'ed'); add(w + c + 'er'); add(w + c + 'est'); }
    if (/y$/.test(w)) { const b = w.slice(0, -1); add(b + 'ies'); add(b + 'ied'); add(b + 'ier'); add(b + 'iest'); add(b + 'ily'); }
  }
})();
console.log('可信词表(含派生): ' + CLEAN.size);
if (process.env.GLUE_DEBUG) {
  ['housework', 'daytime', 'whenever', 'weekend', 'overcome', 'percentage', 'hiking', 'manage', 'managed', 'operate', 'attended', 'password', 'highway', 'slowdown', 'thes'].forEach(k =>
    console.log('  CLEAN[' + k + '] = ' + CLEAN.has(k) + '  PRIME=' + PRIME.has(k)));
}

// ---------- 4. 切分：全枚举 + 打分择优 ----------
function partOk(p) {
  if (!p || BAD_PART.has(p)) return false;
  if (p.length >= 3) return CLEAN.has(p);
  if (p.length === 2) return FUNC.has(p) || GOOD2.has(p);
  return FUNC.has(p);
}
function segsOf(w, maxParts) {
  const out = [];
  (function dfs(pos, parts) {
    if (parts.length >= maxParts) return;
    if (pos === w.length) { if (parts.length >= 2) out.push(parts.slice()); return; }
    for (let i = pos + 1; i <= w.length; i++) {
      const p = w.slice(pos, i);
      if (!partOk(p)) continue;
      parts.push(p); dfs(i, parts); parts.pop();
    }
  })(0, []);
  return out;
}
// a 优于 b：分片更少 > 非原生词更少；同分则保留先找到的（DFS 从左到右，天然偏向「长分片靠后、功能词靠前」）
function better(a, b) {
  if (a.length !== b.length) return a.length < b.length;
  const na = a.filter(p => !PRIME.has(p) && !FUNC.has(p)).length;
  const nb = b.filter(p => !PRIME.has(p) && !FUNC.has(p)).length;
  return na < nb;
}
function safeSplit(w) {
  const list = segsOf(w, 4);
  if (!list.length) return null;
  let best = null;
  for (const s of list) if (best === null || better(s, best)) best = s;
  if (!best || best.length < 2) return null;
  if (!best.some(p => FUNC.has(p))) return null;         // 必须含功能词，避免拆坏纯复合词
  return best;
}

// ---------- 4. 扫描 + 分类 ----------
const map = {}, skippedWord = [];
for (const fp of KNOW_FILES) {
  const raw = fs.readFileSync(fp, 'utf8');
  const re = /[A-Za-z]{8,}/g; let m;
  while ((m = re.exec(raw)) !== null) {
    const w = m[0];
    if (/[A-Z]/.test(w)) continue;
    if (map[w] !== undefined) continue;
    const seg = safeSplit(w);
    if (!seg) continue;
    const fixed = seg.join(' ');
    if (CLEAN.has(w)) { skippedWord.push(w + ' -> ' + fixed); continue; }
    map[w] = fixed;
  }
}
// 合并「已被更短命中」的重复（例如 a+ 前缀命中）
// 人工指定（算法切分不理想 / 不该动的情况）
const OVERRIDE = { alongway: 'a long way', toslowdown: 'to slow down' };
const BLOCK = new Set(['ndependedon']);
for (const k in OVERRIDE) map[k] = OVERRIDE[k];
for (const k of BLOCK) delete map[k];
console.log('修正条目: ' + Object.keys(map).length + ' | 因是真词而跳过: ' + skippedWord.length);

fs.writeFileSync('_glue_review.txt',
  '=== 因命中可信词表而跳过（这些是真词，不能拆） ===\n' + skippedWord.sort().join('\n') +
  '\n\n=== 全部修正条目 ===\n' +
  Object.keys(map).sort().map(k => k + ' -> ' + map[k]).join('\n'), 'utf8');
console.log('wrote _glue_review.txt');

// ---------- 5. 生成 英文修正.json ----------
const today = new Date().toISOString().slice(0, 10);
const out = {
  meta: {
    name: '英文粘连词修正表',
    version: '1.0',
    updated: today,
    count: Object.keys(map).length,
    note: 'PDF 抽取丢失空格导致的粘连英文修正（如 becausethey -> because they）。仅收录高置信度条目，整词为真英文单词的一律不收录。'
  },
  map
};
fs.writeFileSync(dir + '/英文修正.json', JSON.stringify(out), 'utf8');
console.log('wrote 英文修正.json (' + JSON.stringify(out).length + ' B)');
