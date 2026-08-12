# 5-4-5. 発展: DLP（Data Loss Prevention）統合
# 実行には google-cloud-dlp パッケージと GOOGLE_CLOUD_PROJECT 環境変数が必要
"""Google Cloud DLP APIを活用したガードレール"""
import os
from typing import Optional

from google.cloud import dlp_v2
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types


class DlpGuardrail:
    """DLP APIを使用した個人情報保護ガードレール"""

    def __init__(self):
        self.dlp_client = dlp_v2.DlpServiceClient()
        self.project_id = os.environ["GOOGLE_CLOUD_PROJECT"]

    def check_output(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> Optional[LlmResponse]:
        """LLM出力をDLP APIで検査する"""
        response_text = self._extract_text(llm_response)
        if not response_text:
            return None

        # DLP APIで検査
        findings = self._inspect_content(response_text)

        if findings:
            # 検出された情報をマスキング
            masked_text = self._deidentify_content(response_text)
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text=masked_text)],
                    role="model",
                )
            )

        return None

    def _inspect_content(self, text: str) -> list:
        """DLP APIでコンテンツを検査する"""
        parent = f"projects/{self.project_id}/locations/global"

        inspect_config = dlp_v2.InspectConfig(
            info_types=[
                dlp_v2.InfoType(name="PHONE_NUMBER"),
                dlp_v2.InfoType(name="EMAIL_ADDRESS"),
                dlp_v2.InfoType(name="CREDIT_CARD_NUMBER"),
                dlp_v2.InfoType(name="JAPAN_MY_NUMBER"),
                dlp_v2.InfoType(name="JAPAN_PASSPORT"),
            ],
            min_likelihood=dlp_v2.Likelihood.LIKELY,
        )

        item = dlp_v2.ContentItem(value=text)

        response = self.dlp_client.inspect_content(
            request={
                "parent": parent,
                "inspect_config": inspect_config,
                "item": item,
            }
        )

        return response.result.findings

    def _deidentify_content(self, text: str) -> str:
        """DLP APIでコンテンツを匿名化する"""
        parent = f"projects/{self.project_id}/locations/global"

        deidentify_config = dlp_v2.DeidentifyConfig(
            info_type_transformations=dlp_v2.InfoTypeTransformations(
                transformations=[
                    dlp_v2.InfoTypeTransformations.InfoTypeTransformation(
                        primitive_transformation=dlp_v2.PrimitiveTransformation(
                            replace_with_info_type_config=dlp_v2.ReplaceWithInfoTypeConfig()
                        )
                    )
                ]
            )
        )

        inspect_config = dlp_v2.InspectConfig(
            info_types=[
                dlp_v2.InfoType(name="PHONE_NUMBER"),
                dlp_v2.InfoType(name="EMAIL_ADDRESS"),
                dlp_v2.InfoType(name="CREDIT_CARD_NUMBER"),
            ],
        )

        item = dlp_v2.ContentItem(value=text)

        response = self.dlp_client.deidentify_content(
            request={
                "parent": parent,
                "inspect_config": inspect_config,
                "deidentify_config": deidentify_config,
                "item": item,
            }
        )

        return response.item.value

    def _extract_text(
        self,
        response: LlmResponse,
    ) -> Optional[str]:
        """レスポンスからテキストを抽出する"""
        if not response.content or not response.content.parts:
            return None
        for part in response.content.parts:
            if part.text:
                return part.text
        return None
