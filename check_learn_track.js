// 计时逻辑实测：真实 tick 累加 + 后台自动暂停 + 闲置暂停
const fs = require('fs');
const APP = 'C:/Users/GFQH-GF-ZK/WorkBuddy/2026-09-20-12-23-11/学习助手/chat-app/';
const src = fs.readFileSync(APP + 'learn-track.js', 'utf8');

let vis = 'visible';
const store = {};
const fakeLS = { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = String(v); }, removeItem: k => { delete store[k]; } };
const docH = {}, winH = {};
const fakeDoc = {
  get visibilityState() { return vis; },
  addEventListener(ev, fn) { (docH[ev] = docH[ev] || []).push(fn); },
};
const fakeWin = { addEventListener(ev, fn) { (winH[ev] = winH[ev] || []).push(fn); } };
new Function('window', 'document', 'localStorage', 'setInterval', src)(fakeWin, fakeDoc, fakeLS, setInterval);
const LT = fakeWin.LearnTrack;

const sleep = ms => new Promise(r => setTimeout(r, ms));
const sec = () => LT.todaySec();

(async () => {
  const results = [];
  function check(name, ok, detail) { results.push([name, ok, detail]); console.log((ok ? 'PASS  ' : 'FAIL  ') + name + '  ' + detail); }

  console.log('TICK=5s，下面每步等 5.5 秒…');

  // 1) 可见状态：应累加
  LT.start('知识点总结', '不规则动词表');
  await sleep(5500);
  const s1 = sec();
  check('可见时计时累加', s1 >= 4 && s1 <= 7, '5.5秒 → 记录 ' + s1 + ' 秒');

  // 2) 切到后台：应暂停
  vis = 'hidden';
  (docH['visibilitychange'] || []).forEach(f => f());
  const s2 = sec();
  await sleep(5500);
  const s3 = sec();
  check('切后台自动暂停', s3 - s2 <= 1, '后台 5.5 秒 → 只增加 ' + (s3 - s2) + ' 秒');

  // 3) 回到前台：继续累加
  vis = 'visible';
  (docH['visibilitychange'] || []).forEach(f => f());
  await sleep(5500);
  const s4 = sec();
  check('回到前台继续计时', s4 - s3 >= 4, '前台 5.5 秒 → 增加 ' + (s4 - s3) + ' 秒');

  // 4) 切材料：切换前那段先结给旧材料，新材料从切换点开始算；两者相加应≈等待时长
  const db1 = LT.raw().days[new Date().toISOString().slice(0, 10)];
  const oldItem = '不规则动词表', newItem = '单词表';
  const before = JSON.parse(JSON.stringify(db1.byItem));
  LT.start('知识点总结', newItem);
  await sleep(5500);
  const db2 = LT.raw().days[new Date().toISOString().slice(0, 10)];
  const grewNew = (db2.byItem[newItem] || 0) - (before[newItem] || 0);
  const grewOld = (db2.byItem[oldItem] || 0) - (before[oldItem] || 0);
  check('切材料后时长归到新材料', grewNew >= 3, newItem + ' 增加 ' + grewNew.toFixed(1) + ' 秒');
  check('切换前那段结给旧材料', grewOld >= 0 && grewOld <= 2.5, oldItem + ' 增加 ' + grewOld.toFixed(1) + ' 秒');
  check('切换前后合计≈等待时长', Math.abs((grewNew + grewOld) - 5.5) <= 1.5, '合计 ' + (grewNew + grewOld).toFixed(1) + ' 秒（等待 5.5 秒）');

  // 5) 上传考核记录
  LT.trackQuiz({ src: 'know', mod: '单词表', right: 9, wrong: 1, unans: 0, total: 10 });
  const db3 = LT.raw().days[new Date().toISOString().slice(0, 10)];
  const q = db3.quiz[db3.quiz.length - 1];
  check('考核记录写入', q && q.right === 9 && q.wrong === 1, JSON.stringify(q && { src: q.src, right: q.right, wrong: q.wrong }));

  // 6) 全空考核不记录
  const n0 = db3.quiz.length;
  LT.trackQuiz({ src: 'know', mod: 'x', right: 0, wrong: 0, unans: 0 });
  check('全空考核不入库', LT.raw().days[new Date().toISOString().slice(0, 10)].quiz.length === n0, '条数不变');

  const pass = results.filter(r => r[1]).length;
  console.log('\n' + pass + '/' + results.length + ' 通过');
  process.exit(0);
})();
