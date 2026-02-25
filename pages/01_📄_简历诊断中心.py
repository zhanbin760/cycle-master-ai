import streamlit as st
import re
import sys
import os

# 确保能正确引入 utils 模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.llm_engine import render_api_key_input, render_privacy_notice, get_deepseek_client, increment_usage
from utils.rag_engine import get_rag_engine
from utils.data_processor import load_industry_data, get_growth_industries

st.set_page_config(page_title="简历诊断中心", page_icon="📄", layout="wide")

st.title("📄 简历诊断中心：AI识别行业风险并推荐方向")
st.markdown("粘贴您的简历内容，AI将提取您的过往行业经历，自动与周期数据库对比，识别风险并推荐适合的转型方向。")

# 渲染 API Key 和隐私声明
render_api_key_input()
render_privacy_notice()

# ==========================================
# 隐私提示
# ==========================================
st.info("🔒 **隐私声明**：粘贴的简历内容仅用于本次分析，不会被存储。所有数据处理在会话结束后立即清除。")

# ==========================================
# 简历粘贴区域
# ==========================================
st.markdown("### ✏️ 粘贴简历内容")

resume_text = st.text_area(
    "请粘贴您的简历内容（工作经历、项目经验等）：",
    height=300,
    placeholder="""例如：
【工作经历】
2018.06 - 2022.03  某地产公司  项目经理
负责房地产开发项目的全流程管理，包括规划设计、施工监理、成本控制等。

2022.04 - 至今    某建筑公司  高级工程师
负责建筑结构设计，参与多个大型商业综合体项目。

【教育背景】
2014.09 - 2018.06  某大学  土木工程  本科

【技能】
项目管理、AutoCAD、结构设计、成本控制
"""
)

# ==========================================
# 快速行业选择（可选）
# ==========================================
st.markdown("### 🏭 或选择您所在的行业")

# 常用行业列表
common_industries = [
    "房地产", "建筑", "互联网", "金融", "制造业", 
    "教育", "医疗", "零售", "能源", "传媒"
]

col1, col2 = st.columns(2)
with col1:
    selected_industry = st.selectbox(
        "选择您所在的行业（可选）：",
        ["自动识别"] + common_industries + ["其他"]
    )

with col2:
    if selected_industry == "其他":
        custom_industry = st.text_input("请输入您的行业：")
    else:
        custom_industry = ""

# ==========================================
# 简历解析函数
# ==========================================
def parse_resume_with_llm(resume_text: str) -> dict:
    """使用LLM解析简历内容"""
    if not resume_text or len(resume_text.strip()) < 20:
        return {"error": "简历内容太短，无法解析"}
    
    client = get_deepseek_client()
    
    prompt = f"""请从以下简历中提取关键信息，以JSON格式返回：

简历内容：
{resume_text[:4000]}

请提取以下字段：
1. industries: 行业经历列表（每个包含 name行业名称, period时间段, role职位）
2. skills: 核心技能列表（字符串数组）
3. total_years: 工作年限（数字或字符串）
4. education: 最高学历
5. current_role: 当前/最近职位

注意：
- 如果找不到某字段，返回空字符串或空数组
- 行业名称请尽量标准，如"房地产"、"互联网"、"金融"等
- 必须返回有效的JSON格式

返回示例：
{{
    "industries": [
        {{"name": "房地产", "period": "2018-2022", "role": "项目经理"}},
        {{"name": "建筑", "period": "2022-至今", "role": "高级工程师"}}
    ],
    "skills": ["项目管理", "工程管理", "团队协调"],
    "total_years": "6年",
    "education": "本科",
    "current_role": "高级工程师"
}}"""
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的简历解析助手，擅长从简历中提取结构化信息，只返回JSON格式。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        import json
        result_text = response.choices[0].message.content
        
        # 尝试提取JSON
        try:
            # 查找JSON代码块
            json_block = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_block:
                return json.loads(json_block.group(1))
            
            # 查找普通JSON对象
            json_match = re.search(r'\{[\s\S]*\}', result_text)
            if json_match:
                return json.loads(json_match.group())
            
            # 直接解析
            return json.loads(result_text)
        except json.JSONDecodeError:
            return {
                "industries": [],
                "skills": [],
                "parse_error": True,
                "raw_response": result_text
            }
            
    except Exception as e:
        return {"error": str(e)}


def extract_industries_from_text(text: str) -> list:
    """从文本中提取行业关键词（备用方案）"""
    industry_keywords = {
        "房地产": ["房地产", "地产", "置业", "万科", "碧桂园", "恒大"],
        "建筑": ["建筑", "施工", "基建", "中建", "中铁", "承包商"],
        "互联网": ["互联网", "IT", "软件", "阿里", "腾讯", "字节", "美团"],
        "金融": ["金融", "银行", "证券", "保险", "基金", "投资"],
        "制造业": ["制造", "生产", "工厂", "工业", "汽车", "电子"],
        "教育": ["教育", "培训", "学校", "教培", "新东方", "学而思"],
        "医疗": ["医疗", "医药", "医院", "制药", "器械", "健康"],
        "零售": ["零售", "电商", "超市", "商场", "销售", "贸易"],
        "能源": ["能源", "电力", "石油", "煤炭", "新能源", "光伏"],
        "传媒": ["传媒", "广告", "媒体", "影视", "出版", "新闻"],
    }
    
    found_industries = []
    for industry, keywords in industry_keywords.items():
        for keyword in keywords:
            if keyword in text:
                found_industries.append(industry)
                break
    
    return list(set(found_industries))  # 去重


# ==========================================
# 行业风险分析
# ==========================================
def analyze_industry_risks(industries: list) -> dict:
    """分析行业风险"""
    rag_engine = get_rag_engine()
    
    risk_analysis = {
        "高风险": [],
        "中风险": [],
        "低风险": [],
        "未识别": []
    }
    
    for industry in industries:
        results = rag_engine.search_industry(industry, top_k=1)
        if results:
            result = results[0]
            stage = result['当前周期阶段']
            sentiment = result['未来1-3年景气度']
            
            if stage in ['调整期', '衰退期'] or '承压' in sentiment:
                risk_analysis["高风险"].append({
                    "industry": industry,
                    "stage": stage,
                    "sentiment": sentiment,
                    "warning": rag_engine.get_risk_warning(industry)
                })
            elif stage == '成熟期' and '平稳' in sentiment:
                risk_analysis["中风险"].append({
                    "industry": industry,
                    "stage": stage,
                    "sentiment": sentiment
                })
            else:
                risk_analysis["低风险"].append({
                    "industry": industry,
                    "stage": stage,
                    "sentiment": sentiment
                })
        else:
            risk_analysis["未识别"].append(industry)
    
    return risk_analysis


# ==========================================
# 推荐转型方向
# ==========================================
def get_transition_recommendations(current_industries: list, skills: list = None) -> list:
    """获取转型推荐"""
    rag_engine = get_rag_engine()
    df = load_industry_data()
    
    growth_industries = get_growth_industries(df)
    
    recommendations = []
    
    # 行业映射关系
    skill_mappings = {
        "房地产": ["智慧城市", "养老产业", "物业管理", "房地产科技"],
        "建筑": ["光伏基建", "储能", "虚拟电厂", "智能建造"],
        "传统制造": ["智能制造", "工业机器人", "新能源装备", "半导体设备"],
        "教培": ["职业教育", "企业培训", "知识付费", "教育科技"],
        "互联网": ["人工智能", "SaaS", "产业互联网", "云计算"],
        "金融": ["金融科技", "绿色金融", "数字人民币", "区块链金融"],
        "传媒": ["短视频", "直播电商", "AIGC内容", "数字营销"],
        "能源": ["新能源", "储能", "氢能", "碳中和"],
        "零售": ["电商", "直播带货", "跨境电商", "新零售"],
        "医疗": ["生物医药", "医疗器械", "数字医疗", "AI医疗"]
    }
    
    for industry in current_industries:
        for key, targets in skill_mappings.items():
            if key in industry:
                for target in targets:
                    target_data = rag_engine.search_industry(target, top_k=1)
                    if target_data:
                        cycle_stage = target_data[0]['当前周期阶段']
                        if cycle_stage in ['成长期', '初创期']:
                            recommendations.append({
                                "from": industry,
                                "to": target,
                                "reason": f"{key}行业经验可迁移至{target}",
                                "cycle_stage": cycle_stage,
                                "sentiment": target_data[0]['未来1-3年景气度']
                            })
    
    # 如果没有特定匹配，返回通用推荐
    if not recommendations:
        for ind in growth_industries[:5]:
            recommendations.append({
                "from": current_industries[0] if current_industries else "当前行业",
                "to": ind['行业名称'],
                "reason": "当前处于成长期，人才需求旺盛",
                "cycle_stage": ind['周期阶段'],
                "sentiment": ind['景气度']
            })
    
    # 去重
    seen = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec['to'] not in seen:
            seen.add(rec['to'])
            unique_recommendations.append(rec)
    
    return unique_recommendations[:5]


# ==========================================
# 诊断按钮
# ==========================================
st.markdown("---")

if st.button("🔍 开始简历诊断", use_container_width=True, type="primary"):
    # 确定使用的行业信息
    if selected_industry == "自动识别":
        industries_from_select = []
    elif selected_industry == "其他":
        industries_from_select = [custom_industry] if custom_industry else []
    else:
        industries_from_select = [selected_industry]
    
    # 检查是否有输入
    if not resume_text.strip() and not industries_from_select:
        st.error("⚠️ 请粘贴简历内容或选择您所在的行业")
    else:
        with st.spinner("正在分析简历并识别行业风险..."):
            try:
                increment_usage()
                
                # 解析简历
                if resume_text.strip():
                    st.info("📝 正在解析简历内容...")
                    parsed = parse_resume_with_llm(resume_text)
                    
                    # 如果LLM解析失败，使用备用方案
                    if parsed.get("error") or parsed.get("parse_error"):
                        st.warning("使用备用识别方案...")
                        extracted = extract_industries_from_text(resume_text)
                        parsed = {
                            "industries": [{"name": ind, "period": "", "role": ""} for ind in extracted],
                            "skills": [],
                            "total_years": "",
                            "education": "",
                            "current_role": ""
                        }
                else:
                    parsed = {"industries": [], "skills": [], "total_years": "", "education": "", "current_role": ""}
                
                # 合并行业信息
                parsed_industries = [ind.get("name", "") for ind in parsed.get("industries", []) if isinstance(ind, dict)]
                all_industries = list(set(industries_from_select + parsed_industries))
                
                # 显示解析结果
                st.markdown("---")
                st.markdown("### 📋 解析结果")
                
                result_cols = st.columns(2)
                
                with result_cols[0]:
                    st.markdown("**🎯 识别到的行业：**")
                    if all_industries:
                        for ind in all_industries:
                            st.markdown(f"- **{ind}**")
                    else:
                        st.markdown("*未能识别到行业信息*")
                    
                    if parsed.get("total_years"):
                        st.markdown(f"\n**⏱️ 工作年限：** {parsed['total_years']}")
                    if parsed.get("current_role"):
                        st.markdown(f"**💼 当前职位：** {parsed['current_role']}")
                
                with result_cols[1]:
                    st.markdown("**🛠️ 识别到的技能：**")
                    skills = parsed.get("skills", [])
                    if skills:
                        for skill in skills[:10]:  # 最多显示10个
                            st.markdown(f"- {skill}")
                    else:
                        st.markdown("*未能识别到技能信息*")
                
                # 风险分析
                if all_industries:
                    st.markdown("---")
                    st.markdown("### ⚠️ 行业风险分析")
                    
                    risk_analysis = analyze_industry_risks(all_industries)
                    
                    risk_cols = st.columns(4)
                    
                    with risk_cols[0]:
                        count = len(risk_analysis['高风险'])
                        st.error(f"🔴 高风险：{count} 个")
                    with risk_cols[1]:
                        count = len(risk_analysis['中风险'])
                        st.warning(f"🟡 中风险：{count} 个")
                    with risk_cols[2]:
                        count = len(risk_analysis['低风险'])
                        st.success(f"🟢 低风险：{count} 个")
                    with risk_cols[3]:
                        count = len(risk_analysis['未识别'])
                        st.info(f"⚪ 未识别：{count} 个")
                    
                    # 详细风险信息
                    if risk_analysis["高风险"]:
                        st.markdown("---")
                        st.error("🚨 **红色预警：检测到高风险行业！**")
                        
                        for item in risk_analysis["高风险"]:
                            warning = item.get('warning', {})
                            with st.container(border=True):
                                st.markdown(f"**{item['industry']}** - {item['stage']}")
                                st.markdown(f"景气度：**{item['sentiment']}**")
                                if warning:
                                    st.markdown(f"💡 **建议**：{warning.get('建议', '建议尽早规划转型')}")
                                    
                                    # 显示推荐转型方向
                                    if warning.get('推荐方向'):
                                        st.markdown("**推荐方向**：")
                                        for rec in warning['推荐方向'][:3]:
                                            st.markdown(f"- {rec['行业名称']}（{rec['周期阶段']}）")
                    
                    if risk_analysis["中风险"]:
                        with st.expander(f"🟡 中风险行业详情 ({len(risk_analysis['中风险'])}个)"):
                            for item in risk_analysis["中风险"]:
                                st.markdown(f"- **{item['industry']}**：{item['stage']}，{item['sentiment']}")
                    
                    # 转型推荐
                    st.markdown("---")
                    st.markdown("### 🎯 转型推荐方向")
                    
                    recommendations = get_transition_recommendations(all_industries, skills)
                    
                    if recommendations:
                        st.success("基于您的行业背景和周期数据，推荐以下转型方向：")
                        
                        for i, rec in enumerate(recommendations, 1):
                            with st.container(border=True):
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.markdown(f"#### {i}. **{rec['to']}**")
                                    st.markdown(f"- **推荐理由**：{rec['reason']}")
                                    st.markdown(f"- **周期阶段**：{rec['cycle_stage']} | **景气度**：{rec['sentiment']}")
                                with cols[1]:
                                    if st.button(f"查看详情", key=f"btn_detail_{i}"):
                                        st.session_state['target_industry'] = rec['to']
                                        st.switch_page("pages/03_🤖_AI协同规划官.py")
                    else:
                        st.info("未能生成转型推荐，建议咨询AI规划官获取个性化建议")
                    
                    # AI深度分析
                    st.markdown("---")
                    st.markdown("### 🤖 AI深度分析报告")
                    
                    with st.spinner("正在生成深度分析报告..."):
                        increment_usage()
                        
                        client = get_deepseek_client()
                        
                        analysis_prompt = f"""请基于以下信息，为用户提供深度职业分析和建议：

识别到的行业：{all_industries}
工作年限：{parsed.get('total_years', '未知')}
当前职位：{parsed.get('current_role', '未知')}
技能：{parsed.get('skills', [])}
风险分析：高风险{len(risk_analysis['高风险'])}个，中风险{len(risk_analysis['中风险'])}个

请提供以下分析：
1. 当前职业路径的周期定位（基于马江博周期共振理论）
2. 所处行业的风险收益评估
3. 具体的转型建议（目标行业、时间规划、技能准备）
4. 未来3-5年的职业发展策略
5. 行动优先级清单（最近3个月、6个月、1年）

要求：
- 所有建议必须基于周期理论
- 给出具体可执行的行动建议
- 如果当前行业处于风险期，必须明确提示"建议尽早转型"
"""
                        
                        messages = [
                            {"role": "system", "content": "你是Cycle-Master AI职业规划专家，基于马江博周期共振理论进行分析。输出要结构化、有理有据。"},
                            {"role": "user", "content": analysis_prompt}
                        ]
                        
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=messages,
                            temperature=0.6,
                            max_tokens=3000
                        )
                        
                        st.markdown(response.choices[0].message.content)
                
                else:
                    st.warning("未能从简历中识别出行业信息。请尝试直接选择行业，或提供更详细的工作经历描述。")
                    
            except Exception as e:
                st.error(f"诊断过程中出现错误: {str(e)}")
                st.info("请尝试简化简历内容后重新提交，或直接选择行业进行分析")

# ==========================================
# 快捷行业查询
# ==========================================
st.markdown("---")

with st.expander("🔍 快捷查询：不粘贴简历，直接查询行业风险"):
    query_col1, query_col2 = st.columns([2, 1])
    
    with query_col1:
        query_industry = st.text_input("输入行业名称：", placeholder="例如：传统地产、教培、煤炭")
    
    with query_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        query_btn = st.button("🔍 查询风险", use_container_width=True)
    
    if query_btn and query_industry:
        rag_engine = get_rag_engine()
        results = rag_engine.search_industry(query_industry, top_k=1)
        
        if results:
            result = results[0]
            
            st.markdown("---")
            st.markdown(f"### 📊 {result['行业名称']} 周期诊断")
            
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("周期阶段", result['当前周期阶段'])
            with metric_cols[1]:
                st.metric("未来景气度", result['未来1-3年景气度'])
            with metric_cols[2]:
                combo = rag_engine.get_cycle_combination(result['当前周期阶段'])
                st.metric("周期组合", combo.get('组合名称', '未知'))
            
            st.markdown(f"**评价**：{result['评价']}")
            
            warning = rag_engine.get_risk_warning(query_industry)
            if warning:
                st.error(f"🚨 **{warning['风险等级']}**：{warning['预警类型']}")
                st.markdown(f"**💡 建议**：{warning['建议']}")
                
                if warning.get('推荐方向'):
                    st.markdown("**📌 推荐转型方向**：")
                    for rec in warning['推荐方向'][:3]:
                        st.markdown(f"- **{rec['行业名称']}**（{rec['周期阶段']}）- {rec['推荐理由']}")
            else:
                st.success("✅ 该行业当前风险较低，处于正常发展期")
        else:
            st.warning(f"未找到'{query_industry}'的行业数据。请尝试其他关键词，如：房地产、互联网、新能源等")
