"""Claude API 클라이언트"""

import os
import json
import logging
from typing import Optional, Dict, Any
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class ClaudeClient:
    """Anthropic Claude API 클라이언트"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        max_tokens: int = 8000,
    ):
        """
        Args:
            api_key: Anthropic API 키 (None이면 환경변수 사용)
            model: 사용할 모델 ID
            max_tokens: 최대 토큰 수
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_tokens = max_tokens

    def extract_json(
        self,
        user_prompt: str,
        system_prompt: str,
        temperature: float = 0.0,
    ) -> Dict[str, Any]:
        """
        JSON 추출을 위한 LLM 호출

        Args:
            user_prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            temperature: 온도 (0=결정적, 1=창의적)

        Returns:
            파싱된 JSON 딕셔너리

        Raises:
            ValueError: JSON 파싱 실패 시
        """
        try:
            logger.info(f"Claude API 호출 시작 (model={self.model})")

            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            # 응답 텍스트 추출
            content = response.content[0].text
            logger.debug(f"Claude 응답 (길이={len(content)})")

            # JSON 파싱 시도
            # 경우에 따라 마크다운 코드 블록으로 감싸질 수 있음
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            parsed = json.loads(content)
            logger.info("JSON 파싱 성공")

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.error(f"응답 내용:\n{content}")
            raise ValueError(f"LLM 응답이 유효한 JSON이 아닙니다: {e}")

        except Exception as e:
            logger.error(f"Claude API 호출 실패: {e}")
            raise

    def chat(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
    ) -> str:
        """
        일반 텍스트 생성

        Args:
            user_prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택)
            temperature: 온도

        Returns:
            생성된 텍스트
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{
                    "role": "user",
                    "content": user_prompt
                }]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Claude API 호출 실패: {e}")
            raise


if __name__ == "__main__":
    # 테스트
    logging.basicConfig(level=logging.INFO)

    client = ClaudeClient()

    # JSON 추출 테스트
    test_result = client.extract_json(
        system_prompt="너는 JSON을 생성하는 AI다.",
        user_prompt='{"name": "BTS", "members": ["RM", "진", "슈가"]} 형식으로 K-POP 그룹 정보를 반환해줘.',
    )

    print("테스트 결과:", json.dumps(test_result, ensure_ascii=False, indent=2))
