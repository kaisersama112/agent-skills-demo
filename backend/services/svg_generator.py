from typing import Dict, Optional, Any
from backend.core.llm_client import llm_client
import os
import uuid


class SvgGenerator:
    """SVG生成服务，支持生成SVG图表和diagrams"""
    
    def __init__(self):
        self.svg_prompt = """你是一个专业的SVG图表生成专家。请根据用户需求生成SVG代码。

用户需求: {requirement}

要求：
1. 生成完整的SVG代码
2. 确保SVG代码可直接使用
3. 包含适当的样式和布局
4. 确保SVG响应式
5. 提供清晰的视觉效果

请只返回SVG代码，不要其他内容。"""
        
        # 创建SVG存储目录
        self.svg_dir = os.path.join(os.getcwd(), "sandbox", "svgs")
        os.makedirs(self.svg_dir, exist_ok=True)
    
    async def generate_svg(self, requirement: str, svg_type: str = "diagram") -> Dict[str, Any]:
        """生成SVG"""
        # 生成SVG代码
        prompt = self.svg_prompt.format(requirement=requirement)
        
        messages = [
            {"role": "system", "content": "你是一个专业的SVG生成专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            svg_content = await llm_client.chat_str(messages)
            
            # 保存SVG文件
            svg_id = str(uuid.uuid4())
            svg_path = os.path.join(self.svg_dir, f"{svg_id}.svg")
            
            with open(svg_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            # 生成SVG URL
            svg_url = f"/svgs/{svg_id}.svg"
            
            return {
                "success": True,
                "svg_id": svg_id,
                "url": svg_url,
                "content": svg_content,
                "type": svg_type
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_svg_path(self, svg_id: str) -> str:
        """获取SVG路径"""
        return os.path.join(self.svg_dir, f"{svg_id}.svg")


svg_generator = SvgGenerator()