import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_engine import render_api_key_input, render_privacy_notice, get_deepseek_client, increment_usage
from utils.rag_engine import get_rag_engine
from utils.visualization import create_career_path_timeline

st.set_page_config(page_title="职业路径推演", page_icon="🛤️", layout="wide")

st.title("🛤️ 职业路径推演：模拟不同选择的发展路径")
st.markdown("基于周期理论，模拟'如果5年前进入新能源'或'如果现在跳槽去储能'等假设情境，推演未来3-5年的职业发展路径与风险收益比。")

# 渲染 API Key 和隐私声明
render_api_key_input()
render_privacy_notice()

# ==========================================
# 推演模式选择
# ==========================================
st.markdown("### 🎯 选择推演模式")

sim_mode = st.radio(
    "选择您想进行的推演类型：",
    [
        "历史回溯：如果我N年前进入某行业，现在会怎样？",
        "未来推演：如果我现在跳槽去某行业，未来3-5年如何？",
        "双轨对比：对比留在当前行业 vs 转型目标行业的差异"
    ],
    horizontal=True
)

st.markdown("---")

# ==========================================
# 场景1: 历史回溯推演
# ==========================================
if "历史回溯" in sim_mode:
    st.markdown("### ⏮️ 历史回溯推演")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        past_year = st.selectbox("假设在多少年前进入：", [1, 2, 3, 5, 7, 10], index=2)
    
    with col2:
        past_industry = st.text_input("假设进入的行业：", 
                                       value="新能源汽车",
                                       placeholder="例如：新能源汽车")
    
    with col3:
        entry_level = st.selectbox("假设入职时的职级：", 
                                    ["应届生/初级", "中级", "高级", "管理岗"])
    
    if st.button("🚀 开始历史回溯推演", use_container_width=True):
        with st.spinner("正在检索历史数据并进行推演分析..."):
            try:
                # 获取RAG引擎
                rag_engine = get_rag_engine()
                
                # 检索行业数据
                search_results = rag_engine.search_industry(past_industry, top_k=1)
                
                if search_results:
                    result = search_results[0]
                    stage = result['当前周期阶段']
                    sentiment = result['未来1-3年景气度']
                    
                    # 显示推演结果
                    st.success(f"📊 推演场景：{past_year}年前进入 **{past_industry}**（{entry_level}）")
                    
                    # 计算时间线
                    current_year = datetime.now().year
                    start_year = current_year - past_year
                    
                    # 构建时间线数据（模拟）
                    milestones = []
                    base_score = 50
                    
                    if stage == "成长期":
                        # 成长期的收益曲线
                        for i in range(past_year + 1):
                            year = start_year + i
                            score = base_score + (i * 15) + (i * i * 2)  # 加速增长
                            milestone = {
                                "year": year,
                                "score": min(score, 100),
                                "label": f"第{i}年"
                            }
                            if i == 0:
                                milestone["label"] = "入职"
                            elif i == past_year:
                                milestone["label"] = "当前"
                            milestones.append(milestone)
                        
                        career_value = "💰 高增值"
                        salary_growth = f"+{past_year * 20}% ~ +{past_year * 35}%"
                        position_level = f"晋升 {past_year // 2} 级"
                        
                    elif stage == "初创期":
                        # 初创期的高风险高回报
                        for i in range(past_year + 1):
                            year = start_year + i
                            if i < 2:
                                score = base_score + (i * 5)
                            else:
                                score = base_score + 10 + ((i-2) * 20)
                            milestone = {
                                "year": year,
                                "score": min(score, 100),
                                "label": f"第{i}年"
                            }
                            milestones.append(milestone)
                        
                        career_value = "🎲 高风险高回报"
                        salary_growth = f"+{past_year * 15}% ~ +{past_year * 50}%（波动大）"
                        position_level = "可能快速晋升或原地踏步"
                        
                    elif stage in ["成熟期", "调整期"]:
                        # 成熟/调整期的平缓增长
                        for i in range(past_year + 1):
                            year = start_year + i
                            score = base_score + (i * 5)
                            milestone = {
                                "year": year,
                                "score": min(score, 80),
                                "label": f"第{i}年"
                            }
                            milestones.append(milestone)
                        
                        career_value = "📊 稳定/下滑"
                        salary_growth = f"+{past_year * 5}% ~ +{past_year * 10}%"
                        position_level = "晋升缓慢"
                    else:
                        career_value = "⚠️ 风险"
                        salary_growth = "不稳定"
                        position_level = "可能降级/失业"
                        milestones = []
                    
                    # 显示关键指标
                    metric_cols = st.columns(4)
                    with metric_cols[0]:
                        st.metric("职业价值指数", career_value)
                    with metric_cols[1]:
                        st.metric(f"{past_year}年薪资涨幅", salary_growth)
                    with metric_cols[2]:
                        st.metric("职级变化", position_level)
                    with metric_cols[3]:
                        combo = rag_engine.get_cycle_combination(stage)
                        st.metric("周期组合", combo.get('组合名称', '未知'))
                    
                    # 显示时间线图
                    if milestones:
                        st.markdown("### 📈 职业发展轨迹")
                        fig = go.Figure()
                        
                        years = [m['year'] for m in milestones]
                        scores = [m['score'] for m in milestones]
                        
                        fig.add_trace(go.Scatter(
                            x=years, y=scores,
                            mode='lines+markers+text',
                            text=[m['label'] for m in milestones],
                            textposition="top center",
                            line=dict(color='#00C851', width=3),
                            marker=dict(size=15)
                        ))
                        
                        fig.update_layout(
                            title=f"在{past_industry}的假设职业发展轨迹",
                            xaxis_title="年份",
                            yaxis_title="职业价值指数",
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # AI深度分析
                    st.markdown("### 🤖 AI深度分析")
                    
                    client = get_deepseek_client()
                    increment_usage()
                    
                    prompt = f"""请基于以下场景，为用户提供深度职业推演分析：
场景：用户在{past_year}年前（{start_year}年）进入{past_industry}行业，入职职级为{entry_level}。
当前该行业周期阶段：{stage}
未来1-3年景气度：{sentiment}

请分析：
1. 当时进入该行业的时机判断（是否符合周期共振原理）
2. 这{past_year}年间可能经历的行业波动
3. 当前的假设职业状态（薪资、职级、技能积累）
4. 与当时其他选择的对比（如选择同期调整期行业）
5. 经验教训总结
"""
                    
                    messages = [
                        {"role": "system", "content": "你是Cycle-Master AI职业规划专家，基于马江博周期共振理论进行分析。"},
                        {"role": "user", "content": prompt}
                    ]
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        temperature=0.6,
                        max_tokens=2000
                    )
                    
                    st.markdown(response.choices[0].message.content)
                    
                else:
                    st.warning(f"未在知识库中找到'{past_industry}'的相关数据，无法进行推演。")
                    
            except Exception as e:
                st.error(f"推演失败: {str(e)}")

# ==========================================
# 场景2: 未来推演
# ==========================================
elif "未来推演" in sim_mode:
    st.markdown("### 🔮 未来推演：如果现在转型")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        current_ind = st.text_input("您当前的行业：", 
                                     value=st.session_state.get('user_profile', {}).get('current_industry', ''),
                                     placeholder="例如：传统地产")
    
    with col2:
        target_ind = st.text_input("目标转型行业：", 
                                    value=st.session_state.get('target_industry', ''),
                                    placeholder="例如：储能")
    
    with col3:
        forecast_years = st.selectbox("推演时间跨度：", [1, 2, 3, 5], index=2)
    
    if st.button("🔮 开始未来推演", use_container_width=True):
        with st.spinner("正在分析转型路径与未来前景..."):
            try:
                rag_engine = get_rag_engine()
                
                # 获取两个行业的数据
                current_results = rag_engine.search_industry(current_ind, top_k=1)
                target_results = rag_engine.search_industry(target_ind, top_k=1)
                
                if not target_results:
                    st.warning(f"未找到'{target_ind}'的行业数据")
                else:
                    target_stage = target_results[0]['当前周期阶段']
                    target_sentiment = target_results[0]['未来1-3年景气度']
                    
                    st.success(f"📊 推演场景：从 **{current_ind}** 转型到 **{target_ind}**")
                    
                    # 风险收益分析
                    combo = rag_engine.get_cycle_combination(target_stage)
                    
                    analysis_cols = st.columns(2)
                    
                    with analysis_cols[0]:
                        st.markdown("#### 📈 目标行业分析")
                        st.markdown(f"**行业名称**：{target_results[0]['行业名称']}")
                        st.markdown(f"**周期阶段**：{target_stage}")
                        st.markdown(f"**景气度**：{target_sentiment}")
                        st.markdown(f"**周期组合**：{combo.get('组合名称', '')} {combo.get('风险等级', '')}")
                        st.markdown(f"**适合人群**：{combo.get('适合人群', '')}")
                    
                    with analysis_cols[1]:
                        st.markdown("#### ⚖️ 风险收益评估")
                        
                        # 基于周期阶段评估
                        if target_stage == "成长期":
                            risk_level = "中等"
                            return_potential = "高"
                            entry_difficulty = "中等（人才需求大）"
                        elif target_stage == "初创期":
                            risk_level = "高"
                            return_potential = "不确定"
                            entry_difficulty = "较低（早期机会多）"
                        elif target_stage == "成熟期":
                            risk_level = "低"
                            return_potential = "稳定"
                            entry_difficulty = "高（格局已定）"
                        else:
                            risk_level = "高"
                            return_potential = "低/负"
                            entry_difficulty = "不建议进入"
                        
                        st.markdown(f"**风险等级**：{risk_level}")
                        st.markdown(f"**收益潜力**：{return_potential}")
                        st.markdown(f"**入行难度**：{entry_difficulty}")
                    
                    # 未来时间线
                    st.markdown("#### 📅 假设转型后的发展轨迹")
                    
                    current_year = datetime.now().year
                    future_milestones = []
                    
                    for i in range(forecast_years + 1):
                        year = current_year + i
                        if i == 0:
                            label = "转型起点"
                            score = 40  # 转型初期可能下降
                        elif i == 1:
                            label = "适应期"
                            score = 50
                        elif i == forecast_years:
                            label = f"{forecast_years}年后"
                            score = 70 if target_stage == "成长期" else 55
                        else:
                            label = f"第{i}年"
                            score = 50 + (i * 10)
                        
                        future_milestones.append({
                            "year": year,
                            "score": min(score, 100),
                            "label": label
                        })
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=[m['year'] for m in future_milestones],
                        y=[m['score'] for m in future_milestones],
                        mode='lines+markers+text',
                        text=[m['label'] for m in future_milestones],
                        textposition="top center",
                        line=dict(color='#33B5E5', width=3),
                        marker=dict(size=15)
                    ))
                    
                    fig.update_layout(
                        title=f"转型到{target_ind}后的假设发展轨迹",
                        xaxis_title="年份",
                        yaxis_title="职业价值指数",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # AI转型建议
                    st.markdown("### 🤖 AI转型建议")
                    
                    client = get_deepseek_client()
                    increment_usage()
                    
                    transition_prompt = f"""请为以下职业转型提供深度分析和建议：
从行业：{current_ind} {(f"（周期阶段：{current_results[0]['当前周期阶段']}" if current_results else "")}
到行业：{target_ind}（周期阶段：{target_stage}，景气度：{target_sentiment}）
周期组合：{combo.get('组合名称', '')}

请分析：
1. 转型的时机判断（现在是否是好的转型时机）
2. 转型的核心风险点
3. 需要补充的关键技能
4. 推荐的转型路径（直接跳槽/先学习/内部转岗等）
5. {forecast_years}年后的预期状态
6. 如果转型失败，备选方案是什么
"""
                    
                    messages = [
                        {"role": "system", "content": "你是Cycle-Master AI职业规划专家，基于马江博周期共振理论进行分析。"},
                        {"role": "user", "content": transition_prompt}
                    ]
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=messages,
                        temperature=0.6,
                        max_tokens=2500
                    )
                    
                    st.markdown(response.choices[0].message.content)
                    
            except Exception as e:
                st.error(f"推演失败: {str(e)}")

# ==========================================
# 场景3: 双轨对比
# ==========================================
else:
    st.markdown("### ⚖️ 双轨对比：留下 vs 转型")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏠 方案A：留在当前行业")
        stay_industry = st.text_input("当前行业：", 
                                       value=st.session_state.get('user_profile', {}).get('current_industry', ''),
                                       key="stay_ind")
    
    with col2:
        st.markdown("#### 🚀 方案B：转型目标行业")
        move_industry = st.text_input("目标行业：", 
                                       value=st.session_state.get('target_industry', ''),
                                       key="move_ind")
    
    compare_years = st.slider("对比时间跨度（年）：", 1, 10, 5)
    
    if st.button("⚖️ 开始双轨对比", use_container_width=True):
        if not stay_industry or not move_industry:
            st.warning("请输入两个行业名称")
        else:
            with st.spinner("正在生成双轨对比分析..."):
                try:
                    rag_engine = get_rag_engine()
                    
                    stay_results = rag_engine.search_industry(stay_industry, top_k=1)
                    move_results = rag_engine.search_industry(move_industry, top_k=1)
                    
                    if not stay_results or not move_results:
                        st.warning("需要两个行业的数据才能进行对比")
                    else:
                        # 创建对比图表
                        current_year = datetime.now().year
                        years = list(range(current_year, current_year + compare_years + 1))
                        
                        # 模拟两条轨迹
                        stay_stage = stay_results[0]['当前周期阶段']
                        move_stage = move_results[0]['当前周期阶段']
                        
                        # 轨迹A：留下
                        if stay_stage in ["成长期", "初创期"]:
                            stay_trajectory = [50 + i * 12 for i in range(compare_years + 1)]
                        elif stay_stage == "成熟期":
                            stay_trajectory = [50 + i * 5 for i in range(compare_years + 1)]
                        else:
                            stay_trajectory = [50 - i * 5 for i in range(compare_years + 1)]
                        
                        # 轨迹B：转型
                        move_trajectory = [50]  # 转型起点
                        if move_stage == "成长期":
                            for i in range(1, compare_years + 1):
                                if i == 1:
                                    move_trajectory.append(45)  # 适应期下降
                                else:
                                    move_trajectory.append(45 + (i-1) * 15)
                        elif move_stage == "初创期":
                            for i in range(1, compare_years + 1):
                                move_trajectory.append(40 + i * 10)
                        else:
                            for i in range(1, compare_years + 1):
                                move_trajectory.append(45 + i * 5)
                        
                        # 绘制对比图
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=years, y=stay_trajectory,
                            mode='lines+markers',
                            name=f'留在{stay_industry}',
                            line=dict(color='#FF8800', width=3)
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=years, y=move_trajectory,
                            mode='lines+markers',
                            name=f'转型{move_industry}',
                            line=dict(color='#00C851', width=3)
                        ))
                        
                        # 添加交叉点标注
                        for i in range(len(years)):
                            if i > 0 and move_trajectory[i] > stay_trajectory[i] and move_trajectory[i-1] <= stay_trajectory[i-1]:
                                fig.add_annotation(
                                    x=years[i], y=move_trajectory[i],
                                    text="转型收益<br>超过留下",
                                    showarrow=True,
                                    arrowhead=2
                                )
                        
                        fig.update_layout(
                            title=f"{compare_years}年双轨对比：留下 vs 转型",
                            xaxis_title="年份",
                            yaxis_title="职业价值指数",
                            height=500,
                            legend=dict(orientation="h", yanchor="bottom", y=1.02)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 对比表格
                        st.markdown("### 📊 详细对比")
                        
                        comparison_data = {
                            "维度": ["当前周期阶段", "未来景气度", "风险等级", f"{compare_years}年后预期价值", "推荐指数"],
                            f"留下 ({stay_industry})": [
                                stay_stage,
                                stay_results[0]['未来1-3年景气度'],
                                "低" if stay_stage == "成熟期" else "中" if stay_stage == "成长期" else "高",
                                f"{stay_trajectory[-1]:.0f}",
                                "⭐⭐⭐" if stay_stage == "成长期" else "⭐⭐" if stay_stage == "成熟期" else "⭐"
                            ],
                            f"转型 ({move_industry})": [
                                move_stage,
                                move_results[0]['未来1-3年景气度'],
                                "高（短期）→ 低（长期）" if move_stage == "成长期" else "高",
                                f"{move_trajectory[-1]:.0f}",
                                "⭐⭐⭐⭐⭐" if move_stage == "成长期" else "⭐⭐⭐" if move_stage == "初创期" else "⭐⭐"
                            ]
                        }
                        
                        comp_df = pd.DataFrame(comparison_data)
                        st.dataframe(comp_df, use_container_width=True, hide_index=True)
                        
                        # AI综合建议
                        st.markdown("### 🤖 AI综合建议")
                        
                        client = get_deepseek_client()
                        increment_usage()
                        
                        compare_prompt = f"""请对以下两个职业选择方案进行综合对比分析：

方案A（留下）：{stay_industry}
- 周期阶段：{stay_stage}
- 景气度：{stay_results[0]['未来1-3年景气度']}

方案B（转型）：{move_industry}
- 周期阶段：{move_stage}
- 景气度：{move_results[0]['未来1-3年景气度']}

对比时间跨度：{compare_years}年

请分析：
1. 两个方案的优劣对比
2. 不同风险偏好的选择建议
3. 关键决策节点的判断标准
4. 最终推荐及理由
"""
                        
                        messages = [
                            {"role": "system", "content": "你是Cycle-Master AI职业规划专家，基于马江博周期共振理论进行客观分析。"},
                            {"role": "user", "content": compare_prompt}
                        ]
                        
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=messages,
                            temperature=0.6,
                            max_tokens=2500
                        )
                        
                        st.markdown(response.choices[0].message.content)
                        
                except Exception as e:
                    st.error(f"对比分析失败: {str(e)}")

# ==========================================
# 页面底部提示
# ==========================================
st.markdown("---")
st.info("💡 **提示**：推演结果基于周期理论和历史数据模型，仅供参考。实际职业发展受个人能力、市场环境等多重因素影响。")
