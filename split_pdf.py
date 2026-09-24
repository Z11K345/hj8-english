# -*- coding: utf-8 -*-
import fitz, os, re
SRC = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources\一课一练\Unit 1 Section 1 Reading（分层练习）.pdf"
OUT = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources\一课一练"
doc = fitz.open(SRC)
n = doc.page_count
# 检测“解析版”起始页
split = n
for i in range(n):
    t = doc[i].get_text("text")
    if "解析版" in t:
        split = i
        break
print("总页数:", n, " 解析版起始页(0-based):", split, " => 学生版 1-%d, 解析版 %d-%d" % (split, split+1, n))
stu = fitz.open()
ans = fitz.open()
for i in range(n):
    if i < split:
        stu.insert_pdf(doc, from_page=i, to_page=i)
    else:
        ans.insert_pdf(doc, from_page=i, to_page=i)
stu_path = os.path.join(OUT, "Unit 1 Section 1 Reading（学生版）.pdf")
ans_path = os.path.join(OUT, "Unit 1 Section 1 Reading（解析版）.pdf")
stu.save(stu_path)
ans.save(ans_path)
stu.close(); ans.close(); doc.close()
print("已生成:", os.path.basename(stu_path), "页数", split)
print("已生成:", os.path.basename(ans_path), "页数", n-split)
