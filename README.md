# mcp_as_local_module

## 概要
Pythonで書かれたWebアプリケーションにMCPサーバーを内部モジュールとして統合したサンプルです。
modular monolithアーキテクチャでMCPサーバをモジュールとして使い、将来的な外部化（マイクロサービス化）を見据えた設計になっています。

## 特徴
- MCPサーバーをアプリケーション内部モジュールとして使用
- 従来のREST APIとMCPツールの両方をサポート
- 将来的なマイクロサービス化に対応した設計
- FastAPIベースのモダンなWebアプリケーション

## ディレクトリ構成
```
src/
├── mcp_server/
│   └── server.py          # MCPサーバーモジュール
├── web_app/
│   └── main.py           # Webアプリケーション
├── config/
│   └── settings.py       # 設定管理
└── main.py              # エントリーポイント
```

## セットアップ
1. 仮想環境の利用:
   ```bash
   uv .venv
   source .venv/bin/activate
   ```

2. アプリケーション起動:
   ```bash
   python -m src.main
   ```

## API エンドポイント
- `GET /` - ルート
- `GET /health` - ヘルスチェック  
- `GET /api/users` - ユーザー一覧（REST）
- `GET /api/users/{user_id}` - ユーザー詳細（REST）
- `POST /api/users` - ユーザー作成（REST）
- `GET /api/mcp/tools` - MCPツール一覧
- `POST /api/mcp/tools/execute` - MCPツール実行

## 将来的な外部化対応
- `config/settings.py`でMCPモードを切り替え可能
- `mcp_mode: "external"`で外部MCPサーバーに対応
- 同じインターフェースで内部/外部を透過的に使用可能