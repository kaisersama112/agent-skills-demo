from typing import Dict, Any, List
from pydantic import BaseModel, Field
from capability_orchestration.base import SkillInput, SkillOutput, AgentSkill


class DocCoauthoringInput(SkillInput):
    """
    文档协作输入
    """
    doc_title: str = Field(..., description="文档标题")
    doc_content: str = Field(..., description="文档内容")
    collaborators: List[str] = Field([], description="协作者列表")


class DocCoauthoringOutput(SkillOutput):
    """
    文档协作输出
    """
    data: Dict[str, Any] = Field(None, description="执行结果数据")


async def doc_coauthoring_execute(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    文档协作执行函数
    """
    # 生成文档协作界面
    doc_interface = generate_doc_coauthoring_interface(
        input_data.get("doc_title"),
        input_data.get("doc_content"),
        input_data.get("collaborators", [])
    )
    
    return {
        "doc_interface": doc_interface,
        "doc_title": input_data.get("doc_title"),
        "collaborators": input_data.get("collaborators", [])
    }


def generate_doc_coauthoring_interface(doc_title: str, doc_content: str, collaborators: List[str]) -> str:
    """
    生成文档协作界面
    """
    # 生成协作者HTML
    collaborators_html = ''
    for c in collaborators:
        collaborators_html += '<div class="collaborator"><div class="collaborator-avatar">' + c[0].upper() + '</div><span>' + c + '</span></div>'
    
    # 简单的文档协作界面生成
    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{doc_title} - Collaborative Document</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        .container {
            display: flex;
            height: 100vh;
        }
        .sidebar {
            width: 250px;
            background: #333;
            color: white;
            padding: 20px;
        }
        .sidebar h2 {
            margin-top: 0;
        }
        .collaborators {
            margin-top: 20px;
        }
        .collaborator {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .collaborator-avatar {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #4CAF50;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
        }
        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: white;
            padding: 20px;
            border-bottom: 1px solid #ddd;
        }
        .doc-title {
            font-size: 24px;
            font-weight: bold;
            margin: 0;
        }
        .doc-content {
            flex: 1;
            padding: 20px;
            background: white;
            margin: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow-y: auto;
        }
        .editor {
            width: 100%;
            min-height: 400px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: Arial, sans-serif;
            font-size: 16px;
        }
        .toolbar {
            background: #f0f0f0;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }
        .toolbar button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }
        .toolbar button:hover {
            background: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="sidebar">
            <h2>Collaborators</h2>
            <div class="collaborators">
                {collaborators_html}
            </div>
        </div>
        <div class="main-content">
            <div class="header">
                <h1 class="doc-title">{doc_title}</h1>
            </div>
            <div class="toolbar">
                <button onclick="saveDoc()">Save</button>
                <button onclick="shareDoc()">Share</button>
                <button onclick="exportDoc()">Export</button>
            </div>
            <div class="doc-content">
                <textarea class="editor" id="docEditor">{doc_content}</textarea>
            </div>
        </div>
    </div>
    
    <script>
        function saveDoc() {
            const content = document.getElementById('docEditor').value;
            // 这里可以添加保存逻辑
            alert('Document saved!');
        }
        
        function shareDoc() {
            // 这里可以添加分享逻辑
            alert('Document shared!');
        }
        
        function exportDoc() {
            const content = document.getElementById('docEditor').value;
            const blob = new Blob([content], {type: 'text/plain'});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = '{doc_title}_document.txt';
            link.click();
        }
    </script>
</body>
</html>
    """
    # 手动替换模板中的变量
    html = html.replace('{doc_title}', doc_title)
    html = html.replace('{doc_content}', doc_content)
    html = html.replace('{collaborators_html}', collaborators_html)
    html = html.replace('{doc_title}_document.txt', doc_title.replace(' ', '_') + '_document.txt')
    return html


# 技能定义
skill = AgentSkill(
    name="doc-coauthoring",
    description="Creating collaborative documents with multiple authors",
    input_schema=DocCoauthoringInput,
    output_schema=DocCoauthoringOutput,
    execute=doc_coauthoring_execute
)
