import streamlit as st
from openai import OpenAI
import time
import sys
import os

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_engine import (
    render_api_key_input, 
    render_privacy_notice,
    get_deepseek_client,
    analyze_industry_stream,
    analyze_career_transition
)
from utils.rag_engine import get_rag_engine

# ==========================================
# 页面配置与初始化
# ==========================================
st.set_page_config(page_title="AI协同规划官", page_icon="🤖", layout="wide")
st.title("🤖 AI协同规划官 (DeepSeek 驱动)")
st.markdown('基于**"产业周期+政策周期"**二元分析框架，通过人机协同为您提供深度职业规划建议')

# 渲染 API Key 输入和隐私声明
render_api_key_input()
render_privacy_notice()

# 获取 DeepSeek 客户端
client = get_deepseek_client()

# ==========================================
# 侧边栏：用户档案与上下文
# ==========================================
with st.sidebar:
    st.header("👤 您的档案")
    
    # 显示/编辑用户身份
    if 'user_profile' not in st.session_state:
        st.session_state['user_profile'] = {
            'identity': '',
            'current_industry': '',
            'experience_years': 0,
            'risk_preference': '稳健'
        }
    
    user_role = st.text_input("当前职业/角色", 
                              value=st.session_state['user_profile'].get('identity', ''),
                              placeholder="例如：在校大学生 / 互联网产品经理 / 传统制造业工程师")
    
    user_goal = st.selectbox("咨询目的", [
        "职业规划/转型建议",
        "行业景气度/周期阶段研判",
        "具体offer/跳槽决策",
        "技能提升/学习路径",
        "其他"
    ])
    
    current_industry = st.text_input("当前/过往行业", 
                                     value=st.session_state['user_profile'].get('current_industry', ''),
                                     placeholder="例如：传统地产")
    
    target_industry = st.text_input("目标/意向行业", 
                                    value=st.session_state.get('target_industry', ''),
                                    placeholder="例如：新能源汽车")
    
    st.markdown("---")
    
    # 快速操作按钮
    if st.button("🗑️ 清空对话历史"):
        st.session_state.messages = []
        st.session_state['target_industry'] = ""
        st.rerun()
    
    # 快捷功能
    st.markdown("### ⚡ 快捷功能")
    if st.button("📊 查看周期实验室"):
        st.switch_page("pages/02_📊_周期实验室.py")
    if st.button("🛤️ 职业路径推演"):
        st.switch_page("pages/04_🛤️_职业路径推演.py")
    if st.button("📄 简历诊断"):
        st.switch_page("pages/01_📄_简历诊断中心.py")

# 更新用户档案
st.session_state['user_profile']['identity'] = user_role
st.session_state['user_profile']['current_industry'] = current_industry

# ==========================================
# 系统提示词 (System Prompt)
# ==========================================
from utils.llm_engine import get_system_prompt

SYSTEM_PROMPT = get_system_prompt(user_role, "稳健")

# ==========================================
# 对话状态管理 (Session State)
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 初始化欢迎消息
    welcome_msg = "您好！我是 **Cycle-Master AI 协同规划官**，系统已成功载入**周期共振职业规划知识库**。\n\n"
    
    # 检查是否有预设的目标行业
    if st.session_state.get('target_industry'):
        target = st.session_state['target_industry']
        welcome_msg += f"🎯 检测到您关注的行业是 **{target}**，让我为您检索知识库数据...\n\n"
        
        # 使用RAG检索并显示
        try:
            rag_engine = get_rag_engine()
            search_results = rag_engine.search_industry(target, top_k=1)
            if search_results:
                result = search_results[0]
                welcome_msg += f"📊 **知识库检索结果**：\n"
                welcome_msg += f"- 行业：**{result['行业名称']}**\n"
                welcome_msg += f"- 当前周期阶段：**{result['当前周期阶段']}**\n"
                welcome_msg += f"- 未来1-3年景气度：**{result['未来1-3年景气度']}**\n"
                welcome_msg += f"- 评价：{result['评价']}\n\n"
                
                # 添加组合分析
                combo = rag_engine.get_cycle_combination(result['当前周期阶段'])
                welcome_msg += f"🔍 **周期组合研判**：{combo.get('组合名称', '')} {combo.get('风险等级', '')}\n"
                welcome_msg += f"💡 **建议**：{combo.get('策略', '')}\n\n"
                
                # 风险预警
                risk = rag_engine.get_risk_warning(target)
                if risk:
                    welcome_msg += f"⚠️ **风险预警**：{risk['预警类型']}，{risk['建议']}\n\n"
            else:
                welcome_msg += f"未在知识库中找到 **{target}** 的精确匹配，但我可以基于通用周期理论为您分析。\n\n"
        except Exception as e:
            welcome_msg += f"（知识库检索暂时不可用）\n\n"
        
        welcome_msg += "请问您想了解该行业的哪些方面？例如：\n"
        welcome_msg += "- 当前是否适合进入/转型？\n"
        welcome_msg += "- 需要储备哪些核心技能？\n"
        welcome_msg += "- 未来3-5年的发展前景如何？"
    else:
        welcome_msg += "请问您目前关注哪个行业？或者有什么职业规划方面的问题？"
        
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})

# 如果有目标行业变更，更新系统提示
if st.session_state.get('target_industry') != target_industry and target_industry:
    st.session_state['target_industry'] = target_industry
    # 不立即刷新，等待用户主动提问

# ==========================================
# 渲染历史对话
# ==========================================
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ==========================================
# 处理用户输入与 API 调用
# ==========================================

if prompt := st.chat_input("请输入您关注的行业或职业规划问题..."):
    # 构建上下文化提示
    contextual_prompt = prompt
    
    # 添加用户档案上下文
    if user_role or current_industry or target_industry:
        profile_context = "【用户档案】\n"
        if user_role:
            profile_context += f"- 当前角色：{user_role}\n"
        if current_industry:
            profile_context += f"- 当前/过往行业：{current_industry}\n"
        if target_industry:
            profile_context += f"- 目标行业：{target_industry}\n"
        if user_goal:
            profile_context += f"- 咨询目的：{user_goal}\n"
        contextual_prompt = profile_context + "\n【用户问题】\n" + prompt
    
    # 如果有明确提到的行业，注入RAG上下文
    mentioned_industry = target_industry if target_industry else current_industry
    if mentioned_industry:
        try:
            rag_engine = get_rag_engine()
            rag_context = rag_engine.build_context_for_llm(mentioned_industry)
            contextual_prompt = f"【知识库上下文】\n{rag_context}\n\n" + contextual_prompt
        except Exception:
            pass
    
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": contextual_prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用API生成回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 使用流式API
            stream = client.chat.completions.create(
                model="deepseek-chat", 
                messages=st.session_state.messages,
                stream=True,
                temperature=0.6,
                max_tokens=4000
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"DeepSeek API 调用失败：请检查您的 API Key 是否正确: {str(e)}")
            st.stop()
            
    # 保存助手回复到历史
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    # 增加使用次数
    if 'daily_usage' in st.session_state:
        st.session_state['daily_usage'] += 1

# ==========================================
# 快捷分析功能（页面底部）
# ==========================================
st.markdown("---")
st.markdown("### ⚡ 快捷分析")

quick_cols = st.columns(3)

with quick_cols[0]:
    with st.container(border=True):
        st.markdown("**🔄 职业转型对比**")
        st.markdown("分析从A行业转型到B行业的可行性")
        if current_industry and target_industry and st.button("开始对比分析", key="btn_compare"):
            with st.spinner("正在分析职业转型路径..."):
                try:
                    result = analyze_career_transition(current_industry, target_industry, user_role)
                    st.session_state.messages.append({"role": "assistant", "content": result})
                    st.rerun()
                except Exception as e:
                    st.error(f"分析失败: {e}")

with quick_cols[1]:
    with st.container(border=True):
        st.markdown("**📈 行业深度研报**")
        st.markdown("生成目标行业的完整周期分析报告")
        if target_industry and st.button("生成研报", key="btn_report"):
            report_prompt = f"请为{target_industry}生成一份完整的周期分析研报，包括：1)产业周期定位 2)政策环境分析 3)四种典型组合研判 4)职业机会与风险 5)具体行动建议"
            st.session_state.messages.append({"role": "user", "content": report_prompt})
            st.rerun()

with quick_cols[2]:
    with st.container(border=True):
        st.markdown("**🎯 技能迁移分析**")
        st.markdown("分析跨行业技能迁移的可行性")
        if current_industry and target_industry and st.button("分析技能迁移", key="btn_skills"):
            skills_prompt = f"我目前从事{current_industry}，想转型到{target_industry}。请分析：1)两个行业之间的技能共通性 2)需要补充的新技能 3)转型路径建议 4)时间规划"
            st.session_state.messages.append({"role": "user", "content": skills_prompt})
            st.rerun()
