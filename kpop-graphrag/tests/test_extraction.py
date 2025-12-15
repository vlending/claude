"""엔티티 추출 테스트"""

import pytest
from pathlib import Path
import sys

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extraction import KpopEntityExtractor


@pytest.fixture
def sample_text():
    """샘플 위키 텍스트"""
    return """
    방탄소년단(BTS)은 대한민국의 7인조 보이 그룹이다.
    빅히트 엔터테인먼트에서 2013년 6월 13일에 데뷔했다.

    멤버는 RM, 진, 슈가, 제이홉, 지민, 뷔, 정국이다.

    2020년 8월 21일, 디지털 싱글 'Dynamite'를 발매했다.
    """


@pytest.mark.skipif(
    not Path("config/extraction_prompts.yaml").exists(),
    reason="설정 파일 없음"
)
def test_extractor_initialization():
    """추출기 초기화 테스트"""
    extractor = KpopEntityExtractor(
        config_path="config/extraction_prompts.yaml"
    )
    assert extractor is not None
    assert extractor.config is not None


def test_slugify():
    """슬러그 변환 테스트"""
    from src.extraction.entity_extractor import KpopEntityExtractor

    assert KpopEntityExtractor._slugify("방탄소년단") == "bangtansonyeondan"
    assert KpopEntityExtractor._slugify("BLACKPINK") == "blackpink"
    assert KpopEntityExtractor._slugify("아이브 (IVE)") == "aibeu-ive"


# 실제 API 호출 테스트는 환경변수가 설정되었을 때만 실행
@pytest.mark.skipif(
    not Path(".env").exists(),
    reason="환경변수 파일 없음 (API 키 필요)"
)
def test_extraction_with_api(sample_text):
    """실제 API 호출 테스트 (느림, 선택적)"""
    from dotenv import load_dotenv
    load_dotenv()

    extractor = KpopEntityExtractor(
        config_path="config/extraction_prompts.yaml"
    )

    result = extractor.extract(
        wiki_text=sample_text,
        wiki_title="방탄소년단"
    )

    assert result is not None
    assert "entities" in result.model_dump()
    assert len(result.entities.get("groups", [])) > 0
