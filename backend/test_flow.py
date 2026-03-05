import sys
import os



import asyncio
from capability_orchestration import skill_registry

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
    asyncio.run(test_full_flow())
