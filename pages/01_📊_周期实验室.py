import streamlit as st
import plotly.express as px
import os
import sys

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_processor import load_industry_data, filter_industry_data

st.set_page_config(page_title="周期实验室", page_icon="📊", layout="wide")
st.title("📊 周期实验室：细分领域全景图")
st.markdown("基于马江博的二元框架，这里汇集了近 300 个细分行业的周期研判数据。通过全局视角，寻找你的“黄金共振”赛道。")

# ==========================================
# 1. 真实数据加载
# ==========================================
# 请确保 data 文件夹下有 细分领域行业周期研判表.csv 文件
data_path = "data/细分领域行业周期研判表.csv"
df = load_industry_data(data_path)

# ==========================================
# 2. 侧边栏：多维度交互筛选器
# ==========================================
st.sidebar.header("🔍 数据过滤器")

# 获取周期和景气度的唯一值，供用户多选
all_cycles = df['当前周期阶段'].unique().tolist()
all_sentiments = df['未来1-3年景气度'].unique().tolist()

selected_stage = st.sidebar.multiselect("📍 选择产业周期阶段：", options=all_cycles, default=all_cycles)
selected_sentiment = st.sidebar.multiselect("📈 选择未来1-3年景气度：", options=all_sentiments, default=all_sentiments)
search_kw = st.sidebar.text_input("🔑 关键词检索（行业名称或评价）", "")

# 调用清洗与过滤函数
filtered_df = filter_industry_data(df, selected_stages=selected_stage, selected_sentiments=selected_sentiment, search_query=search_kw)

# ==========================================
# 3. 数据可视化大屏 (HUD)
# ==========================================
st.markdown("### 📈 赛道景气度分布")

if not filtered_df.empty:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 统计核心指标
        st.metric(label="当前筛选条件下的行业总数", value=f"{len(filtered_df)} 个")
        
        # 绘制饼图：景气度占比
        sentiment_counts = filtered_df['未来1-3年景气度'].value_counts().reset_index()
        sentiment_counts.columns = ['景气度', '数量']
        fig_pie = px.pie(sentiment_counts, names='景气度', values='数量', hole=0.4, 
                         title="未来1-3年景气度占比",
                         color_discrete_sequence=px.colors.sequential.Teal)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col2:
        # 绘制柱状图：各个周期的行业数量
        cycle_counts = filtered_df['当前周期阶段'].value_counts().reset_index()
        cycle_counts.columns = ['周期阶段', '数量']
        fig_bar = px.bar(cycle_counts, x='周期阶段', y='数量', text='数量',
                         title="不同周期阶段的行业分布",
                         color='周期阶段', template="plotly_white")
        fig_bar.update_traces(textposition='outside')
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("⚠️ 在当前筛选条件下没有找到匹配的行业，请调整左侧过滤器。")

# ==========================================
# 4. 详细数据表格与 AI 联动
# ==========================================
st.markdown("### 📋 详细研判数据")
# 展示过滤后的数据表
st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 💡 深度研判推演")
st.info("发现感兴趣的赛道？请前往 AI 协同规划官模块进行深度分析。")