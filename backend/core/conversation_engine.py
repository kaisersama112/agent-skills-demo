from typing import Dict, List, Optional, Any
from backend.core.llm_client import llm_client
from backend.core.tool_manager import tool_manager
from backend.agents.skill_manager import skill_manager
from backend.models.schemas import IntentResult, IntentType, Session, Message
import json
import uuid


class ConversationEngine:
    def __init__(self):
        self.intent_prompt = """你是一个意图识别助手。请分析用户输入，识别用户意图并返回JSON格式结果。

用户输入: {user_message}

请返回以下格式的JSON:
{{
    "intent": "generate_app|chat|query|action",
    "domain": "应用领域（如fitness, finance, education等，可为空）",
    "components": ["需要的UI组件列表，如input_form, chart, calculator等"],
    "reason": "意图识别理由"
}}

只返回JSON，不要其他内容。"""
        
        self.system_prompt = f"""你是一个智能助手，能够使用技能来解决用户问题。

可用技能:
{skill_manager.get_skill_descriptions()}

当你需要领域专业知识时，可以使用Skill工具加载相应的技能。"""

    async def process_message(self, message: str, session: Optional[Session] = None) -> IntentResult:
        intent_result = await self.detect_intent(message)
        
        if session:
            session.messages.append(Message(role="user", content=message))
        
        return intent_result

    async def detect_intent(self, text: str) -> IntentResult:
        print(f"\n=== 意图检测开始 ===")
        print(f"用户输入: {text}")
        
        prompt = self.intent_prompt.format(user_message=text)
        print(f"生成的提示: {prompt}")
        
        messages = [
            {"role": "system", "content": "你是一个专业的意图识别助手。"},
            {"role": "user", "content": prompt}
        ]
        print(f"发送给LLM的消息: {messages}")
        
        try:
            print("调用LLM进行意图识别...")
            result = await llm_client.chat_json(messages)
            print(f"LLM返回结果: {result}")
            
            intent_str = result.get("intent", "chat")
            print(f"识别的意图字符串: {intent_str}")
            
            if intent_str not in [e.value for e in IntentType]:
                print(f"意图 '{intent_str}' 不在有效列表中，使用默认值 'chat'")
                intent_str = "chat"
            
            intent_result = IntentResult(
                intent=IntentType(intent_str),
                domain=result.get("domain"),
                components=result.get("components", []),
                raw_output=json.dumps(result)
            )
            print(f"意图检测成功: {intent_result}")
            print(f"=== 意图检测完成 ===\n")
            return intent_result
        except Exception as e:
            error_message = f"意图检测失败: {str(e)}"
            print(error_message)
            error_result = IntentResult(
                intent=IntentType.CHAT,
                domain=None,
                components=[],
                raw_output=f"Error: {str(e)}"
            )
            print(f"返回错误结果: {error_result}")
            print(f"=== 意图检测完成 ===\n")
            return error_result
    
    async def chat_with_skills(self, message: str, session: Optional[Session] = None) -> Dict[str, Any]:
        """带技能支持的聊天"""
        # 构建消息历史
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        if session and session.messages:
            for msg in session.messages:
                messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": message})
        
        # 获取工具列表
        tools = tool_manager.get_tools()
        
        # 首次调用
        response = await llm_client.chat_with_tools(messages, tools)
        
        # 处理工具调用
        while response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # 执行工具
                tool_result = tool_manager.execute_tool(tool_name, tool_args)
                print(f"Tool {tool_name} called with args {tool_args} -> Result: {tool_result}")
                # 将工具结果添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }]
                })
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result
                })
            
            # 继续对话
            response = await llm_client.chat_with_tools(messages, tools)
        
        # 获取最终回复
        assistant_response = response.choices[0].message.content
        
        # 更新会话
        if session:
            session.messages.append(Message(role="user", content=message))
            session.messages.append(Message(role="assistant", content=assistant_response))
        
        return {
            "response": assistant_response,
            "messages": messages
        }

    def create_session(self, user_id: str = "default_user") -> Session:
        return Session(
            id=str(uuid.uuid4()),
            user_id=user_id,
            messages=[],
            context_state={},
            metadata={
                "created_by": "conversation_engine",
                "version": "1.0"
            }
        )


conversation_engine = ConversationEngine()
