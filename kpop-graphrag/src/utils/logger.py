"""로깅 설정"""

import logging
import sys
from pathlib import Path


def setup_logger(
    name: str = "kpop_graphrag",
    level: str = "INFO",
    log_file: Path | None = None,
) -> logging.Logger:
    """
    로거 설정

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (None이면 콘솔만)

    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 기존 핸들러 제거
    logger.handlers.clear()

    # 포맷터
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 (선택)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
