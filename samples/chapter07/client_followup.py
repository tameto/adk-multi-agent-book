# samples/chapter07/client_followup.py
"""TASK_STATE_INPUT_REQUIRED のハンドリング（7-2-2）

サーバーが追加情報を要求した場合（TaskState.input_required）に、
既存Taskへ task_id / context_id を指定したフォローアップメッセージを
送信してタスクを継続するA2Aクライアント。

あわせて get_task() によるタスク状態ポーリングの実装例も含む。

実行前に expense_server を起動しておくこと:
    cd samples/chapter07 && python run_servers.py

非対話環境でデモ回答を指定したい場合:
    A2A_FOLLOWUP_ANSWER="2026-07-10、1,280円、品川から渋谷へのタクシー代です。"
"""

import asyncio
import os
import sys
import uuid
from typing import Any

from a2a.client import Client, ClientFactory, create_text_message_object
from a2a.types import (
    Message,
    Role,
    TaskQueryParams,
    TaskState,
)
from google.adk.a2a.converters.part_converter import convert_genai_part_to_a2a_part
from google.genai import types as genai_types

# タスクの終了状態（これ以上状態が変化しない）
TERMINAL_STATES = {TaskState.completed, TaskState.failed, TaskState.canceled}
DEFAULT_FOLLOWUP_ANSWER = "2026-07-10、1,280円、品川から渋谷へのタクシー代です。"


def _find_pending_function_call(task) -> dict[str, Any] | None:
    """ADK由来の input_required に含まれる FunctionCall を取得する"""
    message = task.status.message if task and task.status else None
    if not message:
        return None

    for part in message.parts:
        root = getattr(part, "root", None)
        metadata = getattr(root, "metadata", None) or {}
        data = getattr(root, "data", None)
        if metadata.get("adk_type") == "function_call" and isinstance(data, dict):
            return data
    return None


def _print_agent_message(task) -> None:
    """エージェントからの確認メッセージを表示する"""
    message = task.status.message if task and task.status else None
    if not message:
        return

    for part in message.parts:
        root = getattr(part, "root", None)
        text = getattr(root, "text", None)
        if text:
            print(f"エージェントからの質問: {text}")
            continue

        metadata = getattr(root, "metadata", None) or {}
        data = getattr(root, "data", None)
        if metadata.get("adk_type") == "function_call" and isinstance(data, dict):
            args = data.get("args") or {}
            prompt = args.get("message")
            if prompt:
                print(f"エージェントからの質問: {prompt}")


def _build_function_response_part(function_call: dict[str, Any], user_input: str):
    """ADKの FunctionCall に対応する FunctionResponse Part を作る"""
    response_part = convert_genai_part_to_a2a_part(
        genai_types.Part(
            function_response=genai_types.FunctionResponse(
                id=function_call["id"],
                name=function_call["name"],
                response={"answer": user_input},
            )
        )
    )
    if response_part is None:
        raise RuntimeError("function response をA2A Partへ変換できませんでした")
    return response_part


def _read_followup_answer() -> str:
    """対話入力または環境変数から追加回答を取得する"""
    env_answer = os.environ.get("A2A_FOLLOWUP_ANSWER")
    if env_answer:
        print(f"回答: {env_answer}")
        return env_answer
    if sys.stdin.isatty():
        return input("回答: ")

    print(f"回答: {DEFAULT_FOLLOWUP_ANSWER}")
    return DEFAULT_FOLLOWUP_ANSWER


async def handle_expense_with_followup(client: Client) -> None:
    """追加情報が必要な場合のフロー"""

    # 初回メッセージ送信（金額が不明確な場合を想定）
    initial = create_text_message_object(content="昨日のタクシー代を登録してください")

    task = None
    async for event in client.send_message(initial):
        if isinstance(event, tuple):
            task, _ = event

    # TASK_STATE_INPUT_REQUIRED の場合、追加情報を送信
    while task and task.status.state == TaskState.input_required:
        _print_agent_message(task)
        function_call = _find_pending_function_call(task)
        if function_call is None:
            raise RuntimeError("input_required task に FunctionCall が含まれていません")

        # 追加情報を送信（対話実行時は標準入力、非対話ではデモ回答を使用）
        user_input = _read_followup_answer()

        # 既存Taskに紐づけるため taskId / contextId を指定
        followup = Message(
            role=Role.user,
            parts=[_build_function_response_part(function_call, user_input)],
            message_id=str(uuid.uuid4()),
            task_id=task.id,
            context_id=task.context_id,
        )

        async for event in client.send_message(followup):
            if isinstance(event, tuple):
                task, _ = event

    # 最終結果を処理
    if task and task.status.state == TaskState.completed:
        print("タスク完了")
        printed_result = False
        for artifact in task.artifacts or []:
            for part in artifact.parts:
                if hasattr(part.root, "text"):
                    print(f"結果: {part.root.text}")
                    printed_result = True
        if not printed_result and task.status.message:
            for part in task.status.message.parts:
                if hasattr(part.root, "text"):
                    print(f"結果: {part.root.text}")
    elif task and task.status.state == TaskState.failed:
        print(f"タスク失敗: {task.status.message}")


async def poll_task_status(client: Client, task_id: str):
    """タスクの状態をポーリングする"""
    while True:
        task = await client.get_task(TaskQueryParams(id=task_id))
        state = task.status.state
        print(f"タスク状態: {state}")

        if state in TERMINAL_STATES:
            return task

        # 1秒待機して再確認（asyncio.sleep で非ブロッキング）
        await asyncio.sleep(1)


async def main() -> None:
    # 経費精算A2Aサーバー（ポート8001）に接続してフォローアップフローを実行
    client = await ClientFactory.connect("http://localhost:8001")
    await handle_expense_with_followup(client)


if __name__ == "__main__":
    asyncio.run(main())
