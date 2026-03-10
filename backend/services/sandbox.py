from typing import Optional, Dict, Any
import docker
from config import settings
import subprocess
import tempfile
import os
import uuid


class SandboxExecutor:
    def __init__(self):
        self.docker_client: Optional[docker.DockerClient] = None
        self.enabled = settings.docker_enabled
        
        if self.enabled:
            try:
                self.docker_client = docker.from_env()
            except Exception:
                self.enabled = False
    
    async def run_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        if self.enabled and self.docker_client:
            return await self._run_docker(code, language)
        else:
            return await self._run_direct(code, language)
    
    async def _run_docker(self, code: str, language: str) -> Dict[str, Any]:
        image = "python:3.11-sandbox" if language == "python" else "node:18-sandbox"
        
        try:
            container = self.docker_client.containers.run(
                image,
                f"python -c '{code}'" if language == "python" else f"node -e '{code}'",
                mem_limit=settings.sandbox_memory_limit,
                cpu_period=settings.sandbox_cpu_period,
                detach=True,
                remove=True
            )
            
            result = container.wait()
            logs = container.logs().decode('utf-8')
            
            return {
                "success": result.StatusCode == 0,
                "output": logs,
                "error": None if result.StatusCode == 0 else f"Exit code: {result.StatusCode}"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
    
    async def _run_direct(self, code: str, language: str) -> Dict[str, Any]:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            if language == "python":
                result = subprocess.run(
                    ["python", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif language == "javascript":
                result = subprocess.run(
                    ["node", temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                return {
                    "success": False,
                    "output": None,
                    "error": f"Unsupported language: {language}"
                }
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": None,
                "error": "Execution timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "output": None,
                "error": str(e)
            }
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    async def run_app(self, app_id: str, code: Dict[str, str]) -> Dict[str, Any]:
        # 使用相对路径，避免Windows路径问题
        app_dir = os.path.join(os.getcwd(), "sandbox", "apps", app_id)
        os.makedirs(app_dir, exist_ok=True)
        
        for filename, content in code.items():
            filepath = os.path.join(app_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            "success": True,
            "app_dir": app_dir,
            "status": "deployed",
            "static_url": f"/apps/{app_id}"
        }


sandbox_executor = SandboxExecutor()
