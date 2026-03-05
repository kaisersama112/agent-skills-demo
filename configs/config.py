from pydantic.v1 import BaseModel
from typing import List

import os
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
import yaml
from pydantic import Field

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class ServerConfig(BaseModel):
    """服务器配置"""
    host: Optional[str] = Field(..., description="服务器主机地址")
    port: Optional[int] = Field(..., description="服务器端口号")
    timeout: Optional[int] = Field(..., description="服务器请求超时时间")
    max_workers: Optional[int] = Field(..., description="服务器最大工作线程数")
    keep_alive: Optional[int] = Field(..., description="服务器保持连接时间")
    debug: Optional[bool] = Field(..., description="是否开启调试模式")


class OpenAIConfig(BaseModel):
    """OpenAI 配置"""
    endpoint: Optional[str] = Field(..., description="OpenAI API 端点")
    api_key: Optional[str] = Field(..., description="OpenAI API 密钥")
    model_name: Optional[str] = Field(...,description="OpenAI API 模型")
    timeout: Optional[int] = Field(..., description="OpenAI API 请求超时时间")


class DatabaseConfig(BaseModel):
    """数据库配置"""
    host: Optional[str] = Field(..., description="数据库主机地址")
    port: Optional[int] = Field(..., description="数据库端口号")
    username: Optional[str] = Field(..., description="数据库用户名")
    password: Optional[str] = Field(..., description="数据库密码")


class RedisConfig(BaseModel):
    """Redis 配置"""
    host: Optional[str] = Field(..., description="Redis 主机地址")
    port: Optional[int] = Field(..., description="Redis 端口号")
    db: Optional[int] = Field(..., description="Redis 数据库索引")


class Config(BaseModel):
    """
    配置
    """
    server: Optional[ServerConfig] = None
    openai_config: Optional[OpenAIConfig] = None
    database_config: Optional[DatabaseConfig] = None
    redis_config: Optional[RedisConfig] = None
    # 应用配置
    app_name: str = "LLM App Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    # 执行可靠性配置
    executor_retry_count: int = 1
    executor_retry_backoff_seconds: float = 0.5
    executor_retryable_error_codes: str = "script_timeout,script_failed"

    @property
    def executor_retryable_error_codes_set(self) -> set[str]:
        return {x.strip() for x in self.executor_retryable_error_codes.split(",") if x.strip()}

    idempotency_cache_size: int = 1000

    # 安全配置
    secret_key: str = "change_me_in_env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS配置
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def database_url(self) -> str:
        """获取数据库URL"""
        return "sqlite:///./app.db"


def load_config():
    config_path = BASE_DIR / "configs" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)
    return Config.model_validate(raw_config)


# 加载配置
settings = load_config()
