from typing import Dict, List, Any, Optional
import openai
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置模型信息
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL_NAME = "qwen-turbo"
API_KEY = "sk-561f4f1fcfb9480898ea821083a5ba95"

if not API_KEY:
    raise ValueError("请在 .env 文件中设置 LLM_API_KEY 或直接赋值")

client = openai.OpenAI(api_key=API_KEY, base_url=BASE_URL)

class IntentParser:
    """
    意图解析层：基于大模型的自然语言理解
    负责关键词识别、槽位提取和任务规划
    """
    
    def __init__(self):
        self.intent_templates = {
            "data_tracking": {
                "keywords": ["记录", "打卡", "追踪", "监控"],
                "slots": ["item", "frequency", "unit", "goal"]
            },
            "data_analysis": {
                "keywords": ["统计", "分析", "图表", "报表"],
                "slots": ["data_type", "time_range", "chart_type", "metrics"]
            },
            "ecommerce": {
                "keywords": ["购物", "商品", "订单", "支付"],
                "slots": ["product", "price_range", "quantity", "payment_method"]
            },
            "navigation": {
                "keywords": ["导航", "路线", "地图", "位置"],
                "slots": ["origin", "destination", "mode", "departure_time"]
            }
        }
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """
        解析用户输入的意图
        
        Args:
            user_input: 用户输入的自然语言
            
        Returns:
            解析结果，包含意图类型、关键词、槽位和任务规划
        """
        # 1. 使用大模型进行深度理解
        analysis_result = self._analyze_with_llm(user_input)
        
        # 2. 提取关键词
        keywords = self._extract_keywords(user_input)
        
        # 3. 识别意图类型
        intent_type = self._identify_intent_type(keywords)
        
        # 4. 提取槽位
        slots = self._extract_slots(user_input, intent_type)
        
        # 5. 任务规划
        task_plan = self._generate_task_plan(intent_type, slots, analysis_result)
        
        return {
            "user_input": user_input,
            "intent_type": intent_type,
            "keywords": keywords,
            "slots": slots,
            "task_plan": task_plan,
            "analysis_result": analysis_result
        }
    
    def _analyze_with_llm(self, user_input: str) -> Dict[str, Any]:
        """
        使用大模型进行深度理解
        """
        prompt = f"""
请分析以下用户输入，提取核心需求、界面需求和交互逻辑：

用户输入：{user_input}

分析结果应包含：
1. 核心功能：用户需要的主要功能
2. 界面需求：需要哪些界面元素
3. 交互逻辑：用户如何与系统交互
4. 数据需求：需要哪些数据
5. 外部依赖：是否需要调用外部API

请以JSON格式返回分析结果。
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # 解析LLM返回的JSON
        import json
        try:
            result = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # 如果LLM返回的不是合法JSON，返回默认结构
            result = {
                "核心功能": "未知",
                "界面需求": [],
                "交互逻辑": "未知",
                "数据需求": [],
                "外部依赖": []
            }
        
        return result

    def _extract_keywords(self, user_input: str) -> List[str]:
        """
        提取关键词
        """
        keywords = []
        for intent_type, config in self.intent_templates.items():
            for keyword in config["keywords"]:
                if keyword in user_input:
                    keywords.append(keyword)
        return list(set(keywords))
    
    def _identify_intent_type(self, keywords: List[str]) -> str:
        """
        识别意图类型
        """
        intent_scores = {}
        for intent_type, config in self.intent_templates.items():
            score = 0
            for keyword in keywords:
                if keyword in config["keywords"]:
                    score += 1
            if score > 0:
                intent_scores[intent_type] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        else:
            return "general"
    
    def _extract_slots(self, user_input: str, intent_type: str) -> Dict[str, Any]:
        """
        提取槽位
        """
        slots = {}
        if intent_type in self.intent_templates:
            expected_slots = self.intent_templates[intent_type]["slots"]
            # 这里可以使用更复杂的槽位提取逻辑
            # 为了演示，我们使用简单的基于关键词的提取
            for slot in expected_slots:
                # 这里应该根据具体槽位类型使用不同的提取逻辑
                slots[slot] = "未知"
        return slots
    
    def _generate_task_plan(self, intent_type: str, slots: Dict[str, Any], analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成任务规划
        """
        task_plan = []
        
        # 根据意图类型生成不同的任务计划
        if intent_type == "data_tracking":
            task_plan = [
                {"id": "1", "task": "创建数据记录模块", "priority": "high"},
                {"id": "2", "task": "实现打卡功能", "priority": "high"},
                {"id": "3", "task": "添加数据统计分析", "priority": "medium"},
                {"id": "4", "task": "设计历史记录界面", "priority": "medium"}
            ]
        elif intent_type == "data_analysis":
            task_plan = [
                {"id": "1", "task": "数据收集与处理", "priority": "high"},
                {"id": "2", "task": "选择合适的图表类型", "priority": "high"},
                {"id": "3", "task": "生成数据可视化", "priority": "medium"},
                {"id": "4", "task": "添加数据分析功能", "priority": "medium"}
            ]
        elif intent_type == "ecommerce":
            task_plan = [
                {"id": "1", "task": "商品浏览模块", "priority": "high"},
                {"id": "2", "task": "购物车功能", "priority": "high"},
                {"id": "3", "task": "支付流程", "priority": "high"},
                {"id": "4", "task": "订单管理", "priority": "medium"}
            ]
        elif intent_type == "navigation":
            task_plan = [
                {"id": "1", "task": "地图集成", "priority": "high"},
                {"id": "2", "task": "路线规划", "priority": "high"},
                {"id": "3", "task": "实时导航", "priority": "medium"},
                {"id": "4", "task": "位置搜索", "priority": "medium"}
            ]
        else:
            task_plan = [
                {"id": "1", "task": "分析用户需求", "priority": "high"},
                {"id": "2", "task": "设计解决方案", "priority": "high"},
                {"id": "3", "task": "实现核心功能", "priority": "medium"},
                {"id": "4", "task": "测试与优化", "priority": "medium"}
            ]
        
        return task_plan
    
    def validate_intent(self, intent_result: Dict[str, Any]) -> bool:
        """
        验证意图解析结果
        """
        return all(key in intent_result for key in ["intent_type", "keywords", "slots", "task_plan"])
    
    def get_intent_summary(self, intent_result: Dict[str, Any]) -> str:
        """
        获取意图摘要
        """
        return f"意图类型: {intent_result['intent_type']}, 关键词: {', '.join(intent_result['keywords'])}"

# 示例用法
if __name__ == "__main__":
    parser = IntentParser()
    user_input = "讲解三角函数采用动画形式呈现"
    result = parser.parse_intent(user_input)
    print("意图解析结果:")
    print(result)