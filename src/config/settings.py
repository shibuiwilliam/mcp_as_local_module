from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # アプリケーション設定
    app_name: str = "MCP統合Webアプリケーション"
    debug: bool = False

    # MCP設定（将来的な外部化用）
    mcp_mode: str = "internal"  # "internal" or "external"
    mcp_server_url: Optional[str] = None  # 外部MCP使用時のURL
    mcp_timeout: int = 30

    class Config:
        env_file = ".env"
