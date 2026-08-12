# samples/chapter04/session_db_config.py
"""DatabaseSessionServiceの接続設定例（4-2-2節）

環境変数によるdb_urlの組み立てと、Cloud SQL Auth Proxy経由の接続例。
認証情報はコードに直書きせず、環境変数から取得する。

必要な環境変数:
  DB_USER     : データベースユーザー名
  DB_PASSWORD : データベースパスワード
  DB_HOST     : データベースホスト名（Cloud SQL Auth Proxy使用時は不要）
  DB_NAME     : データベース名
"""
import os

from google.adk.sessions import DatabaseSessionService


def create_database_session_service() -> DatabaseSessionService:
    """本番環境向けのSessionServiceを生成する

    環境変数からDB接続情報を取得してdb_urlを組み立てる。
    """
    # 環境変数からDB接続情報を取得
    db_user = os.environ["DB_USER"]
    db_password = os.environ["DB_PASSWORD"]
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]

    return DatabaseSessionService(
        db_url=f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"
    )


def create_cloud_sql_session_service() -> DatabaseSessionService:
    """Cloud SQL Auth Proxy経由で接続するSessionServiceを生成する

    Cloud SQL Auth Proxyはlocalhost:5432でリッスンしている前提。
    Proxyを起動したうえで、db_urlにはlocalhostを指定するだけでよい。
    """
    # Cloud SQL Auth Proxy経由での接続
    return DatabaseSessionService(
        db_url=f"postgresql+asyncpg://{os.environ['DB_USER']}:"
               f"{os.environ['DB_PASSWORD']}@localhost:5432/"
               f"{os.environ['DB_NAME']}"
    )


if __name__ == "__main__":
    # 環境変数が揃っているかを確認する（接続自体は行わない）
    required = ("DB_USER", "DB_PASSWORD", "DB_NAME")
    missing = [name for name in required if name not in os.environ]
    if missing:
        print(f"環境変数が未設定です: {', '.join(missing)}")
    else:
        service = create_cloud_sql_session_service()
        print(f"DatabaseSessionServiceを生成しました: {type(service).__name__}")
