# 5-5-3. ADKでのHITL実装（承認対象の業務ツール）
# 紙面の掲載パス: tools.py（samples/chapter05 ディレクトリから実行する前提）
"""HITLの承認フローが保護する業務ツール群

ApprovalManager.APPROVAL_RULES のキー（transfer_funds / delete_records /
update_user_role）と名前を一致させる。これらをエージェントに登録することで、
before_tool_callback が実行前に承認チェックを挟めるようになる。
"""


def transfer_funds(amount: int, to_account: str) -> dict:
    """指定口座へ送金する。

    Args:
        amount: 送金額（円）。10万円以上は承認が必要。
        to_account: 送金先の口座番号。
    """
    # デモ用のスタブ実装。実運用では決済APIを呼び出す。
    return {
        "status": "completed",
        "amount": amount,
        "to_account": to_account,
    }


def delete_records(table: str, count: int) -> dict:
    """指定テーブルのレコードを削除する。

    Args:
        table: 対象テーブル名。
        count: 削除件数。10件以上は承認が必要。
    """
    # デモ用のスタブ実装。実運用ではデータストアの削除を実行する。
    return {
        "status": "deleted",
        "table": table,
        "count": count,
    }


def update_user_role(user_id: str, new_role: str) -> dict:
    """ユーザーの権限ロールを変更する。常に承認が必要。

    Args:
        user_id: 対象ユーザーのID。
        new_role: 付与する新しいロール名。
    """
    # デモ用のスタブ実装。実運用ではIDプロバイダのAPIを呼び出す。
    return {
        "status": "updated",
        "user_id": user_id,
        "new_role": new_role,
    }
