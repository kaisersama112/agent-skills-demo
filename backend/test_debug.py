import sys
import os
import asyncio
from capability_orchestration import skill_registry
from services.llm_service import LLMService

async def test_llm_output():
    """测试LLM输出"""
    print("=== 测试LLM输出 ===")
    
    test_queries = [
        "帮我创建一个PPT演示文稿",
        "生成一个PDF文件",
        "设计一个Canvas画布应用",
        "编辑一个Word文档",
        "创建一个Excel表格"
    ]
    
    llm_service = LLMService()
    
    for query in test_queries:
        print(f"\n查询: {query}")
        
        # 构建技能列表
        skill_list = []
        for name, metadata in skill_registry.skill_metadata.items():
            skill_list.append({
                "name": metadata.get("name", name),
                "description": metadata.get("description", "")
            })
        
        import json
        skills_json = json.dumps(skill_list, ensure_ascii=False, indent=2)
        
        prompt = f"""
你是一个智能技能选择器。根据用户输入，从以下可用技能中选择最合适的一个。

可用技能列表：
{skills_json}

要求：
1. 分析用户输入的意图
2. 从可用技能中选择最匹配的技能
3. 如果没有匹配的技能，返回 "none"
4. 只返回技能名称（与列表中的name字段完全一致），不要返回其他内容

用户输入：{query}

请选择最合适的技能：
        """
        
        try:
            response = await llm_service.generate(prompt, temperature=0.0)
            print(f"LLM输出: '{response.strip()}'")
        except Exception as e:
            print(f"错误: {str(e)}")

async def test_full_flow():
    """测试完整流程：意图解析 → 能力编排 → Skill执行"""
    print("=== 测试完整流程 ===")
    
    # 1. 测试LLM意图识别和技能选择
    test_queries = [
        "帮我创建一个PPT演示文稿",
        "生成一个PDF文件",
        "设计一个Canvas画布应用",
        "编辑一个Word文档",
        "创建一个Excel表格"
    ]
    
    for query in test_queries:
        print(f"\n测试查询: {query}")
        
        # 2. 自动选择技能
        try:
            skill = await skill_registry.select_skill_by_llm(query)
            
            if skill:
                print(f"✅ 选择的技能: {skill.name} - {skill.description}")
                
                # 3. 加载技能内容（测试渐进式披露）
                referenced_files = skill.get_referenced_files()
                if referenced_files:
                    print(f"📄 引用的文件: {referenced_files}")
                
                # 4. 测试技能执行
                test_input = {
                    "session_id": "test_session_123",
                    "user_input": query,
                    "context": {"test": "data"}
                }
                
                result = await skill.run(test_input)
                print(f"执行结果: {result}")
            else:
                print("❌ 未找到合适的技能")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_llm_output())
    asyncio.run(test_full_flow())
