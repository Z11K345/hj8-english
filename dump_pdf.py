# -*- coding: utf-8 -*-
import fitz, sys, os
p = r"C:\Users\GFQH-GF-ZK\WorkBuddy\2026-09-20-12-23-11\学习助手\chat-app\resources\一课一练\Unit 1 Section 1 Reading（分层练习）.pdf"
doc = fitz.open(p)
print("PAGES:", doc.page_count)
for i in range(doc.page_count):
    print("\n========== PAGE %d ==========" % (i+1))
    txt = doc[i].get_text("text")
    print(txt)
doc.close()
