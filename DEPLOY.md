# 🚀 Cycle-Master AI 部署指南

## 推荐平台对比

| 平台 | 费用 | 难度 | 适用场景 | 链接 |
|------|------|------|----------|------|
| **Streamlit Cloud** | 免费 | ⭐ 最简单 | 快速分享、团队协作 | [share.streamlit.io](https://share.streamlit.io) |
| **Hugging Face Spaces** | 免费 | ⭐⭐ 简单 | 社区分享、开源展示 | [huggingface.co/spaces](https://huggingface.co/spaces) |
| **Render** | 免费额度 | ⭐⭐⭐ 中等 | 长期运行、自定义域名 | [render.com](https://render.com) |

---

## 方案一：Streamlit Community Cloud（推荐 ⭐）

### 步骤 1：准备 GitHub 仓库

```bash
# 在项目目录初始化 git（如未初始化）
git init

# 添加所有文件
git add .

# 提交（注意：API Key 已从代码中移除，安全！）
git commit -m "Initial commit"

# 推送到 GitHub（需先在 GitHub 创建仓库）
git remote add origin https://github.com/你的用户名/cycle-master-ai.git
git push -u origin main
```

### 步骤 2：部署

1. 访问 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 账号登录
3. 点击 "New app"
4. 选择你的仓库
5. 配置：
   - **Main file path**: `app.py`
   - **Python version**: 3.9

### 步骤 3：配置 Secrets（可选）

如果希望预配置 API Key（团队内部使用）：

1. 进入 App 管理页面 → Settings → Secrets
2. 添加：
```toml
DEEPSEEK_API_KEY = "sk-your-actual-api-key"
```

> 💡 如果不配置，用户需在侧边栏自行输入，适合公开分享

---

## 方案二：Hugging Face Spaces

### 步骤 1：创建 Space

1. 访问 [huggingface.co/spaces](https://huggingface.co/spaces)
2. 点击 "Create new Space"
3. 填写信息：
   - **Space name**: `cycle-master-ai`
   - **SDK**: Streamlit
   - **Space hardware**: CPU (免费)
   - **Visibility**: Public (公开) / Private (私密)

### 步骤 2：上传代码

方式 A - 网页上传：
1. 进入 Space → Files → Upload files
2. 上传所有项目文件

方式 B - Git 命令：
```bash
# 克隆 Space 仓库（在 Space 页面获取地址）
git clone https://huggingface.co/spaces/你的用户名/cycle-master-ai
cd cycle-master-ai

# 复制项目文件到此处，然后推送
git add .
git commit -m "Initial commit"
git push
```

### 步骤 3：配置 Secrets

1. 进入 Space → Settings → Secrets
2. 添加 `DEEPSEEK_API_KEY`（可选）

---

## 方案三：Render

适合需要长期稳定运行的场景。

### 步骤 1：创建 Web Service

1. 访问 [dashboard.render.com](https://dashboard.render.com)
2. New → Web Service
3. 连接 GitHub 仓库

### 步骤 2：配置

- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `streamlit run app.py --server.port $PORT`

### 步骤 3：环境变量

在 Environment 中添加：
```
DEEPSEEK_API_KEY=sk-your-api-key
```

---

## 📋 部署检查清单

- [ ] `requirements.txt` 已创建
- [ ] `.streamlit/config.toml` 已配置
- [ ] 敏感信息（API Key）已从代码中移除
- [ ] `README.md` 已添加项目说明
- [ ] 代码已推送到 GitHub

---

## 🔒 安全提示

1. **永远不要**将真实 API Key 提交到 GitHub
2. 公开分享时，建议让用户自行输入 API Key
3. 定期轮换 API Key
4. 如需预配置 Key，使用平台的 Secrets 功能

---

## 🆘 常见问题

### Q: 部署后提示缺少依赖？
A: 确保 `requirements.txt` 包含所有依赖：
```
streamlit>=1.28.0
openai>=1.0.0
pandas>=2.0.0
plotly>=5.15.0
python-docx>=0.8.11
```

### Q: 页面加载很慢？
A: 免费平台有冷启动时间，首次访问可能较慢，后续会快一些。

### Q: 如何限制访问权限？
A: 
- Streamlit Cloud: 设置为 Private App
- Hugging Face: 设置为 Private Space
- 或添加密码验证：`st.secrets["PASSWORD"]`

### Q: 支持哪些文件格式上传？
A: 如需支持数据文件上传，确保 `requirements.txt` 包含相关库。

---

## 📞 需要帮助？

- Streamlit 文档：[docs.streamlit.io](https://docs.streamlit.io)
- Hugging Face 文档：[huggingface.co/docs](https://huggingface.co/docs)
- DeepSeek API：[platform.deepseek.com](https://platform.deepseek.com)
