"""
RAG (检索增强生成) 引擎
实现CSV知识库的精准检索与上下文注入
"""

import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
import re


class IndustryRAGEngine:
    """
    行业周期知识库检索引擎
    基于《细分领域行业周期研判表.csv》实现精准匹配
    """
    
    def __init__(self, csv_path: str = "data/细分领域行业周期研判表.csv"):
        """
        初始化RAG引擎
        
        Args:
            csv_path: 行业周期数据CSV文件路径
        """
        self.csv_path = csv_path
        self.df = self._load_data()
        self.cycle_theory = self._load_cycle_theory()
    
    def _load_data(self) -> pd.DataFrame:
        """加载并清洗行业周期数据"""
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            # 清洗数据
            df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
            df = df.dropna(how='all')
            df = df.fillna("暂无评价")
            return df
        except Exception as e:
            st.error(f"加载行业数据失败: {e}")
            return pd.DataFrame()
    
    def _load_cycle_theory(self) -> Dict:
        """
        加载马江博周期理论映射
        根据周期阶段返回对应的应对策略
        """
        return {
            "初创期": {
                "特征": "技术突破，市场教育阶段，渗透率低于5%",
                "机会": "早期进入者可能获得超额回报",
                "风险": "技术路线不确定，市场接受度未知",
                "策略": "适合风险偏好高、学习能力强的求职者；关注技术迭代和资本动向",
                "典型行业": "低空经济、脑机接口、量子计算"
            },
            "成长期": {
                "特征": "渗透率快速提升(5%-30%)，资本大量涌入",
                "机会": "行业红利释放，人才需求爆发",
                "风险": "竞争加剧，后期进入者成本上升",
                "策略": "最佳入场时机；重点积累行业核心技能；选择头部或高成长企业",
                "典型行业": "人工智能、新能源汽车、储能"
            },
            "成熟期": {
                "特征": "增速放缓，竞争格局稳定，头部效应明显",
                "机会": "岗位稳定，薪资基准较高",
                "风险": "晋升天花板明显，内卷加剧",
                "策略": "深耕细分领域成为专家；或向上下游延伸；储备转型能力",
                "典型行业": "医药流通、传统消费电子"
            },
            "调整期": {
                "特征": "产能过剩，政策收紧，行业洗牌",
                "机会": "并购整合中的管理岗位",
                "风险": "裁员风险高，薪资下滑",
                "策略": "尽早规划转型；向相关成长期行业迁移技能；避免长期停留",
                "典型行业": "传统地产、水泥、光伏(当前)"
            },
            "衰退期": {
                "特征": "需求萎缩，政策压降，产能出清",
                "机会": "极少",
                "风险": "失业风险极高",
                "策略": "立即启动转型；利用可迁移技能转向相关行业",
                "典型行业": "传统教培(双减后)、P2P"
            }
        }
    
    def search_industry(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        检索行业信息
        
        Args:
            query: 用户输入的行业名称或关键词
            top_k: 返回最相关的K条结果
            
        Returns:
            匹配的行业信息列表
        """
        if self.df.empty:
            return []
        
        results = []
        query_lower = query.lower()
        
        # 1. 精确匹配
        exact_match = self.df[self.df['行业名称'].str.lower() == query_lower]
        if not exact_match.empty:
            for _, row in exact_match.iterrows():
                results.append(self._format_industry_record(row, match_type="精确匹配"))
        
        # 2. 包含匹配
        if len(results) < top_k:
            contain_match = self.df[
                self.df['行业名称'].str.contains(query, case=False, na=False) &
                ~self.df['行业名称'].str.lower().isin([r['行业名称'].lower() for r in results])
            ]
            for _, row in contain_match.head(top_k - len(results)).iterrows():
                results.append(self._format_industry_record(row, match_type="包含匹配"))
        
        # 3. 模糊匹配（关键词分割）
        if len(results) < top_k:
            keywords = re.findall(r'[\u4e00-\u9fff]+', query)
            for keyword in keywords:
                if len(keyword) >= 2:
                    fuzzy_match = self.df[
                        self.df['行业名称'].str.contains(keyword, case=False, na=False) &
                        ~self.df['行业名称'].str.lower().isin([r['行业名称'].lower() for r in results])
                    ]
                    for _, row in fuzzy_match.head(top_k - len(results)).iterrows():
                        results.append(self._format_industry_record(row, match_type="相关匹配"))
                    if len(results) >= top_k:
                        break
        
        return results[:top_k]
    
    def _format_industry_record(self, row: pd.Series, match_type: str = "") -> Dict:
        """格式化行业记录"""
        stage = row.get('当前周期阶段', '未知')
        theory = self.cycle_theory.get(stage, {})
        
        return {
            "序号": row.get('序号', ''),
            "行业名称": row.get('行业名称', ''),
            "当前周期阶段": stage,
            "未来1-3年景气度": row.get('未来1-3年景气度', '未知'),
            "评价": row.get('评价', ''),
            "匹配类型": match_type,
            "理论建议": theory
        }
    
    def get_cycle_combination(self, industry_stage: str, policy_stage: str = None) -> Dict:
        """
        获取周期组合类型
        
        Args:
            industry_stage: 产业周期阶段
            policy_stage: 政策周期阶段（可选）
            
        Returns:
            组合类型及建议
        """
        # 四种典型组合
        combinations = {
            ("初创期", "规划引导期"): {
                "组合名称": "高风险押宝期",
                "风险等级": "🔴 高风险",
                "特征": "技术未验证 + 政策刚出台",
                "适合人群": "风险偏好高、抗压能力强的早期探索者",
                "策略": "小步试错，关注技术突破信号"
            },
            ("成长期", "资源聚焦期"): {
                "组合名称": "红利交叠期",
                "风险等级": "🟢 最佳时机",
                "特征": "渗透率快速提升 + 政策资金涌入",
                "适合人群": "绝大多数求职者，尤其是转型者",
                "策略": "果断入场，积累核心技能，选择高成长企业"
            },
            ("成熟期", "调整退出期"): {
                "组合名称": "红利退坡期",
                "风险等级": "🟡 谨慎",
                "特征": "增速放缓 + 政策收紧",
                "适合人群": "追求稳定的资深从业者",
                "策略": "防御性规划，储备转型能力，关注细分机会"
            },
            ("调整期", "政策压降期"): {
                "组合名称": "红利消失期",
                "风险等级": "🔴 高危",
                "特征": "产能过剩 + 明确限制",
                "适合人群": "不建议进入",
                "策略": "尽早离场，利用可迁移技能转型"
            },
            ("衰退期", "政策压降期"): {
                "组合名称": "红利消失期",
                "风险等级": "🔴 高危",
                "特征": "需求萎缩 + 政策出清",
                "适合人群": "不建议进入",
                "策略": "立即启动转型计划"
            }
        }
        
        # 尝试匹配
        if policy_stage:
            key = (industry_stage, policy_stage)
            if key in combinations:
                return combinations[key]
        
        # 基于产业周期阶段返回默认建议
        stage_advice = {
            "初创期": combinations.get(("初创期", "规划引导期")),
            "成长期": combinations.get(("成长期", "资源聚焦期")),
            "成熟期": combinations.get(("成熟期", "调整退出期")),
            "调整期": combinations.get(("调整期", "政策压降期")),
            "衰退期": combinations.get(("衰退期", "政策压降期"))
        }
        
        return stage_advice.get(industry_stage, {
            "组合名称": "未知组合",
            "风险等级": "⚪ 未知",
            "特征": "无法判断",
            "适合人群": "未知",
            "策略": "建议进一步调研"
        })
    
    def build_context_for_llm(self, industry_name: str) -> str:
        """
        为LLM构建检索上下文
        
        Args:
            industry_name: 行业名称
            
        Returns:
            格式化的上下文文本
        """
        search_results = self.search_industry(industry_name, top_k=2)
        
        if not search_results:
            return f"未在知识库中找到'{industry_name}'的相关信息。请基于通用周期理论进行分析。"
        
        context_parts = []
        context_parts.append(f"【知识库检索结果】用户关注行业：{industry_name}\n")
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"\n--- 匹配结果 {i} ({result['匹配类型']}) ---")
            context_parts.append(f"行业名称：{result['行业名称']}")
            context_parts.append(f"当前周期阶段：{result['当前周期阶段']}")
            context_parts.append(f"未来1-3年景气度：{result['未来1-3年景气度']}")
            context_parts.append(f"评价：{result['评价']}")
            
            # 添加周期理论建议
            theory = result.get('理论建议', {})
            if theory:
                context_parts.append(f"\n周期理论指导：")
                context_parts.append(f"- 阶段特征：{theory.get('特征', '')}")
                context_parts.append(f"- 机会分析：{theory.get('机会', '')}")
                context_parts.append(f"- 风险提示：{theory.get('风险', '')}")
                context_parts.append(f"- 应对策略：{theory.get('策略', '')}")
            
            # 添加组合类型分析
            combo = self.get_cycle_combination(result['当前周期阶段'])
            context_parts.append(f"\n周期组合研判：")
            context_parts.append(f"- 组合类型：{combo.get('组合名称', '')} {combo.get('风险等级', '')}")
            context_parts.append(f"- 适合人群：{combo.get('适合人群', '')}")
            context_parts.append(f"- 行动建议：{combo.get('策略', '')}")
        
        context_parts.append("\n--- 分析要求 ---")
        context_parts.append("请基于以上知识库数据，结合马江博周期理论，为用户提供有理有据的职业规划建议。")
        context_parts.append("避免使用大话套话，所有建议必须基于上述数据支撑。")
        
        return "\n".join(context_parts)
    
    def get_risk_warning(self, industry_name: str) -> Optional[Dict]:
        """
        获取行业风险预警
        
        Args:
            industry_name: 行业名称
            
        Returns:
            风险预警信息，如无风险则返回None
        """
        results = self.search_industry(industry_name, top_k=1)
        if not results:
            return None
        
        result = results[0]
        stage = result['当前周期阶段']
        sentiment = result['未来1-3年景气度']
        
        # 定义风险等级
        if stage in ['调整期', '衰退期'] or '承压' in sentiment:
            return {
                "风险等级": "🔴 高风险",
                "预警类型": "行业处于下行周期",
                "当前阶段": stage,
                "景气度": sentiment,
                "建议": "建议尽早规划转型，利用现有技能向成长期行业迁移",
                "推荐方向": self._get_transition_recommendations(industry_name)
            }
        elif stage == '成熟期' and '平稳' in sentiment:
            return {
                "风险等级": "🟡 中等风险",
                "预警类型": "行业增长放缓",
                "当前阶段": stage,
                "景气度": sentiment,
                "建议": "建议做好防御性规划，储备转型能力",
                "推荐方向": []
            }
        
        return None
    
    def _get_transition_recommendations(self, current_industry: str) -> List[Dict]:
        """
        获取转型推荐方向
        
        Args:
            current_industry: 当前行业
            
        Returns:
            推荐的转型方向列表
        """
        if self.df.empty:
            return []
        
        # 获取成长期行业作为推荐
        growth_industries = self.df[
            self.df['当前周期阶段'].isin(['成长期', '初创期']) &
            self.df['未来1-3年景气度'].str.contains('高成长|高', na=False)
        ].head(5)
        
        recommendations = []
        for _, row in growth_industries.iterrows():
            recommendations.append({
                "行业名称": row['行业名称'],
                "周期阶段": row['当前周期阶段'],
                "景气度": row['未来1-3年景气度'],
                "推荐理由": row['评价']
            })
        
        return recommendations


@st.cache_resource
def get_rag_engine() -> IndustryRAGEngine:
    """获取RAG引擎单例（带缓存）"""
    return IndustryRAGEngine()
