# 系统架构设计师模拟答题学习站

这是一个面向系统架构设计师模拟真题训练的静态网页应用，包含模拟考试、学习刷题、案例/论文训练、自动判分、错题解析和本地草稿保存等功能。

## 功能

- 两套综合知识客观题，支持 150 分钟限时模拟考试。
- 作答自动保存在浏览器 `localStorage`，提交后自动判分。
- 错题显示正确答案、你的答案、考点定位、知识点示例、解题思路和复盘建议。
- 案例分析题按题面结构化重排，范围填空会拆成独立输入框。
- 原始 PDF 和扫描页图片不在网页中展示，避免直接暴露答案。

## 本地运行

直接用浏览器打开 `index.html` 即可运行，无需安装依赖或启动后端服务。

## 部署

仓库内包含 GitHub Pages Actions 工作流。推送到 GitHub 后，在仓库 Settings -> Pages 中选择 GitHub Actions 作为部署来源，即可自动发布。

## 目录

- `index.html`：页面入口。
- `styles.css`：页面样式。
- `app.js`：答题、判分、解析和草稿保存逻辑。
- `data/question-bank.js`：题库数据。
- `scripts/build_question_bank.py`：从 OCR 文本生成题库的脚本。
- `data/ocr-audit-report.md`：OCR 核查记录。
