"""
马江博周期框架回测数据收集工具
用于批量获取行业指数历史数据，计算收益率
"""

import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

# 行业指数代码映射表（可根据需要扩展）
INDUSTRY_INDEX_MAP = {
    "新能源汽车": {"code": "930997", "name": "中证新能源汽车指数", "exchange": "csi"},
    "光伏": {"code": "931151", "name": "中证光伏产业指数", "exchange": "csi"},
    "半导体": {"code": "H30184", "name": "中证半导体指数", "exchange": "csi"},
    "医药": {"code": "000933", "name": "中证医药指数", "exchange": "sse"},
    "房地产": {"code": "931775", "name": "中证全指房地产指数", "exchange": "csi"},
    "互联网": {"code": "930625", "name": "中证沪港深互联网指数", "exchange": "csi"},
    "煤炭": {"code": "399998", "name": "中证煤炭指数", "exchange": "szse"},
    "白酒": {"code": "399997", "name": "中证白酒指数", "exchange": "szse"},
    "军工": {"code": "399967", "name": "中证军工指数", "exchange": "szse"},
    "人工智能": {"code": "930713", "name": "中证人工智能指数", "exchange": "csi"},
    "储能": {"code": "931746", "name": "中证储能产业指数", "exchange": "csi"},
    "CXO": {"code": "931750", "name": "中证创新药指数", "exchange": "csi"},
}

# 基准指数
BENCHMARK_INDEX = {"code": "000300", "name": "沪深300", "exchange": "sse"}


def get_index_return(index_code: str, start_date: str, end_date: str) -> float:
    """
    获取指定指数在时间段内的收益率
    
    Args:
        index_code: 指数代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        区间收益率 (%)
    """
    try:
        df = ak.index_zh_a_hist(
            symbol=index_code,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", "")
        )
        
        if df.empty or len(df) < 2:
            return None
            
        start_price = df.iloc[0]['收盘']
        end_price = df.iloc[-1]['收盘']
        return_rate = (end_price - start_price) / start_price * 100
        
        return round(return_rate, 2)
    except Exception as e:
        print(f"获取指数 {index_code} 数据失败: {e}")
        return None


def calculate_backtest_metrics(
    industry_name: str,
    start_date: str,
    hold_years: int = 1
) -> Dict:
    """
    计算单个行业的回测指标
    
    Args:
        industry_name: 行业名称（需在 INDUSTRY_INDEX_MAP 中）
        start_date: 回测起点 (YYYY-MM-DD)
        hold_years: 持有年限，默认1年
    
    Returns:
        包含各项指标的字典
    """
    if industry_name not in INDUSTRY_INDEX_MAP:
        return {"error": f"未找到行业 '{industry_name}' 的指数映射，请先添加"}
    
    # 计算结束日期
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime(start_dt.year + hold_years, start_dt.month, start_dt.day)
    end_date = end_dt.strftime("%Y-%m-%d")
    
    index_info = INDUSTRY_INDEX_MAP[industry_name]
    
    # 获取行业指数收益
    industry_return = get_index_return(index_info["code"], start_date, end_date)
    
    # 获取沪深300收益
    benchmark_return = get_index_return(BENCHMARK_INDEX["code"], start_date, end_date)
    
    if industry_return is None or benchmark_return is None:
        return {"error": "数据获取失败"}
    
    # 计算相对收益
    relative_return = round(industry_return - benchmark_return, 2)
    
    return {
        "行业名称": industry_name,
        "指数名称": index_info["name"],
        "回测起点": start_date,
        "回测终点": end_date,
        "行业指数涨幅": industry_return,
        "沪深300涨幅": benchmark_return,
        "相对收益": relative_return,
        "是否跑赢大盘": "是" if relative_return > 0 else "否"
    }


def batch_backtest(
    test_cases: List[Tuple[str, str]]
) -> pd.DataFrame:
    """
    批量回测多个行业
    
    Args:
        test_cases: [(行业名称, 开始日期), ...]
    
    Returns:
        DataFrame 包含所有回测结果
    """
    results = []
    
    for industry, start_date in test_cases:
        print(f"正在计算: {industry} ({start_date})...")
        result = calculate_backtest_metrics(industry, start_date)
        if "error" not in result:
            results.append(result)
    
    return pd.DataFrame(results)


def validate_prediction(
    predicted_type: str,
    actual_return: float,
    benchmark_return: float
) -> str:
    """
    验证预测准确性
    
    Args:
        predicted_type: 预测的组合类型
        actual_return: 实际行业收益
        benchmark_return: 基准收益
    
    Returns:
        准确性判定结果
    """
    relative = actual_return - benchmark_return
    
    # 定义各类型的预期收益特征
    type_expectations = {
        "红利交叠期": {"min_relative": 10, "direction": "positive"},
        "高风险押宝期": {"min_relative": -5, "direction": "neutral"},  # 高波动，难预测
        "红利退坡期": {"min_relative": -999, "max_relative": 0, "direction": "negative"},
        "红利消失期": {"min_relative": -999, "max_relative": -5, "direction": "negative"},
    }
    
    if predicted_type not in type_expectations:
        return "未知类型"
    
    exp = type_expectations[predicted_type]
    
    # 判断准确性
    if predicted_type == "红利交叠期":
        if relative > 10:
            return "准确"
        elif relative > 0:
            return "基本准确"
        else:
            return "偏差"
    
    elif predicted_type == "红利消失期":
        if relative < -10:
            return "准确"
        elif relative < 0:
            return "基本准确"
        else:
            return "反例"
    
    elif predicted_type == "红利退坡期":
        if relative < -5:
            return "准确"
        elif relative < 5:
            return "基本准确"
        else:
            return "偏差"
    
    else:  # 高风险押宝期
        return "待观察"  # 波动大，单独评估


# 示例：快速测试
if __name__ == "__main__":
    # 测试案例：新能源汽车 2020年6月
    print("=" * 50)
    print("马江博周期框架回测数据收集工具")
    print("=" * 50)
    
    # 单个测试
    result = calculate_backtest_metrics("新能源汽车", "2020-06-01")
    print("\n单行业测试结果:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    
    # 批量测试
    print("\n" + "=" * 50)
    print("批量回测示例:")
    print("=" * 50)
    
    test_cases = [
        ("新能源汽车", "2020-06-01"),
        ("光伏", "2021-01-01"),
        ("煤炭", "2021-06-01"),
        ("房地产", "2021-06-01"),
        ("互联网", "2021-03-01"),
    ]
    
    df = batch_backtest(test_cases)
    print("\n批量回测结果:")
    print(df.to_string(index=False))
    
    # 保存结果
    output_path = "data/backtest_auto_result.csv"
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n结果已保存至: {output_path}")
