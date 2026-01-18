### ✅ `README.md`（推荐内容）

```markdown
# 桂电AI学姐 — 虚拟主播项目

> 本项目为桂林电子科技大学大模型应用实践课程成果，旨在构建一个具备校园知识问答与情感陪伴能力的AI虚拟主播“小桂”。

---

## 📁 项目结构说明

| 文件/文件夹 | 作用 |
|------------|------|
├── web_app.py # 主程序：Flask Web 服务 + 内嵌 HTML 界面
├── chatbot.py # 核心逻辑：ChatBot 类，封装 DashScope 调用
├── config/ # 配置文件（模型参数、Prompt 模板等）
├── data/ # 测试问题集、知识库样本
├── docs/ # 设计文档、Prompt 示例、中期报告
├── test_model.py # 批量测试脚本（用于评估回复质量）
├── .env # API 密钥（示例：DASHSCOPE_API_KEY=sk-xxx）
├── .gitignore # 自动忽略敏感文件（.env, venv/, pycache/）

---

## 🧠 核心功能

- **智能问答**：回答课程、宿舍、选课等校园常见问题
- **情感陪伴**：提供鼓励性回复，缓解学生焦虑
- **人设一致**：通过 Prompt 工程确保“小桂”风格统一
- **安全兜底**：对不确定问题引导至官网
```

---

## 🛠️ 开发规范

- 所有代码提交前请运行 `git pull` 拉取最新版本
- 提交信息格式建议：
  ```bash
  git commit -m "feat: 添加小桂人设卡"
  git commit -m "fix: 修复 API Key 加载错误"
  ```
- 不要提交 `.env` 和 `venv/` 到 GitHub（由 `.gitignore` 保护）