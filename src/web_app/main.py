from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.logger import make_logger
from src.mcp_server.server import MCPServerModule

logger = make_logger(__name__)


class UserCreateRequest(BaseModel):
    name: str
    email: str


class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]


class WebApplication:
    """
    メインのWebアプリケーション
    modular monolithアーキテクチャを採用
    """

    def __init__(self):
        self.app = FastAPI(title="MCP統合Webアプリケーション")
        self.mcp_server = MCPServerModule()
        self._setup_routes()

    def _setup_routes(self):
        """ルーティングの設定"""

        @self.app.get("/")
        async def root():
            return {"message": "MCP統合Webアプリケーション"}

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "mcp_server": "running"}

        # 従来のREST API
        @self.app.get("/api/users/{user_id}")
        async def get_user_rest(user_id: str):
            """従来のREST API - 内部的にMCPを使用"""
            result = await self.mcp_server.execute_tool("get_user", {"user_id": user_id})
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            return result

        @self.app.get("/api/users")
        async def list_users_rest():
            """従来のREST API - 内部的にMCPを使用"""
            result = await self.mcp_server.execute_tool("list_users", {})
            return result

        @self.app.post("/api/users")
        async def create_user_rest(user: UserCreateRequest):
            """従来のREST API - 内部的にMCPを使用"""
            result = await self.mcp_server.execute_tool("create_user", {"name": user.name, "email": user.email})
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return result

        # MCP Tool API（将来的な外部化を見据えた汎用インターface）
        @self.app.post("/api/mcp/tools/execute")
        async def execute_mcp_tool(request: MCPToolRequest):
            """
            MCPツールの汎用実行エンドポイント
            将来的にMCPサーバーが外部化された際も同じインターフェースで利用可能
            """
            result = await self.mcp_server.execute_tool(request.tool_name, request.arguments)
            return {
                "tool_name": request.tool_name,
                "result": result,
                "execution_mode": "internal",  # 将来は "external" も可能
            }

        @self.app.get("/api/mcp/tools")
        async def list_mcp_tools():
            """利用可能なMCPツールの一覧"""
            tools = self.mcp_server.tools
            return {
                "tools": [
                    {"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema}
                    for tool in tools
                ]
            }
