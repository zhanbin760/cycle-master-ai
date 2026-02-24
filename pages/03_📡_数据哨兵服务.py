import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random

st.set_page_config(page_title="数据哨兵服务", page_icon="📡", layout="wide")
st.title("📡 数据哨兵：周期拐点监测服务")
st.markdown("基于马江博的**“新产业成长期拐点7大判断清单”**，对您关注的赛道进行自动化指标追踪。")

# ==========================================
# 1. 订阅列表与状态管理
# ==========================================
# 初始化用户的“监控列表”
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["低空经济", "银发经济"] # 默认给两个演示数据

# 检查是否从其他页面传递了目标行业过来
if 'target_industry' in st.session_state and st.session_state['target_industry']:
    new_industry = st.session_state['target_industry']
    if new_industry not in st.session_state.watchlist:
        st.session_state.watchlist.append(new_industry)
        st.toast(f"✅ 已将 {new_industry} 自动加入监控哨兵！")
    # 消费完后重置，避免重复添加
    st.session_state['target_industry'] = ""

# ==========================================
# 2. 核心算法：模拟抓取 7 大拐点指标
# ==========================================
# 在实际商业应用中，这里应替换为对数据库、金融API（如万得/同花顺）或爬虫的调用
def get_mock_sentinel_data(industry_name):
    """为特定行业生成模拟的 7 大拐点达标状态"""
    # 随机生成一个基础完成度，用于模拟不同行业的成熟度
    base_score = random.uniform(0.3, 0.9) 
    
    indicators = [
        {"name": "技术成本在2-3年内下降50%以上", "status": random.random() < base_score},
        {"name": "龙头企业毛利率超过20%，净利润转正", "status": random.random() < base_score},
        {"name": "政策文件中明确了财政资金规模和具体补贴标准", "status": random.random() < base_score + 0.1},
        {"name": "市场渗透率在5%-30%之间", "status": random.random() < base_score},
        {"name": "行业资本开支增速维持30%以上", "status": random.random() < base_score},
        {"name": "出现了3家以上年营收超过10亿的企业", "status": random.random() < base_score - 0.1},
        {"name": "产业链上下游配套开始完善", "status": random.random() < base_score + 0.2},
    ]
    
    achieved_count = sum(1 for ind in indicators if ind["status"])
    readiness_score = int((achieved_count / 7) * 100)
    
    return indicators, readiness_score

# ==========================================
# 3. 侧边栏：服务控制台
# ==========================================
with st.sidebar:
    st.header("⚙️ 哨兵控制台")
    st.markdown("您可以手动添加想要长期追踪的细分行业：")
    
    with st.form("add_industry_form"):
        custom_industry = st.text_input("输入行业名称", placeholder="例如：人形机器人")
        submitted = st.form_submit_button("➕ 添加至监控列表")
        if submitted and custom_industry:
            if custom_industry not in st.session_state.watchlist:
                st.session_state.watchlist.append(custom_industry)
                st.success(f"已添加：{custom_industry}")
            else:
                st.warning("该行业已在监控列表中。")
                
    st.markdown("---")
    st.markdown("### 💎 PRO 订阅服务")
    st.info("升级为 PRO 用户，解锁：\n- 每日政策词频抓取提醒\n- 龙头企业财报自动化解析\n- 深度研报一键导出 PDF")
    st.button("立即解锁高级权限 (测试)")

# ==========================================
# 4. 仪表盘渲染：雷达图与指标卡片
# ==========================================
st.markdown("### 🔔 我的监控哨兵库")

if not st.session_state.watchlist:
    st.warning("您的监控列表为空。请从侧边栏添加，或从【周期实验室】推送行业过来。")
else:
    # 动态生成多列布局
    cols = st.columns(2)
    
    for i, industry in enumerate(st.session_state.watchlist):
        indicators, readiness = get_mock_sentinel_data(industry)
        
        # 将卡片交替放入两列中
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(f"🎯 {industry}")
                
                # 绘制雷达图
                fig = go.Figure()
                labels = ['技术降本', '毛利转正', '政策补贴', '渗透率5-30%', '资本开支>30%', '营收超10亿', '配套完善']
                values = [1 if ind["status"] else 0.1 for ind in indicators] # 0.1 for visual rendering
                
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]], # 闭合雷达图
                    theta=labels + [labels[0]],
                    fill='toself',
                    name=industry,
                    line_color='teal' if readiness >= 50 else 'coral'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                    showlegend=False,
                    height=250,
                    margin=dict(l=30, r=30, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 进度条与状态
                st.markdown(f"**成长期拐点爆发指数：{readiness}%**")
                st.progress(readiness / 100)
                
                # 折叠面板展示具体 7 大指标
                with st.expander("展开查看 7 大核心指标详情"):
                    for ind in indicators:
                        icon = "✅" if ind["status"] else "⏳"
                        st.markdown(f"{icon} {ind['name']}")
                
                # 商业化动作模拟
                if st.button(f"生成 {industry} 最新简报", key=f"btn_{i}"):
                    with st.spinner("正在调度后端数据，生成报告中..."):
                        time.sleep(1.5)
                        st.success("简报已生成！(此处可对接 python-docx 导出功能)")