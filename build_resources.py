# -*- coding: utf-8 -*-
import os, re, urllib.parse

# 板块顺序与展示名（与 copy_resources.py 的分类目录名一一对应）
RES_CATS = [
    ("一课一练", "一课一练（分层练习）"),
    ("知识梳理", "知识梳理"),
    ("知识点总结", "知识点总结"),
    ("单元检测", "单元检测（基础/提升）"),
    ("专项练习", "专项练习（题型专练）"),
    ("听力音频", "听力音频"),
]
# 按单元归类的板块（其余按文件名排序）
RES_BASED = {"一课一练", "知识梳理", "单元检测", "听力音频"}
# 转成「在线看题+做题笔记」的板块（笔记类只内嵌查看，不加答题区）
VIEWER_CATS = {"一课一练", "单元检测", "专项练习"}


def _unit_of(name):
    m = re.search(r'Unit\s*(\d+)', name, re.I)
    return int(m.group(1)) if m else 999


def _clean_label(cat, name):
    base = re.sub(r'\.(pdf|mp3|MP3)$', '', name, flags=re.I)
    base = re.sub(r'^【沪教】八上英语', '', base)
    return base.strip()


def _audio_map(res_dir):
    """扫描 听力音频/，按 'UnitNSection1-3' 归一化前缀建索引，供听力卷匹配。"""
    amap = {}
    ad = os.path.join(res_dir, "听力音频")
    if not os.path.isdir(ad):
        return amap
    for af in os.listdir(ad):
        if not af.lower().endswith(('.mp3', '.MP3')):
            continue
        m = re.search(r'Unit\s*\d+\s*Section\s*1-3', af, re.I)
        if not m:
            continue
        key = re.sub(r'\s+', '', m.group(0)).lower()
        amap.setdefault(key, []).append('resources/' + urllib.parse.quote('听力音频/' + af))
    return amap


def _audio_for(amap, paper_name):
    m = re.search(r'Unit\s*\d+\s*Section\s*1-3', paper_name, re.I)
    if not m:
        return []
    key = re.sub(r'\s+', '', m.group(0)).lower()
    return amap.get(key, [])


def _viewer_href(cat, name, audio_urls):
    enc_file = urllib.parse.quote('resources/' + cat + '/' + name)
    enc_audio = '%7C'.join(audio_urls)  # 每个 URL 已编码，用 %7C 分隔
    enc_title = urllib.parse.quote(_clean_label(cat, name))
    href = 'viewer.html?file=' + enc_file + '&title=' + enc_title
    if enc_audio:
        href += '&audio=' + enc_audio
    return href


def _make_item(cat, name, amap):
    href_res = 'resources/' + urllib.parse.quote(cat + '/' + name)
    lab = _clean_label(cat, name)
    if cat in VIEWER_CATS:
        audio_urls = _audio_for(amap, name)
        href = _viewer_href(cat, name, audio_urls)
        # 有音频的试卷标个🎧，提示可听
        badge = ' <span class="res-badge">📝</span>' if not audio_urls else ' <span class="res-badge">📝🎧</span>'
        return ('<a class="res-item res-view" href="' + href +
                '" target="_blank" rel="noopener">' + lab + badge + '</a>')
    # 非 viewer（笔记类 / 音频类）保持原链接行为
    return ('<a class="res-item" href="' + href_res +
            '" target="_blank" rel="noopener">' + lab + '</a>')


def build_resources(res_dir):
    """扫描 res_dir/<分类>/ 下的文件，生成索引 HTML 与切换用的 CSS 规则。
    返回 (radios, labels, contents, rules, label_rules)。"""
    amap = _audio_map(res_dir)
    radios = []
    labels = []
    contents = []
    rules = []
    label_rules = []
    first = True
    for cat, disp in RES_CATS:
        cat_dir = os.path.join(res_dir, cat)
        if not os.path.isdir(cat_dir):
            continue
        files = sorted(
            [f for f in os.listdir(cat_dir) if os.path.isfile(os.path.join(cat_dir, f))],
            key=lambda f: (_unit_of(f), f),
        )
        if cat in RES_BASED:
            groups = {}
            others = []
            for f in files:
                u = _unit_of(f)
                (others.append(f) if u == 999 else groups.setdefault(u, []).append(f))
            items = ''
            for u in sorted(groups):
                items += '<div class="res-unit">Unit ' + str(u) + '</div><div class="res-grid">'
                for f in groups[u]:
                    items += _make_item(cat, f, amap)
                items += '</div>'
            for f in others:
                items += _make_item(cat, f, amap)
        else:
            items = '<div class="res-grid">'
            for f in files:
                items += _make_item(cat, f, amap)
            items += '</div>'
        rid = 'res-cat-' + cat
        chk = ' checked' if first else ''
        radios.append('<input type="radio" name="res-cat" id="' + rid + '-tab"' + chk + '>')
        labels.append('<label for="' + rid + '-tab">' + disp + '</label>')
        contents.append('<div class="res-cat-content" id="' + rid + '">' + items + '</div>')
        rules.append('#' + rid + '-tab:checked ~ .res-contents #' + rid + ' { display:block; }')
        label_rules.append(
            '#' + rid + '-tab:checked ~ .res-labels label[for="' + rid +
            '-tab"] { background:var(--primary-soft); border-color:var(--primary); color:var(--primary); font-weight:600; }'
        )
        first = False
    return ''.join(radios), ''.join(labels), ''.join(contents), '\n'.join(rules), '\n'.join(label_rules)
