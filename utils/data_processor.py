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


def get_industry_by_name(df, industry_name: str):
    """
    根据行业名称获取行业信息（RAG检索支持）
    
    Args:
        df: 行业数据DataFrame
        industry_name: 行业名称
        
    Returns:
        行业信息字典，未找到返回None
    """
    if df.empty or '行业名称' not in df.columns:
        return None
    
    # 精确匹配
    match = df[df['行业名称'] == industry_name]
    if not match.empty:
        row = match.iloc[0]
        return {
            "序号": row.get('序号', ''),
            "行业名称": row.get('行业名称', ''),
            "当前周期阶段": row.get('当前周期阶段', ''),
            "未来1-3年景气度": row.get('未来1-3年景气度', ''),
            "评价": row.get('评价', '')
        }
    
    return None


def search_industries(df, query: str, max_results: int = 5):
    """
    搜索行业（模糊匹配）
    
    Args:
        df: 行业数据DataFrame
        query: 搜索关键词
        max_results: 最大返回结果数
        
    Returns:
        匹配的行业列表
    """
    if df.empty or '行业名称' not in df.columns or not query:
        return []
    
    # 行业名称包含查询词
    name_matches = df[df['行业名称'].str.contains(query, case=False, na=False)]
    
    # 评价包含查询词
    desc_matches = df[df['评价'].str.contains(query, case=False, na=False)]
    
    # 合并结果（去重）
    all_matches = pd.concat([name_matches, desc_matches]).drop_duplicates()
    
    results = []
    for _, row in all_matches.head(max_results).iterrows():
        results.append({
            "序号": row.get('序号', ''),
            "行业名称": row.get('行业名称', ''),
            "当前周期阶段": row.get('当前周期阶段', ''),
            "未来1-3年景气度": row.get('未来1-3年景气度', ''),
            "评价": row.get('评价', '')
        })
    
    return results


def get_growth_industries(df, min_sentiment: str = "高成长"):
    """
    获取成长期行业列表
    
    Args:
        df: 行业数据DataFrame
        min_sentiment: 最小景气度要求
        
    Returns:
        成长期行业列表
    """
    if df.empty:
        return []
    
    # 筛选成长期且景气度高的行业
    growth = df[
        (df['当前周期阶段'].isin(['成长期', '初创期'])) &
        (df['未来1-3年景气度'].str.contains('高成长|高', na=False))
    ]
    
    results = []
    for _, row in growth.iterrows():
        results.append({
            "行业名称": row.get('行业名称', ''),
            "周期阶段": row.get('当前周期阶段', ''),
            "景气度": row.get('未来1-3年景气度', ''),
            "评价": row.get('评价', '')
        })
    
    return results


def get_risk_industries(df):
    """
    获取高风险行业列表（调整期/衰退期）
    
    Args:
        df: 行业数据DataFrame
        
    Returns:
        高风险行业列表
    """
    if df.empty:
        return []
    
    # 筛选调整期或景气度承压的行业
    risk = df[
        (df['当前周期阶段'].isin(['调整期', '衰退期'])) |
        (df['未来1-3年景气度'].str.contains('承压|低', na=False))
    ]
    
    results = []
    for _, row in risk.iterrows():
        results.append({
            "行业名称": row.get('行业名称', ''),
            "周期阶段": row.get('当前周期阶段', ''),
            "景气度": row.get('未来1-3年景气度', ''),
            "评价": row.get('评价', ''),
            "风险等级": "🔴 高风险" if row.get('当前周期阶段') == '衰退期' else "🟡 中高风险"
        })
    
    return results


def get_industry_cycle_score(industry_stage: str) -> int:
    """
    获取产业周期阶段评分（用于可视化）
    
    Args:
        industry_stage: 周期阶段
        
    Returns:
        0-100的评分
    """
    scores = {
        "初创期": 25,
        "成长期": 75,
        "成熟期": 50,
        "调整期": 25,
        "衰退期": 10
    }
    return scores.get(industry_stage, 50)


def get_policy_cycle_score(sentiment: str) -> int:
    """
    获取政策周期阶段评分（用于可视化）
    
    Args:
        sentiment: 景气度描述
        
    Returns:
        0-100的评分
    """
    if "高成长" in sentiment or "高" in sentiment:
        return 80
    elif "平稳" in sentiment:
        return 50
    elif "承压" in sentiment or "低" in sentiment:
        return 20
    return 50
