import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random
import sys
import os

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_engine import render_api_key_input, render_privacy_notice
from utils.visualization import create_sentinel_radar

st.set_page_config(page_title="数据哨兵服务", page_icon="📡", layout="wide")
st.title("📡 数据哨兵服务：新产业成长期拐点追踪")
st.markdown("基于马江博**'新产业进入成长期拐点判断7大清单'**，持续追踪关注行业的关键指标，辅助判断入场时机。")

# ==========================================
# 数据说明提示
# ==========================================
st.warning("""📌 **当前为演示版本**

本页面展示的指标数据为**模拟演示数据**，用于展示系统功能和交互效果。

**当前状态**：
- ✅ 7大拐点指标框架已搭建
- ✅ 可视化组件已完善
- ⏳ 实时数据接入（开发中）

**未来计划**：
我们将根据用户反馈，逐步接入真实数据源：
- 行业财务数据（毛利率、营收等）
- 政策文件数据库
- 市场渗透率统计
- 资本开支数据

💬 **欢迎反馈**：如果您希望优先支持某个行业的真实数据追踪，请通过AI协同规划官页面提出建议！
""")

# 渲染 API Key 和隐私声明
render_api_key_input()
render_privacy_notice()

# ==========================================
# 7大拐点指标定义
# ==========================================
SENTINEL_INDICATORS = [
    {"id": 1, "name": "技术成本下降", "description": "技术成本在2-3年内下降50%以上", "weight": 15},
    {"id": 2, "name": "龙头盈利", "description": "龙头企业毛利率超过20%，净利润转正", "weight": 15},
    {"id": 3, "name": "政策明确", "description": "政策文件中明确了财政资金规模和具体补贴标准", "weight": 15},
    {"id": 4, "name": "渗透率区间", "description": "市场渗透率在5%-30%之间", "weight": 15},
    {"id": 5, "name": "资本开支", "description": "行业资本开支增速维持30%以上", "weight": 15},
    {"id": 6, "name": "营收规模", "description": "出现了3家以上年营收超过10亿的企业", "weight": 15},
    {"id": 7, "name": "产业链配套", "description": "产业链上下游配套开始完善", "weight": 10},
]

# ==========================================
# 初始化关注列表
# ==========================================
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["低空经济", "人形机器人"]

# 检查是否有从其他页面传递的行业
if 'target_industry' in st.session_state and st.session_state['target_industry']:
    new_industry = st.session_state['target_industry']
    if new_industry not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_industry)
        st.toast(f"✅ 已将 {new_industry} 自动加入追踪列表")
    # 清除传递的参数
    st.session_state['target_industry'] = ""

# ==========================================
# 模拟数据生成函数
# ==========================================
def get_sentinel_data(industry_name: str) -> dict:
    """
    为特定行业生成模拟的7大指标数据
    
    Args:
        industry_name: 行业名称
        
    Returns:
        指标数据字典
    """
    # 基于行业名称生成一个固定种子，确保同一行业数据一致
    seed = sum(ord(c) for c in industry_name)
    random.seed(seed)
    
    # 根据行业特性调整基准分数
    high_growth_industries = ["人工智能", "低空经济", "人形机器人", "脑机接口", "量子计算",
                               "储能", "新能源汽车", "半导体", "氢能源"]
    
    if any(hg in industry_name for hg in high_growth_industries):
        base_score = random.uniform(0.6, 0.9)
    else:
        base_score = random.uniform(0.3, 0.7)
    
    indicators = []
    achieved_count = 0
    
    for indicator in SENTINEL_INDICATORS:
        # 根据权重和随机因素确定是否达标
        threshold = 1 - (indicator['weight'] / 100) * base_score
        status = random.random() > threshold
        
        if status:
            achieved_count += 1
        
        indicators.append({
            **indicator,
            "status": status,
            "progress": random.uniform(70, 100) if status else random.uniform(20, 70)
        })
    
    readiness_score = int((achieved_count / 7) * 100)
    
    # 生成趋势数据（近12个月）
    months = []
    scores = []
    for i in range(12):
        month_score = readiness_score + random.randint(-10, 10)
        month_score = max(0, min(100, month_score))
        months.append(f"{i+1}月")
        scores.append(month_score)
    
    return {
        "industry": industry_name,
        "indicators": indicators,
        "readiness_score": readiness_score,
        "achieved_count": achieved_count,
        "trend_months": months,
        "trend_scores": scores,
        "assessment": get_assessment(readiness_score)
    }


def get_assessment(score: int) -> dict:
    """根据就绪分数返回评估结果"""
    if score >= 80:
        return {
            "level": "🟢 强烈推荐",
            "color": "green",
            "message": "该行业已进入红利交叠期，是最佳入场时机！",
            "action": "建议果断入场，优先选择头部企业"
        }
    elif score >= 60:
        return {
            "level": "🟡 值得关注",
            "color": "orange",
            "message": "该行业正在快速发展中，多数指标已达标。",
            "action": "可以开始关注和准备，择机入场"
        }
    elif score >= 40:
        return {
            "level": "🟠 观察等待",
            "color": "orange",
            "message": "该行业尚处于早期阶段，部分指标未达标。",
            "action": "建议持续关注，等待更明确的信号"
        }
    else:
        return {
            "level": "🔴 高风险",
            "color": "red",
            "message": "该行业尚未进入成长期，存在较大不确定性。",
            "action": "建议谨慎观望，不宜贸然进入"
        }


# ==========================================
# 侧边栏：管理控制台
# ==========================================
with st.sidebar:
    st.header("📡 哨兵控制台")
    st.markdown("添加需要持续追踪的细分行业")
    
    with st.form("add_industry_form"):
        custom_industry = st.text_input("行业名称", placeholder="例如：固态电池")
        submitted = st.form_submit_button("➕ 添加到追踪列表")
        if submitted and custom_industry:
            if custom_industry not in st.session_state.watchlist:
                st.session_state.watchlist.append(custom_industry)
                st.success(f"已添加：{custom_industry}")
                st.rerun()
            else:
                st.warning("该行业已在追踪列表中")
    
    st.markdown("---")
    
    # 显示当前追踪列表
    st.markdown("### 📋 当前追踪列表")
    for i, industry in enumerate(st.session_state.watchlist):
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(f"{i+1}. {industry}")
        with cols[1]:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.watchlist.pop(i)
                st.rerun()

# ==========================================
# 主界面：行业追踪卡片
# ==========================================
if not st.session_state.watchlist:
    st.info("📭 追踪列表为空。请在左侧边栏添加需要追踪的行业。")
else:
    st.markdown(f"### 🔍 正在追踪 **{len(st.session_state.watchlist)}** 个行业")
    
    # 动态生成追踪卡片
    cols = st.columns(2)
    
    for i, industry in enumerate(st.session_state.watchlist):
        data = get_sentinel_data(industry)
        
        with cols[i % 2]:
            with st.container(border=True):
                # 标题和总体评分
                header_cols = st.columns([2, 1])
                with header_cols[0]:
                    st.subheader(f"📊 {industry}")
                with header_cols[1]:
                    st.markdown(f"<h2 style='text-align: right; color: {data['assessment']['color']};'>{data['readiness_score']}%</h2>", 
                               unsafe_allow_html=True)
                
                # 评估等级
                st.markdown(f"**{data['assessment']['level']}**")
                st.markdown(f"*{data['assessment']['message']}*")
                
                # 进度条
                st.progress(data['readiness_score'] / 100)
                st.caption(f"已达标指标：{data['achieved_count']} / 7")
                
                # 雷达图
                radar_fig = create_sentinel_radar(data['indicators'])
                st.plotly_chart(radar_fig, use_container_width=True, key=f"radar_{i}")
                
                # 详细指标展开
                with st.expander("📋 查看7大指标详情"):
                    for ind in data['indicators']:
                        icon = "✅" if ind["status"] else "⬜"
                        progress_color = "green" if ind["status"] else "gray"
                        st.markdown(f"{icon} **{ind['name']}**：{ind['description']}")
                        st.progress(ind['progress'] / 100)
                
                # 趋势图
                with st.expander("📈 近12个月趋势"):
                    trend_fig = go.Figure()
                    trend_fig.add_trace(go.Scatter(
                        x=data['trend_months'],
                        y=data['trend_scores'],
                        mode='lines+markers',
                        line=dict(color='teal', width=2),
                        marker=dict(size=8)
                    ))
                    trend_fig.add_hline(y=80, line_dash="dash", line_color="green", 
                                       annotation_text="推荐入场线")
                    trend_fig.add_hline(y=60, line_dash="dash", line_color="orange",
                                       annotation_text="关注线")
                    trend_fig.update_layout(
                        height=250,
                        margin=dict(l=20, r=20, t=20, b=20),
                        showlegend=False,
                        xaxis_title="月份",
                        yaxis_title="就绪度评分"
                    )
                    st.plotly_chart(trend_fig, use_container_width=True, key=f"trend_{i}")
                
                # 行动建议
                st.markdown("---")
                st.markdown(f"**💡 行动建议**：{data['assessment']['action']}")
                
                # 操作按钮
                btn_cols = st.columns(2)
                with btn_cols[0]:
                    if st.button(f"🤖 AI深度分析", key=f"ai_{i}"):
                        st.session_state['target_industry'] = industry
                        st.switch_page("pages/03_🤖_AI协同规划官.py")
                with btn_cols[1]:
                    if st.button(f"🛤️ 路径推演", key=f"path_{i}"):
                        st.session_state['target_industry'] = industry
                        st.switch_page("pages/04_🛤️_职业路径推演.py")

# ==========================================
# 7大指标说明
# ==========================================
st.markdown("---")
with st.expander("📚 7大拐点指标说明"):
    st.markdown("""
    ### 新产业进入成长期拐点判断清单
    
    根据马江博周期共振理论，判断一个新产业是否进入成长期，需要综合评估以下7大指标：
    
    | 序号 | 指标名称 | 达标标准 | 重要性 |
    |-----|---------|---------|--------|
    | 1 | 技术成本 | 2-3年内下降50%以上 | ⭐⭐⭐⭐⭐ |
    | 2 | 龙头盈利 | 毛利率>20%，净利润转正 | ⭐⭐⭐⭐⭐ |
    | 3 | 政策明确 | 财政资金和补贴标准明确 | ⭐⭐⭐⭐⭐ |
    | 4 | 渗透率 | 处于5%-30%区间 | ⭐⭐⭐⭐ |
    | 5 | 资本开支 | 行业增速维持30%以上 | ⭐⭐⭐⭐ |
    | 6 | 营收规模 | 10亿+营收企业>3家 | ⭐⭐⭐ |
    | 7 | 产业链 | 上下游配套完善 | ⭐⭐⭐ |
    
    **评分标准**：
    - 80%+：🟢 红利交叠期，最佳入场时机
    - 60-79%：🟡 快速发展期，值得关注
    - 40-59%：🟠 观察等待期
    - <40%：🔴 高风险期，谨慎入场
    """)

# ==========================================
# 页面底部
# ==========================================
st.markdown("---")
st.caption("📊 数据说明：本页面展示的指标数据为模拟演示数据，仅用于功能演示。真实数据源接入开发中，欢迎通过AI协同规划官页面提出反馈建议！")
