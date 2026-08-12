import jwt
from jwt import PyJWKClient


def verify_a2a_token(
    token: str,
    jwks_url: str,
    expected_audience: str,
    expected_issuer: str,
) -> dict:
    """A2Aリクエストに含まれるOAuth2トークンを検証する"""
    # JWKSエンドポイントから公開鍵を取得
    jwks_client = PyJWKClient(jwks_url)
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    # トークンを検証・デコード
    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=expected_audience,
        issuer=expected_issuer,
    )

    return payload
