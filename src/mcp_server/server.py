import json
from enum import Enum
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import TextContent, Tool

from src.logger import make_logger

logger = make_logger(__name__)


class Gender(Enum):
    FEMALE = "female"
    MALE = "male"


class UserService:
    """ユーザー管理サービス（デモ用）"""

    def __init__(self):
        self._users = {
            "1": {"id": "1", "name": "田中太郎", "email": "tanaka@example.com", "gender": Gender.MALE.value},
            "2": {"id": "2", "name": "佐藤花子", "email": "sato@example.com", "gender": Gender.FEMALE.value},
        }

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self._users.get(user_id)

    async def get_users(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """複数のuser_idに対応するユーザーリストを取得"""
        users = []
        for user_id in user_ids:
            user = self._users.get(user_id)
            if user:
                users.append(user)
        return users

    async def get_users_by_gender(self, gender: str) -> List[Dict[str, Any]]:
        """指定されたgenderのユーザーリストを取得"""
        users = []
        for user in self._users.values():
            if user.get("gender") == gender:
                users.append(user)
        return users

    async def list_users(self) -> List[Dict[str, Any]]:
        return list(self._users.values())

    async def create_user(self, name: str, email: str, gender: str) -> Dict[str, Any]:
        user_id = str(len(self._users) + 1)
        user = {"id": user_id, "name": name, "email": email, "gender": gender}
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
                name="get_users",
                description="指定された複数のIDのユーザー情報リストを取得します",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_ids": {"type": "array", "items": {"type": "string"}, "description": "ユーザーIDのリスト"}
                    },
                    "required": ["user_ids"],
                },
            ),
            Tool(
                name="get_users_by_gender",
                description="指定されたgenderのユーザー情報リストを取得します",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "gender": {"type": "string", "enum": ["female", "male"], "description": "ユーザーの性別"}
                    },
                    "required": ["gender"],
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

            elif name == "get_users":
                users = await self.user_service.get_users(arguments["user_ids"])
                return [TextContent(type="text", text=json.dumps(users, ensure_ascii=False))]

            elif name == "get_users_by_gender":
                users = await self.user_service.get_users_by_gender(arguments["gender"])
                return [TextContent(type="text", text=json.dumps(users, ensure_ascii=False))]

            elif name == "list_users":
                users = await self.user_service.list_users()
                return [TextContent(type="text", text=json.dumps(users, ensure_ascii=False))]
            elif name == "create_user":
                user = await self.user_service.create_user(arguments["name"], arguments["email"], arguments["gender"])
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

            elif tool_name == "get_users":
                users = await self.user_service.get_users(arguments["user_ids"])
                return users
            elif tool_name == "list_users":
                users = await self.user_service.list_users()
                return users

            elif tool_name == "get_users_by_gender":
                users = await self.user_service.get_users_by_gender(arguments["gender"])
                return users

            elif tool_name == "create_user":
                user = await self.user_service.create_user(arguments["name"], arguments["email"], arguments["gender"])
                return user

            else:
                return {"error": f"未知のツール: {tool_name}"}
        except Exception as e:
            return {"error": f"ツール実行エラー: {str(e)}"}
