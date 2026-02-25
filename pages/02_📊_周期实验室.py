import streamlit as st
import plotly.express as px
import os
import sys

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_processor import load_industry_data, filter_industry_data, get_industry_by_name
from utils.visualization import (
    create_cycle_quadrant_chart, 
    create_cycle_distribution_chart,
    create_sentiment_pie_chart
)

st.set_page_config(page_title="周期实验室", page_icon="📊", layout="wide")

st.title("📊 周期实验室：细分领域全景图谱")
st.markdown("基于产业周期与政策周期的二元框架，可视化呈现近300个细分领域的周期定位。通过全局视角，寻找您的'红利交叠期'机会。")

# ==========================================
# 1. 加载数据集
# ==========================================
data_path = "data/细分领域行业周期研判表.csv"
df = load_industry_data(data_path)

# ==========================================
# 2. 侧边栏多维度筛选
# ==========================================
st.sidebar.header("🔍 数据过滤器")

# 获取周期和景气度的唯一值
all_cycles = df['当前周期阶段'].unique().tolist()
all_sentiments = df['未来1-3年景气度'].unique().tolist()

selected_stage = st.sidebar.multiselect("📈 选择产业周期阶段：", options=all_cycles, default=all_cycles)
selected_sentiment = st.sidebar.multiselect("📊 选择未来1-3年景气度：", options=all_sentiments, default=all_sentiments)
search_kw = st.sidebar.text_input("🔎 关键词搜索（行业名称或评价）：", "")

# 应用筛选
filtered_df = filter_industry_data(df, selected_stages=selected_stage, selected_sentiments=selected_sentiment, search_query=search_kw)

# 高亮选择
highlight_industry = st.sidebar.text_input("✨ 高亮显示特定行业：", "")

# ==========================================
# 3. 核心指标展示 (HUD)
# ==========================================
st.markdown("### 📈 核心指标概览")

metric_cols = st.columns(4)

with metric_cols[0]:
    total_count = len(filtered_df)
    st.metric(label="当前筛选条件下行业总数", value=f"{total_count} 个")

with metric_cols[1]:
    growth_count = len(filtered_df[filtered_df['当前周期阶段'] == '成长期'])
    st.metric(label="成长期行业数量", value=f"{growth_count} 个", 
              delta=f"{growth_count/total_count*100:.1f}%" if total_count > 0 else "0%")

with metric_cols[2]:
    high_growth = len(filtered_df[filtered_df['未来1-3年景气度'].str.contains('高成长', na=False)])
    st.metric(label="高景气度行业", value=f"{high_growth} 个",
              delta=f"{high_growth/total_count*100:.1f}%" if total_count > 0 else "0%")

with metric_cols[3]:
    risk_count = len(filtered_df[filtered_df['当前周期阶段'].isin(['调整期', '衰退期'])])
    st.metric(label="风险期行业", value=f"{risk_count} 个",
              delta=f"{risk_count/total_count*100:.1f}%" if total_count > 0 else "0%",
              delta_color="inverse")

st.markdown("---")

# ==========================================
# 4. 周期象限图（核心可视化）
# ==========================================
st.markdown("### 🎯 周期共振象限图")
st.info("📌 **解读说明**：横轴为政策周期阶段，纵轴为产业周期阶段。**第一象限（右上）** 为'红利交叠期'（成长期+聚焦政策），是最佳入场时机；**第四象限（右下）** 为'红利退坡期'，需谨慎。")

quadrant_fig = create_cycle_quadrant_chart(filtered_df, 
                                            highlight_industry if highlight_industry else None)
if quadrant_fig:
    st.plotly_chart(quadrant_fig, use_container_width=True)
else:
    st.warning("暂无可视化数据")

st.markdown("---")

# ==========================================
# 5. 数据分布可视化
# ==========================================
st.markdown("### 📊 数据分布统计")

dist_cols = st.columns(2)

with dist_cols[0]:
    # 周期阶段分布柱状图
    cycle_fig = create_cycle_distribution_chart(filtered_df)
    if cycle_fig:
        st.plotly_chart(cycle_fig, use_container_width=True)

with dist_cols[1]:
    # 景气度分布饼图
    sentiment_fig = create_sentiment_pie_chart(filtered_df)
    if sentiment_fig:
        st.plotly_chart(sentiment_fig, use_container_width=True)

st.markdown("---")

# ==========================================
# 6. 详细数据表格与AI分析入口
# ==========================================
st.markdown("### 🔍 详细行业数据")

# 显示筛选后的数据表
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# 快捷分析按钮
st.markdown("---")
st.markdown("### 🚀 快捷分析")

if highlight_industry:
    st.success(f"已选择行业：**{highlight_industry}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🤖 获取AI职业规划分析", use_container_width=True):
            st.session_state['target_industry'] = highlight_industry
            st.switch_page("pages/03_🤖_AI协同规划官.py")
    with col2:
        if st.button("🛤️ 进行职业路径推演", use_container_width=True):
            st.session_state['target_industry'] = highlight_industry
            st.switch_page("pages/04_🛤️_职业路径推演.py")
else:
    st.info("💡 在左侧边栏输入行业名称并点击回车，可高亮显示该行业，并启用快捷分析功能")

# ==========================================
# 7. 周期理论速查
# ==========================================
with st.expander("📚 周期理论速查表"):
    st.markdown("""
    | 组合类型 | 产业周期 | 政策周期 | 风险等级 | 策略建议 |
    |---------|---------|---------|---------|---------|
    | 🟢 **红利交叠期** | 成长期 | 聚焦期 | 最佳时机 | 果断入场，积累核心技能 |
    | 🔴 **高风险押宝期** | 初创期 | 引导期 | 高风险 | 小步试错，关注技术突破 |
    | 🟡 **红利退坡期** | 成熟期 | 退出期 | 中风险 | 防御性规划，储备能力 |
    | 🔴 **红利消失期** | 衰退期 | 压降期 | 高危 | 立即启动转型 |
    
    **判断标准：**
    - **成长期拐点7大指标**：技术成本下降50% | 龙头毛利>20% | 政策补贴明确 | 渗透率5-30% | 资本开支增速>30% | 10亿营收企业>3家 | 产业链配套完善
    """)

# ==========================================
# 8. 风险提示
# ==========================================
if risk_count > 0:
    with st.expander("⚠️ 当前筛选下的风险行业预警", expanded=False):
        risk_df = filtered_df[filtered_df['当前周期阶段'].isin(['调整期', '衰退期'])]
        st.warning(f"发现 **{len(risk_df)}** 个处于调整期或衰退期的行业：")
        for _, row in risk_df.iterrows():
            st.markdown(f"- **{row['行业名称']}** ({row['当前周期阶段']}) - {row['评价']}")
