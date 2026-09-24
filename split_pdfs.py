# -*- coding: utf-8 -*-
"""把 resources/<分类>/ 下的单份 PDF（学生版+解析版合订）按“解析版”页眉拆成两份。

用法示例：
    python split_pdfs.py "C:\...\chat-app\resources\单元检测"

拆分规则：
1. 扫描每页文本，找到第一个出现“解析版”字样的页面作为解析版起点。
2. 起点之前的页保存为“（学生版）.pdf”。
3. 起点及之后的页保存为“（解析版）.pdf”。
4. 原文件在拆分成功后删除。
"""
import fitz, os, re, sys

def clean_base(name):
    """去掉原文件名里的空格编号后缀，例如 'Unit 6（基础卷） (2).pdf' -> 'Unit 6（基础卷）'"""
    base = re.sub(r'\.pdf$', '', name, flags=re.IGNORECASE)
    base = re.sub(r'\s*\(\d+\)\s*$', '', base)
    return base

def find_split(doc):
    for i in range(doc.page_count):
        txt = doc[i].get_text("text")
        if '解析版' in txt:
            return i
    return None

def split_pdf(src, dry=False):
    doc = fitz.open(src)
    total_pages = doc.page_count
    try:
        split = find_split(doc)
        if split is None or split == 0:
            print(f"[跳过] {os.path.basename(src)}: 未找到解析版起点或起点在第1页")
            return False
        base = clean_base(os.path.basename(src))
        folder = os.path.dirname(src)
        stu_path = os.path.join(folder, base + "（学生版）.pdf")
        ans_path = os.path.join(folder, base + "（解析版）.pdf")
        if dry:
            print(f"[预览] {os.path.basename(src)} 共{total_pages}页, 解析版从第{split+1}页开始 -> 学生版{split}页, 解析版{total_pages-split}页")
            return True
        # 学生版
        stu = fitz.open()
        stu.insert_pdf(doc, from_page=0, to_page=split-1)
        stu.save(stu_path, garbage=4, deflate=True)
        stu.close()
        # 解析版
        ans = fitz.open()
        ans.insert_pdf(doc, from_page=split, to_page=total_pages-1)
        ans.save(ans_path, garbage=4, deflate=True)
        ans.close()
        os.remove(src)
        print(f"[完成] {base}: 学生版{split}页, 解析版{total_pages-split}页")
        return True
    except Exception as e:
        print(f"[失败] {os.path.basename(src)}: {e}")
        return False
    finally:
        try:
            doc.close()
        except Exception:
            pass

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    if not folder:
        folder = os.path.join(os.path.dirname(__file__), 'resources', '单元检测')
    folder = os.path.abspath(folder)
    if not os.path.isdir(folder):
        print(f"目录不存在: {folder}")
        sys.exit(1)
    pdfs = [f for f in sorted(os.listdir(folder)) if f.lower().endswith('.pdf') and not f.endswith('（学生版）.pdf') and not f.endswith('（解析版）.pdf')]
    print(f"处理目录: {folder}, 共 {len(pdfs)} 个待拆分 PDF")
    for f in pdfs:
        split_pdf(os.path.join(folder, f))

if __name__ == '__main__':
    main()
