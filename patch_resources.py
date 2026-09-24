# -*- coding: utf-8 -*-
import os

base = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app"
bp = os.path.join(base, "build_chat.py")
s = open(bp, encoding="utf-8").read()

# 1) 顶部导入 build_resources
s = s.replace(
    "import json, re, os\n",
    "import json, re, os, sys\n"
    "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
    "from build_resources import build_resources\n",
)

# 2) 在 html = f""" 前注入：扫描资源 + 追加 CSS
inject = '''
# ---- 练习与资料：扫描 resources/ 生成板块索引 ----
RES_DIR = os.path.join(BASE, "chat-app", "resources")
res_radios, res_labels, res_contents, res_rules, res_label_rules = build_resources(RES_DIR)

css_res = """
.top-labels{display:flex;gap:6px;overflow-x:auto;padding:14px 0 6px;}
.top-labels label{flex:0 0 auto;padding:8px 14px;border:1px solid var(--border);background:var(--card);border-radius:8px;cursor:pointer;font-size:14px;color:var(--muted);white-space:nowrap;user-select:none;}
.top-labels label:hover{background:var(--bg);}
.top-content{display:none;}
.res-panel{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 16px;margin-bottom:12px;}
.res-labels{display:flex;gap:6px;overflow-x:auto;padding:10px 0 10px;flex-wrap:wrap;}
.res-labels label{flex:0 0 auto;padding:7px 12px;border:1px solid var(--border);background:var(--card);border-radius:8px;cursor:pointer;font-size:13.5px;color:var(--muted);white-space:nowrap;user-select:none;}
.res-labels label:hover{background:var(--bg);}
.res-cat-content{display:none;}
.res-unit{font-weight:700;color:var(--primary);margin:12px 0 6px;font-size:15px;}
.res-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin-bottom:6px;}
.res-item{display:block;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:var(--bg);font-size:14px;color:var(--text);text-decoration:none;line-height:1.4;}
.res-item:hover{background:var(--primary-soft);border-color:var(--primary);}
.res-item .res-name{font-size:12.5px;color:var(--muted);margin-top:4px;}
.res-item audio{width:100%;margin-bottom:6px;}
@media(max-width:760px){ .res-grid{grid-template-columns:1fr;} }
#top-textbook:checked ~ .top-content#top-content-textbook{display:block;}
#top-resources:checked ~ .top-content#top-content-resources{display:block;}
#top-textbook:checked ~ .top-labels label[for='top-textbook']{background:var(--primary-soft);border-color:var(--primary);color:var(--primary);font-weight:600;}
#top-resources:checked ~ .top-labels label[for='top-resources']{background:var(--primary-soft);border-color:var(--primary);color:var(--primary);font-weight:600;}
"""
css_chat = css_chat + css_res + "\\n" + res_rules + "\\n" + res_label_rules + "\\n"

'''
marker = 'html = f"""'
idx = s.find(marker)
if idx == -1:
    raise ValueError("html marker not found")
s = s[:idx] + inject + s[idx:]

# 3) 在 study-col 内加入顶层标签页（教材内容 / 练习与资料）
old_block = '''  <div class="study-col">
    <div class="wrap" style="padding:0;">
      <div id="versionPanel">{version_html}</div>
      <div class="unit-tabs">
        {unit_radios}
        <div class="unit-labels">{unit_labels}</div>
        <div class="tab-contents">{''.join(parts)}</div>
      </div>
      <div id="about">
        <b>使用说明</b><br>
        · 点上方「单元」标签切换单元，左侧（手机端上方横滑）点模块标题切换内容。<br>
        · 右侧聊天框已启用云端免密钥模式，打开即可就当前课文实时提问（词汇/语法/阅读/写作/考点）；如需改用自有 API Key，点右上角 ⚙ 设置。<br>
        · 本页教材内容纯静态、无脚本依赖；聊天框需联网。
      </div>
    </div>
  </div>'''
new_block = '''  <div class="study-col">
    <div class="wrap" style="padding:0;">
      <input type="radio" name="top" id="top-textbook" checked>
      <input type="radio" name="top" id="top-resources">
      <div class="top-labels"><label for="top-textbook">教材内容</label><label for="top-resources">练习与资料</label></div>
      <div class="top-content" id="top-content-textbook">
        <div id="versionPanel">{version_html}</div>
        <div class="unit-tabs">
          {unit_radios}
          <div class="unit-labels">{unit_labels}</div>
          <div class="tab-contents">{''.join(parts)}</div>
        </div>
        <div id="about">
          <b>使用说明</b><br>
          · 点上方「单元」标签切换单元，左侧（手机端上方横滑）点模块标题切换内容。<br>
          · 右侧聊天框已启用云端免密钥模式，打开即可就当前课文实时提问（词汇/语法/阅读/写作/考点）；如需改用自有 API Key，点右上角 ⚙ 设置。<br>
          · 本页教材内容纯静态、无脚本依赖；聊天框需联网。
        </div>
      </div>
      <div class="top-content" id="top-content-resources">
        <div class="res-panel">
          {res_radios}
          <div class="res-labels">{res_labels}</div>
          <div class="res-contents">{res_contents}</div>
        </div>
      </div>
    </div>
  </div>'''
if old_block not in s:
    raise ValueError("study-col block not found")
s = s.replace(old_block, new_block)

open(bp, 'w', encoding='utf-8').write(s)
print("patched build_chat.py for resources")
