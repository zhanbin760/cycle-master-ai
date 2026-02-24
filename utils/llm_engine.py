# utils/llm_engine.py
import streamlit as st
from openai import OpenAI

def get_api_key():
    """
    获取 DeepSeek API Key，优先级：
    1. Streamlit Secrets（适合私密部署）
    2. 侧边栏用户输入（适合公开试用）
    3. 环境变量
    """
    # 尝试从 secrets 读取
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
        if api_key and api_key != "your-api-key-here":
            return api_key
    except Exception:
        pass
    
    # 尝试从 session_state 读取（用户已输入）
    if "user_api_key" in st.session_state and st.session_state["user_api_key"]:
        return st.session_state["user_api_key"]
    
    return None

def render_api_key_input():
    """
    在侧边栏渲染 API Key 输入框（用于公开试用）
    """
    with st.sidebar:
        st.divider()
        st.markdown("### 🔑 API 配置")
        
        # 检查是否已有有效 Key
        current_key = get_api_key()
        
        if current_key:
            st.success("✅ API Key 已配置")
            if st.button("🔄 重新输入 Key"):
                st.session_state["user_api_key"] = ""
                st.rerun()
        else:
            st.warning("⚠️ 请输入 DeepSeek API Key")
            api_key = st.text_input(
                "DeepSeek API Key",
                type="password",
                placeholder="sk-...",
                help="请访问 platform.deepseek.com 获取 API Key",
                key="api_key_input"
            )
            
            if api_key:
                st.session_state["user_api_key"] = api_key
                st.rerun()
            
            st.info("💡 没有 API Key？前往 [DeepSeek 平台](https://platform.deepseek.com) 注册获取")
            st.stop()

def get_deepseek_client():
    """
    初始化并返回 DeepSeek 客户端。
    """
    api_key = get_api_key()
    
    if not api_key:
        st.error("⚠️ 未找到 DeepSeek API Key，请在侧边栏输入或配置 Secrets。")
        st.stop()
    
    try:
        client = OpenAI(
            api_key=api_key, 
            base_url="https://api.deepseek.com"
        )
        return client
    except Exception as e:
        st.error(f"⚠️ 初始化客户端失败: {str(e)}")
        st.stop()

def get_system_prompt():
    """
    获取 Cycle-Master AI 的核心系统提示词。
    内嵌了马江博周期理论的核心框架与7大拐点量化指标。
    """
    return """
# [ SYSTEM_NAME: Cycle-Master AI (周期共振职业规划师) ]

## 00. 运行时协议
1. 角色绑定: 你是基于"马江博周期共振理论"构建的顶级职业规划与产业分析专家。
2. 理论刚性: 分析必须严格遵循以下二元分析框架：
   - 产业周期4阶段: 初创期、成长期、成熟期、调整衰退期。
   - 政策周期4阶段: 规划引导期、资源聚焦期、调整退出期、政策压降期。
3. 输出模式: 结构化输出，并在每次回复结尾生成一个 HUD 仪表盘。
4. 步进交互: 严禁一次性输出所有内容，必须按 Phase 步进引导用户完成分析。

## 01. 系统内核
* 财富效率研判: 必须识别行业属于以下哪种典型组合：
  1. 高风险押宝期 (初创产业 + 引导政策)
  2. 红利交叠期 (成长产业 + 聚焦政策) - 最佳入场时机
  3. 红利退坡期 (成熟产业 + 退出政策) - 需做防御性打算
  4. 红利消失期 (衰退产业 + 压降政策) - 建议早走一定比晚走好
* 行业类型定性: 判断标的是否属于"技术突破型"、"国家安全型"或"消费升级型"。

## 02. 双核对抗引擎
* 🟢 Core A [执行核]: 定位象限，并**生成专业的 AI 检索 Prompt**，指导用户去核实关键数据（例如：检索职业技能培训或银发经济领域的最新资本开支增速）。
* 🔴 Core B [审计核]: 必须利用【新产业成长期拐点判断7大清单】对标的进行严格审计：
  □ 技术成本在2-3年内下降50%以上
  □ 龙头企业毛利率超过20%，净利润转正
  □ 政策文件中明确了财政资金规模和具体补贴标准
  □ 市场渗透率在5%-30%之间
  □ 行业资本开支增速维持30%以上
  □ 出现了3家以上年营收超过10亿的企业
  □ 产业链上下游配套开始完善

## 03. 仪表盘 (HUD)
每次回复的最后，必须严格渲染以下代码块（实时更新状态）：
```text
╭─ 🧭 Cycle-Master AI ── [Status: Phase X] ─╮
│ 🎯 Target: [当前分析的行业]                 │
│ 📊 Cycle: 产业 [阶段] | 政策 [阶段]        │
│ 💡 Type: [分类：如 消费升级型]              │
│ 👉 NEXT: [提示用户下一步骤或需要提供的数据]   │
╰──────────────────────────────────────────╯
```
"""

def analyze_industry(industry_name, user_input=""):
    """
    对指定行业进行周期分析。
    
    Args:
        industry_name: 行业名称
        user_input: 用户的额外输入
        
    Returns:
        AI 生成的分析报告
    """
    client = get_deepseek_client()
    
    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": f"请分析行业：{industry_name}\n\n补充信息：{user_input}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 分析失败: {str(e)}"
