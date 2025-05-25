import json
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import TextContent, Tool

from src.logger import make_logger

logger = make_logger(__name__)


class UserService:
    """ユーザー管理サービス（デモ用）"""

    def __init__(self):
        self._users = {
            "1": {"id": "1", "name": "田中太郎", "email": "tanaka@example.com"},
            "2": {"id": "2", "name": "佐藤花子", "email": "sato@example.com"},
        }

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    async def list_users(self) -> List[Dict[str, Any]]:
        return list(self._users.values())

    async def create_user(self, name: str, email: str) -> Dict[str, Any]:
        user_id = str(len(self._users) + 1)
        user = {"id": user_id, "name": name, "email": email}
        self._users[user_id] = user
        return user


class MCPServerModule:
    """
    MCPサーバーモジュール
    アプリケーション内部で使用し、将来的な外部化に対応
    """

    def __init__(self):
        self.server = Server("user-management-server")
        self.user_service = UserService()
        self.tools = [
            Tool(
                name="get_user",
                description="指定されたIDのユーザー情報を取得します",
                inputSchema={
                    "type": "object",
                    "properties": {"user_id": {"type": "string", "description": "ユーザーID"}},
                    "required": ["user_id"],
                },
            ),
            Tool(
                name="list_users",
                description="全ユーザーのリストを取得します",
                inputSchema={"type": "object", "properties": {}},
            ),
            Tool(
                name="create_user",
                description="新しいユーザーを作成します",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "ユーザー名"},
                        "email": {"type": "string", "description": "メールアドレス"},
                    },
                    "required": ["name", "email"],
                },
            ),
        ]
        self._setup_tools()

    def _setup_tools(self):
        """MCPツールの設定"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return self.tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "get_user":
                user = await self.user_service.get_user(arguments["user_id"])
                result = user if user else {"message": "ユーザーが見つかりません"}
                return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False))]

            elif name == "list_users":
                users = await self.user_service.list_users()
                return [TextContent(type="text", text=json.dumps(users, ensure_ascii=False))]

            elif name == "create_user":
                user = await self.user_service.create_user(arguments["name"], arguments["email"])
                return [TextContent(type="text", text=json.dumps(user, ensure_ascii=False))]

            else:
                return [TextContent(type="text", text=json.dumps({"error": f"未知のツール: {name}"}))]

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        ツールを実行する内部メソッド
        アプリケーション内から直接呼び出し可能
        """
        try:
            # 直接ビジネスロジックを呼び出す（MCPサーバーを経由せずに）
            if tool_name == "get_user":
                user = await self.user_service.get_user(arguments["user_id"])
                return user if user else {"message": "ユーザーが見つかりません"}

            elif tool_name == "list_users":
                users = await self.user_service.list_users()
                return users

            elif tool_name == "create_user":
                user = await self.user_service.create_user(arguments["name"], arguments["email"])
                return user

            else:
                return {"error": f"未知のツール: {tool_name}"}

        except Exception as e:
            return {"error": f"ツール実行エラー: {str(e)}"}
