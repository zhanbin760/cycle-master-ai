# utils/llm_engine.py
import streamlit as st
from openai import OpenAI
from utils.rag_engine import get_rag_engine

# ==========================================
# API Key 管理
# ==========================================

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


def render_privacy_notice():
    """
    在侧边栏渲染隐私声明和使用限制
    """
    with st.sidebar:
        st.divider()
        with st.expander("🔒 隐私与安全声明", expanded=False):
            st.markdown("""
            **隐私保护承诺：**
            
            ✅ 本系统**不留存**任何用户个人隐私数据
            
            ✅ 所有对话分析均**实时调用** DeepSeek 大模型处理
            
            ✅ 关闭页面后，对话记录**自动清除**
            
            ✅ 简历等上传文件**仅用于临时分析**，不会保存到服务器
            
            ---
            **使用限制：**
            
            为防止恶意刷取 API Token，系统限制每日生成次数。
            """)
        
        # 使用次数限制检查
        check_usage_limit()


DAILY_LIMIT = 20  # 每日使用次数限制

def check_usage_limit():
    """
    检查并显示每日使用次数限制
    """
    if 'daily_usage' not in st.session_state:
        st.session_state['daily_usage'] = 0
    
    remaining = DAILY_LIMIT - st.session_state['daily_usage']
    
    with st.sidebar:
        st.markdown("### 📊 今日使用配额")
        st.progress(min(st.session_state['daily_usage'] / DAILY_LIMIT, 1.0))
        st.caption(f"已使用: {st.session_state['daily_usage']} / {DAILY_LIMIT} 次")
        
        if remaining <= 0:
            st.error("⚠️ 今日使用次数已达上限，请明日再试")
            st.stop()
        elif remaining <= 10:
            st.warning(f"⚠️ 今日剩余 {remaining} 次使用机会")


def increment_usage():
    """增加使用次数计数"""
    if 'daily_usage' not in st.session_state:
        st.session_state['daily_usage'] = 0
    st.session_state['daily_usage'] += 1


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


# ==========================================
# 系统提示词 (System Prompt)
# ==========================================

def get_system_prompt(user_identity: str = "", user_risk_preference: str = "稳健") -> str:
    """
    获取 Cycle-Master AI 的核心系统提示词。
    内嵌了马江博周期理论的核心框架与硬性约束。
    
    Args:
        user_identity: 用户身份类型（应届生/职场转型者/高管跨界）
        user_risk_preference: 用户风险偏好
    """
    identity_advice = {
        "应届生": "重点关注成长期行业，利用职业早期的高容错性积累高价值经验。",
        "职场转型者": "优先考虑技能可迁移的成长期行业，避免进入调整期行业。",
        "高管跨界": "关注技术突破型和国家安全型赛道，利用管理经验获取跨界机会。",
        "": "根据用户具体情况提供个性化建议。"
    }
    
    return f"""# [ SYSTEM_NAME: Cycle-Master AI (周期共振职业规划师) ]

## 00. 运行时协议（硬性约束）
1. 角色绑定: 你是基于"马江博周期共振理论"构建的顶级职业规划与产业分析专家。
2. 理论刚性: 分析**必须严格遵循**以下二元分析框架，不得偏离：
   - 产业周期4阶段: 初创期、成长期、成熟期、调整衰退期。
   - 政策周期4阶段: 规划引导期、资源聚焦期、调整退出期、政策压降期。
3. 数据驱动: 所有建议**必须基于**提供的知识库数据，禁止编造信息。
4. 输出模式: 结构化输出，并在每次回复结尾生成一个 HUD 仪表盘。
5. 身份适配: 当前用户身份为【{user_identity}】，风险偏好【{user_risk_preference}】。{identity_advice.get(user_identity, "")}

## 01. 系统内核 - 四种典型组合（必须严格应用）
财富效率研判必须识别行业属于以下哪种典型组合：

1. 🔴 **高风险押宝期** (初创产业 + 引导政策)
   - 特征: 技术未验证，政策刚出台
   - 适合: 风险偏好极高、抗压能力强的早期探索者
   - 策略: 小步试错，控制投入，密切关注技术突破信号

2. 🟢 **红利交叠期** (成长产业 + 聚焦政策) - **最佳入场时机**
   - 特征: 渗透率快速提升(5%-30%)，政策资金涌入
   - 适合: 绝大多数求职者，尤其是转型者
   - 策略: 果断入场，选择头部或高成长企业，积累核心技能

3. 🟡 **红利退坡期** (成熟产业 + 退出政策) - **需做防御性打算**
   - 特征: 增速放缓，政策收紧，竞争格局稳定
   - 适合: 追求稳定的资深从业者
   - 策略: 深耕细分领域成为专家，或向上下游延伸，储备转型能力

4. 🔴 **红利消失期** (衰退产业 + 压降政策) - **建议早走一定比晚走好**
   - 特征: 产能过剩，政策明确限制，需求萎缩
   - 适合: 不建议进入
   - 策略: 立即启动转型，利用可迁移技能转向成长期行业

## 02. 双核对抗引擎
* 🟢 Core A [执行核]: 定位象限，**生成专业的 AI 检索 Prompt**，指导用户去核实关键数据。
* 🔴 Core B [审计核]: 必须利用【新产业成长期拐点判断7大清单】对标的进行严格审计：
  □ 技术成本在2-3年内下降50%以上
  □ 龙头企业毛利率超过20%，净利润转正
  □ 政策文件中明确了财政资金规模和具体补贴标准
  □ 市场渗透率在5%-30%之间
  □ 行业资本开支增速维持30%以上
  □ 出现了3家以上年营收超过10亿的企业
  □ 产业链上下游配套开始完善

## 03. 输出规范
1. **数据引用**: 必须引用知识库中的具体数据支撑观点
2. **风险提示**: 必须明确告知用户所处周期的风险等级
3. **行动建议**: 必须给出具体可执行的行动建议
4. **替代方案**: 如果当前行业处于风险期，必须推荐替代方向

## 04. 仪表盘 (HUD)
每次回复的最后，必须严格渲染以下代码块（实时更新状态）：
```text
╭─ 🧭 Cycle-Master AI ── [Status: Active] ─╮
│ 🎯 Target: [当前分析的行业]                 │
│ 📊 Cycle: 产业 [阶段] | 政策 [阶段]        │
│ 💡 Type: [组合类型：如红利交叠期]          │
│ ⚠️ Risk: [风险等级]                        │
│ 👉 NEXT: [提示用户下一步骤]                │
╰──────────────────────────────────────────╯
```
"""


def analyze_industry_with_rag(industry_name: str, user_input: str = "", 
                               user_identity: str = "", user_risk_preference: str = "稳健") -> str:
    """
    基于RAG对指定行业进行周期分析。
    
    Args:
        industry_name: 行业名称
        user_input: 用户的额外输入
        user_identity: 用户身份
        user_risk_preference: 用户风险偏好
        
    Returns:
        AI 生成的分析报告
    """
    # 增加使用次数
    increment_usage()
    
    # 获取RAG引擎
    rag_engine = get_rag_engine()
    
    # 构建检索上下文
    context = rag_engine.build_context_for_llm(industry_name)
    
    # 获取DeepSeek客户端
    client = get_deepseek_client()
    
    # 构建消息
    messages = [
        {"role": "system", "content": get_system_prompt(user_identity, user_risk_preference)},
        {"role": "user", "content": f"【知识库检索上下文】\n{context}\n\n【用户问题】\n请分析行业：{industry_name}\n\n补充信息：{user_input}"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.5,  # 降低温度以获得更确定的回答
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 分析失败: {str(e)}"


def analyze_industry_stream(industry_name: str, user_input: str = "",
                             user_identity: str = "", user_risk_preference: str = "稳健"):
    """
    基于RAG进行流式分析（用于实时显示）
    
    Args:
        industry_name: 行业名称
        user_input: 用户的额外输入
        user_identity: 用户身份
        user_risk_preference: 用户风险偏好
        
    Returns:
        流式响应生成器
    """
    # 增加使用次数
    increment_usage()
    
    # 获取RAG引擎
    rag_engine = get_rag_engine()
    
    # 构建检索上下文
    context = rag_engine.build_context_for_llm(industry_name)
    
    # 获取DeepSeek客户端
    client = get_deepseek_client()
    
    # 构建消息
    messages = [
        {"role": "system", "content": get_system_prompt(user_identity, user_risk_preference)},
        {"role": "user", "content": f"【知识库检索上下文】\n{context}\n\n【用户问题】\n请分析行业：{industry_name}\n\n补充信息：{user_input}"}
    ]
    
    try:
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
            temperature=0.5,
            max_tokens=4000
        )
        return stream
    except Exception as e:
        raise e


def analyze_career_transition(current_industry: str, target_industry: str, 
                               user_background: str = "") -> str:
    """
    分析职业转型路径
    
    Args:
        current_industry: 当前行业
        target_industry: 目标行业
        user_background: 用户背景
        
    Returns:
        AI生成的转型分析报告
    """
    increment_usage()
    
    rag_engine = get_rag_engine()
    client = get_deepseek_client()
    
    # 获取两个行业的上下文
    current_context = rag_engine.build_context_for_llm(current_industry)
    target_context = rag_engine.build_context_for_llm(target_industry)
    
    prompt = f"""【当前行业分析】
{current_context}

【目标行业分析】
{target_context}

【用户背景】
{user_background}

请基于以上数据，为用户提供详细的职业转型分析：
1. 两个行业的周期阶段对比
2. 技能迁移的可行性评估
3. 转型风险与机会分析
4. 具体的转型路径建议
5. 需要补充的技能或资质
"""
    
    messages = [
        {"role": "system", "content": get_system_prompt("职场转型者", "稳健")},
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.6,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 分析失败: {str(e)}"
