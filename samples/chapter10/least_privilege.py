from google.adk import Agent

# 顧客データ操作ツールは tool_auth.py（同ディレクトリ）の定義を共用する
try:
    from .tool_auth import (
        delete_customer_data,
        read_customer_data,
        update_customer_data,
    )
except ImportError:
    from tool_auth import (
        delete_customer_data,
        read_customer_data,
        update_customer_data,
    )


# 悪い例: 1つのエージェントに全権限を付与
# bad_agent = Agent(
#     name="god_agent",
#     tools=[read_data, write_data, delete_data, admin_tool, export_tool],
# )

# 良い例: 権限レベルに応じてエージェントを分離
read_only_agent = Agent(
    name="reader_agent",
    model="gemini-3.5-flash",
    instruction="顧客データの参照のみを行います。データの変更はできません。",
    tools=[read_customer_data],  # 読み取り専用ツールのみ
)

write_agent = Agent(
    name="writer_agent",
    model="gemini-3.5-flash",
    instruction="顧客データの参照と更新を行います。削除はできません。",
    tools=[read_customer_data, update_customer_data],  # 更新まで
)

admin_agent = Agent(
    name="admin_agent",
    model="gemini-3.5-flash",
    instruction="顧客データの全操作を行います。削除操作は実行前に確認を求めてください。",
    tools=[read_customer_data, update_customer_data, delete_customer_data],
)
