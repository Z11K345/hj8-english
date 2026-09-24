# -*- coding: utf-8 -*-
"""从知识点总结类 PDF 提取结构化数据，用于右侧交互学习面板。"""
import pdfplumber
import json
import os
import re
from pathlib import Path

BASE = Path(r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app")
OUT_DIR = BASE / "knowledge-data"
RES_DIR = BASE / "resources"

def out(rel):
    p = OUT_DIR / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def save(rel, data):
    p = out(rel)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("saved", p)

# ---------------- 不规则动词表 ----------------
def extract_irregular_verbs():
    pdf_path = RES_DIR / "知识点总结" / "【沪教】八上英语不规则动词表（背诵版）.pdf"
    items = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for t in tables:
                # 表头通常是 ["原形","过去式","过去分词"]
                for row in t[1:]:
                    if len(row) < 3:
                        continue
                    base = (row[0] or "").strip()
                    past = (row[1] or "").strip()
                    pp = (row[2] or "").strip()
                    if not base:
                        continue
                    items.append({"原形": base, "过去式": past, "过去分词": pp})
    data = {
        "title": "沪教版·八上英语·不规则动词表",
        "type": "table",
        "columns": ["原形", "过去式", "过去分词"],
        "items": items,
        "quizModes": [
            {"id": "past", "name": "看原形，写过去式", "prompt": "原形", "answerKeys": ["过去式"]},
            {"id": "pp", "name": "看原形，写过去分词", "prompt": "原形", "answerKeys": ["过去分词"]},
            {"id": "base", "name": "看过分词，写原形", "prompt": "过去分词", "answerKeys": ["原形"]},
            {"id": "all", "name": "看原形，写过去式和过去分词", "prompt": "原形", "answerKeys": ["过去式", "过去分词"]}
        ]
    }
    save("知识点总结/【沪教】八上英语不规则动词表（背诵版）.json", data)

# ---------------- 单词表（按单元拆分） ----------------
def parse_word_cell(cell):
    """单元格内容：单词\n音标 或 短语，返回 (英文, 音标)。"""
    if not cell:
        return "", ""
    lines = [ln.strip() for ln in cell.splitlines() if ln.strip()]
    if not lines:
        return "", ""
    word = lines[0]
    phonetic = lines[1] if len(lines) > 1 else ""
    return word, phonetic

def extract_word_list():
    pdf_path = RES_DIR / "知识点总结" / "【沪教】八上英语单词表.pdf"
    units = {}
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            text = (page.extract_text() or "").strip()
            unit_match = re.search(r'^\s*unit\s*(\d+)\b', text, re.IGNORECASE)
            unit = unit_match.group(1) if unit_match else None
            tables = page.extract_tables()
            if not tables:
                continue
            for t in tables:
                # 跳过表头
                for row in t[1:]:
                    # row: [序号, 英文, 中文, 序号, 英文, 中文]
                    if len(row) < 3:
                        continue
                    def parse_entry(no_raw, en_raw, cn_raw):
                        no = (no_raw or "").strip()
                        en, phonetic = parse_word_cell(en_raw)
                        cn = (cn_raw or "").strip()
                        if not no or not en:
                            return None
                        return {"序号": no, "英文": en, "音标": phonetic, "中文": cn}
                    a = parse_entry(row[0], row[1], row[2])
                    if a:
                        units.setdefault(unit, []).append(a)
                    if len(row) >= 6:
                        b = parse_entry(row[3], row[4], row[5])
                        if b:
                            units.setdefault(unit, []).append(b)
    # 保存每个单元 + 全册合并
    all_items = []
    for unit in sorted(units.keys(), key=lambda x: int(x) if x and x.isdigit() else 999):
        items = units[unit]
        all_items.extend(items)
        data = {
            "title": f"沪教版·八上英语·单词表 Unit {unit}",
            "type": "vocab",
            "columns": ["英文", "音标", "中文"],
            "items": items,
            "quizModes": [
                {"id": "en2cn", "name": "看英文，写中文", "prompt": "英文", "answerKeys": ["中文"]},
                {"id": "cn2en", "name": "看中文，写英文", "prompt": "中文", "answerKeys": ["英文"]},
                {"id": "phonetic", "name": "看英文，写音标", "prompt": "英文", "answerKeys": ["音标"]}
            ]
        }
        save(f"知识点总结/单词表/Unit {unit}.json", data)
    # 全册合并
    full = {
        "title": "沪教版·八上英语·单词表（全册）",
        "type": "vocab",
        "columns": ["英文", "音标", "中文"],
        "items": all_items,
        "quizModes": [
            {"id": "en2cn", "name": "看英文，写中文", "prompt": "英文", "answerKeys": ["中文"]},
            {"id": "cn2en", "name": "看中文，写英文", "prompt": "中文", "answerKeys": ["英文"]}
        ]
    }
    save("知识点总结/【沪教】八上英语单词表.json", full)

if __name__ == "__main__":
    extract_irregular_verbs()
    extract_word_list()
    print("提取完成")
