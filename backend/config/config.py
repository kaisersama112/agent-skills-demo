from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    # 应用配置
    app_name: str = "LLM App Platform"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./app.db"
    
    # Redis配置
    redis_url: str = "redis://localhost:6379/0"

    # LLM配置
    llm_api_key: str = "sk-561f4f1fcfb9480898ea821083a5ba95"
    llm_model: str ="qwen-turbo"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    
    # 安全配置
    secret_key: str = "your_secret_key_here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS配置
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """获取CORS源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 创建全局配置实例
settings = Settings()
