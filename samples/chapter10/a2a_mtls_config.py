import ssl


def create_mtls_context(
    cert_path: str,
    key_path: str,
    ca_cert_path: str,
) -> ssl.SSLContext:
    """mTLS用のSSLコンテキストを生成する"""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    # クライアント証明書の設定
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)
    # CA証明書の設定（相手の証明書を検証）
    context.load_verify_locations(cafile=ca_cert_path)
    # 相手の証明書を必ず検証する
    context.verify_mode = ssl.CERT_REQUIRED
    return context
