"""
可视化组件库
包含周期象限图、雷达图、仪表盘等职业规划专用可视化
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
from typing import List, Dict, Optional


def create_cycle_quadrant_chart(df, highlight_industry: Optional[str] = None):
    """
    创建周期象限图（产业周期 × 政策周期）
    
    Args:
        df: 行业数据DataFrame
        highlight_industry: 要高亮显示的行业名称
        
    Returns:
        Plotly Figure 对象
    """
    if df.empty:
        return None
    
    # 计算坐标
    from utils.data_processor import get_industry_cycle_score, get_policy_cycle_score
    
    df = df.copy()
    df['产业周期评分'] = df['当前周期阶段'].apply(get_industry_cycle_score)
    df['政策周期评分'] = df['未来1-3年景气度'].apply(get_policy_cycle_score)
    
    # 确定颜色
    def get_color(row):
        if highlight_industry and row['行业名称'] == highlight_industry:
            return '#FF0000'  # 高亮红色
        
        stage = row['当前周期阶段']
        if stage == '成长期':
            return '#00C851'  # 绿色
        elif stage == '初创期':
            return '#33B5E5'  # 蓝色
        elif stage == '成熟期':
            return '#FFBB33'  # 黄色
        elif stage == '调整期':
            return '#FF8800'  # 橙色
        else:
            return '#CC0000'  # 红色
    
    df['颜色'] = df.apply(get_color, axis=1)
    df['大小'] = df.apply(lambda x: 20 if highlight_industry and x['行业名称'] == highlight_industry else 10, axis=1)
    
    # 创建散点图
    fig = go.Figure()
    
    # 按周期阶段分组绘制，确保图例正确
    stage_order = ['成长期', '初创期', '成熟期', '调整期', '衰退期']
    colors_map = {
        '成长期': '#00C851',
        '初创期': '#33B5E5',
        '成熟期': '#FFBB33',
        '调整期': '#FF8800',
        '衰退期': '#CC0000'
    }
    
    for stage in stage_order:
        stage_df = df[df['当前周期阶段'] == stage]
        if not stage_df.empty:
            fig.add_trace(go.Scatter(
                x=stage_df['政策周期评分'],
                y=stage_df['产业周期评分'],
                mode='markers+text',
                name=stage,
                text=stage_df['行业名称'],
                textposition="top center",
                textfont=dict(size=8),
                marker=dict(
                    size=stage_df['大小'],
                    color=colors_map.get(stage, '#999999'),
                    opacity=0.8,
                    line=dict(width=1, color='white')
                ),
                hovertemplate='<b>%{text}</b><br>政策周期评分: %{x}<br>产业周期评分: %{y}<extra></extra>'
            ))
    
    # 添加高亮行业的特殊标记
    if highlight_industry:
        highlight_df = df[df['行业名称'] == highlight_industry]
        if not highlight_df.empty:
            fig.add_trace(go.Scatter(
                x=highlight_df['政策周期评分'],
                y=highlight_df['产业周期评分'],
                mode='markers',
                name='当前选中',
                marker=dict(
                    size=30,
                    color='rgba(255, 0, 0, 0.3)',
                    line=dict(width=3, color='red')
                ),
                hoverinfo='skip'
            ))
    
    # 添加象限分割线
    fig.add_hline(y=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    
    # 添加象限标注
    fig.add_annotation(x=75, y=75, text="🟢 红利交叠期<br>(最佳入场)", showarrow=False, 
                       font=dict(size=12, color="green"), bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=25, y=75, text="🔴 高风险押宝期", showarrow=False,
                       font=dict(size=12, color="blue"), bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=75, y=25, text="🟡 红利退坡期", showarrow=False,
                       font=dict(size=12, color="orange"), bgcolor="rgba(255,255,255,0.8)")
    fig.add_annotation(x=25, y=25, text="🔴 红利消失期<br>(建议离场)", showarrow=False,
                       font=dict(size=12, color="red"), bgcolor="rgba(255,255,255,0.8)")
    
    # 更新布局
    fig.update_layout(
        title="产业周期 × 政策周期 象限图",
        xaxis_title="政策周期阶段 (0-100)",
        yaxis_title="产业周期阶段 (0-100)",
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100]),
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_radar_chart(indicators: Dict[str, float], title: str = "行业指标雷达图"):
    """
    创建雷达图
    
    Args:
        indicators: 指标名称和数值的字典
        title: 图表标题
        
    Returns:
        Plotly Figure 对象
    """
    categories = list(indicators.keys())
    values = list(indicators.values())
    
    # 闭合雷达图
    categories.append(categories[0])
    values.append(values[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 200, 81, 0.3)',
        line=dict(color='rgb(0, 200, 81)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        title=title,
        showlegend=False,
        height=400
    )
    
    return fig


def create_sentinel_radar(indicators: List[Dict]):
    """
    创建数据哨兵7大指标雷达图
    
    Args:
        indicators: 7大指标状态列表
        
    Returns:
        Plotly Figure 对象
    """
    labels = ['技术成本\n下降50%', '龙头毛利\n>20%', '政策\n明确补贴', 
              '渗透率\n5-30%', '资本开支\n增速>30%', '营收10亿\n企业>3家', '产业链\n配套完善']
    
    values = [100 if ind["status"] else 30 for ind in indicators]
    values.append(values[0])  # 闭合
    labels.append(labels[0])
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
        fillcolor='rgba(0, 200, 81, 0.3)',
        line=dict(color='rgb(0, 200, 81)', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='array',
                tickvals=[30, 100],
                ticktext=['未达标', '已达标']
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=30, b=30)
    )
    
    return fig


def create_cycle_distribution_chart(df):
    """
    创建周期阶段分布图
    
    Args:
        df: 行业数据DataFrame
        
    Returns:
        Plotly Figure 对象
    """
    if df.empty or '当前周期阶段' not in df.columns:
        return None
    
    cycle_counts = df['当前周期阶段'].value_counts().reset_index()
    cycle_counts.columns = ['周期阶段', '数量']
    
    # 定义颜色
    color_map = {
        '成长期': '#00C851',
        '初创期': '#33B5E5',
        '成熟期': '#FFBB33',
        '调整期': '#FF8800',
        '衰退期': '#CC0000'
    }
    
    fig = px.bar(
        cycle_counts, 
        x='周期阶段', 
        y='数量', 
        text='数量',
        color='周期阶段',
        color_discrete_map=color_map,
        title="各周期阶段行业分布"
    )
    
    fig.update_traces(textposition='outside')
    fig.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="周期阶段",
        yaxis_title="行业数量"
    )
    
    return fig


def create_sentiment_pie_chart(df):
    """
    创建景气度分布饼图
    
    Args:
        df: 行业数据DataFrame
        
    Returns:
        Plotly Figure 对象
    """
    if df.empty or '未来1-3年景气度' not in df.columns:
        return None
    
    sentiment_counts = df['未来1-3年景气度'].value_counts().reset_index()
    sentiment_counts.columns = ['景气度', '数量']
    
    fig = px.pie(
        sentiment_counts,
        names='景气度',
        values='数量',
        hole=0.4,
        title="未来1-3年景气度分布"
    )
    
    fig.update_layout(height=400)
    
    return fig


def create_career_path_timeline(current_industry: str, target_industry: str, 
                                 milestones: List[Dict]):
    """
    创建职业发展时间线
    
    Args:
        current_industry: 当前行业
        target_industry: 目标行业
        milestones: 里程碑列表
        
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure()
    
    # 添加时间线
    years = list(range(len(milestones)))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=[m.get('score', 50) for m in milestones],
        mode='lines+markers+text',
        text=[m.get('label', '') for m in milestones],
        textposition="top center",
        line=dict(color='#00C851', width=3),
        marker=dict(size=15, color='#00C851'),
        name='预期发展路径'
    ))
    
    # 添加当前位置标记
    fig.add_annotation(
        x=0, y=milestones[0].get('score', 50),
        text=f"当前: {current_industry}",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40
    )
    
    # 添加目标位置标记
    fig.add_annotation(
        x=len(milestones)-1, y=milestones[-1].get('score', 50),
        text=f"目标: {target_industry}",
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-40
    )
    
    fig.update_layout(
        title="职业发展路径推演",
        xaxis_title="时间（年）",
        yaxis_title="职业价值指数",
        height=400,
        showlegend=False
    )
    
    return fig


def create_gauge_chart(value: int, title: str = "综合评分"):
    """
    创建仪表盘图
    
    Args:
        value: 0-100的数值
        title: 标题
        
    Returns:
        Plotly Figure 对象
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'red'},
                {'range': [30, 50], 'color': 'orange'},
                {'range': [50, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'green'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=300)
    
    return fig
