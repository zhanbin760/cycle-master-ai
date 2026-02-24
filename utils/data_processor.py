# utils/data_processor.py
import pandas as pd
import streamlit as st

@st.cache_data
def load_industry_data(file_path="data/细分领域行业周期研判表.csv"):
    """
    加载并清洗行业周期数据。
    使用 @st.cache_data 装饰器，确保每次刷新页面时不会重复读取硬盘，提升应用加载速度。
    """
    try:
        # 读取 CSV 数据
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # 清洗数据：去除可能因为末尾逗号产生的未命名空列 (例如 'Unnamed: 5')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 清洗数据：去除完全为空的行，并填充 NaN 值
        df = df.dropna(how='all')
        df = df.fillna("暂无评价")
        
        # 确保核心列存在，如果不存在则抛出异常提示
        expected_columns = ['序号', '行业名称', '当前周期阶段', '未来1-3年景气度', '评价']
        for col in expected_columns:
            if col not in df.columns:
                raise ValueError(f"数据源缺少必要列：{col}")
                
        return df
    except FileNotFoundError:
        st.error(f"⚠️ 找不到数据文件：{file_path}。请确保文件已存放在项目根目录的 data 文件夹下。")
        st.stop()
    except Exception as e:
        st.error(f"⚠️ 数据加载出错: {str(e)}")
        st.stop()

def get_cycle_distribution(df):
    """
    获取各个周期阶段的行业数量统计，用于前端渲染饼图或柱状图。
    返回格式: Series (索引为周期阶段，值为数量)
    """
    if '当前周期阶段' in df.columns:
        return df['当前周期阶段'].value_counts()
    return pd.Series()

def get_sentiment_distribution(df):
    """
    获取未来1-3年景气度的数量统计。
    """
    if '未来1-3年景气度' in df.columns:
        return df['未来1-3年景气度'].value_counts()
    return pd.Series()

def filter_industry_data(df, selected_stages=None, selected_sentiments=None, search_query=""):
    """
    多维度过滤行业数据。
    
    参数:
    - df: 原始 DataFrame
    - selected_stages: list, 用户选中的周期阶段集合
    - selected_sentiments: list, 用户选中的景气度集合
    - search_query: str, 用户搜索的特定行业关键词
    """
    filtered_df = df.copy()
    
    # 按阶段过滤
    if selected_stages:
        filtered_df = filtered_df[filtered_df['当前周期阶段'].isin(selected_stages)]
        
    # 按景气度过滤
    if selected_sentiments:
        filtered_df = filtered_df[filtered_df['未来1-3年景气度'].isin(selected_sentiments)]
        
    # 模糊搜索过滤 (行业名称或评价中包含关键词)
    if search_query:
        search_mask = (
            filtered_df['行业名称'].str.contains(search_query, case=False, na=False) | 
            filtered_df['评价'].str.contains(search_query, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
        
    return filtered_df