import streamlit as st
from utils.llm_engine import render_api_key_input, render_privacy_notice

# ==========================================
# 全局页面配置
# ==========================================
st.set_page_config(
    page_title="周期共振职业规划系统",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 初始化全局会话状态
# ==========================================
if 'target_industry' not in st.session_state:
    st.session_state['target_industry'] = ""
if 'user_profile' not in st.session_state:
    st.session_state['user_profile'] = {
        'identity': None,  # 应届生/职场转型者/高管跨界
        'current_industry': '',
        'experience_years': 0,
        'risk_preference': '稳健'
    }
if 'daily_usage' not in st.session_state:
    st.session_state['daily_usage'] = 0

# ==========================================
# 侧边栏：API配置 + 隐私声明 + 使用限制
# ==========================================
render_api_key_input()
render_privacy_notice()

# ==========================================
# 主页面标题与介绍
# ==========================================
st.title("🧬 周期共振职业规划系统")
st.markdown("基于马江博'政策周期与产业周期'二元分析框架的智能职业规划工具")

# ==========================================
# 🚀 使用流程（突出显示）
# ==========================================
st.markdown("---")
st.markdown("## 🚀 使用流程（5步完成职业规划）")

flow_cols = st.columns(5)

with flow_cols[0]:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center;">
            <h3>① 📄</h3>
            <h4>简历诊断</h4>
            <p style="font-size: 14px; color: #666;">粘贴简历<br/>识别行业风险</p>
        </div>
        """, unsafe_allow_html=True)

with flow_cols[1]:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center;">
            <h3>② 📊</h3>
            <h4>周期实验室</h4>
            <p style="font-size: 14px; color: #666;">查看行业<br/>周期全景图</p>
        </div>
        """, unsafe_allow_html=True)

with flow_cols[2]:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center;">
            <h3>③ 🤖</h3>
            <h4>AI规划官</h4>
            <p style="font-size: 14px; color: #666;">获取AI<br/>职业规划建议</p>
        </div>
        """, unsafe_allow_html=True)

with flow_cols[3]:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center;">
            <h3>④ 🛤️</h3>
            <h4>路径推演</h4>
            <p style="font-size: 14px; color: #666;">模拟不同<br/>选择的发展</p>
        </div>
        """, unsafe_allow_html=True)

with flow_cols[4]:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center;">
            <h3>⑤ 📡</h3>
            <h4>数据哨兵</h4>
            <p style="font-size: 14px; color: #666;">追踪目标<br/>行业拐点</p>
        </div>
        """, unsafe_allow_html=True)

# 快速开始按钮
st.markdown("<br>", unsafe_allow_html=True)
start_col1, start_col2, start_col3 = st.columns([1, 2, 1])
with start_col2:
    if st.button("🚀 立即开始诊断（第一步）", use_container_width=True, type="primary"):
        st.switch_page("pages/01_📄_简历诊断中心.py")

st.markdown("---")

# ==========================================
# 受众细分：身份选择引导
# ==========================================
st.markdown("### 👤 请选择您的身份类型（可选）")

identity_cols = st.columns(3)

with identity_cols[0]:
    with st.container(border=True):
        st.markdown("#### 🎓 应届生/在校生")
        st.markdown("选专业 · 择业指导 · 入行规划")
        if st.button("选择此身份", key="btn_fresh_grad", use_container_width=True):
            st.session_state['user_profile']['identity'] = '应届生'
            st.session_state['user_profile']['risk_preference'] = '积极'
            st.toast("已选择：应届生/在校生身份")
            st.rerun()

with identity_cols[1]:
    with st.container(border=True):
        st.markdown("#### 💼 职场转型者")
        st.markdown("防内卷 · 跨行转型 · 技能迁移")
        if st.button("选择此身份", key="btn_career_change", use_container_width=True):
            st.session_state['user_profile']['identity'] = '职场转型者'
            st.session_state['user_profile']['risk_preference'] = '稳健'
            st.toast("已选择：职场转型者身份")
            st.rerun()

with identity_cols[2]:
    with st.container(border=True):
        st.markdown("#### 🎯 高管/跨界人才")
        st.markdown("战略视野 · 跨界机会 · 资源对接")
        if st.button("选择此身份", key="btn_executive", use_container_width=True):
            st.session_state['user_profile']['identity'] = '高管跨界'
            st.session_state['user_profile']['risk_preference'] = '稳健'
            st.toast("已选择：高管/跨界人才身份")
            st.rerun()

# 显示当前身份
if st.session_state['user_profile']['identity']:
    st.success(f"当前身份：**{st.session_state['user_profile']['identity']}** | 风险偏好：**{st.session_state['user_profile']['risk_preference']}**")

st.markdown("---")

# ==========================================
# 系统功能介绍
# ==========================================
st.markdown("### 🚀 系统功能模块（按使用顺序）")

feature_cols = st.columns(5)

with feature_cols[0]:
    with st.container(border=True):
        st.markdown("**📄 简历诊断**")
        st.markdown("① 了解自己的行业风险")
        if st.button("开始诊断", key="goto_resume", use_container_width=True):
            st.switch_page("pages/01_📄_简历诊断中心.py")

with feature_cols[1]:
    with st.container(border=True):
        st.markdown("**📊 周期实验室**")
        st.markdown("② 查看行业周期全景")
        if st.button("进入实验室", key="goto_lab", use_container_width=True):
            st.switch_page("pages/02_📊_周期实验室.py")

with feature_cols[2]:
    with st.container(border=True):
        st.markdown("**🤖 AI协同规划官**")
        st.markdown("③ 获取AI规划建议")
        if st.button("开始规划", key="goto_ai", use_container_width=True):
            st.switch_page("pages/03_🤖_AI协同规划官.py")

with feature_cols[3]:
    with st.container(border=True):
        st.markdown("**🛤️ 职业路径推演**")
        st.markdown("④ 模拟不同选择")
        if st.button("开始推演", key="goto_sim", use_container_width=True):
            st.switch_page("pages/04_🛤️_职业路径推演.py")

with feature_cols[4]:
    with st.container(border=True):
        st.markdown("**📡 数据哨兵**")
        st.markdown("⑤ 追踪目标行业")
        if st.button("开始追踪", key="goto_sentinel", use_container_width=True):
            st.switch_page("pages/05_📡_数据哨兵服务.py")

st.markdown("---")

# ==========================================
# 热门行业快速分析
# ==========================================
st.markdown("### 🔥 热门行业快速分析")

hot_industries = [
    ("人工智能", "成长期", "高成长"),
    ("新能源汽车", "成长期", "高成长"),
    ("半导体", "成长期", "高成长"),
    ("银发经济", "初创期", "高成长"),
    ("生物医药", "成熟期", "平稳"),
    ("低空经济", "初创期", "高成长"),
    ("储能", "成长期", "高成长"),
    ("光伏", "调整期", "承压")
]

# 根据用户身份调整推荐策略
def get_recommendation_score(industry, stage, sentiment, identity):
    """根据用户身份计算推荐分数"""
    if not identity:
        return 0
    
    stage_scores = {
        '应届生': {'初创期': 3, '成长期': 5, '成熟期': 2, '调整期': 1},
        '职场转型者': {'初创期': 2, '成长期': 5, '成熟期': 3, '调整期': 2},
        '高管跨界': {'初创期': 4, '成长期': 4, '成熟期': 3, '调整期': 1}
    }
    
    return stage_scores.get(identity, {}).get(stage, 3)

# 按推荐度排序
identity = st.session_state['user_profile']['identity']
if identity:
    hot_industries_sorted = sorted(
        hot_industries,
        key=lambda x: get_recommendation_score(x[0], x[1], x[2], identity),
        reverse=True
    )
else:
    hot_industries_sorted = hot_industries

# 显示热门行业按钮
industry_cols = st.columns(4)
for i, (industry, stage, sentiment) in enumerate(hot_industries_sorted):
    with industry_cols[i % 4]:
        # 根据周期阶段设置颜色
        stage_emoji = {"初创期": "🌱", "成长期": "🚀", "成熟期": "🏭", "调整期": "⚠️"}.get(stage, "📊")
        if st.button(f"{stage_emoji} {industry}", key=f"hot_{industry}"):
            st.session_state['target_industry'] = industry
            st.switch_page("pages/03_🤖_AI协同规划官.py")

# ==========================================
# 详细使用说明
# ==========================================
st.markdown("---")
st.subheader("📖 详细使用说明")

with st.expander("点击查看完整使用指南", expanded=True):
    st.markdown("""
    ### 📋 完整使用流程
    
    #### Step 1: 配置API Key
    在左侧边栏输入您的 DeepSeek API Key（每位用户每日限20次使用）
    
    #### Step 2: 简历诊断（了解现状）
    - 进入「简历诊断中心」
    - 粘贴您的简历内容或选择所在行业
    - AI自动识别您的行业周期阶段
    - **红色预警**：如果检测到高风险行业，会提示转型建议
    
    #### Step 3: 周期实验室（查看全景）
    - 进入「周期实验室」
    - 查看近300个细分领域的周期分布
    - 使用象限图找到"红利交叠期"行业
    - 搜索您感兴趣的行业
    
    #### Step 4: AI协同规划官（获取建议）
    - 进入「AI协同规划官」
    - 与AI对话，获取个性化职业规划
    - 基于RAG知识库，所有建议有理有据
    - 可以询问：转型建议、技能准备、时机判断等
    
    #### Step 5: 职业路径推演（模拟决策）
    - 进入「职业路径推演」
    - 选择推演模式：历史回溯 / 未来推演 / 双轨对比
    - 模拟不同选择的发展路径
    - 量化风险收益比
    
    #### Step 6: 数据哨兵服务（追踪执行）
    - 进入「数据哨兵服务」
    - 添加目标行业到追踪列表
    - 监控7大拐点指标（演示数据）
    - 辅助判断入场时机
    
    ---
    
    ### 💡 使用技巧
    
    1. **新用户建议**：从「简历诊断」开始，先了解自己当前所处行业的风险
    2. **转型决策**：使用「路径推演」对比不同选择，再做决策
    3. **持续关注**：定期查看「数据哨兵」，追踪目标行业动态
    4. **深度咨询**：有任何问题都可以问「AI协同规划官」
    """)

# ==========================================
# 理论框架简介
# ==========================================
with st.expander("📚 关于周期共振理论"):
    st.markdown("""
    **马江博周期共振理论核心框架：**
    
    **产业周期四阶段：**
    - 🌱 **初创期**：技术突破，市场教育阶段
    - 🚀 **成长期**：渗透率快速提升，红利释放期
    - 🏭 **成熟期**：增速放缓，竞争格局稳定
    - ⚠️ **调整衰退期**：产能过剩，行业洗牌
    
    **政策周期四阶段：**
    - 📋 **规划引导期**：政策出台，方向明确
    - 🎯 **资源聚焦期**：资金涌入，补贴到位
    - 🔄 **调整退出期**：政策收紧，优胜劣汰
    - 📉 **政策压降期**：明确限制，产能出清
    
    **四种典型组合：**
    1. 🔴 **高风险押宝期** (初创+引导)：高风险高回报，适合激进型
    2. 🟢 **红利交叠期** (成长+聚焦)：最佳入场时机，黄金窗口
    3. 🟡 **红利退坡期** (成熟+退出)：需做防御性打算
    4. 🔴 **红利消失期** (衰退+压降)：建议尽早转型
    """)

# ==========================================
# 页脚
# ==========================================
st.divider()
footer_cols = st.columns([3, 1])
with footer_cols[0]:
    st.caption("基于马江博周期共振理论构建 | 仅供职业规划研究参考")
with footer_cols[1]:
    st.caption(f"今日使用次数: {st.session_state['daily_usage']} / 20")
