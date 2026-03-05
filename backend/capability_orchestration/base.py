import os
import re
import json
import subprocess
from typing import Dict, List, Optional, Any, Set, Callable
from pydantic import BaseModel, Field
from enum import Enum
from urllib.parse import urlparse


class MarkdownReferenceLoader:
    """Markdown引用加载器 - 实现渐进式披露机制"""

    MARKDOWN_LINK_PATTERN = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    MARKDOWN_IMAGE_PATTERN = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')

    def __init__(self, base_dir: str, max_depth: int = 3):
        self.base_dir = base_dir
        self.max_depth = max_depth
        self._loaded_files: Dict[str, str] = {}
        self._reference_graph: Dict[str, List[str]] = {}

    def parse_markdown_links(self, content: str) -> List[str]:
        """解析Markdown内容中的所有链接"""
        links = []

        for match in self.MARKDOWN_LINK_PATTERN.finditer(content):
            link = match.group(2)
            if not self._is_external_link(link):
                links.append(link)

        return links

    def _is_external_link(self, link: str) -> bool:
        """判断是否为外部链接"""
        parsed = urlparse(link)
        return bool(parsed.scheme) or link.startswith('http://') or link.startswith('https://')

    def resolve_path(self, link: str, current_file: str) -> Optional[str]:
        """解析相对路径为绝对路径"""
        current_dir = os.path.dirname(current_file)

        if link.startswith('/'):
            link = link.lstrip('/')

        resolved = os.path.normpath(os.path.join(current_dir, link))
        full_path = os.path.join(self.base_dir, resolved)

        if os.path.exists(full_path) and os.path.isfile(full_path):
            return resolved
        return None

    def load_file(self, file_path: str) -> Optional[str]:
        """加载单个文件"""
        if file_path in self._loaded_files:
            return self._loaded_files[file_path]

        full_path = os.path.join(self.base_dir, file_path)
        if not os.path.exists(full_path):
            return None

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self._loaded_files[file_path] = content
        return content

    def load_with_references(
        self,
        main_file: str,
        current_depth: int = 0
    ) -> Dict[str, Any]:
        """渐进式加载主文件及其引用

        返回结构:
        {
            "main": "主文件内容",
            "references": {
                "filename.md": "文件内容",
                ...
            },
            "graph": {"main.md": ["ref1.md", "ref2.md"]}
        }
        """
        if current_depth >= self.max_depth:
            return {"main": "", "references": {}, "graph": {}}

        main_content = self.load_file(main_file)
        if not main_content:
            return {"main": "", "references": {}, "graph": {}}

        result = {
            "main": main_content,
            "references": {},
            "graph": {main_file: []}
        }

        links = self.parse_markdown_links(main_content)

        for link in links:
            resolved = self.resolve_path(link, main_file)
            if resolved and resolved != main_file:
                result["graph"][main_file].append(resolved)

                if resolved not in self._loaded_files:
                    ref_result = self.load_with_references(resolved, current_depth + 1)
                    result["references"][resolved] = ref_result["main"]
                    result["references"].update(ref_result["references"])

        return result

    def get_full_context(self, main_file: str) -> str:
        """获取完整的上下文字符串（用于LLM）"""
        loaded = self.load_with_references(main_file)

        parts = [f"# {main_file}\n{loaded['main']}"]

        for filename, content in loaded["references"].items():
            parts.append(f"\n# {filename}\n{content}")

        return "\n\n".join(parts)

    def list_referenced_files(self, main_file: str) -> List[str]:
        """列出主文件引用的所有文件"""
        loaded = self.load_with_references(main_file)
        return list(loaded["references"].keys())


class InputField(BaseModel):
    """输入字段定义"""
    name: str
    type: str
    required: bool = True
    description: str = ""


class OutputField(BaseModel):
    """输出字段定义"""
    name: str
    type: str
    description: str = ""


class SkillMetadata(BaseModel):
    """技能元数据"""
    name: str
    description: str
    version: str = "1.0.0"
    license: Optional[str] = None
    input_fields: List[InputField] = []
    output_fields: List[OutputField] = []
    examples: List[str] = []
    guidelines: List[str] = []


class SkillInput(BaseModel):
    """技能输入基类"""
    session_id: str = Field(..., description="会话ID")
    user_input: str = Field(..., description="用户输入")
    context: Optional[Dict[str, Any]] = Field(default=None, description="上下文信息")


class SkillOutput(BaseModel):
    """技能输出基类"""
    success: bool = Field(..., description="执行是否成功")
    message: str = Field(..., description="执行结果消息")
    data: Optional[Dict[str, Any]] = Field(default=None, description="执行结果数据")
    skill_name: str = Field(..., description="技能名称")


class ToolType(str, Enum):
    """工具类型"""
    API = "api"
    SCRIPT = "script"
    DATABASE = "database"


class Tool(BaseModel):
    """工具定义"""
    name: str
    type: ToolType
    description: str
    handler: Any = None


class SkillResources:
    """技能资源管理器"""

    def __init__(self, skill_dir: str):
        self.skill_dir = skill_dir
        self.scripts_dir = os.path.join(skill_dir, "scripts")
        self.templates_dir = os.path.join(skill_dir, "templates")
        self.resources_dir = os.path.join(skill_dir, "resources")
        self.examples_dir = os.path.join(skill_dir, "examples")
        self.assets_dir = os.path.join(skill_dir, "assets")
        self.references_dir = os.path.join(skill_dir, "references")

        self._scripts: Dict[str, str] = {}
        self._templates: Dict[str, str] = {}
        self._resources: Dict[str, str] = {}
        self._examples: Dict[str, str] = {}
        self._assets: Dict[str, str] = {}
        self._references: Dict[str, str] = {}

    def load_all(self):
        """加载所有资源"""
        self._load_directory(self.scripts_dir, self._scripts)
        self._load_directory(self.templates_dir, self._templates)
        self._load_directory(self.resources_dir, self._resources)
        self._load_directory(self.examples_dir, self._examples)
        self._load_directory(self.assets_dir, self._assets)
        self._load_directory(self.references_dir, self._references)

    def _load_directory(self, dir_path: str, storage: Dict[str, str]):
        """加载目录中的所有文件"""
        if not os.path.exists(dir_path):
            return

        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, dir_path)

                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        storage[rel_path] = f.read()
                except UnicodeDecodeError:
                    with open(filepath, 'rb') as f:
                        storage[rel_path] = f.read()

    @property
    def scripts(self) -> Dict[str, str]:
        """获取所有脚本"""
        return self._scripts

    @property
    def templates(self) -> Dict[str, str]:
        """获取所有模板"""
        return self._templates

    @property
    def resources(self) -> Dict[str, str]:
        """获取所有资源"""
        return self._resources

    @property
    def examples(self) -> Dict[str, str]:
        """获取所有示例"""
        return self._examples

    @property
    def assets(self) -> Dict[str, str]:
        """获取所有静态资源"""
        return self._assets

    @property
    def references(self) -> Dict[str, str]:
        """获取所有参考文档"""
        return self._references

    def get_script(self, name: str) -> Optional[str]:
        """获取脚本内容"""
        return self._scripts.get(name)

    def get_template(self, name: str) -> Optional[str]:
        """获取模板内容"""
        return self._templates.get(name)

    def get_resource(self, name: str) -> Optional[str]:
        """获取资源内容"""
        return self._resources.get(name)

    def get_example(self, name: str) -> Optional[str]:
        """获取示例内容"""
        return self._examples.get(name)

    def get_asset(self, name: str) -> Optional[str]:
        """获取静态资源"""
        return self._assets.get(name)

    def get_reference(self, name: str) -> Optional[str]:
        """获取参考文档"""
        return self._references.get(name)

    def has_scripts(self) -> bool:
        """是否有脚本"""
        return len(self._scripts) > 0

    def has_templates(self) -> bool:
        """是否有模板"""
        return len(self._templates) > 0

    def has_examples(self) -> bool:
        """是否有示例"""
        return len(self._examples) > 0

    def has_assets(self) -> bool:
        """是否有静态资源"""
        return len(self._assets) > 0

    def list_scripts(self) -> List[str]:
        """列出所有脚本"""
        return list(self._scripts.keys())

    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self._templates.keys())

    def list_examples(self) -> List[str]:
        """列出所有示例"""
        return list(self._examples.keys())

    def list_references(self) -> List[str]:
        """列出所有参考文档"""
        return list(self._references.keys())


class Skill:
    """技能基类"""

    def __init__(
        self,
        name: str,
        description: str,
        version: str = "1.0.0",
        input_schema: type = SkillInput,
        output_schema: type = SkillOutput,
        tools: Optional[List[Tool]] = None,
        skill_dir: Optional[str] = None,
        execute_handler: Optional[Callable] = None
    ):
        self.name = name
        self.description = description
        self.version = version
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.tools = tools or []
        self.skill_dir = skill_dir
        self.execute_handler = execute_handler
        self._resources: Optional[SkillResources] = None
        self._reference_loader: Optional[MarkdownReferenceLoader] = None
        self._skill_content: Optional[Dict[str, Any]] = None

    @property
    def resources(self) -> Optional[SkillResources]:
        """获取技能资源"""
        if self._resources is None and self.skill_dir:
            self._resources = SkillResources(self.skill_dir)
            self._resources.load_all()
        return self._resources

    @property
    def reference_loader(self) -> Optional[MarkdownReferenceLoader]:
        """获取引用加载器"""
        if self._reference_loader is None and self.skill_dir:
            self._reference_loader = MarkdownReferenceLoader(self.skill_dir)
        return self._reference_loader

    def load_skill_content(self) -> Dict[str, Any]:
        """加载技能内容（SKILL.md + 引用的文档）"""
        if self._skill_content is not None:
            return self._skill_content

        if not self.skill_dir or not self.reference_loader:
            return {"main": "", "references": {}}

        skill_md_path = os.path.join(self.skill_dir, "SKILL.md")
        if not os.path.exists(skill_md_path):
            return {"main": "", "references": {}}

        self._skill_content = self.reference_loader.load_with_references("SKILL.md")
        return self._skill_content

    def get_skill_content(self) -> str:
        """获取完整的技能内容（用于LLM）"""
        if not self.reference_loader:
            return ""

        return self.reference_loader.get_full_context("SKILL.md")

    def get_skill_instructions(self) -> str:
        """获取技能指令（SKILL.md主体内容）"""
        content = self.load_skill_content()
        return content.get("main", "")

    def get_referenced_files(self) -> List[str]:
        """获取引用的文件列表"""
        if not self.reference_loader:
            return []

        skill_md_path = os.path.join(self.skill_dir, "SKILL.md")
        return self.reference_loader.list_referenced_files(skill_md_path)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行技能"""
        if self.execute_handler:
            return await self.execute_handler(input_data)

        script_result = self._execute_script_for_action(input_data)
        if script_result is not None:
            return script_result

        # 默认实现：返回技能信息
        return {
            "skill_name": self.name,
            "description": self.description,
            "input_data": input_data,
            "message": "技能执行成功（默认实现）"
        }

    def _execute_script_for_action(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Claude Skills风格的脚本路由：action/operation -> scripts/<action>.py"""
        if not self.skill_dir:
            return None

        action = input_data.get("action") or input_data.get("operation")
        if not action:
            return None

        scripts_dir = os.path.join(self.skill_dir, "scripts")
        script_path = os.path.join(scripts_dir, f"{action}.py")
        if not os.path.exists(script_path):
            return {
                "skill_name": self.name,
                "action": action,
                "status": "no_script",
                "message": f"未找到脚本: scripts/{action}.py"
            }

        process = subprocess.run(
            ["python", script_path, json.dumps(input_data, ensure_ascii=False)],
            capture_output=True,
            text=True,
            cwd=self.skill_dir
        )

        return {
            "skill_name": self.name,
            "action": action,
            "script": f"scripts/{action}.py",
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "status": "success" if process.returncode == 0 else "failed"
        }

    def get_script(self, name: str) -> Optional[str]:
        """获取脚本内容"""
        if self.resources:
            return self.resources.get_script(name)
        return None

    def get_template(self, name: str) -> Optional[str]:
        """获取模板内容"""
        if self.resources:
            return self.resources.get_template(name)
        return None

    def get_example(self, name: str) -> Optional[str]:
        """获取示例内容"""
        if self.resources:
            return self.resources.get_example(name)
        return None

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        try:
            self.input_schema(**input_data)
            return True
        except Exception as e:
            print(f"输入验证失败: {str(e)}")
            return False

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """运行技能"""
        if not self.validate_input(input_data):
            return self.output_schema(
                success=False,
                message="输入数据验证失败",
                data=None,
                skill_name=self.name
            ).dict()

        try:
            result = await self.execute(input_data)
            return self.output_schema(
                success=True,
                message="执行成功",
                data=result,
                skill_name=self.name
            ).dict()
        except Exception as e:
            return self.output_schema(
                success=False,
                message=f"执行失败: {str(e)}",
                data=None,
                skill_name=self.name
            ).dict()

    def get_metadata(self) -> SkillMetadata:
        """获取技能元数据"""
        return SkillMetadata(
            name=self.name,
            description=self.description,
            version=self.version,
            input_fields=[
                InputField(name="session_id", type="string", required=True, description="会话ID"),
                InputField(name="user_input", type="string", required=True, description="用户输入"),
                InputField(name="context", type="object", required=False, description="上下文信息")
            ],
            output_fields=[
                OutputField(name="success", type="boolean", description="执行是否成功"),
                OutputField(name="message", type="string", description="执行结果消息"),
                OutputField(name="data", type="object", description="执行结果数据")
            ]
        )


AgentSkill = Skill
