from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from backend.models.schemas import Task, AgentResult
import time


class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, task: Task) -> AgentResult:
        pass
    
    async def run(self, task: Task) -> AgentResult:
        start_time = time.time()
        try:
            result = await self.execute(task)
            result.execution_time = time.time() - start_time
            return result
        except Exception as e:
            return AgentResult(
                agent=self.name,
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
