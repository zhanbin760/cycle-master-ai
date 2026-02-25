# 🚀 周期共振职业规划系统 - 部署指南

## 系统概述

基于马江博"政策周期与产业周期"二元分析框架的智能职业规划工具。

---

## 推荐部署平台

| 平台 | 费用 | 难度 | 适用场景 | 链接 |
|------|------|------|----------|------|
| **Streamlit Cloud** | 免费 | ⭐ 最简单 | 快速分享、个人使用 | [share.streamlit.io](https://share.streamlit.io) |
| **Hugging Face Spaces** | 免费 | ⭐⭐ 简单 | 社区分享、开源展示 | [huggingface.co/spaces](https://huggingface.co/spaces) |

---

## 方案一：Streamlit Community Cloud（推荐）

### 步骤 1：准备 GitHub 仓库

```bash
# 在项目目录初始化 git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 周期共振职业规划系统"

# 推送到 GitHub（需先在 GitHub 创建仓库）
git remote add origin https://github.com/你的用户名/cycle-master-career.git
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
   - **Space name**: `cycle-master-career`
   - **SDK**: Streamlit
   - **Space hardware**: CPU (免费)
   - **Visibility**: Public / Private

### 步骤 2：上传代码

```bash
# 克隆 Space 仓库
git clone https://huggingface.co/spaces/你的用户名/cycle-master-career
cd cycle-master-career

# 复制项目文件
# ...

# 推送
git add .
git commit -m "Initial commit"
git push
```

### 步骤 3：配置 Secrets

在 Space → Settings → Secrets 中添加 `DEEPSEEK_API_KEY`（可选）

---

## 方案三：本地运行

```bash
# 1. 克隆/下载代码
cd cycle_master_system

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
streamlit run app.py

# 5. 浏览器访问
# http://localhost:8501
```

---

## 部署检查清单

- [ ] `requirements.txt` 已创建并包含所有依赖
- [ ] `.streamlit/config.toml` 已配置（可选）
- [ ] 敏感信息（API Key）已从代码中移除
- [ ] `data/细分领域行业周期研判表.csv` 数据文件已上传
- [ ] `README.md` 已添加项目说明
- [ ] 代码已推送到 GitHub

---

## 文件结构要求

```
cycle_master_system/
├── app.py                          # 主入口
├── requirements.txt                # 依赖列表
├── README.md                       # 项目说明
├── DEPLOY.md                       # 部署指南
├── data/
│   └── 细分领域行业周期研判表.csv   # 核心数据
├── utils/
│   ├── __init__.py
│   ├── llm_engine.py              # LLM引擎
│   ├── rag_engine.py              # RAG检索引擎
│   ├── data_processor.py          # 数据处理
│   └── visualization.py           # 可视化组件
├── pages/
│   ├── 01_📊_周期实验室.py
│   ├── 02_🤖_AI协同规划官.py
│   ├── 03_📡_数据哨兵服务.py
│   ├── 04_🛤️_职业路径推演.py
│   └── 05_📄_简历诊断中心.py
└── .streamlit/
    └── config.toml                # Streamlit配置（可选）
```

---

## 安全提示

1. **永远不要**将真实 API Key 提交到 GitHub
2. 公开分享时，建议让用户自行输入 API Key
3. 定期轮换 API Key
4. 如需预配置 Key，使用平台的 Secrets 功能

---

## 常见问题

### Q: 部署后提示缺少依赖？

确保 `requirements.txt` 包含：
```
streamlit>=1.28.0
openai>=1.0.0
pandas>=2.0.0
plotly>=5.15.0
python-docx>=0.8.11
PyPDF2>=3.0.0
```

### Q: 数据文件找不到？

确保 `data/细分领域行业周期研判表.csv` 已上传到仓库，且文件名正确。

### Q: 页面加载很慢？

免费平台有冷启动时间，首次访问可能较慢，后续会快一些。

### Q: 如何限制访问权限？

- Streamlit Cloud: 设置为 Private App
- Hugging Face: 设置为 Private Space

### Q: 中文文件名显示乱码？

确保文件使用 UTF-8 编码，并在读取时指定编码：
```python
df = pd.read_csv(file_path, encoding='utf-8')
```

---

## 技术支持

- Streamlit 文档：[docs.streamlit.io](https://docs.streamlit.io)
- DeepSeek API：[platform.deepseek.com](https://platform.deepseek.com)
- 马江博周期理论：参考系统内理论说明
