// 批量用云端模型为「文本型知识资料」预生成小题，落成本地 JSON，供 app 运行时秒查
// 用法：node build_quiz.js            —— 正式生成（跳过已完成的）
//       node build_quiz.js --dry      —— 只列出任务，不调用云端
const fs = require('fs');

const ROOT = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app/';
const KD = ROOT + 'knowledge-data/';
const OUT = KD + '出题库.json';
const CKPT = ROOT + '_quiz_progress.json';

const ENDPOINT = 'https://hj8-english.app.workbuddy.host';
const KEY = 'wbpk_9qIMV7q3yKetV5njz3ea2G_y20o9SesGLDsQhd0xO2fQgybLltRLeoc';
const MODEL = 'deepseek-v4-flash';
const CONC = 2;
const CTX_MAX = 9000;   // 单次送进模型的资料上限（字符）

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
  const raw = j.blocks || [];
  let keep = raw.filter(function (b) { return !isHeadingOnly(b); });
  if (!keep.length) keep = raw;
  let ctx = keep.map(function (b) { return (b.title ? '【' + b.title + '】\n' : '') + (b.text || ''); }).join('\n\n').trim();
  if (!ctx) return;

  // 资料太长时不要在开头截断——改成取「首 / 中 / 尾」三段，各出 1 题，3 题覆盖整份资料
  let prompt = '', mode = 'plain';
  if (ctx.length > CTX_MAX) {
    const part = Math.floor(CTX_MAX / 3);
    const mid = Math.max(0, ((ctx.length - part) >> 1));
    const slices = [ctx.slice(0, part), ctx.slice(mid, mid + part), ctx.slice(-part)];
    prompt = slices.map(function (s, i) { return '【资料片段' + (i + 1) + '】\n' + s; }).join('\n\n');
    mode = 'slices';
  } else {
    prompt = '【资料内容】\n' + ctx;
  }

  jobs.push({ key: String(j.title || full.replace(KD, '')).trim(), file: full.replace(KD, ''), ctx: prompt, mode: mode, blocks: keep.length });
});

console.log('文本型模块: ' + jobs.length + '（总资料 ' + jobs.reduce(function (a, b) { return a + b.ctx.length; }, 0) + ' 字符）');

if (process.argv.indexOf('--dry') >= 0) {
  jobs.forEach(function (j) { console.log('  [' + j.key + '] ctx=' + j.ctx.length + ' 模式=' + j.mode + ' blocks=' + j.blocks + '  ' + j.file); });
  process.exit(0);
}

// ---------- 云端调用 ----------
const SYS = '你是初中英语辅导老师。下面是一份初二英语复习资料，请基于资料出 3 道小题（含答案），题型可以是单词拼写、短语翻译或语法填空，适合初二学生。'
  + '要求：① 3 道题分别对应资料里不同的板块（如核心词汇、核心短语、重点句型、核心语法），不要重复考同一个点；'
  + '② 每题先写题目，再在下一行写「答案：…」；'
  + '③ 只输出这 3 道题，不要标题、不要解释、不要 markdown 代码块、不要多余空行。';
const SYS_SLICES = '你是初中英语辅导老师。下面是一份初二英语复习资料的三个片段，请**每个片段各出 1 道小题**（共 3 道，含答案），题型可以是单词拼写、短语翻译或语法填空，适合初二学生。'
  + '要求：① 按片段的先后顺序排列这 3 道题，每道题的知识点分别来自对应片段；'
  + '② 题目里**绝对不要出现「片段」「资料片段」「根据片段」这类字样**，直接写题目本身；'
  + '③ 每题先写题目，再在下一行写「答案：…」；'
  + '④ 只输出这 3 道题，不要标题、不要解释、不要 markdown 代码块、不要多余空行。';

async function chat(ctx, mode) {
  const ctl = new AbortController();
  const to = setTimeout(function () { ctl.abort(); }, 180000);
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
          { role: 'system', content: mode === 'slices' ? SYS_SLICES : SYS },
          { role: 'user', content: ctx + '\n\n请基于上面资料出 3 道小题并附答案。' }
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
      version: 1,
      updated: new Date().toISOString().slice(0, 10),
      note: '本地出题库：文本型知识资料的小题由云端模型批量生成后内置，运行时秒出；未收录时才回退云端。',
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
      const raw = await chat(j.ctx, j.mode);
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
  await Promise.all([worker(1), worker(2)]);
  save();
  console.log('');
  console.log('=== 完成 ===');
  console.log('成功 ' + okCount + ' / 失败 ' + failCount + ' / 落盘条目 ' + Object.keys(done).length);
  const missing = jobs.filter(function (j) { return !done[j.key]; }).map(function (j) { return j.key; });
  if (missing.length) console.log('仍缺: ' + missing.join(', '));
  console.log('输出: ' + OUT);
})();
