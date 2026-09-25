// 批量用云端模型为「文本型知识资料」预生成小题，落成本地 JSON，供 app 运行时秒查
// 用法：node build_quiz.js            —— 正式生成（跳过已完成的）
//       node build_quiz.js --dry      —— 只列出任务，不调用云端
//
// 索引键（必须与 exam.html 的 quizKey() 完全一致）：
//   '资料标题##全部'        —— 整份资料综合练
//   '资料标题##要点标题'    —— 只练某一个要点（核心词汇 / 核心短语 / 重点句型 / 核心语法 …）
// 每个键预生成 6 道题；`app 里还能「换一组」继续联网出新题。
const fs = require('fs');

const ROOT = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app/';
const KD = ROOT + 'knowledge-data/';
const OUT = KD + '出题库.json';
const CKPT = ROOT + '_quiz_progress.json';

const ENDPOINT = 'https://hj8-english.app.workbuddy.host';
const KEY = 'wbpk_9qIMV7q3yKetV5njz3ea2G_y20o9SesGLDsQhd0xO2fQgybLltRLeoc';
const MODEL = 'deepseek-v4-flash';
const CONC = 3;
const CTX_MAX = 9000;   // 单次送进模型的资料上限（字符）
const QUIZ_N = 6;       // 每个条目预生成的小题数量

// ---------- 与 exam.html 保持一致的「标题行过滤」 ----------
function isHeadingOnly(b) {
  const raw = String((b && b.text) || '');
  const t = raw.replace(/\s+/g, ' ').trim();
  if (!t) return true;
  if (t.length < 14) return true;
  const lines = raw.split(/\n/).map(x => x.trim()).filter(Boolean);
  const cjk = (t.match(/[\u4e00-\u9fa5]/g) || []).length;
  if (lines.length <= 1 && t.length < 40 && cjk < 12) return true;
  if (!/[\u4e00-\u9fa5]/.test(t) && (t.match(/[A-Za-z]+/g) || []).length <= 4) return true;
  return false;
}

// ---------- 与 exam.html 保持一致的「要点名」 ----------
function blockLabel(b, i) {
  const t = String((b && b.title) || '').trim();
  if (t) return t;
  return '第 ' + (i + 1) + ' 部分';   // 没标题的块（如知识梳理正文）用序号定位
}
function blocksOf(j) {
  const raw = j.blocks || [];
  const keep = raw.filter(function (b) { return !isHeadingOnly(b); });
  return keep.length ? keep : raw;
}
function ctxOfBlock(b) { return (b.title ? '【' + b.title + '】\n' : '') + String(b.text || ''); }
function ctxOfAll(blocks) { return blocks.map(ctxOfBlock).join('\n\n'); }

// ---------- 收集文本型模块 ----------
function walk(p, out) {
  let items;
  try { items = fs.readdirSync(p, { withFileTypes: true }); } catch (e) { return; }
  items.forEach(function (it) {
    const full = p + '/' + it.name;
    if (it.isDirectory()) walk(full, out);
    else if (/\.json$/.test(it.name) && it.name.indexOf('例句库') < 0 && it.name.indexOf('出题库') < 0) out.push(full);
  });
}
const files = [];
walk(KD, files);

const jobs = [];
files.forEach(function (full) {
  let j;
  try { j = JSON.parse(fs.readFileSync(full, 'utf8')); } catch (e) { return; }
  if (j.type !== 'text') return;
  const title = String(j.title || full.replace(KD, '')).trim();
  const blocks = blocksOf(j);
  if (!blocks.length) return;
  const file = full.replace(KD, '');
  // ① 每个要点单独一条：学生可以「只练这一点」。只有一个块的资料不重复生成（与「全部」等价）
  if (blocks.length > 1) blocks.forEach(function (b, i) {
    const ctx = ctxOfBlock(b).trim();
    if (!ctx) return;
    jobs.push({ key: title + '##' + blockLabel(b, i), label: blockLabel(b, i), scope: 'one', ctx: ctx, file: file, blocks: 1 });
  });
  // ② 整份资料综合一条
  const all = ctxOfAll(blocks).trim();
  if (all) jobs.push({ key: title + '##全部', label: '全部', scope: 'all', ctx: all, file: file, blocks: blocks.length });
});

console.log('出题条目: ' + jobs.length + '（单要点 ' + jobs.filter(function (x) { return x.scope === 'one'; }).length
  + ' + 综合 ' + jobs.filter(function (x) { return x.scope === 'all'; }).length
  + '，总资料 ' + jobs.reduce(function (a, b) { return a + b.ctx.length; }, 0) + ' 字符）');

if (process.argv.indexOf('--dry') >= 0) {
  jobs.forEach(function (j) { console.log('  [' + j.key + '] ctx=' + j.ctx.length + ' ' + j.file); });
  process.exit(0);
}

// ---------- 云端调用 ----------
// 长资料不要在开头截断——取「首 / 中 / 尾」三段，每段出题，覆盖整份资料
function promptFor(ctx, scope) {
  if (ctx.length > CTX_MAX) {
    const part = Math.floor(CTX_MAX / 3);
    const mid = Math.max(0, ((ctx.length - part) >> 1));
    const slices = [ctx.slice(0, part), ctx.slice(mid, mid + part), ctx.slice(-part)];
    return { ctx: slices.map(function (s, i) { return '【资料片段' + (i + 1) + '】\n' + s; }).join('\n\n'), mode: 'slices' };
  }
  return { ctx: '【资料内容】\n' + ctx, mode: 'plain' };
}

function sysFor(mode, scope) {
  const common = '你是初中英语辅导老师。下面是一份初二英语复习资料' + (scope === 'one' ? '的某个要点' : '') + '，请依据它出 ' + QUIZ_N + ' 道小题（含答案），适合初二学生。';
  const angles = scope === 'one'
    ? '要求：① ' + QUIZ_N + ' 道题必须全部围绕同一个要点，但角度要不同（如单词拼写、词义辨析、固定搭配、句型转换、语法选择、完成句子），不要重复考同一个点；'
    : '要求：① ' + QUIZ_N + ' 道题覆盖资料里不同的板块（核心词汇 / 核心短语 / 重点句型 / 核心语法等），不要扎堆在同一处；';
  const slicesNote = mode === 'slices'
    ? '② 三个片段按先后顺序各出 2 道题，题目里**绝对不要出现「片段」「资料片段」「根据片段」这类字样**，直接写题目本身；'
    : '② 题目里不要出现「要点」「资料」「根据上面」这类字样，直接写题目本身；';
  return common + angles + slicesNote
    + '③ 每题先写题目，再在下一行写「答案：…」；'
    + '④ 只输出这 ' + QUIZ_N + ' 道题，不要标题、不要解释、不要 markdown 代码块、不要多余空行。';
}
function userFor(scope) {
  return scope === 'one' ? '请围绕上面这个要点出 ' + QUIZ_N + ' 道小题并附答案。' : '请基于上面资料出 ' + QUIZ_N + ' 道小题并附答案。';
}

async function chat(ctx, mode, scope) {
  const ctl = new AbortController();
  const to = setTimeout(function () { ctl.abort(); }, 240000);
  try {
    const r = await fetch(ENDPOINT + '/.cloud/llm/chat/completions', {
      method: 'POST',
      signal: ctl.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'x-wb-webapp-access-key': KEY
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [
          { role: 'system', content: sysFor(mode, scope) },
          { role: 'user', content: ctx + '\n\n' + userFor(scope) }
        ],
        stream: true,
        temperature: 0.6
      })
    });
    if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + (await r.text()).slice(0, 200));
    const txt = await r.text();
    let out = '';
    txt.split(/\r?\n/).forEach(function (line) {
      const s = line.trim();
      if (!s.startsWith('data:')) return;
      const p = s.slice(5).trim();
      if (p === '[DONE]') return;
      let d; try { d = JSON.parse(p); } catch (e) { return; }
      const dd = d.choices && d.choices[0] && d.choices[0].delta;
      if (dd && dd.content) out += dd.content;
    });
    return out;
  } finally { clearTimeout(to); }
}

function clean(text) {
  let t = String(text || '').trim();
  t = t.replace(/^```[a-z]*\s*/i, '').replace(/\s*```$/, '').trim();
  t = t.replace(/^\s*\n+/, '').replace(/\n{3,}/g, '\n\n');
  if (!/答案\s*[：:]/.test(t)) return '';      // 没答案的算失败
  const n = (t.match(/答案\s*[：:]/g) || []).length;
  if (n < Math.floor(QUIZ_N / 2)) return '';   // 题数明显不足（模型偷懒）也当失败，下次续跑会重来
  return t;
}

// ---------- 断点续跑 ----------
let done = {};
if (fs.existsSync(OUT)) {
  try {
    const prev = JSON.parse(fs.readFileSync(OUT, 'utf8'));
    done = (prev && prev.entries) || {};
    console.log('已有出题条目: ' + Object.keys(done).length);
  } catch (e) { done = {}; }
}

const todo = jobs.filter(function (j) { return !done[j.key] || !done[j.key].t; });
console.log('待生成: ' + todo.length);

let okCount = 0, failCount = 0;
let cursor = 0;

function save() {
  const entries = {};
  jobs.forEach(function (j) { if (done[j.key] && done[j.key].t) entries[j.key] = done[j.key]; });
  fs.writeFileSync(OUT, JSON.stringify({
    meta: {
      name: '英语出题库',
      version: 2,
      updated: new Date().toISOString().slice(0, 10),
      note: '本地出题库：键为「资料标题##要点名」（##全部 = 整份资料综合），每条 6 道小题，由云端模型批量生成后内置，运行时秒出；未收录或点「换一组」时才联网生成。',
      count: Object.keys(entries).length
    },
    entries: entries
  }, null, 1), 'utf8');
}

async function worker(id) {
  while (true) {
    const j = todo[cursor++];
    if (!j) return;
    const t0 = Date.now();
    try {
      const p = promptFor(j.ctx, j.scope);
      const raw = await chat(p.ctx, p.mode, j.scope);
      const t = clean(raw);
      if (!t) throw new Error('内容不合格');
      done[j.key] = { t: t, file: j.file, gen: new Date().toISOString().slice(0, 10) };
      okCount++;
      save();
      console.log('[w' + id + '] OK  ' + j.key + '  ' + t.length + '字  ' + ((Date.now() - t0) / 1000).toFixed(1) + 's');
    } catch (e) {
      failCount++;
      console.log('[w' + id + '] FAIL ' + j.key + '  ' + e.message);
    }
  }
}

(async function () {
  await Promise.all(Array.from({ length: CONC }, function (_, i) { return worker(i + 1); }));
  save();
  console.log('');
  console.log('=== 完成 ===');
  console.log('成功 ' + okCount + ' / 失败 ' + failCount + ' / 落盘条目 ' + Object.keys(done).length);
  const missing = jobs.filter(function (j) { return !done[j.key]; }).map(function (j) { return j.key; });
  if (missing.length) console.log('仍缺: ' + missing.join(', '));
  console.log('输出: ' + OUT);
})();
