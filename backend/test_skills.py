import sys
import os
import asyncio
from capability_orchestration import skill_registry

async def test_skill_registry():
    """测试技能注册表"""
    print("=== 测试技能注册表 ===")
    
    # 打印技能元数据
    print("\n1. 技能元数据:")
    for name, metadata in skill_registry.skill_metadata.items():
        print(f"  {name}: {metadata.get('description', '')[:50]}...")
    
    # 打印技能对象
    print("\n2. 技能对象:")
    for name, skill in skill_registry.skills.items():
        print(f"  {name}: {type(skill).__name__}")
    
    # 测试技能获取
    test_skill_names = ['pptx', 'pdf', 'canvas-design', 'docx', 'xlsx']
    print("\n3. 测试技能获取:")
    for name in test_skill_names:
        skill = skill_registry.get_skill(name)
        print(f"  {name}: {skill}")
    
    # 测试LLM选择
    test_queries = [
        "帮我创建一个PPT演示文稿",
        "生成一个PDF文件",
        "设计一个Canvas画布应用",
        "编辑一个Word文档",
        "创建一个Excel表格"
    ]
    
    print("\n4. 测试LLM选择:")
    for query in test_queries:
        print(f"\n  查询: {query}")
        try:
            skill = await skill_registry.select_skill_by_llm(query)
            print(f"  选择: {skill.name if skill else 'None'}")
        except Exception as e:
            print(f"  错误: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_skill_registry())
