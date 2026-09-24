# -*- coding: utf-8 -*-
import os, re, shutil

SRC = r"C:\Users\GFQH-GF-ZK\Downloads\沪教版"
DST = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources"

# source top folder -> (category name, file kinds to copy). _0630101631 是副本，忽略
MAP = {
    "【沪教】八上英语一课一练-新版": ("一课一练", None),
    "【沪教】八上英语知识梳理-新版": ("知识梳理", None),
    "【沪教】八上英语知识点总结-新版": ("知识点总结", None),
    "【沪教】八上英语单元检测-新版": ("单元检测", None),
    "【沪教】八上英语专项练习-新版": ("专项练习", None),
    "【沪教】八上英语一课一练-音频": ("听力音频", None),
}
DUP_SUFFIX = "_0630101631"

os.makedirs(DST, exist_ok=True)
copied = 0
skipped_dup = 0
for top in os.listdir(SRC):
    sp = os.path.join(SRC, top)
    if not os.path.isdir(sp):
        continue
    if top.endswith(DUP_SUFFIX):
        skipped_dup += 1
        print("忽略重复副本:", top)
        continue
    if top not in MAP:
        print("未匹配(跳过):", top)
        continue
    cat = MAP[top][0]
    cat_dir = os.path.join(DST, cat)
    os.makedirs(cat_dir, exist_ok=True)
    for dp, dn, fn in os.walk(sp):
        for f in fn:
            src_f = os.path.join(dp, f)
            # 保持原文件名（含中文/括号），直接拷贝到分类目录
            dst_f = os.path.join(cat_dir, f)
            # 若分类目录已存在同名文件，跳过（避免重复）
            if os.path.exists(dst_f):
                print("  已存在跳过:", cat, f)
                continue
            shutil.copy2(src_f, dst_f)
            copied += 1
            print(f"  [{cat}] {f}")

print("拷贝完成：", copied, "个文件；忽略副本文件夹：", skipped_dup)
