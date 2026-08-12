# samples/chapter07/run_servers.py
"""全A2Aサーバーの起動スクリプト

経費精算エージェント（ポート8001）と承認エージェント（ポート8002）を
サブプロセスとして同時に起動する。
Ctrl+C で全サーバーを停止する。
"""

import subprocess
import sys
import signal
import os
import site
import time
from contextlib import suppress
from pathlib import Path

# スクリプトのディレクトリ
BASE_DIR = Path(__file__).parent
REPO_ROOT = BASE_DIR.parents[1]


def _python_executable() -> str:
    """子サーバーを起動するPython実行ファイルを決定する"""
    virtual_env = os.environ.get("VIRTUAL_ENV")
    if virtual_env:
        candidate = Path(virtual_env) / "bin" / "python"
        if candidate.exists():
            return str(candidate)

    repo_venv = REPO_ROOT / ".venv-adk" / "bin" / "python"
    if repo_venv.exists():
        return str(repo_venv)

    return sys.executable


def _site_package_paths() -> list[str]:
    """子サーバーに引き継ぐsite-packages候補を返す"""
    paths: list[str] = []

    virtual_env = os.environ.get("VIRTUAL_ENV")
    candidates = []
    if virtual_env:
        candidates.append(Path(virtual_env))
    candidates.append(REPO_ROOT / ".venv-adk")

    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    for venv in candidates:
        site_packages = venv / "lib" / version / "site-packages"
        if site_packages.exists():
            paths.append(str(site_packages))

    paths.extend(p for p in site.getsitepackages() if p)
    return list(dict.fromkeys(paths))


def main() -> None:
    """全A2Aサーバーを起動する"""
    processes: list[subprocess.Popen] = []
    shutting_down = False
    child_env = os.environ.copy()
    child_env["PYTHONNOUSERSITE"] = "1"
    python_executable = _python_executable()
    site_paths = _site_package_paths()
    if site_paths:
        current_pythonpath = child_env.get("PYTHONPATH")
        child_env["PYTHONPATH"] = os.pathsep.join(
            site_paths + ([current_pythonpath] if current_pythonpath else [])
        )

    # サーバー定義: (名前, ディレクトリ, スクリプト)
    servers = [
        ("経費精算エージェント", BASE_DIR / "expense_server", "agent.py"),
        ("承認エージェント", BASE_DIR / "approval_server", "agent.py"),
    ]

    def shutdown() -> None:
        """全サーバーを停止する"""
        nonlocal shutting_down
        if shutting_down:
            return
        shutting_down = True
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)

        print("\n[INFO] 全サーバーを停止します...")
        for proc in processes:
            if proc.poll() is None:
                with suppress(ProcessLookupError, PermissionError):
                    os.killpg(proc.pid, signal.SIGTERM)

        for proc in processes:
            try:
                proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                with suppress(ProcessLookupError, PermissionError):
                    os.killpg(proc.pid, signal.SIGKILL)
                with suppress(subprocess.TimeoutExpired):
                    proc.wait(timeout=5)

        # Popen.poll() calls waitpid(..., WNOHANG), so it also reaps any child
        # that already exited while another process was still shutting down.
        deadline = time.monotonic() + 2
        for proc in processes:
            while proc.poll() is None and time.monotonic() < deadline:
                time.sleep(0.1)

        print("[INFO] 全サーバーが停止しました。")
        raise SystemExit(0)

    def request_shutdown(signum: int, frame=None) -> None:
        """待機ループを抜け、通常の制御フローで停止処理へ移る"""
        raise KeyboardInterrupt

    # Ctrl+C / SIGTERM を待機ループの外側で処理する
    signal.signal(signal.SIGINT, request_shutdown)
    signal.signal(signal.SIGTERM, request_shutdown)

    print("=" * 60)
    print("A2Aマルチエージェント経費精算システム")
    print("=" * 60)

    # 各サーバーをサブプロセスとして起動
    for name, cwd, script in servers:
        print(f"[INFO] {name} を起動中... ({cwd / script})")
        proc = subprocess.Popen(
            [python_executable, script],
            cwd=str(cwd),
            env=child_env,
            start_new_session=True,
        )
        processes.append(proc)
        print(f"[INFO] {name} (PID: {proc.pid}) を起動しました。")

    print()
    print("起動中のサーバー:")
    print("  - 経費精算エージェント: http://localhost:8001")
    print("  - 承認エージェント:     http://localhost:8002")
    print()
    print("Agent Card の確認:")
    print("  curl http://localhost:8001/.well-known/agent-card.json | jq .")
    print("  curl http://localhost:8002/.well-known/agent-card.json | jq .")
    print()
    print("停止するには Ctrl+C を押してください。")
    print("=" * 60)

    # サーバーの終了を待機
    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
