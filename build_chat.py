# -*- coding: utf-8 -*-
"""生成托管版学习助手（chat-app/index.html）。
- 主视图：在线做题（exam.html iframe，含计时考试 + 家长码解锁答案）。
- 教材内容（unit/module 选项卡）已移除，不再生成。
- AI 答疑：右下角浮动按钮呼出，需输入密码才能使用；密码仅存内存（刷新/重开页面需重新输入）。
  · 优先：云服务免密钥 LLM（CLOUD_CFG 填入时），支持模型选择、免费/积分倍率展示。
  · 兜底：本地模式，用户在前端设置里填入自己的 OpenAI 兼容 API Key（仅存浏览器 localStorage）。
- 系统提示词：通用英语辅导老师（任何年级/任何英语问题都答，八上考点优先；不编造、不跑题、适合中学生、多举例）。
"""
import os

BASE = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手"
OUT = os.path.join(BASE, "chat-app", "index.html")

BOOK_TITLE = "沪教·英语 八年级上册（全国版·2025版）"
CACHE_BUSTER = "20260928b"

css = """
:root{
  /* 字体：界面用无衬线，英文/长文用衬线，避免一律默认黑体的“AI 味” */
  --font-ui:"PingFang SC","HarmonyOS Sans SC","Microsoft YaHei","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  --font-read:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,"Times New Roman",serif;
  --font-en:Georgia,"Times New Roman","Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",serif;
  /* 与 exam.html 同一套令牌：暖纸底 + 深墨蓝 + 统一 3px 小圆角（印刷品手感） */
  --bg:#f4f2ed; --card:#ffffff; --primary:#1d4a6b; --primary-soft:#eef2f5; --primary-line:#c9d6e0; --primary-dark:#153a52;
  --ink:#1a1d21; --ink-soft:#596069; --rule:#dedad2;
  --text:#1a1d21; --muted:#6d7580; --border:#dedad2; --accent:#8a5a18; --warn:#8a6212; --bad:#9e2f26;
  --radius:3px;
}
*{box-sizing:border-box;}
body{margin:0;font-family:var(--font-ui);background:var(--bg);color:var(--text);
  line-height:1.7;font-size:16px;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}
.wrap{max-width:1400px;margin:0 auto;padding:0 12px;}
.main{margin:8px 0;}
.exam-frame{width:100%;height:calc(100vh - 28px);border:1px solid var(--rule);border-radius:var(--radius);background:#fff;display:block;}
@media(max-width:760px){
  .exam-frame{height:calc(100vh - 20px);}
}
/* 浮动入口：改成带文字的方形标签，比圆形表情按钮更像个工具（原文案是 💬） */.chat-fab{position:fixed;right:18px;bottom:18px;height:40px;padding:0 18px;border-radius:var(--radius);background:var(--primary);color:#fff;font-family:var(--font-ui);font-size:13.5px;font-weight:600;letter-spacing:.08em;border:none;box-shadow:0 3px 14px rgba(26,29,33,.22);z-index:40;cursor:pointer;}
.chat-fab:hover{background:var(--primary-dark);}
/* AI 弹层：右侧抽屉，不遮挡试卷中心，试卷仍可查看/滚动 */
.ai-mask{position:fixed;inset:0;display:none;z-index:50;pointer-events:none;background:transparent;}
.ai-mask.show{display:block;}
.ai-panel{position:fixed;right:0;top:0;height:100vh;width:min(440px,94vw);background:#fff;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid var(--rule);box-shadow:-8px 0 28px rgba(26,29,33,.07);pointer-events:auto;}
/* AI 面板为悬浮层，打开时不缩小试卷版面（试卷保持全宽，面板浮于其上、可关闭） */
.ai-head{background:#fff;color:var(--ink);padding:11px 14px;font-size:14.5px;font-weight:600;letter-spacing:.04em;
  border-bottom:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;}
.ai-head .tools{display:flex;gap:14px;align-items:center;font-weight:400;font-size:12.5px;letter-spacing:.06em;}
.ai-head .gear,.ai-head .x{cursor:pointer;user-select:none;color:var(--muted);}
.ai-head .gear:hover,.ai-head .x:hover{color:var(--ink);}
.ai-sub{font-family:var(--font-ui);font-size:11.5px;color:var(--muted);letter-spacing:.04em;padding:8px 14px;border-bottom:1px solid var(--rule);line-height:1.6;}
.ai-lock{padding:26px 22px;flex:1 1 auto;display:flex;flex-direction:column;justify-content:center;}
.ai-lock .t{font-size:15px;font-weight:700;margin-bottom:14px;}
.ai-lock .row{display:flex;gap:8px;align-items:center;}
.ai-lock input{flex:1 1 auto;padding:10px 12px;border:1px solid var(--rule);border-radius:var(--radius);font-size:15px;font-family:inherit;}
.ai-lock .ok{background:var(--primary);color:#fff;border:none;border-radius:var(--radius);padding:10px 20px;font-size:14px;cursor:pointer;font-family:inherit;letter-spacing:.06em;}
.ai-lock .ok:hover{background:var(--primary-dark);}
.ai-lock .msg{color:var(--bad);font-size:13px;margin-top:10px;min-height:18px;}
.ai-body{flex:1 1 auto;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px;background:#fff;}
.ai-body .msg{max-width:88%;padding:9px 12px;border-radius:var(--radius);font-size:14.5px;line-height:1.68;white-space:pre-wrap;word-break:break-word;}
/* 用户消息：淡墨蓝底 + 发丝边；AI 消息：白底 + 左侧细色条（区分靠位置和色条，不靠大色块） */
.ai-body .msg.user{align-self:flex-end;background:var(--primary-soft);color:var(--ink);border:1px solid var(--primary-line);}
.ai-body .msg.bot{align-self:flex-start;background:#fff;color:var(--ink);border:1px solid var(--rule);border-left:3px solid var(--primary-line);}
.ai-body .msg.sys{align-self:stretch;background:#faf7f1;color:var(--warn);font-size:12.5px;border:0;border-left:3px solid #e4d8c0;max-width:100%;text-align:left;border-radius:0;padding:8px 12px;}
.ai-input{display:flex;gap:8px;padding:10px;border-top:1px solid var(--rule);background:#fff;}
.ai-input textarea{flex:1 1 auto;resize:none;height:44px;border:1px solid var(--rule);border-radius:var(--radius);padding:8px 10px;font-family:inherit;font-size:14px;line-height:1.5;color:var(--ink);}
.ai-input textarea:focus{outline:none;border-color:var(--primary);}
.ai-input button{border:none;background:var(--primary);color:#fff;border-radius:var(--radius);padding:0 16px;font-size:13.5px;cursor:pointer;font-family:inherit;letter-spacing:.06em;}
.ai-input button:hover{background:var(--primary-dark);}
.ai-input button:disabled{opacity:.5;cursor:default;}
.ai-input button.stop{background:var(--bad);}
.ai-input button.img-btn{font-size:12.5px;padding:0 12px;line-height:1;letter-spacing:.04em;background:#fff;color:var(--ink-soft);border:1px solid var(--rule);}
.ai-input button.img-btn:hover{background:var(--primary-soft);color:var(--ink);}
/* 待发送图片预览条 */
#imgPrev{display:none;flex-wrap:wrap;gap:8px;padding:8px 10px 0;background:#fff;}
.thumb{position:relative;width:62px;height:62px;border:1px solid var(--rule);border-radius:var(--radius);overflow:hidden;background:#fff;}
.thumb img{width:100%;height:100%;object-fit:cover;display:block;}
.thumb-x{position:absolute;top:1px;right:2px;color:#fff;background:rgba(26,29,33,.55);border-radius:50%;width:18px;height:18px;line-height:18px;text-align:center;font-size:13px;cursor:pointer;}
/* 用户消息中的图片（已发送） */
.u-imgs{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}
.u-img{max-width:150px;max-height:150px;border-radius:var(--radius);display:block;}
.ai-model{display:flex;align-items:center;gap:8px;padding:8px 10px;border-top:1px solid var(--rule);background:#fff;font-size:13px;color:var(--muted);}
.ai-model select{flex:1 1 auto;padding:6px 8px;border:1px solid var(--rule);border-radius:var(--radius);font-size:13px;font-family:inherit;}
/* 防止浏览器把 AI 密码识别为登录密码而弹出“保存密码”提示，暴露 8888 */
.code-mask{-webkit-text-security:disc;}
/* ---- 读一读（粘贴即读）---- */
.read-btn{position:fixed;right:18px;bottom:66px;height:40px;padding:0 18px;border-radius:var(--radius);background:#fff;color:var(--primary);font-family:var(--font-ui);font-size:13.5px;font-weight:600;letter-spacing:.08em;border:1px solid var(--primary-line);box-shadow:0 3px 14px rgba(26,29,33,.18);z-index:40;cursor:pointer;}
.read-btn:hover{background:var(--primary-soft);}
.read-mask{position:fixed;inset:0;background:rgba(26,29,33,.34);display:none;align-items:center;justify-content:center;z-index:70;}
.read-mask.show{display:flex;}
.read-card{background:#fff;border:1px solid var(--rule);border-radius:var(--radius);width:min(560px,94vw);max-height:92vh;overflow:auto;box-shadow:0 12px 34px rgba(26,29,33,.16);}
.read-head{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid var(--rule);font-size:14.5px;font-weight:600;letter-spacing:.04em;}
.read-head .tools{display:flex;gap:14px;font-weight:400;font-size:12.5px;letter-spacing:.06em;}
.read-head .hbtn{cursor:pointer;user-select:none;color:var(--muted);}
.read-head .hbtn:hover{color:var(--ink);}
.read-sub{font-size:11.5px;color:var(--muted);letter-spacing:.04em;padding:8px 16px;border-bottom:1px solid var(--rule);line-height:1.6;}
.read-body{padding:14px 16px 4px;}
.read-input{width:100%;min-height:78px;padding:10px 12px;border:1px solid var(--rule);border-radius:var(--radius);font-family:var(--font-en);font-size:18px;line-height:1.6;resize:vertical;color:var(--ink);}
.read-input:focus{outline:none;border-color:var(--primary);}
.read-hint{font-size:12px;color:var(--muted);margin-top:7px;line-height:1.7;}
.read-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:12px;}
.read-row button{border:1px solid var(--rule);background:#fff;color:var(--ink-soft);border-radius:var(--radius);padding:6px 15px;font-size:13.5px;cursor:pointer;font-family:var(--font-ui);letter-spacing:.04em;}
.read-row button:hover{background:var(--primary-soft);color:var(--ink);}
.read-row button.primary{background:var(--primary);color:#fff;border-color:var(--primary);font-weight:600;letter-spacing:.08em;padding:7px 20px;}
.read-row button.primary:hover{background:var(--primary-dark);color:#fff;}
.read-row .sp{font-size:11.5px;color:var(--muted);letter-spacing:.06em;margin-left:auto;}
.read-list{border-top:1px solid var(--rule);margin:14px 0 0;padding:0;list-style:none;}
/* 正在朗读的那一条：左侧色条 + 序号变色，不整行变色（整行变色会像选中态，且和 hover 撞） */
.read-list li{display:grid;grid-template-columns:22px 1fr;column-gap:9px;border-bottom:1px solid var(--rule);border-left:3px solid transparent;padding:13px 0 13px 8px;transition:border-color .12s;}
.read-list li.playing{border-left-color:var(--primary);background:#fbfaf7;}
.read-list li.playing .n{color:var(--primary);font-weight:700;}
.read-list li:hover{background:#fbfaf7;}
.read-list .n{grid-column:1;text-align:right;color:var(--muted);font-family:var(--font-en);font-size:13.5px;line-height:1.65;font-variant-numeric:tabular-nums;}
.read-list .bd{grid-column:2;min-width:0;}
.read-list .en{font-family:var(--font-en);font-size:19px;font-weight:600;color:var(--ink);line-height:1.5;word-break:break-word;letter-spacing:.01em;}
.read-list .zh{font-family:var(--font-read);font-size:14px;color:var(--ink-soft);margin-top:6px;line-height:1.75;white-space:pre-wrap;}
/* 音标 / 词性一行：音标必须走英文字族（--font-en），中文界面字族缺 IPA 字形时会掉字或错位 */
.read-list .meta{font-family:var(--font-en);font-size:12.5px;color:var(--muted);margin-top:7px;letter-spacing:.02em;word-break:break-word;}
.read-list .meta .pos{font-family:var(--font-ui);font-style:italic;color:var(--ink-soft);}
.read-list .ex{font-family:var(--font-en);font-size:14.5px;color:var(--ink);margin-top:9px;line-height:1.6;padding-left:10px;border-left:2px solid var(--rule);}
.read-list .ex .exzh{display:block;font-family:var(--font-read);font-size:13.5px;color:var(--muted);margin-top:3px;}
.read-list .acts{display:flex;gap:6px;margin-top:9px;flex-wrap:wrap;}
.read-list .acts button{border:1px solid var(--rule);background:#fff;color:var(--ink-soft);border-radius:var(--radius);padding:4px 12px;font-size:12.5px;cursor:pointer;font-family:var(--font-ui);letter-spacing:.04em;}
.read-list .acts button:hover{background:var(--primary-soft);}
.read-list .acts button.spk{color:var(--primary);border-color:var(--primary-line);}
.read-empty{font-size:13px;color:var(--muted);padding:14px 0 4px;line-height:1.75;}
.read-foot{font-size:11.5px;color:var(--muted);letter-spacing:.04em;padding:10px 16px 14px;line-height:1.7;}
@media(max-width:760px){ .read-btn{bottom:60px;} }
/* 设置弹层 */
.modal-mask{position:fixed;inset:0;background:rgba(26,29,33,.34);display:none;align-items:center;justify-content:center;z-index:60;}
.modal-mask.show{display:flex;}
.modal{background:#fff;border:1px solid var(--rule);border-radius:var(--radius);padding:18px 20px;width:min(420px,92vw);box-shadow:0 12px 34px rgba(26,29,33,.16);}
.modal h3{margin:0 0 12px;font-size:15.5px;}
.modal label{display:block;font-size:13px;color:var(--muted);margin:10px 0 4px;}
.modal input{width:100%;padding:8px 10px;border:1px solid var(--rule);border-radius:var(--radius);font-size:14px;font-family:inherit;}
.modal .row{display:flex;gap:10px;justify-content:flex-end;margin-top:16px;}
.modal .row button{border:none;border-radius:var(--radius);padding:8px 16px;font-size:14px;cursor:pointer;font-family:inherit;}
.modal .save{background:var(--primary);color:#fff;}
.modal .save:hover{background:var(--primary-dark);}
.modal .cancel{background:#eceae4;color:var(--text);}
@media(max-width:760px){ .exam-frame{height:calc(100vh - 130px);} }
"""

chat_js = r"""
const SYSTEM_PROMPT = `你是英语辅导老师，服务对象以初中生为主（也兼顾小学高年级与高中基础）。规则：
1) 任何年级、任何英语问题都正常回答：词汇、语法、时态、句型、阅读、写作、听力、发音、翻译等，不因“超出某册教材”而拒答；
2) 优先贴合沪教·英语八年级上册（全国版·2025版）的考点，但七上/七下/八下、乃至高中基础问题也要讲清楚，并说明它属于哪个阶段、与八上考点有何关系；
3) 不编造；不确定或需核实的（如最新考纲、有争议的用法）明确标注“需核实”，不硬答；
4) 解释循序渐进、由浅入深，多用例子；例子尽量覆盖不同形式（如动词的 am/is/are/was/were、单复数、时态变化），并配中文翻译，讲清“为什么、要注意什么”；
5) 可用中文讲解，英文例句给出中文翻译；回答简洁、直击要点，不啰嗦。`;

const CLOUD_CFG = {endpoint: "https://hj8-english.app.workbuddy.host", publishableKey: "wbpk_9qIMV7q3yKetV5njz3ea2G_y20o9SesGLDsQhd0xO2fQgybLltRLeoc"};

// AI 中继地址：云端只放行 WorkBuddy 自己域名的 Origin，GitHub Pages 等外部域名会被 403。
// 中继由服务端转发（服务端没有浏览器 Origin），因此任何站点都能用它调用同一个云端 AI。
// 调试时可在控制台执行 localStorage.setItem('aiRelayBase','http://127.0.0.1:8901') 覆盖。
const AI_RELAY_BASE = (function(){
  try{ return localStorage.getItem('aiRelayBase') || "https://hj8-english-ai-relay.app.workbuddy.host"; }
  catch(e){ return "https://hj8-english-ai-relay.app.workbuddy.host"; }
})();

// AI 使用密码：仅存内存变量，刷新页面或重新打开必须重新输入。改成你自己的密码即可。
const AI_PASSWORD = '8888';

const body = document.getElementById('chatBody');
const ta = document.getElementById('chatInput');
const sendBtn = document.getElementById('chatSend');
const stopBtn = document.getElementById('chatStop');
const gear = document.getElementById('chatGear');
const modal = document.getElementById('cfgModal');
const imgBtn = document.getElementById('chatImgBtn');
const imgInput = document.getElementById('chatImgInput');
const imgPrev = document.getElementById('imgPrev');

let history = [];
let generating = false;
let controller = null;
let userAborted = false;   // 用户点了「停止」
let conversationId = '';
let aiUnlocked = false;   // 仅内存：页面刷新/重开即重置，需重新输密码
let selectedModelId = localStorage.getItem('chatModelId') || '';  // 用户自选模型，空=默认
let modelsCached = null;  // 云端模型列表缓存，避免每次请求重复拉取
let pendingImages = [];   // 待发送图片：[{name, dataUrl}]

function initCloud(){
  if(!CLOUD_CFG || !window.WorkBuddyCloud) return null;
  try { return window.WorkBuddyCloud.createWorkBuddyCloud({ endpoint: CLOUD_CFG.endpoint, publishableKey: CLOUD_CFG.publishableKey }); }
  catch(e){ console.error('initCloud 失败', e); return null; }
}
const cloud = initCloud();
let cloudReady = false;        // 云端是否实际可达（页面加载时探测一次）
let relayReady = false;        // 云端不可达时，是否可用自建中继（GitHub Pages 版走这条路）
let aiRoute = '';              // 'cloud' | 'relay' | 'local'
function loadModelsFromRelay(){
  return fetch(AI_RELAY_BASE.replace(/\/$/,'') + '/models', {cache:'no-store'})
    .then(r=> r.ok ? r.json() : null)
    .then(j=>{ const list = Array.isArray(j) ? j : (j && (j.models || j.data)) || []; if(list.length){ modelsCached = list; return true; } return false; })
    .catch(()=> false);
}
function probeCloud(){
  return (async()=>{
    // 云端只放行自身域名的 Origin：外部域名（如 GitHub Pages）直连必被 CORS 拦下。
    // 已配置中继时就不再发这一次注定失败的请求——省一个往返，也免得控制台刷红。
    let sameOrigin = false;
    try{ sameOrigin = (new URL(CLOUD_CFG.endpoint)).origin === location.origin; }catch(e){}
    if(cloud && (sameOrigin || !AI_RELAY_BASE)){
      try{ modelsCached = (await cloud.llm.models.list()) || []; cloudReady = true; aiRoute = 'cloud'; return; }
      catch(e){ console.warn('云端直连失败，尝试自建中继', e); cloudReady = false; }
    }
    if(AI_RELAY_BASE && await loadModelsFromRelay()){ relayReady = true; aiRoute = 'relay'; return; }
    relayReady = false; aiRoute = '';
  })();
}
const cloudProbePromise = probeCloud();

function getLocalCfg(){
  try { return JSON.parse(localStorage.getItem('llmCfg')||'null'); } catch(e){ return null; }
}
// 默认模型：必须是快而稳的文本模型。auto 会先跑完整条推理链，实测同一个提问 150 秒都不返回；
// deepseek-v4-flash 两三秒就能答完 —— 答疑场景等不起推理链。
const FAST_MODELS = ['deepseek-v4-flash', 'hy3', 'deepseek-v4'];
// 只认「文本对话」模型：图像模型等条目只有 id/name，没有任何能力字段，选了不会回答
const isChatModel = (m)=> m.id === 'auto' || !!(m.maxInputTokens || m.maxOutputTokens || m.supportsToolCall || m.vendor);
function defaultChatModel(list){
  const pool = (list||[]).filter(m=>m.disabled!==true);
  for(const id of FAST_MODELS){ const hit = pool.find(m=>m.id===id); if(hit) return hit; }
  return pool.find(m=> !m.onlyReasoning && !m.supportsReasoning) || pool[0] || null;
}
function loadConvId(){
  conversationId = localStorage.getItem('chatConvId') || ('conv_'+Date.now()+'_'+Math.random().toString(36).slice(2,9));
  localStorage.setItem('chatConvId', conversationId);
}
loadConvId();

function addMsg(text, who){
  const d = document.createElement('div');
  d.className = 'msg ' + who;
  d.textContent = text;
  body.appendChild(d);
  body.scrollTop = body.scrollHeight;
  return d;
}

// 模型爱写 markdown（**加粗**、###、`代码`、- 列表），但这里是纯文本展示，抹平成干净文字
function plainify(s){
  return String(s==null?'':s)
    .replace(/```[a-z]*\n?/gi,'')
    .replace(/\*\*([^*\n]+)\*\*/g,'$1')
    .replace(/(^|\n)#{1,6}\s*/g,'$1')
    .replace(/(^|\n)\s*[-*]\s+/g,'$1· ')
    .replace(/`([^`\n]+)`/g,'$1')
    .replace(/\*\*/g,'');
}

// 用户消息（支持图文混排）：text 可为空，images 为待发送图片数组副本
function addUserMsg(text, images){
  const d = document.createElement('div');
  d.className = 'msg user';
  if(text) d.appendChild(document.createTextNode(text));
  if(images && images.length){
    const wrap = document.createElement('div');
    wrap.className = 'u-imgs';
    images.forEach(im=>{
      const img = document.createElement('img');
      img.src = im.dataUrl; img.alt = im.name || '图片'; img.className = 'u-img';
      wrap.appendChild(img);
    });
    d.appendChild(wrap);
  }
  body.appendChild(d);
  body.scrollTop = body.scrollHeight;
  return d;
}

// 把图片文件转成压缩后的 dataURL（最长边 ≤1280，jpeg 0.85），控制请求体积、利于视觉模型识别
function fileToDataUrl(file, cb){
  const reader = new FileReader();
  reader.onload = ()=>{
    const src = reader.result;
    const img = new Image();
    img.onload = ()=>{
      const maxDim = 1280;
      let w = img.width, h = img.height;
      if(w > maxDim || h > maxDim){
        const r = Math.min(maxDim / w, maxDim / h);
        w = Math.round(w * r); h = Math.round(h * r);
      }
      try {
        const c = document.createElement('canvas');
        c.width = w; c.height = h;
        c.getContext('2d').drawImage(img, 0, 0, w, h);
        cb(c.toDataURL('image/jpeg', 0.85));
      } catch(e){ cb(src); }
    };
    img.onerror = ()=> cb(src);
    img.src = src;
  };
  reader.onerror = ()=> cb(null);
  reader.readAsDataURL(file);
}

function addImage(file){
  if(!file) return;
  fileToDataUrl(file, durl=>{
    if(!durl) return;
    pendingImages.push({name: file.name || '图片', dataUrl: durl});
    renderImgPrev();
  });
}

function renderImgPrev(){
  imgPrev.innerHTML = '';
  if(!pendingImages.length){ imgPrev.style.display = 'none'; return; }
  imgPrev.style.display = 'flex';
  pendingImages.forEach((im, idx)=>{
    const box = document.createElement('div');
    box.className = 'thumb';
    const el = document.createElement('img');
    el.src = im.dataUrl; el.alt = im.name || '图片';
    const x = document.createElement('span');
    x.className = 'thumb-x'; x.textContent = '×'; x.title = '移除';
    x.onclick = ()=>{ pendingImages.splice(idx, 1); renderImgPrev(); };
    box.appendChild(el); box.appendChild(x);
    imgPrev.appendChild(box);
  });
}

// 构建发给模型的 user content：无图时仍用纯文本字符串（兼容旧逻辑），有图时改为多模态数组
function buildUserContent(text, images){
  if(!images || !images.length) return text;
  const parts = [];
  if(text) parts.push({type:'text', text});
  images.forEach(im=> parts.push({type:'image_url', image_url:{url: im.dataUrl}}));
  return parts;
}

async function callCloudLLM(messages){
  if(!cloud) throw new Error('NO_BACKEND');
  const models = await cloud.llm.models.list();
  const enabled = (models||[]).filter(m=>m.disabled!==true);
  // 优先用用户在下拉框中选的模型；未选则挑快而稳的（auto 会跑完整推理链，实测同一个请求 150 秒都不返回）
  const model = enabled.find(m=>m.id===selectedModelId) || defaultChatModel(enabled);
  if(!model) throw new Error('NO_MODEL');
  let text='';
  if(controller) controller.abort();
  controller = new AbortController();
  // 45 秒超时，避免“正在思考…”永久卡住
  const to = setTimeout(()=>{ try{ controller.abort(); }catch(e){} }, 45000);
  try{
    for await (const c of cloud.llm.chat.completions.create({
      model: model.id, messages, stream: true,
      stream_options: { include_usage: true }, temperature: 0.6,
      conversationId: conversationId, signal: controller.signal
    })){
      const delta = c.choices?.[0]?.delta;
      if(delta?.content) text += delta.content;
    }
  } finally { clearTimeout(to); }
  return text;
}

async function callLocalLLM(messages){
  const cfg = getLocalCfg();
  if(!cfg || !cfg.base || !cfg.key) throw new Error('NO_BACKEND');
  if(controller) controller.abort();
  controller = new AbortController();
  const r = await fetch(cfg.base.replace(/\/$/,'') + '/chat/completions', {
    method: 'POST',
    headers: {'Content-Type':'application/json','Authorization':'Bearer '+cfg.key},
    body: JSON.stringify({model: cfg.model||'gpt-4o-mini', messages, stream:false, temperature:0.6}),
    signal: controller.signal
  });
  if(!r.ok){ const t = await r.text(); throw new Error('HTTP '+r.status+' '+t.slice(0,200)); }
  const j = await r.json();
  return j.choices[0].message.content;
}

// 自建中继：与云端同一个模型、同一份额度，只是改由中继的服务端转发（外部域名也能用）
async function callRelayLLM(messages){
  if(!relayReady || !AI_RELAY_BASE) throw new Error('NO_BACKEND');
  const enabled = (modelsCached||[]).filter(m=>m.disabled!==true && isChatModel(m));
  const model = enabled.find(m=>m.id===selectedModelId) || defaultChatModel(enabled) || {id:'deepseek-v4-flash'};
  if(controller) controller.abort();
  controller = new AbortController();
  const to = setTimeout(()=>{ try{ controller.abort(); }catch(e){} }, 60000);
  try{
    const r = await fetch(AI_RELAY_BASE.replace(/\/$/,'') + '/ai', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({model: model.id, messages, stream:true, temperature:0.6}),
      signal: controller.signal
    });
    if(!r.ok){ const t = await r.text().catch(()=> ''); throw new Error('HTTP '+r.status+' '+t.slice(0,200)); }
    const raw = await r.text();
    let text = '';
    raw.split(/\r?\n/).forEach(line=>{
      const s = line.trim();
      if(!s.startsWith('data:')) return;
      const p = s.slice(5).trim();
      if(!p || p === '[DONE]') return;
      let d; try{ d = JSON.parse(p); }catch(e){ return; }
      const c = d.choices && d.choices[0] && d.choices[0].delta && d.choices[0].delta.content;
      if(c) text += c;
    });
    if(!text.trim()) throw new Error('EMPTY_REPLY');
    return text;
  } finally { clearTimeout(to); }
}

function friendlyError(e){
  const msg = e.message || String(e);
  if(msg==='NO_BACKEND') return 'AI 后端未就绪：点右上角「设置」填入你自己的 OpenAI 兼容 API Key；若使用 GitHub Pages 版，请确认网络能访问 AI 中继。';
  if(msg==='NO_MODEL') return '当前无可用模型，请稍后重试。';
  if(msg==='EMPTY_REPLY') return 'AI 没返回内容，请再试一次。';
  if(msg==='AbortError' || /abort/i.test(msg)) return '请求超时，请稍后重试或检查网络。';
  const code = (e.error && e.error.code) || '';
  if(code.startsWith('auth_')) return '后端授权/来源校验失败：请刷新页面或重新发布后再试。';
  if(code.startsWith('quota_')) return '配额不足或调用过于频繁，请稍后重试。';
  if(code.startsWith('request_')) return '请求参数错误：'+msg;
  if(code.startsWith('gateway_') || code.startsWith('model_')) return '模型服务暂时不可用，请稍后重试。'+msg;
  return '调用出错：'+msg+'（若使用自有 Key，请确认服务商允许浏览器跨域/CORS）';
}

async function send(){
  const text = ta.value.trim();
  if(generating) return;
  if(!text && pendingImages.length === 0) return;
  ta.value='';
  const imgs = pendingImages.slice();
  addUserMsg(text, imgs);
  const content = buildUserContent(text, imgs);
  history.push({role:'user', content});
  pendingImages = []; renderImgPrev();
  const bot = addMsg('正在思考…','bot');
  generating=true; userAborted=false; sendBtn.disabled=true; if(stopBtn) stopBtn.style.display='';
  const messages = [{role:'system', content: SYSTEM_PROMPT}].concat(history.slice(-12));
  try{
    // 通路顺序：云端直连（WorkBuddy 站）→ 自建中继（GitHub 等外部站）→ 用户自有 Key
    await cloudProbePromise;
    let ans;
    if(cloudReady){
      try{ ans = await callCloudLLM(messages); }
      catch(e){
        if(userAborted) throw e;
        if(relayReady){ ans = await callRelayLLM(messages); }
        else if(getLocalCfg()){ ans = await callLocalLLM(messages); addMsg('云端暂不可用，已自动切换到你配置的本地 AI。','sys'); }
        else throw e;
      }
    } else if(relayReady){
      try{ ans = await callRelayLLM(messages); }
      catch(e){
        if(userAborted) throw e;
        if(getLocalCfg()){ ans = await callLocalLLM(messages); addMsg('在线通道暂不可用，已自动切换到你配置的本地 AI。','sys'); }
        else throw e;
      }
    } else {
      ans = await callLocalLLM(messages);
    }
    bot.textContent = plainify(ans || '（未返回内容）');
    history.push({role:'assistant', content: ans || ''});
  }catch(e){
    bot.className='msg sys';
    bot.textContent = userAborted ? '（已停止）' : friendlyError(e);
  }finally{
    generating=false; userAborted=false; sendBtn.disabled=false; if(stopBtn) stopBtn.style.display='none'; controller=null; body.scrollTop=body.scrollHeight;
  }
}
sendBtn.onclick = send;
if(stopBtn) stopBtn.onclick = ()=>{ userAborted=true; if(controller){ try{ controller.abort(); }catch(e){} } };
ta.addEventListener('keydown', e=>{ if(e.key==='Enter' && !e.shiftKey){ e.preventDefault(); send(); } });

// 图片：点击按钮选文件 + 在输入框粘贴截图
imgBtn.onclick = ()=> imgInput.click();
imgInput.onchange = e=>{ for(const f of (e.target.files||[])) addImage(f); imgInput.value=''; };
ta.addEventListener('paste', e=>{
  const items = (e.clipboardData && e.clipboardData.items) || [];
  for(const it of items){
    if(it.type && it.type.startsWith('image/')){
      const f = it.getAsFile();
      if(f) addImage(f);
    }
  }
});

gear.onclick = ()=>{
  const cfg = getLocalCfg() || {base:'https://api.openai.com/v1', key:'', model:'gpt-4o-mini'};
  document.getElementById('cfgBase').value = cfg.base||'';
  document.getElementById('cfgKey').value = cfg.key||'';
  document.getElementById('cfgModel').value = cfg.model||'';
  modal.classList.add('show');
};
document.getElementById('cfgCancel').onclick = ()=> modal.classList.remove('show');
document.getElementById('cfgSave').onclick = ()=>{
  const cfg = {base:document.getElementById('cfgBase').value.trim(), key:document.getElementById('cfgKey').value.trim(), model:document.getElementById('cfgModel').value.trim()};
  localStorage.setItem('llmCfg', JSON.stringify(cfg));
  modal.classList.remove('show');
  addMsg('已保存本地 API 设置（仅存于此浏览器）。云端模式启用时不会使用本地 Key。','sys');
};

// ---- 密码门禁 ----
const fab = document.getElementById('chatFab');
const aiMask = document.getElementById('aiMask');
const aiLock = document.getElementById('aiLock');
const aiPwd = document.getElementById('aiPwd');
const aiPwdBtn = document.getElementById('aiPwdBtn');
const aiPwdMsg = document.getElementById('aiPwdMsg');
const aiClose = document.getElementById('aiClose');

function openAI(){
  aiMask.classList.add('show');
  const ef=document.querySelector('.exam-frame'); if(ef) ef.classList.add('ai-open');
  if(!aiUnlocked){
    aiLock.style.display='flex';
    document.getElementById('chatBody').style.display='none';
    document.getElementById('aiInput').style.display='none';
    aiPwd.value=''; aiPwdMsg.textContent='';
    try{ aiPwd.focus(); }catch(e){}
  } else {
    showChat();
  }
}
function showChat(){
  aiLock.style.display='none';
  document.getElementById('chatBody').style.display='flex';
  document.getElementById('aiInput').style.display='flex';
  // 等云端探测结束再决定显示模型选择与提示，避免 localhost 下误判
  cloudProbePromise.then(()=>{ loadModels(); ensureGuidance(); });
}

// 在线通道（云端直连 / 自建中继）都不可达且未配置本地 Key 时，给出明确引导（不静默失败）
function ensureGuidance(){
  if(!cloudReady && !relayReady && !getLocalCfg()){
    addMsg('在线 AI 暂时连不上。点右上角「设置」填入你自己的 OpenAI 兼容 API Key（仅存本机浏览器），即可继续答疑。','sys');
  }
}

// 拉取并填充可选模型；两种在线通道都不可达时自动隐藏，由 ensureGuidance 引导本地模式
async function loadModels(){
  const row = document.getElementById('aiModelRow');
  const sel = document.getElementById('modelSel');
  if(!cloudReady && !relayReady){ row.style.display='none'; return; }
  try{
    if(!modelsCached){ modelsCached = cloudReady ? ((await cloud.llm.models.list()) || []) : modelsCached; }
    const models = modelsCached || [];
    if(!models.length){ row.style.display='none'; return; }
    sel.innerHTML = '';
    const def = document.createElement('option');
    def.value = ''; def.textContent = '默认（' + ((defaultChatModel(models)||{}).id || '推荐模型') + '）';
    sel.appendChild(def);
    // 标签：依据云端返回的 credits 字段如实标注积分倍率；0 或缺失 → 免费；auto → 倍率浮动
    const modelTag = (m)=>{
      if(m.id === 'auto') return '倍率浮动';
      const c = (m.credits || '').trim();
      if(!c) return '免费';
      const num = parseFloat(String(c).replace(/[^0-9.]/g, ''));
      if(num === 0) return '免费';
      return num + 'x';
    };
    models.filter(m => !m.disabled && isChatModel(m)).forEach(m=>{
      const o = document.createElement('option');
      const tag = modelTag(m);
      o.value = m.id;
      o.textContent = (m.name || m.id) + (tag ? '  ' + tag : '');
      const tips = [];
      if(m.credits) tips.push('积分消耗：' + m.credits);
      if(m.description) tips.push(m.description);
      if(tips.length) o.title = tips.join(' | ');
      sel.appendChild(o);
    });
    // 保持上次选择；若已下线的模型则回退默认
    sel.value = (selectedModelId && models.some(m=>m.id===selectedModelId)) ? selectedModelId : '';
    row.style.display = 'flex';
  }catch(e){
    console.warn('loadModels 失败', e);
    row.style.display = 'none';
  }
}

function tryPwd(){
  if((aiPwd.value||'').trim() === AI_PASSWORD){
    aiUnlocked = true;
    showChat();
  } else {
    aiPwdMsg.textContent = '密码不正确，请重试';
    aiPwd.value=''; try{ aiPwd.focus(); }catch(e){}
  }
}
fab.onclick = openAI;
aiPwdBtn.onclick = tryPwd;
aiPwd.addEventListener('keydown', e=>{ if(e.key==='Enter') tryPwd(); });
function closeAI(){ aiMask.classList.remove('show'); const ef=document.querySelector('.exam-frame'); if(ef) ef.classList.remove('ai-open'); }
aiClose.onclick = closeAI;
document.addEventListener('keydown', e=>{ if(e.key==='Escape' && aiMask.classList.contains('show')) closeAI(); });

// 来自试卷 iframe 的消息：截题问AI 的截图 / 圈选朗读 / 圈选问AI
window.addEventListener('message', function(e){
  const d = e.data || {};
  if(d.type === 'exam-screenshot' && d.image){
    pendingImages.push({ name:'截题.png', dataUrl: d.image });
    renderImgPrev();
    openAI();
    return;
  }
  // 试卷里圈选一段英文 → 直接读（走本页「读一读」同一套语音，体验一致）
  if(d.type === 'read-aloud' && d.text){
    try{ rdReadFromExam(String(d.text), !!d.slow); }catch(err){}
    return;
  }
  // 试卷里圈选一段英文 → 丢给 AI 答疑讲解
  if(d.type === 'ask-ai' && d.text){
    openAI();
    const box = document.getElementById('chatIn');
    if(box){ box.value = String(d.text); box.focus(); }
    return;
  }
  // 试卷里按 Esc：焦点在 iframe 内，键不会冒泡到这里，由 iframe 转交 → 关掉当前打开的面板
  if(d.type === 'esc'){
    if(rdMask.classList.contains('show')) rdClose();
    else if(aiMask.classList.contains('show')) closeAI();
    return;
  }
});

// 模型选择变更：记忆到 localStorage，下次打开仍生效
document.getElementById('modelSel').addEventListener('change', e=>{
  selectedModelId = e.target.value;
  try{ localStorage.setItem('chatModelId', selectedModelId); }catch(_){}
});

/* ==================== 读一读 · 粘贴即读 ====================
   目标：孩子遇到不会读的单词/短语，粘进来就能听到读音（并且能知道什么意思）。
   1) 朗读：Web Speech API（浏览器内置语音，离线可用，不联网、不花钱）
   2) 音标/词性/中文：调用应用内已有的云端 AI（不引入新后端）
   3) 重复粘贴同一条 → 直接命中缓存，秒出
*/
const RD_KEY = 'readKb_v1';                       // 释义缓存（本机）
const RD_PREF = 'readPref_v1';                    // 语速 / 自动读
const RD_LIMIT = 30;                              // 单次最多处理这么多条，避免刷爆额度
// 语音偏好：先找英式，再找高质量美式，最后任何英文语音都行（宁可音色一般，也不能没声音）
const RD_VOICE_PREF = [
  'Microsoft Libby','Microsoft Ryan','Microsoft Sonia','Microsoft Thomas','Microsoft Hazel','Microsoft George',
  'Daniel','Serena','Kate','Oliver','Arthur','Stephanie','Google UK English Female','Google UK English Male',
  'Google US English','Microsoft Aria','Microsoft Jenny','Microsoft Guy','Microsoft Michelle','Samantha','Karen','Moira','Alex','Tessa','Fiona'
];

const rdMask = document.getElementById('readMask');
const rdBtn = document.getElementById('readBtn');
const rdInput = document.getElementById('readInput');
const rdList = document.getElementById('readList');
const rdRate = document.getElementById('readRate');
const rdAuto = document.getElementById('readAuto');
const rdFoot = document.getElementById('readFoot');

let rdItems = [];        // [{t, en, zh, phon, pos, err}]
let rdSeq = 0;           // 朗读代次：换一批就 +1，让上一批的队列自动作废
let rdCache = {};
let rdVoices = [];
let rdSpeakingKey = '';
// 两种模式：'word'（粘贴单词/短语，按行拆分查释义） / 'passage'（试卷圈选整段，按句朗读+翻译）
// 必须在这里声明：下面的 rdLoadVoices→rdVoiceHint 会在初始化时就读取它
let rdMode = 'word';

try{ rdCache = JSON.parse(localStorage.getItem(RD_KEY) || '{}') || {}; }catch(e){ rdCache = {}; }
try{
  const p = JSON.parse(localStorage.getItem(RD_PREF) || '{}') || {};
  if(p.rate) rdRate.value = p.rate;
  if(typeof p.auto === 'boolean') rdAuto.checked = p.auto;
}catch(e){}
function rdSavePref(){ try{ localStorage.setItem(RD_PREF, JSON.stringify({rate: rdRate.value, auto: rdAuto.checked})); }catch(e){} }
rdRate.onchange = rdSavePref; rdAuto.onchange = rdSavePref;

/* ---------- 拆分：一行一条，逗号/分号/顿号也当分隔；去掉题号与多余空白 ---------- */
function rdSplit(text){
  return String(text || '')
    .replace(/\r/g, '')
    .split(/[\n;；]+/)
    .map(s => s.replace(/[，,、]+/g, '\n'))
    .join('\n')
    .split('\n')
    .map(s => s.replace(/^\s*(?:[-*·•]|\(?\d{1,2}\)?[.、)])\s*/, '').trim())
    .filter(Boolean)
    .filter((s, i, a) => a.indexOf(s) === i);
}

/* ---------- 语音：挑选最像「英式」的本地英文语音 ---------- */
// 注意：rdLoadVoices 只负责取列表，绝不能回头调 rdPickVoice/rdVoiceHint ——
// 否则「取不到语音 → 去取 → 取不到」会互相递归到爆栈。
function rdLoadVoices(){
  try{ rdVoices = (window.speechSynthesis.getVoices() || []).filter(v => /^en/i.test(v.lang || '')); }
  catch(e){ rdVoices = []; }
  rdVoiceHint();
  return rdVoices;
}
if('speechSynthesis' in window){
  rdLoadVoices();
  window.speechSynthesis.onvoiceschanged = ()=>{ rdLoadVoices(); };
}
function rdPickVoice(){
  // 只读已缓存列表；为空时最多主动取一次（用标志位防止重入）
  if(!rdVoices.length && !rdPickVoice._busy){
    rdPickVoice._busy = true;
    try{ rdVoices = (window.speechSynthesis.getVoices() || []).filter(v => /^en/i.test(v.lang || '')); }
    catch(e){}
    rdPickVoice._busy = false;
  }
  const pool = rdVoices.slice();
  for(const name of RD_VOICE_PREF){
    const hit = pool.find(v => (v.name || '').toLowerCase().indexOf(name.toLowerCase()) === 0);
    if(hit) return hit;
  }
  // 没有命中名单时：优先 en-GB，其次本地(localService)语音（更稳、无需联网），最后任意英文语音
  return pool.find(v => v.lang === 'en-GB')
      || pool.find(v => v.localService)
      || pool.find(v => /^en/i.test(v.lang))
      || null;
}
// 朗读文本：把换行与连续空白压平，避免读成奇怪的停顿。
// 英式音标里的括注 (r)（如 fɔː(r)）直接念会被读出 "r"，而多数语音又读不出连读 r 音，故去掉。
function rdSpeechText(s){
  return String(s || '')
    .replace(/\(r\)/gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}
// 逐条朗读；每次只查当批的当前项，避免把已过期的项读出来
function rdPlayAt(i){
  const my = rdSeq;
  if(i >= rdItems.length){ rdSpeakingKey = ''; rdMarkPlaying(''); return; }
  const raw = rdItems[i].t;
  const text = rdSpeechText(raw);
  if(!text){ rdPlayAt(i + 1); return; }
  const u = new SpeechSynthesisUtterance(text);
  const v = rdPickVoice();
  if(v){ u.voice = v; u.lang = v.lang || 'en-US'; } else { u.lang = 'en-US'; }
  u.rate = parseFloat(rdRate.value) || 0.85;
  u.pitch = 1;
  rdSpeakingKey = raw; rdMarkPlaying(raw);
  u.onend = ()=>{ if(my === rdSeq) rdPlayAt(i + 1); };
  u.onerror = ()=>{ if(my === rdSeq) rdPlayAt(i + 1); };
  try{ window.speechSynthesis.speak(u); }catch(e){ rdMarkPlaying(''); }
}
function rdSpeakOne(text, btn){
  if(!('speechSynthesis' in window)){ alert('这个浏览器不支持语音朗读，建议用 Chrome 或 Edge 打开。'); return; }
  try{ window.speechSynthesis.cancel(); }catch(e){}
  rdSeq++;
  rdItems = [{t: text}];
  rdPlayAt(0);
}
function rdStop(){ rdSeq++; try{ window.speechSynthesis.cancel(); }catch(e){} rdSpeakingKey = ''; rdMarkPlaying(''); }
// 「正在读」用左侧色条 + 序号变色表示，不整行变色（整行变色会像选中态）
function rdMarkPlaying(key){
  Array.prototype.forEach.call(rdList.querySelectorAll('li'), li=>{
    li.classList.toggle('playing', !!(key && li.getAttribute('data-t') === key));
  });
}
function rdPlayAll(){
  if(!rdItems.length) return;
  if(!('speechSynthesis' in window)){ alert('这个浏览器不支持语音朗读，建议用 Chrome 或 Edge 打开。'); return; }
  rdStop();
  rdPlayAt(0);
}

/* ---------- 渲染 ---------- */
function rdEsc(s){ return String(s == null ? '' : s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
// 把「实际会用哪个人声」写在面板上：孩子听到的口音和看到的音标不一致时，家长要知道原因
function rdVoiceAccent(){
  const v = rdPickVoice();
  if(!v) return null;
  const lang = String(v.lang || '').toLowerCase();
  const accent = lang === 'en-gb' ? '英式' : (lang === 'en-us' ? '美式' : (lang.indexOf('en-') === 0 ? lang.slice(3).toUpperCase() : '英文'));
  return {name: v.name || accent + '语音', accent};
}
function rdVoiceHint(){
  const box = document.getElementById('readSub');
  if(!box) return;
  let it = null;
  try{ it = rdVoiceAccent(); }catch(e){ it = null; }
  const what = rdMode === 'passage' ? '整段英文逐句读' : '单词/短语/句子都能读';
  box.textContent = '沪教·英语 八年级上册（全国版·2025版） · ' + what + ' · 当前人声：'
    + (it ? it.name + '（' + it.accent + '）' : '未检测到英文语音 — 点「说明」');
}
// 两种模式：'word'（粘贴单词/短语，按行拆分查释义） / 'passage'（试卷圈选整段，按句朗读+翻译）
function rdSetMode(m){
  rdMode = (m === 'passage') ? 'passage' : 'word';
  const ti = document.getElementById('readTitle');
  const hi = document.getElementById('readHint');
  const inp = document.getElementById('readInput');
  if(ti) ti.textContent = rdMode === 'passage' ? '读一读 · 试卷整段朗读' : '读一读 · 粘贴即读';
  if(hi) hi.innerHTML = rdMode === 'passage'
    ? '已按句拆开，逐句朗读；每一句给出中文翻译。<br>想读单词/短语，点「关闭」后重新打开面板即可。'
    : '粘贴后自动拆分并朗读；也可以直接打字，按 Ctrl+Enter 立即读。一行一个，或用逗号、分号隔开。<br>在左边试卷上圈选一段英文，这里会自动读起来。';
  if(inp) inp.placeholder = rdMode === 'passage'
    ? '这里显示从试卷圈选的段落，每行一句'
    : '把不会读的单词或短语粘进来，例如：\nbe famous for\ncommunicate\nas soon as possible';
  rdVoiceHint();
}
function rdRender(){
  rdList.innerHTML = '';
  rdVoiceHint();
  if(!rdItems.length){ rdFoot.textContent = '发音由浏览器内置语音合成提供（离线可用，不联网、不消耗积分）。'; return; }
  const known = rdItems.filter(x => x.zh).length;
  rdItems.forEach((it, i)=>{
    const li = document.createElement('li');
    li.setAttribute('data-t', it.t);
    const metaBits = [];
    if(it.phon) metaBits.push('/' + it.phon.replace(/^\/|\/$/g, '') + '/');
    if(it.pos) metaBits.push(it.pos);
    li.innerHTML = '<span class="n">' + (i + 1) + '</span>'
      + '<div class="bd">'
      + '<div class="en" title="点这一行也能读">' + rdEsc(it.t) + '</div>'
      + (it.zh ? '<div class="zh">' + rdEsc(it.zh) + '</div>' : '')
      + (metaBits.length ? '<div class="meta">' + rdEsc(it.phon ? '/' + it.phon.replace(/^\/|\/$/g, '') + '/' : '')
          + (it.pos ? (it.phon ? '  ' : '') + '<span class="pos">' + rdEsc(it.pos) + '</span>' : '') + '</div>' : '')
      + (it.ex ? '<div class="ex">例：' + rdEsc(it.ex) + (it.exZh ? '<span class="exzh">' + rdEsc(it.exZh) + '</span>' : '') + '</div>' : '')
      + '<div class="acts">'
      +   '<button class="spk" data-a="play">读一遍</button>'
      +   '<button data-a="slow">慢慢读</button>'
      +   (it.ex ? '<button data-a="ex">读例句</button>' : '')
      +   (it.zh ? '' : '<button data-a="ask">问 AI 意思</button>')
      + '</div></div>';
    li.querySelector('.en').onclick = ()=> rdSpeakOne(it.t);
    li.querySelector('.acts').addEventListener('click', ev=>{
      const b = ev.target.closest('button'); if(!b) return;
      const a = b.getAttribute('data-a');
      if(a === 'play') rdSpeakOne(it.t);
      else if(a === 'ex') rdSpeakOne(it.ex);
      else if(a === 'slow'){
        const old = rdRate.value; rdRate.value = '0.7';
        rdSpeakOne(it.t, b);
        setTimeout(()=>{ rdRate.value = old; rdSavePref(); }, 2600);
      } else if(a === 'ask'){
        openAI();
        ta.value = '请说明「' + it.t + '」的意思、词性、读音要点，并给两个英文例句（附中文翻译）。';
        try{ ta.focus(); }catch(e){}
      }
    });
    rdList.appendChild(li);
  });
  rdFoot.textContent = '共 ' + rdItems.length + ' 条 · 已标注 ' + known + ' 条释义 · 发音由浏览器内置语音提供（离线可用）';
}

/* ---------- 取释义：先查本机缓存，未命中才联网（与答题卡/知识面板同一套云端通路） ---------- */
async function rdAskAI(list){
  const messages = [
    {role:'system', content:'你是英语词典。用户会给出一批英文单词或短语（每行一条）。只输出 JSON，不要任何解释文字，不要 markdown 代码块。'},
    {role:'user', content:
      '为下面每一条英文给出：音标（国际音标，不带斜杠；英式优先）、词性（n./v./adj./adv./phr./prep. 等，短语写 phr.）、'
      + '中文意思（多义项用「；」隔开，简短，最多 12 字）、一个最贴近中学语境的英文例句并附中文翻译。\n'
      + '严格按这个 JSON 结构返回，顺序与输入一致：\n'
      + '{"items":[{"en":"原文原样","phon":"...","pos":"...","zh":"...","ex":"...","exZh":"..."}]}\n'
      + '原文：\n' + list.join('\n')}
  ];
  await cloudProbePromise;
  if(cloudReady) return await callCloudLLM(messages);
  if(relayReady) return await callRelayLLM(messages);
  const cfg = getLocalCfg();
  if(cfg) return await callLocalLLM(messages);
  throw new Error('NO_BACKEND');
}
function rdParseJson(text){
  let s = String(text || '').replace(/```[a-z]*/gi, '').trim();
  const a = s.indexOf('{'), b = s.lastIndexOf('}');
  if(a >= 0 && b > a) s = s.slice(a, b + 1);
  const j = JSON.parse(s);
  return (j && j.items) || [];
}

// 把一次云端结果落地到缓存与卡片上；返回成功写入释义的条数
function rdApply(list, targets, items){
  let hit = 0;
  targets.forEach((t, i)=>{
    const o = items[i] || {};
    if(!o.zh && !o.phon) return;                 // 空壳结果不覆盖缓存，留给重试
    const key = t.toLowerCase();
    rdCache[key] = {phon: o.phon || '', pos: o.pos || '', zh: o.zh || '', ex: o.ex || '', exZh: o.exZh || '', at: Date.now()};
    const box = list[i];
    if(box){ box.phon = rdCache[key].phon; box.pos = rdCache[key].pos; box.zh = rdCache[key].zh; box.ex = rdCache[key].ex; box.exZh = rdCache[key].exZh; if(box.zh) hit++; }
  });
  try{ localStorage.setItem(RD_KEY, JSON.stringify(rdCache)); }catch(e){}
  rdRender();
  return hit;
}
// 云端偶发抖动很常见：失败或返回不完整时自动再试一次，避免「粘贴了却没释义」。
async function rdAnnotate(list, targets){
  const tries = 2;
  for(let n = 0; n < tries; n++){
    if(n) { rdFoot.textContent = '联网有点慢，正在重试（第 2 次）…'; await new Promise(r=>setTimeout(r, 1200)); }
    else { rdFoot.textContent = '正在标音标与释义…'; }
    try{
      const items = rdParseJson(await rdAskAI(targets));
      const hit = rdApply(list, targets, items);
      if(hit){
        rdFoot.textContent = '共 ' + rdItems.length + ' 条 · 已标注 ' + hit + ' 条释义 · 发音由浏览器内置语音提供（离线可用）';
        return;
      }
      if(n === tries - 1) rdFoot.textContent = '共 ' + rdItems.length + ' 条 · 朗读可用；这次没取到释义，点条目里的「问 AI 意思」可单独查。';
    }catch(e){
      const noBackend = (e && e.message) === 'NO_BACKEND';
      if(n === tries - 1){
        rdFoot.textContent = noBackend
          ? '在线 AI 暂时连不上，本条只能朗读、看不到释义。可点右上角「设置」填入 API Key，或直接在「AI 答疑」里问。'
          : '释义获取失败（' + ((e && e.message) || e) + '），朗读不受影响。';
      }
    }
  }
}

// ▼▼ 试卷圈选朗读入口：从 exam.html 收到一段试卷原文 ▼▼
// 一段话和「一个短语」不一样：不能按行拆成 30 条去查音标（那是给单词表用的）。
// 这里按句子切分，每条是一句完整英文——朗读自然，释义也才有意义。
function rdSplitPassage(text){
  const t = String(text || '')
    .replace(/[\u00ad]/g, '')
    .replace(/[_—–-]{2,}/g, ' blank ')        // 试卷填空横线：读成 blank，比念一串下划线自然
    .replace(/\s+/g, ' ')
    .replace(/\s*([,.;:!?])\s*/g, '$1 ')
    .trim();
  if(!t) return [];
  // 先按句末标点切；粘连的长句再按分号/逗号兜底
  const parts = t.match(/[^.!?]+[.!?]+["”']?|[^.!?]+$/g) || [t];
  const out = [];
  for(const p0 of parts){
    let p = p0.trim();
    if(!p) continue;
    if(p.length < 12 && out.length){ out[out.length - 1] += ' ' + p; continue; }
    // 单句过长（PDF 抽取常整段无句号）：按分号或逗号再切，但仍归成同一条，朗读按自然停顿
    out.push(p);
  }
  return out.slice(0, 12);   // 一次最多 12 句，够读一整段了
}
// 按句朗读一段话（不查释义，纯粹读），可放慢
function rdSpeakPassage(sentences, slow){
  if(!('speechSynthesis' in window)){ rdFoot.textContent = '这个浏览器不支持语音朗读，建议用 Chrome 或 Edge 打开。'; return; }
  try{ window.speechSynthesis.cancel(); }catch(e){}
  const my = ++rdSeq;
  const rate = slow ? 0.7 : (parseFloat(rdRate.value) || 0.85);
  const speakAt = (i)=>{
    if(my !== rdSeq) return;
    if(i >= sentences.length){ rdSpeakingKey = ''; rdMarkPlaying(''); rdFoot.textContent = '整段读完（共 ' + sentences.length + ' 句）。'; return; }
    const u = new SpeechSynthesisUtterance(sentences[i]);
    const v = rdPickVoice();
    if(v){ u.voice = v; u.lang = v.lang || 'en-US'; } else { u.lang = 'en-US'; }
    u.rate = rate; u.pitch = 1;
    rdSpeakingKey = sentences[i];
    rdMarkPlaying(sentences[i]);
    u.onend = ()=>{ if(my === rdSeq) speakAt(i + 1); };
    u.onerror = ()=>{ if(my === rdSeq) speakAt(i + 1); };
    try{ window.speechSynthesis.speak(u); }catch(e){}
  };
  speakAt(0);
}
// 入口：试卷里圈选一段 → 打开「读一读」面板、填入原文、开始逐句朗读并标释义
function rdReadFromExam(text, slow){
  const clean = String(text || '').trim();
  if(!clean) return;
  const sentences = rdSplitPassage(clean);
  if(!sentences.length) return;
  rdMask.classList.add('show');
  rdVoiceHint();
  // 切换成「读段落」模式：面板标题与提示语相应变化，避免误导成「一行一个」
  try{ rdSetMode('passage'); }catch(e){}
  rdSuppressInput = true;
  rdInput.value = sentences.join('\n');
  rdSuppressInput = false;
  // 已在缓存里的句子直接显示释义，命中则不发请求
  rdItems = sentences.map(t=>{
    const c = rdCache[t.toLowerCase()];
    return {t, phon: c ? c.phon : '', pos: c ? c.pos : '', zh: c && c.zh ? c.zh : '', ex: c ? (c.ex || '') : '', exZh: c ? (c.exZh || '') : ''};
  });
  rdSeq++;
  rdRender();
  rdFoot.textContent = '已从试卷取到 ' + sentences.length + ' 句，正在朗读…';
  rdSpeakPassage(sentences, !!slow);
  // 句子较长时仍尝试标出整句意思（一条一句，不走单词表那套）
  const targets = [], boxes = [];
  rdItems.forEach(b=>{ if(!b.zh){ targets.push(b.t); boxes.push(b); } });
  if(targets.length) rdAnnotateSentences(boxes, targets);
}
// 句子释义：只取中文意思（不要求音标/词性，句子没有这些），失败也不影响朗读
async function rdAnnotateSentences(list, targets){
  try{
    const messages = [
      {role:'system', content:'你是英语老师。用户给的是一段英文试卷里的若干句子。为每一句给出简洁的中文翻译，只输出 JSON，不要解释文字、不要 markdown。'},
      {role:'user', content:'按这个结构返回，顺序与输入一致：\n{"items":[{"en":"原句","zh":"中文翻译"}]}\n句子：\n' + targets.join('\n')}
    ];
    await cloudProbePromise;
    let raw;
    if(cloudReady) raw = await callCloudLLM(messages);
    else if(relayReady) raw = await callRelayLLM(messages);
    else { const cfg = getLocalCfg(); if(!cfg) return; raw = await callLocalLLM(messages); }
    const items = rdParseJson(raw);
    let hit = 0;
    targets.forEach((t, i)=>{
      const o = items[i] || {};
      if(!o.zh) return;
      const key = t.toLowerCase();
      rdCache[key] = Object.assign({}, rdCache[key] || {}, {zh: o.zh, ex:'', exZh:'', at: Date.now()});
      if(list[i]){ list[i].zh = o.zh; hit++; }
    });
    try{ localStorage.setItem(RD_KEY, JSON.stringify(rdCache)); }catch(e){}
    if(hit){ rdRender(); rdFoot.textContent = '已从试卷取到 ' + rdItems.length + ' 句 · 已译 ' + hit + ' 句 · 逐句朗读中'; }
  }catch(e){ /* 译文拿不到不影响朗读 */ }
}
// ▼▲

/* ---------- 主流程：粘贴 → 拆分 → 朗读 → 标注 ---------- */
function rdRun(text, autoSpeak){
  const all = rdSplit(text);
  if(!all.length){ rdItems = []; rdRender(); rdFoot.textContent = '还没读到内容：把单词或短语粘到上面的框里。'; return; }
  const shown = all.slice(0, RD_LIMIT);
  const extra = all.length - shown.length;
  const targets = [];
  const boxes = [];
  rdItems = shown.map(t=>{
    const c = rdCache[t.toLowerCase()];
    const box = (c && c.zh)
      ? {t, phon:c.phon, pos:c.pos, zh:c.zh, ex:c.ex || '', exZh:c.exZh || ''}
      : {t, phon: c ? c.phon : '', pos: c ? c.pos : '', zh: '', ex:'', exZh:''};
    if(!box.zh){ targets.push(t); boxes.push(box); }
    return box;
  });
  rdSeq++;
  rdRender();
  if(extra > 0) rdFoot.textContent = '共 ' + all.length + ' 条，先处理前 ' + RD_LIMIT + ' 条（一次太多会拖慢）。剩下的再粘一次即可。';
  if(autoSpeak) rdPlayAll();
  if(targets.length) rdAnnotate(boxes, targets);
  else rdFoot.textContent = '共 ' + rdItems.length + ' 条 · 全部命中本机缓存（离线秒出）· 发音由浏览器内置语音提供';
}

rdBtn.onclick = ()=>{
  rdMask.classList.add('show');
  // 手动点开面板 = 回到「单词/短语」模式（试卷圈选那条路会自己切换成整段模式）
  if(rdMode !== 'word' && !rdInput.value.trim()) rdSetMode('word');
  rdVoiceHint();
  try{ rdInput.focus(); }catch(e){}
};
function rdClose(){
  rdStop();
  rdMask.classList.remove('show');
  rdSetMode('word');
}
document.getElementById('readClose').onclick = rdClose;
document.getElementById('readHelp').onclick = ()=>{
  const has = rdVoices.length;
  alert('读一读 使用说明\n\n'
    + '【最常用的两种用法】\n'
    + '① 试卷上圈选：用鼠标在左边试卷（PDF）上拖选一段英文，会浮出「读一遍 / 慢慢读 / 问 AI」，点一下就逐句读，并给出每句中文翻译。\n'
    + '② 粘贴单词/短语：把不会读的单词或短语粘到框里，自动拆分、朗读，并标出音标、词性、中文意思。\n\n'
    + '【细节】\n'
    + '3. 一行一个；用逗号、分号隔开也行。\n'
    + '4. 每条可以「读一遍」「慢慢读」；朗读完全在本机完成，不联网、不消耗积分。\n'
    + '5. 释义由在线 AI 生成，第一次会遇到云端；同样的内容再读时直接用本机缓存。\n'
    + '6. 试卷上双击单词可以只选中一个词；圈选整段则整段逐句读。\n\n'
    + '当前本机可用的英文语音：' + (has ? has + ' 个' : '0 个（这会导致没声音）') + '\n'
    + (has ? '' : '开启方法：Windows「设置 → 时间和语言 → 语言和区域」→ 给「英语(美国)」或「英语(英国)」添加语音包；或直接用 Chrome / Edge 打开本页。'));
};
document.getElementById('readClear').onclick = ()=>{ rdStop(); rdSuppressInput = true; rdInput.value=''; rdSuppressInput = false; rdItems=[]; rdSetMode('word'); rdRender(); rdFoot.textContent='发音由浏览器内置语音合成提供（离线可用，不联网、不消耗积分）。'; try{ rdInput.focus(); }catch(e){} };
document.getElementById('readPaste').onclick = async ()=>{
  try{
    const t = await navigator.clipboard.readText();
    if(!t){ alert('剪贴板里没有文字（或浏览器未授权读取剪贴板）。请用 Ctrl+V 粘到输入框。'); return; }
    rdInput.value = (rdInput.value ? rdInput.value.replace(/\s*$/, '\n') : '') + t;
    rdInput.dispatchEvent(new Event('input'));
  }catch(e){ alert('浏览器不允许直接读剪贴板，请点输入框后按 Ctrl+V。'); }
};
document.getElementById('readPlayAll').onclick = rdPlayAll;

// 粘贴即读：在输入框里 Ctrl+V 之后自动跑
rdInput.addEventListener('paste', ()=>{
  setTimeout(()=>{
    rdInput.dispatchEvent(new Event('input'));
  }, 0);
});
let rdTimer = null;
let rdSuppressInput = false;      // 程序填入输入框（试卷圈选）时不要触发下面的 word 模式逻辑
rdInput.addEventListener('input', ()=>{
  if(rdSuppressInput) return;
  if(rdMode === 'passage') rdSetMode('word');   // 用户自己动手改内容了 → 回到单词/短语模式
  const v = rdInput.value;
  if(!v.trim()){ rdStop(); rdItems = []; rdRender(); return; }
  if(rdTimer) clearTimeout(rdTimer);
  rdTimer = setTimeout(()=>{
    if(rdAuto.checked) rdRun(v, true);
    else { const list = rdSplit(v); rdItems = list.map(t=>{ const c=rdCache[t.toLowerCase()]||{}; return {t, phon:c.phon||'', pos:c.pos||'', zh:c.zh||'', ex:c.ex||'', exZh:c.exZh||''}; }); rdRender(); }
  }, 420);
});
rdInput.addEventListener('keydown', e=>{
  if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)){ e.preventDefault(); rdRun(rdInput.value, true); }
});
// 面板打开时若已经有内容但还没读过，补读一遍（用标志位防止反复触发）
let rdFocusArmed = false;
rdInput.addEventListener('focus', ()=>{
  if(rdFocusArmed) return;
  if(!rdInput.value.trim() || rdItems.length || !rdAuto.checked) return;
  rdFocusArmed = true;
  setTimeout(()=>{ rdFocusArmed = false; }, 800);
  rdRun(rdInput.value, true);
});

// Esc 关面板（比 AI 面板优先：读一读开着就先关它）
document.addEventListener('keydown', e=>{
  if(e.key !== 'Escape' || !rdMask.classList.contains('show')) return;
  e.stopPropagation();
  rdClose();
}, true);
"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>{BOOK_TITLE} · 学习助手</title>
<style>{css}</style>
<script src="https://cdn.jsdelivr.net/npm/@tencent-ai/workbuddy-cloud-sdk@dev/lib/index.global.js"></script>
</head>
<body>
<div class="wrap">
  <div class="main">
    <iframe class="exam-frame" src="exam.html?v={CACHE_BUSTER}" title="在线做题"></iframe>
  </div>
</div>
<button class="chat-fab" id="chatFab" title="AI 答疑">AI 答疑</button>
<button class="read-btn" id="readBtn" title="① 在试卷上圈选一段英文，直接读；② 也可以把单词/短语粘进来，自动标音标、给中文">读一读</button>
<div class="read-mask" id="readMask">
  <div class="read-card">
    <div class="read-head"><span id="readTitle">读一读 · 粘贴即读</span><span class="tools"><span class="hbtn" id="readHelp">说明</span><span class="hbtn" id="readClose">关闭</span></span></div>
    <div class="read-sub" id="readSub">沪教·英语 八年级上册（全国版·2025版） · 单词/短语/句子都能读</div>
    <div class="read-body">
      <textarea id="readInput" class="read-input" placeholder="把不会读的单词或短语粘进来，例如：&#10;be famous for&#10;communicate&#10;as soon as possible"></textarea>
      <div class="read-hint" id="readHint">粘贴后自动拆分并朗读；也可以直接打字，按 Ctrl+Enter 立即读。一行一个，或用逗号、分号隔开。<br>在左边试卷上圈选一段英文，这里会自动读起来。</div>
      <div class="read-row">
        <button class="primary" id="readPlayAll">全部朗读</button>
        <button id="readClear">清空</button>
        <button id="readPaste">粘贴</button>
        <span class="sp">语速</span>
        <select id="readRate" style="padding:6px 8px;border:1px solid var(--rule);border-radius:var(--radius);font-size:13px;font-family:inherit;background:#fff;">
          <option value="0.7">慢 0.7×</option>
          <option value="0.85" selected>稍慢 0.85×</option>
          <option value="1">正常 1×</option>
        </select>
        <label style="font-size:12.5px;color:var(--muted);display:flex;align-items:center;gap:5px;cursor:pointer;">
          <input type="checkbox" id="readAuto" checked> 粘贴后自动读
        </label>
      </div>
    </div>
    <ul class="read-list" id="readList"></ul>
    <div class="read-foot" id="readFoot">发音由浏览器内置语音合成提供（离线可用，不联网、不消耗积分）。若本机没有英文语音，请点「说明」查看开启方式。</div>
  </div>
</div>
<div class="ai-mask" id="aiMask">
  <div class="ai-panel">
    <div class="ai-head"><span>AI 答疑</span><span class="tools"><span class="gear" id="chatGear" title="设置 API">设置</span><span class="x" id="aiClose" title="关闭">关闭</span></span></div>
    <div class="ai-sub">沪教·英语 八年级上册（全国版·2025版） · 答疑不限年级，优先贴合本册考点</div>
    <div class="ai-lock" id="aiLock">
      <div class="t">请输入密码使用 AI 答疑</div>
      <div class="row">
        <input id="aiPwd" type="text" class="code-mask" placeholder="输入密码" inputmode="text" autocomplete="off">
        <button class="ok" id="aiPwdBtn">确定</button>
      </div>
      <div class="msg" id="aiPwdMsg"></div>
    </div>
    <div class="ai-body" id="chatBody" style="display:none;">
      <div class="msg sys">我是你的英语辅导老师，任何年级、任何英语问题都能问（单词、语法、时态、阅读、写作、听力都行）。直接在下方输入，或粘贴/上传题目截图。</div>
    </div>
    <div class="ai-model" id="aiModelRow" style="display:none;">
      <span>模型</span>
      <select id="modelSel"><option value="">默认（第一个可用）</option></select>
    </div>
    <div id="imgPrev"></div>
    <div class="ai-input" id="aiInput" style="display:none;">
      <textarea id="chatInput" placeholder="问任何英语问题，或粘贴/上传题目图片"></textarea>
      <button id="chatImgBtn" class="img-btn" title="上传/粘贴图片" type="button">图片</button>
      <button id="chatSend">发送</button>
      <button id="chatStop" class="stop" type="button" style="display:none;">停止</button>
      <input type="file" id="chatImgInput" accept="image/*" multiple hidden>
    </div>
  </div>
</div>
<div class="modal-mask" id="cfgModal">
  <div class="modal">
    <h3>本地 AI 设置（OpenAI 兼容）</h3>
    <label>API Base URL（以 /v1 结尾）</label>
    <input id="cfgBase" placeholder="https://api.openai.com/v1">
    <label>API Key（仅存本机浏览器，不会上传）</label>
    <input id="cfgKey" type="password" placeholder="sk-...">
    <label>模型名</label>
    <input id="cfgModel" placeholder="gpt-4o-mini">
    <div class="row">
      <button class="cancel" id="cfgCancel">取消</button>
      <button class="save" id="cfgSave">保存</button>
    </div>
  </div>
</div>
<script>
{chat_js}
</script>
</body>
</html>"""

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("生成 chat-app/index.html 完成")
print("大小 KB:", round(len(html)/1024, 1))
