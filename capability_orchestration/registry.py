import os
import json
import re
import sys
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple

from .base import Skill, SkillMetadata, SkillResources

try:
    import yaml
except Exception:
    yaml = None

try:
    from services.llm_service import LLMService
except ImportError:
    from services.llm_service import LLMService


@dataclass
class ParsedSkillDocument:
    metadata: SkillMetadata
    body: str
    yaml_header: str


class SkillMetadataParser:
    """SKILL.md元数据解析器"""

    @staticmethod
    def parse_file(skill_dir: str) -> Optional[SkillMetadata]:
        skill_md_path = os.path.join(skill_dir, "SKILL.md")
        if not os.path.exists(skill_md_path):
            return None

        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        return SkillMetadataParser.parse_content(content)

    @staticmethod
    def parse_content(content: str) -> SkillMetadata:
        return SkillMetadataParser.parse_content_with_body(content).metadata

    @staticmethod
    def _split_frontmatter(content: str) -> Tuple[str, str]:
        normalized = content.lstrip()
        if not normalized.startswith("---"):
            return "", content

        lines = normalized.splitlines()
        if not lines or lines[0].strip() != "---":
            return "", content

        closing_idx = None
        for idx in range(1, len(lines)):
            if lines[idx].strip() == "---":
                closing_idx = idx
                break

        if closing_idx is None:
            return "", content

        header = "\n".join(lines[1:closing_idx])
        body = "\n".join(lines[closing_idx + 1:])
        return header, body

    @staticmethod
    def _parse_header_to_dict(yaml_header: str) -> Dict[str, Any]:
        if not yaml_header.strip():
            return {}

        if yaml:
            parsed = yaml.safe_load(yaml_header) or {}
            if isinstance(parsed, dict):
                return parsed

        metadata_dict: Dict[str, Any] = {}
        for raw_line in yaml_header.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            metadata_dict[key.strip()] = value.strip().strip('"').strip("'")
        return metadata_dict

    @staticmethod
    def parse_content_with_body(content: str) -> ParsedSkillDocument:
        yaml_header, body = SkillMetadataParser._split_frontmatter(content)
        metadata_dict = SkillMetadataParser._parse_header_to_dict(yaml_header)

        metadata = SkillMetadata(
            name=metadata_dict.get("name", "unknown"),
            description=metadata_dict.get("description", ""),
            version=metadata_dict.get("version", "1.0.0"),
            license=metadata_dict.get("license"),
        )

        return ParsedSkillDocument(
            metadata=metadata,
            body=body.strip(),
            yaml_header=yaml_header.strip(),
        )


class SkillRegistry:
    """技能注册表 - 通过SKILL.md自动发现技能"""

    ACTION_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")
    DEFAULT_SCRIPT_TIMEOUT_SECONDS = 20
    MAX_SCRIPT_TIMEOUT_SECONDS = 120

    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.skill_metadata: Dict[str, Dict[str, Any]] = {}
        self._skill_dirs: Dict[str, str] = {}
        self._skill_bodies: Dict[str, str] = {}

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill
        self.skill_metadata[skill.name] = skill.get_metadata().model_dump()
        print(f"注册技能: {skill.name} - {skill.description}")

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        return self.skills.get(skill_name)

    def get_skill_metadata(self, skill_name: str) -> Optional[Dict[str, Any]]:
        return self.skill_metadata.get(skill_name)

    def list_all_metadata(self) -> List[Dict[str, Any]]:
        return list(self.skill_metadata.values())

    def list_skills(self) -> List[Dict[str, Any]]:
        result = []
        for name, metadata in self.skill_metadata.items():
            skill_dir = self._skill_dirs.get(name)
            resources_info = self._get_resources_info(skill_dir) if skill_dir else {}
            result.append(
                {
                    "name": metadata.get("name", name),
                    "description": metadata.get("description", ""),
                    "version": metadata.get("version", "1.0.0"),
                    "has_implementation": name in self.skills,
                    "skill_dir": skill_dir,
                    "resources": resources_info,
                }
            )
        return result

    def _get_resources_info(self, skill_dir: str) -> Dict[str, Any]:
        if not skill_dir or not os.path.exists(skill_dir):
            return {}

        info: Dict[str, Any] = {}
        for dir_name in ["scripts", "templates", "resources", "examples", "assets", "references"]:
            dir_path = os.path.join(skill_dir, dir_name)
            if not os.path.exists(dir_path):
                continue

            files: List[str] = []
            for root, _, filenames in os.walk(dir_path):
                for filename in filenames:
                    rel_path = os.path.relpath(os.path.join(root, filename), dir_path)
                    files.append(rel_path)

            if files:
                info[dir_name] = sorted(files)

        return info

    def discover_skills(self, skills_dir: str):
        if not os.path.exists(skills_dir):
            print(f"技能目录不存在: {skills_dir}")
            return

        for item in sorted(os.listdir(skills_dir)):
            skill_dir = os.path.join(skills_dir, item)
            if not os.path.isdir(skill_dir):
                continue

            skill_md_path = os.path.join(skill_dir, "SKILL.md")
            if not os.path.exists(skill_md_path):
                continue

            with open(skill_md_path, "r", encoding="utf-8") as f:
                skill_content = f.read()

            parsed = SkillMetadataParser.parse_content_with_body(skill_content)
            skill_name = parsed.metadata.name

            self.skill_metadata[skill_name] = parsed.metadata.model_dump()
            self._skill_dirs[skill_name] = skill_dir
            self._skill_bodies[skill_name] = self._build_full_skill_body(skill_dir, parsed.body)

    def _build_full_skill_body(self, skill_dir: str, skill_main_body: str) -> str:
        parts: List[str] = [skill_main_body.strip()] if skill_main_body.strip() else []

        md_files = sorted(
            file_name
            for file_name in os.listdir(skill_dir)
            if file_name.endswith(".md") and file_name != "SKILL.md"
        )

        for file_name in md_files:
            file_path = os.path.join(skill_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                parts.append(f"## {file_name}\n{content}")

        return "\n\n".join(parts)

    def get_skill_prompt_context(self, skill_name: str) -> str:
        return self._skill_bodies.get(skill_name, "")

    def build_skills_prompt(self) -> str:
        sections: List[str] = []
        for skill_name, metadata in sorted(self.skill_metadata.items()):
            section = "\n".join(
                [
                    f"Skill: {metadata.get('name', skill_name)}",
                    f"Description: {metadata.get('description', '')}",
                    self.get_skill_prompt_context(skill_name),
                ]
            ).strip()
            sections.append(section)

        if not sections:
            return "You have access to the following skills:\n\n(none)"

        return "You have access to the following skills:\n\n" + "\n\n".join(sections)

    def discover_and_register_skills(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        self.discover_skills(skills_dir)

    def get_skill_resources(self, skill_name: str) -> Optional[SkillResources]:
        skill_dir = self._skill_dirs.get(skill_name)
        if not skill_dir:
            return None
        return SkillResources(skill_dir)

    def get_or_create_skill(self, skill_name: str) -> Optional[Skill]:
        if not skill_name:
            return None

        if skill_name in self.skills:
            return self.skills[skill_name]

        metadata = self.skill_metadata.get(skill_name)
        if not metadata:
            return None

        skill = Skill(
            name=skill_name,
            description=metadata.get("description", ""),
            version=metadata.get("version", "1.0.0"),
            skill_dir=self._skill_dirs.get(skill_name),
        )
        self.skills[skill_name] = skill
        print(f"创建技能: {skill_name}")
        return skill

    def get_skill_by_intent(self, intent: str) -> Optional[Skill]:
        intent_skill_map = {
            "sandbox_app": "sandbox_app",
            "chat": "chat",
            "document": "document",
            "algorithmic_art": "algorithmic-art",
            "canvas_design": "canvas-design",
            "docx": "docx",
            "pdf": "pdf",
            "pptx": "pptx",
            "xlsx": "xlsx",
            "theme": "theme-factory",
            "internal_comms": "internal-comms",
            "brand": "brand-guidelines",
        }
        return self.get_or_create_skill(intent_skill_map.get(intent))

    def execute_skill_action(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Skill Runtime: 把 action/operation 映射到 scripts/<action> 并执行。"""
        skill_dir = self._skill_dirs.get(skill_name)
        if not skill_dir:
            return {"status": "error", "error_code": "skill_not_found", "message": f"技能不存在: {skill_name}"}

        action = input_data.get("action") or input_data.get("operation")
        if not action:
            return {"status": "error", "error_code": "missing_action", "message": "缺少 action 或 operation"}

        # Remove .py extension if present
        if action.endswith(".py"):
            action = action[:-3]

        # Validate action pattern
        if not isinstance(action, str):
            return {"status": "error", "error_code": "invalid_action", "message": f"非法 action: {action}"}

        scripts_dir = os.path.abspath(os.path.join(skill_dir, "scripts"))
        script_path = os.path.abspath(os.path.join(scripts_dir, f"{action}.py"))
        
        # Check if script path is within scripts directory
        if not script_path.startswith(f"{scripts_dir}{os.sep}"):
            return {"status": "error", "error_code": "path_violation", "message": "脚本路径校验失败"}

        if not os.path.exists(script_path):
            return {
                "status": "error",
                "error_code": "script_not_found",
                "message": f"脚本不存在: scripts/{action}.py",
                "skill": skill_name,
                "action": action,
            }

        timeout_seconds = self.DEFAULT_SCRIPT_TIMEOUT_SECONDS
        if isinstance(input_data.get("timeout_seconds"), int):
            timeout_seconds = max(1, min(self.MAX_SCRIPT_TIMEOUT_SECONDS, input_data["timeout_seconds"]))

        try:
            process = subprocess.run(
                [sys.executable, script_path],
                input=json.dumps(input_data, ensure_ascii=False),
                text=True,
                capture_output=True,
                cwd=skill_dir,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "error",
                "error_code": "script_timeout",
                "skill": skill_name,
                "action": action,
                "script": f"scripts/{action}.py",
                "timeout_seconds": timeout_seconds,
                "stdout": exc.stdout or "",
                "stderr": exc.stderr or "",
                "message": f"脚本执行超时（{timeout_seconds}s）",
            }

        result = {
            "status": "success" if process.returncode == 0 else "failed",
            "skill": skill_name,
            "action": action,
            "script": f"scripts/{action}.py",
            "returncode": process.returncode,
            "stdout": process.stdout,
            "stderr": process.stderr,
        }
        if process.returncode != 0:
            result["error_code"] = "script_failed"
            result["message"] = f"脚本执行失败，退出码 {process.returncode}"
        return result

    async def select_skill_by_llm(self, user_input: str) -> Optional[Skill]:
        if not self.skill_metadata:
            return None

        skill_list = [
            {"name": m.get("name", n), "description": m.get("description", "")}
            for n, m in self.skill_metadata.items()
        ]
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

用户输入：{user_input}

请选择最合适的技能：
        """

        llm_service = LLMService()
        response = await llm_service.generate(prompt, temperature=0.0)
        selected_skill_name = response.strip()

        if selected_skill_name.lower() == "none":
            return None

        return self.get_or_create_skill(selected_skill_name)
