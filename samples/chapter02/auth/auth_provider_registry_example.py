# auth_provider_registry_example.py
# 2-7-5. AuthProviderRegistry: プラグイン認証（完全版）
# 複数の認証方式を1か所で登録・管理し、ツールごとにプロバイダーを割り当てる。
# 注意: @experimental(FeatureName.PLUGGABLE_AUTH) デコレータ付きの実験的API。

from fastapi.openapi.models import APIKey

# v2.2.0でもサブモジュールからの明示的importが必要
from google.adk.auth.auth_provider_registry import AuthProviderRegistry
from google.adk.auth.auth_schemes import OpenIdConnectWithConfig
from google.adk.auth.base_auth_provider import BaseAuthProvider

# --- ここから補完: 紙面では前提とされているプロバイダーのダミー実装 ---
# プロバイダーはBaseAuthProviderを継承し、get_auth_credential()を実装する。


class DummyApiKeyProvider(BaseAuthProvider):
    """API Key認証プロバイダーのダミー実装"""

    @property
    def supported_auth_schemes(self) -> tuple[type, ...]:
        return (APIKey,)

    async def get_auth_credential(self, auth_config, context):
        # 実際の実装ではSecret Manager等からAPIキーを取得して返す
        return None


class DummyOAuth2Provider(BaseAuthProvider):
    """OAuth 2.0認証プロバイダーのダミー実装"""

    @property
    def supported_auth_schemes(self) -> tuple[type, ...]:
        return (OpenIdConnectWithConfig,)

    async def get_auth_credential(self, auth_config, context):
        # 実際の実装ではトークンストアから交換済みトークンを取得して返す
        return None


api_key_provider = DummyApiKeyProvider()
oauth2_provider = DummyOAuth2Provider()

# --- ここまで補完 ---

# 認証プロバイダーの一元管理
# 登録キーはツール名ではなく認証スキームの型。get_provider()は
# 渡されたauth_schemeの型でプロバイダーを引くため、文字列キーでは取得できない。
registry = AuthProviderRegistry()
registry.register(APIKey, api_key_provider)
registry.register(OpenIdConnectWithConfig, oauth2_provider)

if __name__ == "__main__":
    # 登録内容の確認（スキーマ型をキーに引き当てられることを確認する）
    print(f"APIKey -> {registry.get_provider(APIKey)}")
    oidc_provider = registry.get_provider(OpenIdConnectWithConfig)
    print(f"OpenIdConnectWithConfig -> {oidc_provider}")
