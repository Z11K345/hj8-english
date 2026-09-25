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
CACHE_BUSTER = "20260924e"

css = """
:root{
  /* 字体：界面用无衬线，英文/长文用衬线，避免一律默认黑体的“AI 味” */
  --font-ui:"PingFang SC","HarmonyOS Sans SC","Microsoft YaHei","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  --font-read:"Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",Georgia,"Times New Roman",serif;
  --font-en:Georgia,"Times New Roman","Source Han Serif SC","Noto Serif SC","Songti SC","SimSun",serif;
  --bg:#ffffff; --card:#ffffff; --primary:#2b6cb0; --primary-soft:#eef3f8;
  --ink:#232a33; --ink-soft:#5b6674; --rule:#dfe4ea;
  --text:#232a33; --muted:#5b6674; --border:#dfe4ea; --warn:#8a6212; --bad:#a93226;
}
*{box-sizing:border-box;}
body{margin:0;font-family:var(--font-ui);background:var(--bg);color:var(--text);
  line-height:1.7;font-size:16px;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}
.wrap{max-width:1400px;margin:0 auto;padding:0 12px;}
.main{margin:8px 0;}
.exam-frame{width:100%;height:calc(100vh - 28px);border:1px solid var(--rule);border-radius:3px;background:#fff;display:block;}
@media(max-width:760px){
  .exam-frame{height:calc(100vh - 20px);}
}
/* 浮动 AI 按钮 */
.chat-fab{position:fixed;right:18px;bottom:18px;width:54px;height:54px;border-radius:50%;background:var(--primary);color:#fff;font-size:24px;border:none;box-shadow:0 2px 10px rgba(35,42,51,.18);z-index:40;cursor:pointer;}
.chat-fab:hover{filter:brightness(1.06);}
/* AI 弹层：右侧抽屉，不遮挡试卷中心，试卷仍可查看/滚动 */
.ai-mask{position:fixed;inset:0;display:none;z-index:50;pointer-events:none;background:transparent;}
.ai-mask.show{display:block;}
.ai-panel{position:fixed;right:0;top:0;height:100vh;width:min(440px,94vw);background:#fff;display:flex;flex-direction:column;overflow:hidden;border-left:1px solid var(--rule);box-shadow:-8px 0 28px rgba(35,42,51,.07);pointer-events:auto;}
/* AI 面板为悬浮层，打开时不缩小试卷版面（试卷保持全宽，面板浮于其上、可关闭） */
.ai-head{background:#fff;color:var(--ink);padding:12px 14px;font-size:14.5px;font-weight:600;letter-spacing:.02em;
  border-bottom:1px solid var(--rule);display:flex;align-items:center;justify-content:space-between;}
.ai-head .gear{cursor:pointer;font-size:16px;user-select:none;color:var(--ink-soft);}
.ai-head .x{cursor:pointer;font-size:16px;user-select:none;color:var(--ink-soft);}
.ai-head .gear:hover,.ai-head .x:hover{color:var(--ink);}
.ai-lock{padding:26px 22px;flex:1 1 auto;display:flex;flex-direction:column;justify-content:center;}
.ai-lock .t{font-size:15px;font-weight:700;margin-bottom:14px;}
.ai-lock .row{display:flex;gap:8px;align-items:center;}
.ai-lock input{flex:1 1 auto;padding:10px 12px;border:1px solid var(--rule);border-radius:4px;font-size:15px;font-family:inherit;}
.ai-lock .ok{background:var(--primary);color:#fff;border:none;border-radius:4px;padding:10px 20px;font-size:14px;cursor:pointer;font-family:inherit;}
.ai-lock .msg{color:var(--bad);font-size:13px;margin-top:10px;min-height:18px;}
.ai-body{flex:1 1 auto;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:12px;background:#fff;}
.ai-body .msg{max-width:88%;padding:9px 12px;border-radius:4px;font-size:14.5px;line-height:1.68;white-space:pre-wrap;word-break:break-word;}
.ai-body .msg.user{align-self:flex-end;background:var(--primary-soft);color:var(--ink);border:1px solid #d9e4ee;}
.ai-body .msg.bot{align-self:flex-start;background:#fff;color:var(--ink);border:1px solid var(--rule);border-left:3px solid #c9d3dd;}
.ai-body .msg.sys{align-self:stretch;background:#faf8f3;color:var(--warn);font-size:12.5px;border:0;border-left:3px solid #e6d9bd;max-width:100%;text-align:left;border-radius:0;padding:8px 12px;}
.ai-input{display:flex;gap:8px;padding:10px;border-top:1px solid var(--rule);background:#fff;}
.ai-input textarea{flex:1 1 auto;resize:none;height:44px;border:1px solid var(--rule);border-radius:4px;padding:8px 10px;font-family:inherit;font-size:14px;line-height:1.5;color:var(--ink);}
.ai-input textarea:focus{outline:none;border-color:var(--primary);}
.ai-input button{border:none;background:var(--primary);color:#fff;border-radius:4px;padding:0 16px;font-size:14px;cursor:pointer;font-family:inherit;}
.ai-input button:disabled{opacity:.5;cursor:default;}
.ai-input button.stop{background:var(--bad);}
.ai-input button.img-btn{font-size:17px;padding:0 12px;line-height:1;}
/* 待发送图片预览条 */
#imgPrev{display:none;flex-wrap:wrap;gap:8px;padding:8px 10px 0;background:#fff;}
.thumb{position:relative;width:62px;height:62px;border:1px solid var(--rule);border-radius:3px;overflow:hidden;background:#fff;}
.thumb img{width:100%;height:100%;object-fit:cover;display:block;}
.thumb-x{position:absolute;top:1px;right:2px;color:#fff;background:rgba(35,42,51,.55);border-radius:50%;width:18px;height:18px;line-height:18px;text-align:center;font-size:13px;cursor:pointer;}
/* 用户消息中的图片（已发送） */
.u-imgs{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;}
.u-img{max-width:150px;max-height:150px;border-radius:3px;display:block;}
.ai-model{display:flex;align-items:center;gap:8px;padding:8px 10px;border-top:1px solid var(--rule);background:#fff;font-size:13px;color:var(--muted);}
.ai-model select{flex:1 1 auto;padding:6px 8px;border:1px solid var(--rule);border-radius:4px;font-size:13px;font-family:inherit;}
/* 防止浏览器把 AI 密码识别为登录密码而弹出“保存密码”提示，暴露 8888 */
.code-mask{-webkit-text-security:disc;}
/* 设置弹层 */
.modal-mask{position:fixed;inset:0;background:rgba(35,42,51,.34);display:none;align-items:center;justify-content:center;z-index:60;}
.modal-mask.show{display:flex;}
.modal{background:#fff;border:1px solid var(--rule);border-radius:4px;padding:18px 20px;width:min(420px,92vw);box-shadow:0 12px 34px rgba(35,42,51,.16);}
.modal h3{margin:0 0 12px;font-size:15.5px;}
.modal label{display:block;font-size:13px;color:var(--muted);margin:10px 0 4px;}
.modal input{width:100%;padding:8px 10px;border:1px solid var(--rule);border-radius:4px;font-size:14px;font-family:inherit;}
.modal .row{display:flex;gap:10px;justify-content:flex-end;margin-top:16px;}
.modal .row button{border:none;border-radius:4px;padding:8px 16px;font-size:14px;cursor:pointer;font-family:inherit;}
.modal .save{background:var(--primary);color:#fff;}
.modal .cancel{background:#eef1f4;color:var(--text);}
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
  if(msg==='NO_BACKEND') return 'AI 后端未就绪：点右上角 ⚙ 填入你自己的 OpenAI 兼容 API Key；若使用 GitHub Pages 版，请确认网络能访问 AI 中继。';
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
    addMsg('在线 AI 暂时连不上。点右上角 ⚙ 填入你自己的 OpenAI 兼容 API Key（仅存本机浏览器），即可继续答疑。','sys');
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

// 来自试卷 iframe 的「截题问AI」截图：接收图片并打开 AI 提问
window.addEventListener('message', function(e){
  const d = e.data || {};
  if(d.type === 'exam-screenshot' && d.image){
    pendingImages.push({ name:'截题.png', dataUrl: d.image });
    renderImgPrev();
    openAI();
  }
});

// 模型选择变更：记忆到 localStorage，下次打开仍生效
document.getElementById('modelSel').addEventListener('change', e=>{
  selectedModelId = e.target.value;
  try{ localStorage.setItem('chatModelId', selectedModelId); }catch(_){}
});
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
<button class="chat-fab" id="chatFab" title="AI 答疑">💬</button>
<div class="ai-mask" id="aiMask">
  <div class="ai-panel">
    <div class="ai-head"><span>课文答疑（AI）</span><span style="display:flex;gap:14px;align-items:center;"><span class="gear" id="chatGear" title="设置 API">⚙</span><span class="x" id="aiClose" title="关闭">✕</span></span></div>
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
      <button id="chatImgBtn" class="img-btn" title="上传/粘贴图片" type="button">🖼️</button>
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
