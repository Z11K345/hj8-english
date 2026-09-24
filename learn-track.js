/* =====================================================================
 * 学习记录（本机浏览器，不上传）
 *   - 活跃时长：页面可见 + 近期有操作才算，后台挂着/长时间无操作不计
 *   - 考核成绩：测一测、抽背自查、答题卡交卷 的对错与得分
 * 所有数据存 localStorage['learnLog']，仅存在孩子这台设备上。
 * ===================================================================== */
(function (global) {
  'use strict';

  var KEY = 'learnLog';
  var VERSION = 1;
  var MAX_DAYS = 180;               // 最多保留半年
  var MAX_QUIZ_PER_DAY = 300;       // 单日考核记录上限
  var IDLE_MS = 3 * 60 * 1000;      // 3 分钟无操作 → 暂停计时
  var TICK_MS = 5000;               // 每 5 秒结算一次
  var SUSPEND_CAP_MS = TICK_MS * 4; // 休眠/切后台回来，一次最多补记 20 秒

  // ---------- 基础 ----------
  function pad(n) { return String(n).padStart(2, '0'); }
  function dateKey(d) {
    d = d || new Date();
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }
  function dayLabel(k) {
    var p = String(k).split('-');
    return p.length === 3 ? (+p[1]) + '月' + (+p[2]) + '日' : k;
  }
  function load() {
    try {
      var j = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (j && j.v === VERSION && j.days) return j;
    } catch (e) { /* 损坏则重建 */ }
    return { v: VERSION, days: {} };
  }
  function save(db) {
    try {
      var keys = Object.keys(db.days).sort();
      if (keys.length > MAX_DAYS) keys.slice(0, keys.length - MAX_DAYS).forEach(function (k) { delete db.days[k]; });
      localStorage.setItem(KEY, JSON.stringify(db));
    } catch (e) { /* 隐私模式/配额满：静默降级 */ }
  }
  function dayOf(db, k) {
    k = k || dateKey();
    var d = db.days[k];
    if (!d) { d = db.days[k] = { sec: 0, byCat: {}, byItem: {}, visits: 0, quiz: [] }; }
    d.sec = d.sec || 0; d.byCat = d.byCat || {}; d.byItem = d.byItem || {}; d.visits = d.visits || 0; d.quiz = d.quiz || [];
    return d;
  }
  function normKey(s) { return String(s == null ? '' : s).replace(/[|｜\n\r\t]/g, ' ').trim().slice(0, 80); }

  // ---------- 计时 ----------
  var cur = { cat: '', item: '' };     // 当前正在看的材料
  var lastAct = Date.now();
  var ticking = false;

  function isActive() {
    try { if (document.visibilityState && document.visibilityState !== 'visible') return false; } catch (e) { /* ignore */ }
    return (Date.now() - lastAct) < IDLE_MS;
  }
  function flush(force) {
    var now = Date.now();
    var ms = now - (flush._last || now);
    flush._last = now;
    if (!force && !isActive()) return;
    if (ms <= 0) return;
    if (ms > SUSPEND_CAP_MS) ms = SUSPEND_CAP_MS;   // 合盖/切后台回来，不补记大段
    var sec = ms / 1000;
    var db = load();
    var d = dayOf(db);
    d.sec += sec;
    if (cur.cat) d.byCat[cur.cat] = (d.byCat[cur.cat] || 0) + sec;
    if (cur.item) d.byItem[cur.item] = (d.byItem[cur.item] || 0) + sec;
    save(db);
  }
  function startTicking() {
    if (ticking) return;
    ticking = true;
    flush._last = Date.now();
    setInterval(function () { flush(false); }, TICK_MS);
    ['click', 'keydown', 'scroll', 'touchstart', 'pointerdown', 'mousemove'].forEach(function (ev) {
      document.addEventListener(ev, function () { lastAct = Date.now(); }, { passive: true });
    });
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'visible') { lastAct = Date.now(); flush._last = Date.now(); }
      else flush(true);      // 离开页面前把已计的时间落盘
    });
    global.addEventListener('pagehide', function () { flush(true); });
    global.addEventListener('beforeunload', function () { flush(true); });
  }

  // ---------- 对外 API ----------
  var API = {
    // 进入某份材料（切卷/切知识模块时调用）；重复调用同一份不会重置计时
    start: function (cat, item) {
      cat = normKey(cat); item = normKey(item);
      if (cat === cur.cat && item === cur.item) return;
      flush(false);
      cur.cat = cat; cur.item = item;
      if (item) {   // 记一次访问
        var db = load(); var d = dayOf(db);
        d.visits += 1; save(db);
      }
      flush._last = Date.now();
      startTicking();
    },
    // 离开材料（可选，切卷时自动处理）
    stop: function () { flush(false); cur.cat = ''; cur.item = ''; },
    // 上报一次考核：src = know(测一测) / rec(抽背自查) / card(答题卡交卷)
    trackQuiz: function (o) {
      o = o || {};
      var right = Math.max(0, +o.right || 0);
      var wrong = Math.max(0, +o.wrong || 0);
      var unans = Math.max(0, +o.unans || 0);
      if (!right && !wrong && !unans) return;      // 没有任何可判分内容就不记
      var db = load(); var d = dayOf(db);
      d.quiz.push({
        t: Date.now(),
        src: normKey(o.src) || 'quiz',
        mod: normKey(o.mod) || '未命名',
        right: right, wrong: wrong, unans: unans,
        total: Math.max(0, +o.total || (right + wrong))
      });
      if (d.quiz.length > MAX_QUIZ_PER_DAY) d.quiz = d.quiz.slice(-MAX_QUIZ_PER_DAY);
      save(db);
    },
    // 今天累计秒数（用于页面上的小提示）
    todaySec: function () { var d = load().days[dateKey()]; return d ? Math.floor(d.sec) : 0; },
    todayQuizCount: function () { var d = load().days[dateKey()]; return d ? (d.quiz || []).length : 0; },
    raw: function () { return load(); },
    exportJson: function () { return JSON.stringify({ exportedAt: new Date().toISOString(), learnLog: load() }, null, 2); },
    clear: function () { try { localStorage.removeItem(KEY); } catch (e) { } },
    // ---------- 汇总（给报告页用） ----------
    report: function (days) {
      days = days || 7;
      var db = load();
      var keys = Object.keys(db.days).sort();
      var todayK = dateKey();
      var rangeKeys = keys.slice(-days);
      var agg = {
        today: { key: todayK, sec: 0, quiz: 0, visits: 0 },
        range: { days: days, keys: rangeKeys, sec: 0, quiz: 0, right: 0, wrong: 0, unans: 0 },
        series: [],            // 近 N 天 [{key,label,sec,rate,quizzes}]
        byCat: [],             // 分模块时长
        byItem: [],            // 单份材料时长 Top
        mods: [],              // 按模块正确率
        recent: [],            // 最近考核明细
        streak: 0,             // 连续学习天数（>=1 分钟算一天）
        firstDay: keys[0] || todayK,
        totalDays: keys.length
      };

      var todayD = db.days[todayK];
      if (todayD) { agg.today.sec = Math.floor(todayD.sec); agg.today.quiz = (todayD.quiz || []).length; agg.today.visits = todayD.visits || 0; }

      var catMap = {}, itemMap = {}, modMap = {}, allQuiz = [];
      keys.forEach(function (k) {
        var d = db.days[k];
        (d.quiz || []).forEach(function (q) { allQuiz.push(Object.assign({ day: k }, q)); });
      });
      rangeKeys.forEach(function (k) {
        var d = db.days[k];
        agg.range.sec += d.sec || 0;
        (d.quiz || []).forEach(function (q) {
          agg.range.quiz++;
          agg.range.right += q.right || 0;
          agg.range.wrong += q.wrong || 0;
          agg.range.unans += q.unans || 0;
        });
        Object.keys(d.byCat || {}).forEach(function (c) { catMap[c] = (catMap[c] || 0) + d.byCat[c]; });
        Object.keys(d.byItem || {}).forEach(function (c) { itemMap[c] = (itemMap[c] || 0) + d.byItem[c]; });
        (d.quiz || []).forEach(function (q) {
          var m = modMap[q.mod] || (modMap[q.mod] = { mod: q.mod, right: 0, wrong: 0, unans: 0, n: 0 });
          m.right += q.right || 0; m.wrong += q.wrong || 0; m.unans += q.unans || 0; m.n++;
        });
      });
      agg.range.sec = Math.floor(agg.range.sec);
      agg.range.rate = (agg.range.right + agg.range.wrong) ? Math.round(agg.range.right / (agg.range.right + agg.range.wrong) * 100) : null;

      var maxSec = 0;
      rangeKeys.forEach(function (k) { maxSec = Math.max(maxSec, db.days[k].sec || 0); });
      agg.series = rangeKeys.map(function (k) {
        var d = db.days[k], r = 0, w = 0;
        (d.quiz || []).forEach(function (q) { r += q.right || 0; w += q.wrong || 0; });
        return {
          key: k, label: dayLabel(k), sec: Math.floor(d.sec || 0),
          pct: maxSec ? Math.round((d.sec || 0) / maxSec * 100) : 0,
          quizzes: (d.quiz || []).length,
          rate: (r + w) ? Math.round(r / (r + w) * 100) : null
        };
      });

      function toArr(map, nameKey) {
        return Object.keys(map).map(function (k) { var o = {}; o[nameKey] = k; o.sec = Math.floor(map[k]); return o; })
          .sort(function (a, b) { return b.sec - a.sec; });
      }
      agg.byCat = toArr(catMap, 'cat');
      agg.byItem = toArr(itemMap, 'item').slice(0, 12);
      var catTotal = agg.byCat.reduce(function (s, x) { return s + x.sec; }, 0);
      agg.byCat.forEach(function (x) { x.pct = catTotal ? Math.round(x.sec / catTotal * 100) : 0; });

      agg.mods = Object.keys(modMap).map(function (k) {
        var m = modMap[k], judged = m.right + m.wrong;
        return { mod: m.mod, right: m.right, wrong: m.wrong, unans: m.unans, n: m.n, judged: judged,
                 rate: judged ? Math.round(m.right / judged * 100) : null };
      }).sort(function (a, b) { return (a.rate === null ? 101 : a.rate) - (b.rate === null ? 101 : b.rate); });

      agg.recent = allQuiz.sort(function (a, b) { return b.t - a.t; }).slice(0, 20).map(function (q) {
        return { day: q.day, time: new Date(q.t).getHours() + ':' + pad(new Date(q.t).getMinutes()),
                 src: q.src, mod: q.mod, right: q.right, wrong: q.wrong, unans: q.unans,
                 total: q.total, rate: (q.right + q.wrong) ? Math.round(q.right / (q.right + q.wrong) * 100) : null };
      });

      // 连续学习天数（一天满 60 秒算学过；今天还没学不算断，从昨天往前推）
      var cursor = new Date();
      for (var i = 0; i < 400; i++) {
        var dd = db.days[dateKey(cursor)];
        var studied = !!(dd && dd.sec >= 60);
        if (studied) agg.streak++;
        else if (i > 0) break;
        cursor.setDate(cursor.getDate() - 1);
      }

      // 「努力 vs 效果」：正确率不到 70% 的模块，题量多的排前面（题量少的也列，但会标注）
      agg.watch = agg.mods.filter(function (m) { return m.rate !== null && m.rate < 70; })
        .sort(function (a, b) { return b.judged - a.judged; })
        .slice(0, 8);
      return agg;
    }
  };

  global.LearnTrack = API;
})(window);
