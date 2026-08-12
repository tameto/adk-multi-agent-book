# auth_provider_registry_example.py
# 2-7-5. AuthProviderRegistry: プラグイン認証（完全版）
# 複数の認証方式を1か所で登録・管理し、ツールごとにプロバイダーを割り当てる。
# 注意: @experimental(FeatureName.PLUGGABLE_AUTH) デコレータ付きの実験的API。

# v2.2.0でもサブモジュールからの明示的importが必要
from google.adk.auth.auth_provider_registry import AuthProviderRegistry

# --- ここから補完: 紙面では前提とされているプロバイダーのダミー実装 ---
# 実際の実装ではBaseAuthProviderを継承したプロバイダーを渡す。


class DummyApiKeyProvider:
    """API Key認証プロバイダーのダミー実装"""

    name: str = "api_key_provider"


class DummyOAuth2Provider:
    """OAuth 2.0認証プロバイダーのダミー実装"""

    name: str = "oauth2_provider"


api_key_provider = DummyApiKeyProvider()
oauth2_provider = DummyOAuth2Provider()

# --- ここまで補完 ---

# 認証プロバイダーの一元管理
registry = AuthProviderRegistry()
registry.register("weather_api", api_key_provider)
registry.register("calendar_api", oauth2_provider)

if __name__ == "__main__":
    # 登録内容の確認
    print("登録済みプロバイダー: weather_api（API Key）/ calendar_api（OAuth 2.0）")
