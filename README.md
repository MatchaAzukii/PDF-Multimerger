# PDF MultiMerger 📄✨  
*A high-performance PDF page merger with dynamic layout support*

---

## 📌 项目简介  
PDF MultiMerger 是一个基于 Python 的高效 PDF 文件合并工具，支持：  
- 多进程并行处理加速  
- 动态布局（每页显示 1/2/4/6/9 个原始页面）  
- 自然排序（按文件名数字排序）  
- 自动修复常见 PDF 结构问题  

适用于制作演示文稿、报告预览、文档归档等场景。

---

## 🚀 核心功能  
✅ **动态布局**  
支持 `pages_per_sheet=1/2/4/6/9`，自动计算行列分布与缩放比例  

✅ **多进程加速**  
利用 CPU 多核特性，显著提升大文件处理速度  

✅ **智能排序**  
按文件名中的数字排序（如 `Word - 1.pdf` → `Word - 10.pdf` 顺序正确）  

✅ **异常容错**  
- 自动跳过空文件  
- 捕获并记录解析错误  
- 支持 `strict=False` 模式忽略非关键警告  

---

## 📦 安装指南  
```bash
# 安装依赖（需 Python 3.8+）
pip install pypdf

# 可选：升级到最新版 pypdf（推荐）
pip install --upgrade pypdf
```


This program is generated using Qwen 