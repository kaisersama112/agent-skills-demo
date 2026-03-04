from typing import Dict, Any, List
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class CanvasDesignInput(SkillInput):
    """
    画布设计输入
    """
    design_type: str = Field(..., description="设计类型")
    width: int = Field(800, description="画布宽度")
    height: int = Field(600, description="画布高度")
    elements: List[Dict[str, Any]] = Field([], description="设计元素")


class CanvasDesignOutput(SkillOutput):
    """
    画布设计输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def canvas_design_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    画布设计执行函数
    """
    # 生成画布设计
    design = generate_canvas_design(
        input_data.get("design_type"),
        input_data.get("width", 800),
        input_data.get("height", 600),
        input_data.get("elements", [])
    )
    
    return {
        "design": design,
        "design_type": input_data.get("design_type"),
        "width": input_data.get("width", 800),
        "height": input_data.get("height", 600)
    }


def generate_canvas_design(design_type: str, width: int, height: int, elements: List[Dict[str, Any]]) -> str:
    """
    生成画布设计
    """
    # 简单的画布设计生成
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Canvas Design</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            font-family: Arial, sans-serif;
        }
        #canvas-container {
            display: flex;
            justify-content: center;
            margin-bottom: 20px;
        }
        canvas {
            border: 1px solid #ddd;
            background: white;
        }
        #controls {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .control-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <h1>{design_type} Design</h1>
    <div id="canvas-container">
        <canvas id="designCanvas" width="{width}" height="{height}"></canvas>
    </div>
    <div id="controls">
        <h2>Controls</h2>
        <div class="control-group">
            <label>Element Type</label>
            <select id="elementType">
                <option value="rectangle">Rectangle</option>
                <option value="circle">Circle</option>
                <option value="text">Text</option>
            </select>
        </div>
        <div class="control-group">
            <label>X Position</label>
            <input type="number" id="xPos" value="100">
        </div>
        <div class="control-group">
            <label>Y Position</label>
            <input type="number" id="yPos" value="100">
        </div>
        <div class="control-group">
            <label>Width</label>
            <input type="number" id="elementWidth" value="100">
        </div>
        <div class="control-group">
            <label>Height</label>
            <input type="number" id="elementHeight" value="100">
        </div>
        <div class="control-group">
            <label>Color</label>
            <input type="color" id="elementColor" value="#4CAF50">
        </div>
        <div class="control-group">
            <label>Text</label>
            <input type="text" id="elementText" value="Hello">
        </div>
        <div class="control-group">
            <button onclick="addElement()">Add Element</button>
            <button onclick="clearCanvas()">Clear Canvas</button>
            <button onclick="download()">Download</button>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('designCanvas');
        const ctx = canvas.getContext('2d');
        
        // 初始化画布
        function initCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        // 添加元素
        function addElement() {
            const type = document.getElementById('elementType').value;
            const x = parseInt(document.getElementById('xPos').value);
            const y = parseInt(document.getElementById('yPos').value);
            const width = parseInt(document.getElementById('elementWidth').value);
            const height = parseInt(document.getElementById('elementHeight').value);
            const color = document.getElementById('elementColor').value;
            const text = document.getElementById('elementText').value;
            
            ctx.fillStyle = color;
            
            if (type === 'rectangle') {
                ctx.fillRect(x, y, width, height);
            } else if (type === 'circle') {
                ctx.beginPath();
                ctx.arc(x, y, width / 2, 0, Math.PI * 2);
                ctx.fill();
            } else if (type === 'text') {
                ctx.font = '20px Arial';
                ctx.fillText(text, x, y);
            }
        }
        
        // 清除画布
        function clearCanvas() {
            initCanvas();
        }
        
        // 下载画布
        function download() {
            const dataURL = canvas.toDataURL('image/png');
            const link = document.createElement('a');
            link.href = dataURL;
            link.download = '{design_type}_design.png';
            link.click();
        }
        
        // 初始化
        initCanvas();
        
        // 添加预设元素
        const presetElements = {elements};
        presetElements.forEach(element => {
            ctx.fillStyle = element.color || '#4CAF50';
            
            if (element.type === 'rectangle') {
                ctx.fillRect(element.x, element.y, element.width, element.height);
            } else if (element.type === 'circle') {
                ctx.beginPath();
                ctx.arc(element.x, element.y, element.radius, 0, Math.PI * 2);
                ctx.fill();
            } else if (element.type === 'text') {
                ctx.font = element.font || '20px Arial';
                ctx.fillText(element.text, element.x, element.y);
            }
        });
    </script>
</body>
</html>
    """
    # 手动替换模板中的变量
    html = html.replace('{design_type}', design_type)
    html = html.replace('{width}', str(width))
    html = html.replace('{height}', str(height))
    html = html.replace('{elements}', str(elements))
    return html


# 技能定义
skill = AgentSkill(
    name="canvas-design",
    description="Creating canvas designs with interactive elements",
    input_schema=CanvasDesignInput,
    output_schema=CanvasDesignOutput,
    execute=canvas_design_execute
)
