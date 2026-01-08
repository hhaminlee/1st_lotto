"""
로또 번호 분석 모듈
빈도 분석 및 번호 추천 로직
"""

from typing import Optional
import pandas as pd
import numpy as np


def analyze_number_frequency(df: pd.DataFrame) -> Optional[pd.Series]:
    """
    DataFrame에서 번호별 출현 빈도를 분석합니다.

    Args:
        df: 로또 당첨 번호 DataFrame (num1~num6 컬럼 필요)

    Returns:
        번호별 출현 빈도 Series (내림차순 정렬) 또는 실패 시 None
    """
    if df.empty:
        return None

    try:
        win_numbers_only = df[["num1", "num2", "num3", "num4", "num5", "num6"]]
        all_numbers = win_numbers_only.values.flatten()
        return pd.Series(all_numbers).value_counts()
    except KeyError:
        return None


def get_recommended_numbers(
    freq: pd.Series, strategy: str, count: int = 6
) -> list[int]:
    """
    전략에 따라 추천 번호를 생성합니다.

    Args:
        freq: 번호별 빈도 Series
        strategy: 'top20' (자주 나온 번호) 또는 'bottom20' (적게 나온 번호)
        count: 추천할 번호 개수 (기본 6개)

    Returns:
        정렬된 추천 번호 리스트
    """
    if freq is None or freq.empty:
        return []

    if strategy == "top20":
        # 가장 많이 나온 상위 20개 번호에서 선택
        candidate_numbers = freq.head(20).index.tolist()
    elif strategy == "bottom20":
        # 가장 적게 나온 하위 20개 번호에서 선택
        candidate_numbers = freq.tail(20).index.tolist()
    else:
        return []

    # 랜덤하게 count개 선택
    selected = np.random.choice(
        candidate_numbers, size=min(count, len(candidate_numbers)), replace=False
    )
    return sorted(selected.tolist())
