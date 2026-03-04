from typing import Dict, Any
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class AlgorithmicArtInput(SkillInput):
    """
    算法艺术输入
    """
    prompt: str = Field(..., description="用户的艺术需求")
    seed: int = Field(12345, description="随机种子")
    width: int = Field(1200, description="画布宽度")
    height: int = Field(1200, description="画布高度")


class AlgorithmicArtOutput(SkillOutput):
    """
    算法艺术输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def algorithmic_art_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    算法艺术执行函数
    """
    # 生成算法哲学
    philosophy = generate_algorithmic_philosophy(input_data.get("prompt"))
    
    # 生成p5.js代码
    html_artifact = generate_p5js_artifact(
        input_data.get("prompt"),
        input_data.get("seed", 12345),
        input_data.get("width", 1200),
        input_data.get("height", 1200)
    )
    
    return {
        "philosophy": philosophy,
        "html_artifact": html_artifact,
        "seed": input_data.get("seed", 12345)
    }


def generate_algorithmic_philosophy(prompt: str) -> str:
    """
    生成算法哲学
    """
    # 简单的算法哲学生成
    philosophy = f"""# 算法艺术哲学

基于用户需求: {prompt}

## 算法哲学

算法艺术是一种通过计算过程表达美学的艺术形式，它融合了数学、计算机科学和艺术创作。本作品通过精心设计的算法，探索了随机与秩序、简单与复杂之间的平衡。

### 核心概念

1. **种子随机性**：使用固定种子确保作品的可复现性，同时通过种子的变化创造无限的变体。

2. **涌现行为**：简单的规则通过迭代和相互作用，产生复杂而有机的视觉效果。

3. **参数化设计**：通过调整参数，探索作品在不同条件下的表现，为用户提供交互式的创作体验。

4. **数学美感**：利用数学函数和几何关系，创造具有和谐比例和结构的视觉效果。

### 技术实现

本作品使用p5.js库实现，通过以下技术手段实现算法艺术：

- 噪声函数生成自然的随机效果
- 粒子系统模拟有机运动
- 几何变换创造视觉深度
- 颜色理论实现和谐的色彩方案

通过这些技术，我们创造了一个既具有算法严谨性，又富有艺术表现力的作品。"""
    return philosophy


def generate_p5js_artifact(prompt: str, seed: int, width: int, height: int) -> str:
    """
    生成p5.js艺术作品
    """
    # 简单的p5.js艺术作品模板
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Algorithmic Art</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.7.0/p5.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            font-family: 'Poppins', sans-serif;
        }
        #canvas-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 20px;
        }
        #controls {
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .control-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        input[type="range"] {
            width: 100%;
        }
        .value-display {
            display: inline-block;
            width: 50px;
            text-align: right;
            margin-left: 10px;
        }
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
        }
        button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="controls">
        <h2>Algorithmic Art Controls</h2>
        
        <div class="control-group">
            <label>Seed: <span id="seed-value">{seed}</span></label>
            <div>
                <button onclick="prevSeed()">Previous</button>
                <button onclick="nextSeed()">Next</button>
                <button onclick="randomSeed()">Random</button>
                <input type="number" id="seed-input" value="{seed}" style="width: 100px;">
                <button onclick="jumpToSeed()">Go</button>
            </div>
        </div>
        
        <div class="control-group">
            <label>Particle Count: <span id="particle-count-value">500</span></label>
            <input type="range" id="particle-count" min="100" max="2000" step="100" value="500" oninput="updateParam('particleCount', this.value)">
        </div>
        
        <div class="control-group">
            <label>Noise Scale: <span id="noise-scale-value">0.01</span></label>
            <input type="range" id="noise-scale" min="0.001" max="0.1" step="0.001" value="0.01" oninput="updateParam('noiseScale', this.value)">
        </div>
        
        <div class="control-group">
            <label>Speed: <span id="speed-value">1</span></label>
            <input type="range" id="speed" min="0.1" max="5" step="0.1" value="1" oninput="updateParam('speed', this.value)">
        </div>
        
        <div class="control-group">
            <button onclick="regenerate()">Regenerate</button>
            <button onclick="reset()">Reset</button>
            <button onclick="download()">Download PNG</button>
        </div>
    </div>
    
    <script>
        let params = {
            seed: {seed},
            particleCount: 500,
            noiseScale: 0.01,
            speed: 1
        };
        
        let particles = [];
        
        function setup() {
            createCanvas({width}, {height});
            resetSketch();
        }
        
        function resetSketch() {
            randomSeed(params.seed);
            noiseSeed(params.seed);
            
            particles = [];
            for (let i = 0; i < params.particleCount; i++) {
                particles.push({
                    x: random(width),
                    y: random(height),
                    angle: random(TWO_PI),
                    speed: random(0.5, 2) * params.speed
                });
            }
            
            background(240);
        }
        
        function draw() {
            noStroke();
            fill(0, 5);
            
            for (let particle of particles) {
                let noiseValue = noise(particle.x * params.noiseScale, particle.y * params.noiseScale);
                particle.angle = noiseValue * TWO_PI * 2;
                
                particle.x += cos(particle.angle) * particle.speed;
                particle.y += sin(particle.angle) * particle.speed;
                
                if (particle.x < 0) particle.x = width;
                if (particle.x > width) particle.x = 0;
                if (particle.y < 0) particle.y = height;
                if (particle.y > height) particle.y = 0;
                
                ellipse(particle.x, particle.y, 2, 2);
            }
        }
        
        function updateParam(param, value) {
            params[param] = parseFloat(value);
            document.getElementById(param.replace(/([A-Z])/g, '-$1').toLowerCase() + '-value').textContent = value;
            resetSketch();
        }
        
        function prevSeed() {
            params.seed--;
            updateSeedDisplay();
            resetSketch();
        }
        
        function nextSeed() {
            params.seed++;
            updateSeedDisplay();
            resetSketch();
        }
        
        function randomSeed() {
            params.seed = Math.floor(Math.random() * 1000000);
            updateSeedDisplay();
            resetSketch();
        }
        
        function jumpToSeed() {
            let seedInput = document.getElementById('seed-input');
            params.seed = parseInt(seedInput.value) || 0;
            updateSeedDisplay();
            resetSketch();
        }
        
        function updateSeedDisplay() {
            document.getElementById('seed-value').textContent = params.seed;
            document.getElementById('seed-input').value = params.seed;
        }
        
        function regenerate() {
            resetSketch();
        }
        
        function reset() {
            params = {
                seed: {seed},
                particleCount: 500,
                noiseScale: 0.01,
                speed: 1
            };
            
            document.getElementById('particle-count').value = params.particleCount;
            document.getElementById('particle-count-value').textContent = params.particleCount;
            
            document.getElementById('noise-scale').value = params.noiseScale;
            document.getElementById('noise-scale-value').textContent = params.noiseScale;
            
            document.getElementById('speed').value = params.speed;
            document.getElementById('speed-value').textContent = params.speed;
            
            updateSeedDisplay();
            resetSketch();
        }
        
        function download() {
            saveCanvas('algorithmic-art', 'png');
        }
    </script>
</body>
</html>
    """
    # 手动替换模板中的变量
    html = html.replace('{seed}', str(seed))
    html = html.replace('{width}', str(width))
    html = html.replace('{height}', str(height))
    return html


# 技能定义
skill = AgentSkill(
    name="algorithmic-art",
    description="Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration",
    input_schema=AlgorithmicArtInput,
    output_schema=AlgorithmicArtOutput,
    execute=algorithmic_art_execute
)
