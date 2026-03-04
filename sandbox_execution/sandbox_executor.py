from typing import Dict, List, Any, Optional, Callable
import json
import base64

class SandboxExecutor:
    """
    端侧沙箱执行器
    负责安全生成和执行任意代码
    """
    
    def __init__(self):
        self.whitelist_apis = {
            "console": ["log", "warn", "error"],
            "Math": ["random", "abs", "ceil", "floor", "round"],
            "Date": ["now", "parse", "UTC"],
            "JSON": ["parse", "stringify"],
            "Array": ["from", "isArray"],
            "Object": ["keys", "values", "entries"]
        }
        self.sandboxes = {}
    
    def create_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """
        创建沙箱
        
        Args:
            sandbox_id: 沙箱ID
            
        Returns:
            沙箱信息
        """
        sandbox = {
            "id": sandbox_id,
            "status": "created",
            "code": "",
            "dependencies": [],
            "created_at": "now"
        }
        self.sandboxes[sandbox_id] = sandbox
        return sandbox
    
    def destroy_sandbox(self, sandbox_id: str) -> Dict[str, Any]:
        """
        销毁沙箱
        
        Args:
            sandbox_id: 沙箱ID
            
        Returns:
            销毁结果
        """
        if sandbox_id in self.sandboxes:
            del self.sandboxes[sandbox_id]
            return {
                "success": True,
                "message": f"沙箱 {sandbox_id} 已销毁"
            }
        else:
            return {
                "success": False,
                "message": f"沙箱 {sandbox_id} 不存在"
            }
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        验证代码安全性
        
        Args:
            code: 代码字符串
            
        Returns:
            验证结果
        """
        # 检查危险操作
        dangerous_patterns = [
            "eval(",
            "new Function(",
            "document.write(",
            "document.body.innerHTML",
            "localStorage",
            "sessionStorage",
            "XMLHttpRequest",
            "fetch(",
            "import(",
            "require("
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                return {
                    "valid": False,
                    "message": f"检测到危险操作: {pattern}"
                }
        
        return {
            "valid": True,
            "message": "代码验证通过"
        }
    
    def generate_sandbox_code(self, code: str) -> str:
        """
        生成沙箱代码
        
        Args:
            code: 原始代码
            
        Returns:
            沙箱包装后的代码
        """
        # 生成沙箱环境
        sandbox_code = f"""
// 沙箱环境
const sandbox = {json.dumps(self.whitelist_apis, indent=2)};

// 创建安全的全局对象
const safeGlobal = Object.create(null);

// 导入白名单API
for (const [api, methods] of Object.entries(sandbox)) {{
    safeGlobal[api] = Object.create(null);
    for (const method of methods) {{
        if (typeof window[api]?.[method] === 'function') {{
            safeGlobal[api][method] = window[api][method].bind(window[api]);
        }}
    }}
}}

// 执行用户代码
(function(global) {{
    'use strict';
    
    // 用户代码
    {code}
    
}})(safeGlobal);
        """
        
        return sandbox_code
    
    def generate_iframe_html(self, code: str, dependencies: List[str] = None) -> str:
        """
        生成iframe HTML
        
        Args:
            code: 代码字符串
            dependencies: 依赖列表
            
        Returns:
            iframe HTML
        """
        if dependencies is None:
            dependencies = []
        
        # 生成依赖脚本标签
        dependency_scripts = ""
        for dep in dependencies:
            dependency_scripts += f'<script src="{dep}"></script>\n'
        
        # 生成沙箱代码
        sandbox_code = self.generate_sandbox_code(code)
        
        # 生成iframe HTML
        iframe_html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>沙箱执行环境</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        #app {{
            width: 100%;
            height: 100%;
        }}
    </style>
    {dependency_scripts}
</head>
<body>
    <div id="app"></div>
    <script>
        {sandbox_code}
    </script>
</body>
</html>
        """
        
        return iframe_html
    
    def generate_web_worker_code(self, code: str) -> str:
        """
        生成Web Worker代码
        
        Args:
            code: 代码字符串
            
        Returns:
            Web Worker代码
        """
        worker_code = f"""
// Web Worker 沙箱环境
const sandbox = {json.dumps(self.whitelist_apis, indent=2)};

// 创建安全的全局对象
const safeGlobal = Object.create(null);

// 导入白名单API
for (const [api, methods] of Object.entries(sandbox)) {{
    safeGlobal[api] = Object.create(null);
    for (const method of methods) {{
        if (typeof self[api]?.[method] === 'function') {{
            safeGlobal[api][method] = self[api][method].bind(self[api]);
        }}
    }}
}}

// 监听消息
self.addEventListener('message', (event) => {{
    try {{
        // 执行用户代码
        (function(global) {{
            'use strict';
            
            // 用户代码
            {code}
            
            // 发送执行结果
            self.postMessage({{ "success": true, "result": "执行成功" }});
        }})(safeGlobal);
    }} catch (error) {{
        // 发送错误信息
        self.postMessage({{ "success": false, "error": error.message }});
    }}
}});
        """
        
        return worker_code
    
    def execute_in_sandbox(self, sandbox_id: str, code: str, dependencies: List[str] = None) -> Dict[str, Any]:
        """
        在沙箱中执行代码
        
        Args:
            sandbox_id: 沙箱ID
            code: 代码字符串
            dependencies: 依赖列表
            
        Returns:
            执行结果
        """
        execution_steps = []
        
        # 步骤1: 验证代码
        execution_steps.append({
            "step": 1,
            "name": "验证代码",
            "status": "开始"
        })
        validation = self.validate_code(code)
        execution_steps.append({
            "step": 1,
            "name": "验证代码",
            "status": "完成",
            "result": validation
        })
        
        if not validation["valid"]:
            return {
                **validation,
                "execution_steps": execution_steps
            }
        
        # 步骤2: 创建沙箱
        execution_steps.append({
            "step": 2,
            "name": "创建沙箱",
            "status": "开始"
        })
        if sandbox_id not in self.sandboxes:
            self.create_sandbox(sandbox_id)
        
        # 更新沙箱信息
        self.sandboxes[sandbox_id].update({
            "code": code,
            "dependencies": dependencies or [],
            "status": "running"
        })
        execution_steps.append({
            "step": 2,
            "name": "创建沙箱",
            "status": "完成",
            "result": {
                "sandbox_id": sandbox_id,
                "status": "running"
            }
        })
        
        # 步骤3: 生成iframe HTML
        execution_steps.append({
            "step": 3,
            "name": "生成iframe HTML",
            "status": "开始"
        })
        iframe_html = self.generate_iframe_html(code, dependencies)
        execution_steps.append({
            "step": 3,
            "name": "生成iframe HTML",
            "status": "完成",
            "result": {
                "html_length": len(iframe_html),
                "dependencies": dependencies or []
            }
        })
        
        # 步骤4: 生成Web Worker代码
        execution_steps.append({
            "step": 4,
            "name": "生成Web Worker代码",
            "status": "开始"
        })
        worker_code = self.generate_web_worker_code(code)
        execution_steps.append({
            "step": 4,
            "name": "生成Web Worker代码",
            "status": "完成",
            "result": {
                "code_length": len(worker_code)
            }
        })
        
        # 步骤5: 更新沙箱状态
        execution_steps.append({
            "step": 5,
            "name": "更新沙箱状态",
            "status": "开始"
        })
        self.sandboxes[sandbox_id]["status"] = "completed"
        self.sandboxes[sandbox_id]["execution_steps"] = execution_steps
        execution_steps.append({
            "step": 5,
            "name": "更新沙箱状态",
            "status": "完成",
            "result": {
                "status": "completed"
            }
        })
        
        return {
            "success": True,
            "message": "代码执行成功",
            "iframe_html": iframe_html,
            "worker_code": worker_code,
            "sandbox_id": sandbox_id,
            "execution_steps": execution_steps,
            "sandbox_info": self.sandboxes[sandbox_id]
        }
    
    def get_sandbox_status(self, sandbox_id: str) -> Dict[str, Any]:
        """
        获取沙箱状态
        
        Args:
            sandbox_id: 沙箱ID
            
        Returns:
            沙箱状态
        """
        if sandbox_id in self.sandboxes:
            return self.sandboxes[sandbox_id]
        else:
            return {
                "error": "沙箱不存在"
            }
    
    def list_sandboxes(self) -> List[Dict[str, Any]]:
        """
        列出所有沙箱
        
        Returns:
            沙箱列表
        """
        return list(self.sandboxes.values())

# 示例用法
if __name__ == "__main__":
    executor = SandboxExecutor()
    
    # 测试代码
    test_code = """
// 创建一个简单的React组件
const App = () => {
    return React.createElement('div', null, 
        React.createElement('h1', null, 'Hello, Sandbox!'),
        React.createElement('p', null, 'This is a safe sandbox environment.')
    );
};

// 渲染组件
ReactDOM.render(
    React.createElement(App),
    document.getElementById('app')
);
    """
    
    # 依赖
    dependencies = [
        "https://unpkg.com/react@18/umd/react.development.js",
        "https://unpkg.com/react-dom@18/umd/react-dom.development.js"
    ]
    
    # 执行代码
    result = executor.execute_in_sandbox("test-sandbox", test_code, dependencies)
    print("执行结果:")
    print(result)
    
    # 列出沙箱
    print("\n沙箱列表:")
    print(executor.list_sandboxes())
    
    # 销毁沙箱
    destroy_result = executor.destroy_sandbox("test-sandbox")
    print("\n销毁沙箱结果:")
    print(destroy_result)