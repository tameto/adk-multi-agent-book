# samples/chapter09/design_review/tools.py
"""設計レビューエージェントのツール関数

ADKで構築されたエージェントのソースコードを分析するためのツール群。
AST（抽象構文木）を使ってコード構造を解析する。
"""
import ast
import json
import os
from pathlib import Path

ALLOWED_MODEL_RECOMMENDATIONS = (
    "gemini-3.5-flash",
)
FORBIDDEN_MODEL_RECOMMENDATIONS = (
    "gemini-1.5-flash",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
)


def _allowed_review_dir() -> str:
    return os.path.realpath(os.environ.get("REVIEW_BASE_DIR", "."))


def _resolve_review_path(input_path: str) -> str:
    """cwdの違いを吸収しつつ、REVIEW_BASE_DIR内の実パスを返す。"""
    path = Path(input_path)
    candidates = [path]
    if not path.is_absolute():
        candidates.extend(parent / path for parent in Path.cwd().parents)

    existing_path = next(
        (candidate for candidate in candidates if candidate.exists()),
        path,
    )
    real_path = os.path.realpath(existing_path)
    allowed_dir = _allowed_review_dir()
    try:
        if os.path.commonpath([allowed_dir, real_path]) != allowed_dir:
            raise ValueError
    except ValueError:
        raise ValueError("許可されたディレクトリ外のパスは参照できません") from None
    return real_path


def read_source_file(file_path: str) -> dict:
    """指定されたPythonファイルのソースコードを読み取る

    Args:
        file_path: 読み取るPythonファイルのパス
    """
    try:
        real_path = _resolve_review_path(file_path)
    except ValueError:
        return {"error": "許可されたディレクトリ外のファイルは読み取れません"}

    if not os.path.exists(real_path):
        return {"error": f"ファイルが見つかりません: {file_path}"}

    if not file_path.endswith(".py"):
        return {"error": "Pythonファイル（.py）のみ対応しています"}

    with open(real_path, encoding="utf-8") as f:
        source_code = f.read()

    return {
        "file_path": file_path,
        "source_code": source_code,
        "lines": len(source_code.splitlines()),
    }


def list_files(directory_path: str = ".", pattern: str = "*.json") -> dict:
    """許可されたディレクトリ内のファイル一覧を返す。

    設計レビュー中に評価セットなどの補助ファイルの有無を確認するための
    読み取り専用ツール。REVIEW_BASE_DIR の外側は参照しない。

    Args:
        directory_path: 一覧するディレクトリのパス
        pattern: glob パターン。例: "*.json", "**/*.py"
    """
    if os.path.isabs(pattern) or ".." in Path(pattern).parts:
        return {"error": "patternに絶対パスや親ディレクトリ参照は指定できません"}

    try:
        real_dir = _resolve_review_path(directory_path)
    except ValueError:
        return {"error": "許可されたディレクトリ外の一覧は取得できません"}

    allowed_dir = _allowed_review_dir()
    target_dir = Path(real_dir)
    if not target_dir.exists():
        return {"error": f"ディレクトリが見つかりません: {directory_path}"}
    if not target_dir.is_dir():
        return {"error": f"ディレクトリではありません: {directory_path}"}

    files = [
        str(path.relative_to(allowed_dir))
        for path in sorted(target_dir.glob(pattern))
        if path.is_file()
    ]
    return {
        "directory_path": directory_path,
        "pattern": pattern,
        "files": files[:50],
        "truncated": len(files) > 50,
    }


def analyze_ast(source_code: str) -> dict:
    """Pythonソースコードを抽象構文木（AST）で解析する

    エージェント定義、ツール関数、コールバック、インポートを抽出する。

    Args:
        source_code: 解析するPythonソースコード
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"error": f"構文エラー: {e}"}

    agents: list[dict] = []
    tools: list[dict] = []
    callbacks: list[str] = []
    imports: list[str] = []

    # ADKエージェントクラス名
    agent_class_names = (
        "Agent", "LlmAgent", "SequentialAgent", "ParallelAgent", "LoopAgent",
    )

    for node in ast.walk(tree):
        # エージェントインスタンス化の検出
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in agent_class_names:
                agent_info: dict = {"type": func_name, "kwargs": {}}
                for keyword in node.keywords:
                    if keyword.arg == "name" and isinstance(
                        keyword.value, ast.Constant
                    ):
                        agent_info["kwargs"]["name"] = keyword.value.value
                    elif keyword.arg == "model" and isinstance(
                        keyword.value, ast.Constant
                    ):
                        agent_info["kwargs"]["model"] = keyword.value.value
                    elif keyword.arg == "tools" and isinstance(
                        keyword.value, ast.List
                    ):
                        agent_info["kwargs"]["tool_count"] = len(
                            keyword.value.elts
                        )
                    elif keyword.arg == "instruction" and isinstance(
                        keyword.value, ast.Constant
                    ):
                        agent_info["kwargs"]["instruction_length"] = len(
                            keyword.value.value
                        )
                    elif keyword.arg in (
                        "before_tool_callback",
                        "after_tool_callback",
                        "before_model_callback",
                        "after_model_callback",
                    ):
                        callbacks.append(keyword.arg)
                agents.append(agent_info)

        # 関数定義（ツール候補）の抽出
        if isinstance(node, ast.FunctionDef):
            has_docstring = (
                isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                if node.body
                else False
            )
            tools.append({
                "name": node.name,
                "args": [
                    arg.arg for arg in node.args.args if arg.arg != "self"
                ],
                "has_docstring": has_docstring,
            })

        # インポートの抽出
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

    return {
        "agents": agents,
        "tools": tools,
        "callbacks": callbacks,
        "imports": imports,
        "total_lines": len(source_code.splitlines()),
    }


def _parse_analysis_result(analysis_result: str | dict) -> dict:
    """エージェント間Stateに保存された解析結果を辞書として取り出す。"""
    if isinstance(analysis_result, dict):
        return analysis_result
    if not isinstance(analysis_result, str):
        return {"error": "analysis_result はJSON文字列またはdictで指定してください。"}

    text = analysis_result.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    for candidate in (text, _extract_json_like_object(text)):
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(candidate)
            except (SyntaxError, ValueError):
                continue
        if isinstance(parsed, dict):
            return parsed

    return {"error": "analysis_result を解析できませんでした。"}


def _extract_json_like_object(text: str) -> str:
    """説明文に埋め込まれたJSON/Python dict風オブジェクトを切り出す。"""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return ""
    return text[start:end + 1]


def _parse_error_result(message: str) -> dict:
    return {
        "total_findings": 1,
        "findings": [{
            "category": "quality",
            "severity": "high",
            "rule": "Q-PARSE",
            "message": message,
        }],
        "summary": {
            "architecture": 0,
            "security": 0,
            "operations": 0,
            "cost": 0,
            "quality": 1,
        },
        "model_policy": _model_policy(),
    }


def _model_policy() -> dict:
    return {
        "allowed_recommendations": list(ALLOWED_MODEL_RECOMMENDATIONS),
        "forbidden_recommendations": list(FORBIDDEN_MODEL_RECOMMENDATIONS),
        "message": (
            "ADK v2.2.0 前提のレビューでは、モデル提案は "
            "gemini-3.5-flash に限定する。"
            "gemini-1.5-flash、gemini-2.5-flash、gemini-3-flash-preview、"
            "gemini-3.1-pro-preview は古い例として提案しない。"
        ),
    }


def check_design_rules(analysis_result: str) -> dict:
    """AST解析結果に基づいて設計ルールへの準拠をチェックする

    第9章の設計原則10選に基づくルールでチェックを実行する。

    Args:
        analysis_result: analyze_astの出力結果（JSON文字列）
    """
    result = _parse_analysis_result(analysis_result)
    if error := result.get("error"):
        return _parse_error_result(error)

    findings: list[dict] = []
    agents = result.get("agents", [])
    callbacks = result.get("callbacks", [])
    imports = result.get("imports", [])

    # --- アーキテクチャチェック ---

    for agent in agents:
        kwargs = agent.get("kwargs", {})

        # A-2: ツール数チェック（推奨: 5個以下、上限: 10個）
        tool_count = kwargs.get("tool_count", 0)
        if tool_count > 10:
            findings.append({
                "category": "architecture",
                "severity": "high",
                "rule": "A-2",
                "agent": kwargs.get("name", "unknown"),
                "message": f"ツール数が{tool_count}個です。"
                           f"10個以下に分割してください。",
            })
        elif tool_count > 5:
            findings.append({
                "category": "architecture",
                "severity": "medium",
                "rule": "A-2",
                "agent": kwargs.get("name", "unknown"),
                "message": f"ツール数が{tool_count}個です。"
                           f"5個以下への分割を検討してください。",
            })

        # A-6: Instruction長チェック（推奨: 500文字以下）
        instruction_length = kwargs.get("instruction_length", 0)
        if instruction_length > 2000:
            findings.append({
                "category": "architecture",
                "severity": "high",
                "rule": "A-6",
                "agent": kwargs.get("name", "unknown"),
                "message": f"Instructionが{instruction_length}文字です。"
                           f"Agent Skillsで外部化してください。",
            })
        elif instruction_length > 500:
            findings.append({
                "category": "architecture",
                "severity": "medium",
                "rule": "A-6",
                "agent": kwargs.get("name", "unknown"),
                "message": f"Instructionが{instruction_length}文字です。"
                           f"構造化と外部化を検討してください。",
            })

    # --- セキュリティチェック ---

    # S-6: before_tool_callbackの有無
    has_before_tool = "before_tool_callback" in callbacks
    has_tools = any(
        a.get("kwargs", {}).get("tool_count", 0) > 0 for a in agents
    )
    if not has_before_tool and has_tools:
        findings.append({
            "category": "security",
            "severity": "medium",
            "rule": "S-6",
            "message": "before_tool_callbackが設定されていません。"
                       "ツール実行前の権限チェックを検討してください。",
        })

    # S-2: before_model_callbackの有無（入力検証）
    has_before_model = "before_model_callback" in callbacks
    if not has_before_model:
        findings.append({
            "category": "security",
            "severity": "medium",
            "rule": "S-2",
            "message": "before_model_callbackが設定されていません。"
                       "入力のサニタイズ・検証を検討してください。",
        })

    # S-4: 認証情報直書きチェック（os.environ経由での取得を確認）
    # imports に "os" が含まれていなければ、APIキー等を環境変数から
    # 取得する方法を用意していない可能性が高い
    has_os_import = "os" in imports
    if agents and not has_os_import:
        findings.append({
            "category": "security",
            "severity": "high",
            "rule": "S-4",
            "message": "os モジュールのインポートがありません。"
                       "APIキー等の認証情報がコードに直書きされている恐れがあります。"
                       "os.environ[...] 経由で取得してください。",
        })

    # --- 運用チェック ---

    # O-1: 可観測性（loggingまたはOpenTelemetryの使用）
    has_otel = any("opentelemetry" in imp for imp in imports)
    has_logging = any("logging" in imp for imp in imports)
    if not has_otel and not has_logging:
        findings.append({
            "category": "operations",
            "severity": "medium",
            "rule": "O-1",
            "message": "OpenTelemetryもloggingもインポートされていません。"
                       "可観測性の実装を検討してください。",
        })

    # O-4: LoopAgent使用時のmax_iterations確認
    has_loop_agent = any(a.get("type") == "LoopAgent" for a in agents)
    if has_loop_agent:
        findings.append({
            "category": "operations",
            "severity": "low",
            "rule": "O-4",
            "message": "LoopAgentが使用されています。"
                       "max_iterationsが設定されていることを確認してください。",
        })

    # --- コストチェック ---

    # C-1: モデル設定（本書の検証対象モデルから外れている場合に警告）
    models_used = [
        a.get("kwargs", {}).get("model", "") for a in agents
    ]
    non_standard_models = sorted(
        {
            model
            for model in models_used
            if model and model not in ALLOWED_MODEL_RECOMMENDATIONS
        }
    )
    if non_standard_models:
        findings.append({
            "category": "cost",
            "severity": "medium",
            "rule": "C-1",
            "message": "本書の検証対象外のモデルが使われています: "
                       f"{', '.join(non_standard_models)}。"
                       "サンプルではgemini-3.5-flashを明示してください。",
        })

    legacy_models = sorted(
        {
            model
            for model in models_used
            if model in FORBIDDEN_MODEL_RECOMMENDATIONS
        }
    )
    if legacy_models:
        findings.append({
            "category": "cost",
            "severity": "high",
            "rule": "C-1",
            "message": "古いモデル名が使われています: "
                       f"{', '.join(legacy_models)}。"
                       "ADK v2.2.0 前提の本書サンプルでは "
                       "gemini-3.5-flash へ更新してください。",
        })

    # --- 品質チェック ---

    # Q-1 / Q-2 はAST解析だけでは判定困難（評価セット存在確認・Instruction内容精査が必要）
    # 本ツールでは最低限の注意喚起を出力し、別途手動確認を促す
    if agents:
        findings.append({
            "category": "quality",
            "severity": "low",
            "rule": "Q-1",
            "message": "評価セット（eval_set.json）が用意されているか別途確認してください。",
        })

    return {
        "total_findings": len(findings),
        "findings": findings,
        "summary": {
            "architecture": len(
                [f for f in findings if f["category"] == "architecture"]
            ),
            "security": len(
                [f for f in findings if f["category"] == "security"]
            ),
            "operations": len(
                [f for f in findings if f["category"] == "operations"]
            ),
            "cost": len(
                [f for f in findings if f["category"] == "cost"]
            ),
            "quality": len(
                [f for f in findings if f["category"] == "quality"]
            ),
        },
        "model_policy": _model_policy(),
    }
