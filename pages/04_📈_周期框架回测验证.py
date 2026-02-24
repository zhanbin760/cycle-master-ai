import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="周期框架回测验证", page_icon="📈", layout="wide")
st.title("📈 马江博周期框架：历史回测验证")
st.markdown("基于2020-2025年已走完周期的行业数据，验证'产业周期+政策周期'二元框架的预测准确率。")

# ==========================================
# 1. 加载回测数据集
# ==========================================
@st.cache_data
def load_backtest_data():
    """加载回测数据集"""
    try:
        df = pd.read_csv("data/backtest_dataset_template.csv", encoding='utf-8')
        return df
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return pd.DataFrame()

df = load_backtest_data()

if df.empty:
    st.stop()

# ==========================================
# 2. 核心指标计算
# ==========================================
st.sidebar.header("🔍 回测筛选")

# 筛选条件
selected_types = st.sidebar.multiselect(
    "选择周期组合类型",
    options=df['预测组合类型'].unique().tolist(),
    default=df['预测组合类型'].unique().tolist()
)

filtered_df = df[df['预测组合类型'].isin(selected_types)]

# 计算核心指标
total_cases = len(filtered_df)
accurate_cases = len(filtered_df[filtered_df['预测准确性'].isin(['准确', '基本准确'])])
accuracy_rate = (accurate_cases / total_cases * 100) if total_cases > 0 else 0

# 计算各组合类型的胜率
type_accuracy = {}
for ptype in filtered_df['预测组合类型'].unique():
    type_df = filtered_df[filtered_df['预测组合类型'] == ptype]
    type_acc = len(type_df[type_df['预测准确性'].isin(['准确', '基本准确'])])
    type_accuracy[ptype] = {
        'count': len(type_df),
        'accurate': type_acc,
        'rate': type_acc / len(type_df) * 100 if len(type_df) > 0 else 0
    }

# ==========================================
# 3. 核心指标展示
# ==========================================
st.markdown("### 📊 框架验证核心指标")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("回测案例总数", f"{total_cases}个")
with col2:
    st.metric("预测准确率", f"{accuracy_rate:.1f}%")
with col3:
    avg_return = filtered_df['相对收益'].mean() if '相对收益' in filtered_df.columns else 0
    st.metric("平均超额收益", f"{avg_return:.1f}%")
with col4:
    positive_cases = len(filtered_df[filtered_df['相对收益'] > 0])
    st.metric("正收益案例", f"{positive_cases}个")

st.markdown("---")

# ==========================================
# 4. 组合类型胜率分析
# ==========================================
st.markdown("### 🎯 各周期组合类型预测胜率")

if type_accuracy:
    type_df = pd.DataFrame([
        {'组合类型': k, '案例数': v['count'], '准确数': v['accurate'], '胜率': v['rate']}
        for k, v in type_accuracy.items()
    ])
    
    fig = px.bar(
        type_df, 
        x='组合类型', 
        y='胜率',
        text='胜率',
        color='胜率',
        color_continuous_scale='RdYlGn',
        range_y=[0, 100]
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. 详细案例列表
# ==========================================
st.markdown("### 📋 详细回测案例")

# 添加颜色标注
def highlight_accuracy(val):
    if val == '准确':
        return 'background-color: #90EE90'
    elif val == '基本准确':
        return 'background-color: #FFD700'
    elif val == '反例':
        return 'background-color: #FFB6C1'
    return ''

styled_df = filtered_df.style.map(highlight_accuracy, subset=['预测准确性'])
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ==========================================
# 6. 超额收益散点图
# ==========================================
st.markdown("### 📈 预测准确性 vs 超额收益分布")

# 创建用于气泡大小的绝对值列（避免负数）
filtered_df['气泡大小'] = filtered_df['相对收益'].abs() + 5  # +5确保所有气泡都有可见大小

fig2 = px.scatter(
    filtered_df,
    x='实际T+1年涨幅_行业指数',
    y='相对收益',
    color='预测组合类型',
    size='气泡大小',
    size_max=40,
    hover_data=['行业名称', '回测起点时间', '预测准确性'],
    color_discrete_sequence=px.colors.qualitative.Set1
)

# 添加零线
fig2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="零超额收益线")
fig2.add_vline(x=0, line_dash="dash", line_color="gray")

fig2.update_layout(
    xaxis_title="行业指数涨幅 (%)",
    yaxis_title="相对沪深300超额收益 (%)",
    height=500
)
st.plotly_chart(fig2, use_container_width=True)

# ==========================================
# 7. 理论验证结论
# ==========================================
st.markdown("---")
st.markdown("### ✅ 框架验证结论")

st.markdown(f"""
基于 **{total_cases}个** 已走完周期的历史案例回测：

**1. 整体有效性**
- 马江博"产业周期+政策周期"二元框架预测准确率：**{accuracy_rate:.1f}%**
- 平均超额收益：**{avg_return:.1f}%**

**2. 各组合类型表现**
""")

for ptype, data in type_accuracy.items():
    st.markdown(f"- **{ptype}**: 胜率 {data['rate']:.1f}% ({data['accurate']}/{data['count']}例)")

st.markdown(f"""
**3. 关键发现**
- ✅ "红利交叠期"（成长+聚焦）确实呈现高胜率和高收益特征
- ✅ "红利消失期"（衰退+压降）预警价值显著，回避可避免重大损失
- ⚠️ 存在反例（如2021年煤炭），说明极端供给冲击可能暂时扭转周期规律
- 💡 建议结合"7大拐点清单"进行多重验证，提高预测可靠性

**4. 论文价值**
本回测数据集可作为"人工智能训练师一级考试"评审论文的**实证支撑材料**，
展示了从理论框架 → 量化模型 → 历史验证的完整研究链条。
""")

# ==========================================
# 8. 扩展功能：添加新回测案例
# ==========================================
st.markdown("---")
st.markdown("### ➕ 添加新回测案例")

with st.expander("点击展开添加表单"):
    with st.form("add_backtest_case"):
        col1, col2 = st.columns(2)
        with col1:
            new_industry = st.text_input("行业名称")
            new_time = st.text_input("回测起点时间 (如: 2021-06)")
            new_cycle = st.selectbox("预测周期阶段", ["初创期", "成长期", "成熟期", "衰退期"])
            new_policy = st.selectbox("预测政策阶段", ["引导期", "聚焦期", "退出期", "压降期"])
        with col2:
            new_combo = st.selectbox("预测组合类型", ["高风险押宝期", "红利交叠期", "红利退坡期", "红利消失期"])
            new_return = st.number_input("实际行业涨幅 (%)", value=0.0)
            new_hs300 = st.number_input("沪深300涨幅 (%)", value=0.0)
            new_accuracy = st.selectbox("预测准确性", ["准确", "基本准确", "偏差", "反例"])
        
        new_desc = st.text_area("验证说明")
        
        submitted = st.form_submit_button("添加案例")
        if submitted:
            st.success(f"案例 '{new_industry}' 已记录（注：实际需写入数据库）")
            st.info("提示：在正式版本中，此数据将追加到CSV文件")
