from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "灵光 Lite API"
    debug: bool = True
    
    openai_api_key: str = "sk-your-key-here"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    docker_enabled: bool = False
    sandbox_memory_limit: str = "512m"
    sandbox_cpu_period: int = 50000
    
    db_url: str = "sqlite+aiosqlite:///./data.db"
    
    class Config:
        env_file = ".env"


settings = Settings()
