// 批量用云端模型生成「例句库」，落成本地 JSON，供 app 运行时秒查
const fs = require('fs');
const path = require('path');

const ROOT = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app/';
const KD = ROOT + 'knowledge-data/';
const OUT = KD + '例句库.json';
const CKPT = ROOT + '_kb_progress.json';

const ENDPOINT = 'https://hj8-english.app.workbuddy.host';
const KEY = 'wbpk_9qIMV7q3yKetV5njz3ea2G_y20o9SesGLDsQhd0xO2fQgybLltRLeoc';
const MODEL = 'deepseek-v4-flash';
const BATCH = 8;
const CONC = 3;

// ---------- 键生成（必须与 exam.html 内实现一致）----------
function enOnly(s) {
  return String(s || '')
    .replace(/[\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef]+/g, ' ')
    .replace(/[^A-Za-z' -]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
function posFix(s) {
  return String(s || '').replace(/([A-Za-z]{2})((?:n|v|vt|vi|adj|adv|prep|conj|pron|num|art|int|interj)\.)/g, '$1 $2');
}
function keyCode(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9']/g, ''); }
function keyGeneric(s) { return (enOnly(posFix(s)).split(' ')[0] || '').toLowerCase(); }

function readJson(p) { return JSON.parse(fs.readFileSync(KD + p, 'utf8')); }

// ---------- 收集目标 ----------
const targets = new Map();
function add(key, disp, hint, kind) {
  if (!key || !/^[a-z0-9]/.test(key)) return;
  const prev = targets.get(key);
  if (prev) {
    if (!prev.hint && hint) prev.hint = hint;
    if (enOnly(disp).split(' ').length > enOnly(prev.disp).split(' ').length) prev.disp = disp;
    prev.kinds.add(kind);
    return;
  }
  targets.set(key, { key, disp: String(disp).trim(), hint: hint || '', kinds: new Set([kind]) });
}

readJson('知识点总结/【沪教】八上英语不规则动词表（背诵版）.json').items.forEach(it => {
  add(keyCode(it['原形']), it['原形'], '过去式 ' + (it['过去式'] || '') + '；过去分词 ' + (it['过去分词'] || ''), 'verb');
});
readJson('知识点总结/【沪教】八上英语单词表.json').items.forEach(it => {
  add(keyCode(it['英文']), it['英文'], it['中文'] || '', 'vocab');
});
readJson('知识点总结/【沪教】八上英语短语归纳.json').items.forEach(it => {
  add(keyCode(it['英文']), it['英文'], it['中文'] || '', 'vocab');
});
readJson('知识点总结/【沪教】八上英语词性转换.json').items.forEach(it => {
  add(keyGeneric(it['原词']), it['原词'], it['转化'] || '', 'generic');
});

const list = [...targets.values()];
console.log('unique targets:', list.length);

// ---------- 云端调用 ----------
const SYS = `你在为初中英语学习程序制作离线「例句库」，学生点击一个词就能立刻看到由浅入深的例句。
对每个输入词条，输出 4 个字段：
- head：词条的规范英文形式。若输入英文有明显粘连或缺失空格（例如 "befamous for"、"dieout"），请还原为正确英文（"be famous for"、"die out"）。
- forms：形态说明。动词必须列出 原形/第三人称单数/过去式/过去分词/现在分词；名词列单复数；形容词列比较级最高级；短语动词说明其中动词的变化。确实无形态变化的写"无形态变化"。
- tip：一句话用法要点或易错点，中文，30 字以内。
- ex：3 个例句，必须由浅入深——第 1 句最短最基础，第 2 句贴近日常情景，第 3 句稍长、含常见搭配或时态变化。若该词条有形态变化，3 句要尽量体现不同形态。
  每个例句含 en（英文）、zh（中文翻译）、note（中文，说明为什么这样用、要注意什么，25 字以内）。
严格输出 JSON 数组，元素为 {"i":<输入编号>,"head":"","forms":"","tip":"","ex":[{"en":"","zh":"","note":""}]}，顺序与输入一致。
禁止输出任何解释文字，禁止 markdown 代码块，禁止注释。`;

function sanitize(raw) {
  let t = String(raw || '').trim();
  t = t.replace(/^```(?:json)?/i, '').replace(/```$/, '').trim();
  const a = t.indexOf('['), b = t.lastIndexOf(']');
  if (a === -1 || b === -1 || b < a) throw new Error('no array');
  t = t.slice(a, b + 1);
  // 修复全角冒号造成的非法 key（如 "note：xxx"）
  t = t.replace(/"\s*(i|head|forms|tip|en|zh|note|ex)\s*[：:]\s*/g, '"$1":');
  t = t.replace(/,\s*([\]}])/g, '$1');
  const arr = JSON.parse(t);
  if (!Array.isArray(arr)) throw new Error('not array');
  return arr;
}

async function chat(messages, temperature) {
  const ctl = new AbortController();
  const to = setTimeout(() => ctl.abort(), 120000);
  try {
    const r = await fetch(ENDPOINT + '/.cloud/llm/chat/completions', {
      method: 'POST',
      signal: ctl.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'x-wb-webapp-access-key': KEY
      },
      body: JSON.stringify({ model: MODEL, messages, stream: true, temperature })
    });
    if (!r.ok) throw new Error('HTTP ' + r.status + ' ' + (await r.text()).slice(0, 160));
    const txt = await r.text();
    let out = '';
    for (const line of txt.split(/\r?\n/)) {
      const s = line.trim();
      if (!s.startsWith('data:')) continue;
      const p = s.slice(5).trim();
      if (p === '[DONE]') continue;
      let d; try { d = JSON.parse(p); } catch (e) { continue; }
      const dd = d.choices && d.choices[0] && d.choices[0].delta;
      if (dd && dd.content) out += dd.content;
    }
    return out;
  } finally { clearTimeout(to); }
}

function cleanEntry(e) {
  const ex = (e.ex || []).filter(x => x && String(x.en || '').trim() && String(x.zh || '').trim())
    .slice(0, 4).map(x => ({ en: String(x.en).trim(), zh: String(x.zh).trim(), note: String(x.note || '').trim() }));
  if (!ex.length) return null;
  return {
    head: String(e.head || '').trim(),
    forms: String(e.forms || '').trim(),
    tip: String(e.tip || '').trim(),
    ex
  };
}

async function runBatch(items, attempt) {
  const numbered = items.map((it, i) => '[' + (i + 1) + '] ' + it.disp + (it.hint ? '   —— ' + it.hint : '')).join('\n');
  const raw = await chat([
    { role: 'system', content: SYS },
    { role: 'user', content: '词条：\n' + numbered + '\n\n若某词条夹杂中文释义或词性标注，请忽略它们，只根据英文与中文含义判断。请输出 JSON 数组。' }
  ], 0.5);
  let arr;
  try { arr = sanitize(raw); }
  catch (err) {
    if (attempt < 3 && items.length > 1) {
      const mid = Math.ceil(items.length / 2);
      const r1 = await runBatch(items.slice(0, mid), attempt + 1);
      const r2 = await runBatch(items.slice(mid), attempt + 1);
      return [...r1, ...r2];
    }
    console.log('  !! batch failed', err.message, '| first item:', items[0] && items[0].disp);
    return [];
  }
  const res = [];
  arr.forEach((e, idx) => {
    const n = Number(e.i);
    const it = (Number.isFinite(n) && items[n - 1]) ? items[n - 1] : items[idx];
    if (!it) return;
    const c = cleanEntry(e);
    if (c) res.push([it.key, c]);
  });
  return res;
}

// ---------- 主流程 ----------
(async () => {
  let store = {};
  const ckptPath = process.env.KB_CKPT || CKPT;
  if (fs.existsSync(ckptPath)) {
    try { store = JSON.parse(fs.readFileSync(ckptPath, 'utf8')); } catch (e) { store = {}; }
    console.log('resume from checkpoint:', Object.keys(store).length);
  }
  const LIMIT = Number(process.env.KB_LIMIT || 0);
  let todo = list.filter(t => !store[t.key]);
  if (LIMIT) todo = todo.slice(0, LIMIT);
  console.log('todo:', todo.length);
  const batches = [];
  for (let i = 0; i < todo.length; i += BATCH) batches.push(todo.slice(i, i + BATCH));
  console.log('batches:', batches.length, 'concurrency:', CONC);

  let done = 0, failed = 0;
  for (let i = 0; i < batches.length; i += CONC) {
    const group = batches.slice(i, i + CONC);
    const out = await Promise.all(group.map(b => runBatch(b, 0)));
    for (const pairs of out) {
      if (!pairs.length) failed++;
      for (const [k, v] of pairs) store[k] = v;
    }
    done += group.length;
    fs.writeFileSync(ckptPath, JSON.stringify(store), 'utf8');
    process.stdout.write('  progress ' + Math.min(done * BATCH, todo.length) + '/' + todo.length + ' keys=' + Object.keys(store).length + ' failBatches=' + failed + '\n');
  }

  const entries = {};
  for (const t of list) if (store[t.key]) entries[t.key] = store[t.key];
  const outPath = process.env.KB_OUT || OUT;
  const payload = {
    meta: {
      name: '英语例句库',
      version: 2,
      updated: new Date().toISOString().slice(0, 10),
      note: '本地例句库：由云端模型批量生成后内置，运行时秒查；查不到时回退云端 AI。',
      count: Object.keys(entries).length
    },
    entries
  };
  fs.writeFileSync(outPath, JSON.stringify(payload), 'utf8');
  const exTotal = Object.values(entries).reduce((s, e) => s + e.ex.length, 0);
  console.log('DONE entries=' + Object.keys(entries).length + ' examples=' + exTotal + ' size=' + fs.statSync(outPath).size + 'B');
  const missing = list.filter(t => !entries[t.key]).map(t => t.key);
  console.log('missing=' + missing.length, missing.slice(0, 20).join(', '));

  // ---------- 覆盖率自检：app 里的知识条目是否都能在本库命中 ----------
  function keyOfItem(item, columns) {
    if (columns.includes('原形')) return keyCode(item['原形']);
    if (columns.includes('英文')) return keyCode(item['英文']);
    return keyGeneric(item[columns[0]]);
  }
  const SRC = [
    '知识点总结/【沪教】八上英语不规则动词表（背诵版）.json',
    '知识点总结/【沪教】八上英语单词表.json',
    '知识点总结/【沪教】八上英语短语归纳.json',
    '知识点总结/【沪教】八上英语词性转换.json'
  ];
  console.log('---- coverage ----');
  let T = 0, H = 0;
  SRC.forEach(f => {
    const j = JSON.parse(fs.readFileSync(KD + f, 'utf8'));
    let h = 0;
    j.items.forEach(it => { const k = keyOfItem(it, j.columns); if (k && entries[k]) h++; });
    T += j.items.length; H += h;
    console.log('  ' + f.split('/').pop() + '  ' + h + '/' + j.items.length);
  });
  console.log('  TOTAL ' + H + '/' + T + ' (' + Math.round(H / T * 100) + '%)');
})();
