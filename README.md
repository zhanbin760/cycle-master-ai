# 🧬 Cycle-Master AI 周期共振导航系统

基于马江博"政策周期与产业周期"二元分析框架的智能职业规划与投资分析工具。

## 系统功能

1. **📊 周期实验室** - 可视化呈现近300个细分领域的周期阶段
2. **🤖 AI协同规划官** - 生成深度行业研报
3. **📡 数据哨兵服务** - 追踪关键指标
4. **📈 回测验证** - 历史数据回测

## 快速部署

### 方式一：Streamlit Community Cloud（推荐）

1. 将代码推送到 GitHub 仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io) 部署
3. 在 Settings > Secrets 中添加：
   ```toml
   DEEPSEEK_API_KEY = "your-api-key"
   ```

### 方式二：Hugging Face Spaces

1. 访问 [huggingface.co/spaces](https://huggingface.co/spaces)
2. 创建 New Space，选择 Streamlit 模板
3. 上传代码文件
4. 在 Settings > Secrets 中配置 API Key

### 方式三：本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## API Key 配置

系统需要 DeepSeek API Key，可通过以下方式配置：
- 环境变量：`DEEPSEEK_API_KEY`
- Streamlit Secrets：部署平台设置
- 侧边栏输入：运行时手动输入（推荐公开试用）

## 技术栈

- Python 3.8+
- Streamlit
- OpenAI SDK (DeepSeek API)
- Plotly / Pandas
