"""
로또 당첨번호 API 모듈
동행복권 사이트에서 당첨번호를 가져오는 로직
"""

from typing import Optional, TypedDict
import requests
from bs4 import BeautifulSoup

from .constants import DHLOTTERY_API_URL, DHLOTTERY_MAIN_URL, DEFAULT_TIMEOUT


class LottoDrawResult(TypedDict):
    """로또 추첨 결과 타입"""

    draw_no: int
    num1: int
    num2: int
    num3: int
    num4: int
    num5: int
    num6: int
    bonus: int


def get_lotto_win_numbers(
    draw_no: int, timeout: int = DEFAULT_TIMEOUT
) -> Optional[LottoDrawResult]:
    """
    특정 회차의 로또 당첨 번호를 가져옵니다.

    Args:
        draw_no: 회차 번호
        timeout: 요청 타임아웃 (초)

    Returns:
        LottoDrawResult 또는 실패 시 None
    """
    url = f"{DHLOTTERY_API_URL}{draw_no}"
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if data.get("returnValue") != "success":
            return None

        return LottoDrawResult(
            draw_no=data.get("drwNo"),
            num1=data.get("drwtNo1"),
            num2=data.get("drwtNo2"),
            num3=data.get("drwtNo3"),
            num4=data.get("drwtNo4"),
            num5=data.get("drwtNo5"),
            num6=data.get("drwtNo6"),
            bonus=data.get("bnusNo"),
        )
    except requests.exceptions.RequestException:
        return None
    except ValueError:
        # JSON 파싱 실패
        return None


def get_latest_draw_number(timeout: int = DEFAULT_TIMEOUT) -> Optional[int]:
    """
    동행복권 메인 페이지에서 최신 회차 번호를 가져옵니다.

    Args:
        timeout: 요청 타임아웃 (초)

    Returns:
        최신 회차 번호 또는 실패 시 None
    """
    try:
        response = requests.get(DHLOTTERY_MAIN_URL, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        draw_no_element = soup.select_one("#lottoDrwNo")

        if draw_no_element:
            return int(draw_no_element.text)
        return None
    except (requests.exceptions.RequestException, ValueError, AttributeError):
        return None


def fetch_draw_range(start_no: int, end_no: int) -> list[LottoDrawResult]:
    """
    지정된 범위의 회차 데이터를 가져옵니다.

    Args:
        start_no: 시작 회차
        end_no: 끝 회차 (포함)

    Returns:
        LottoDrawResult 리스트
    """
    results = []
    for draw_no in range(start_no, end_no + 1):
        result = get_lotto_win_numbers(draw_no)
        if result:
            results.append(result)
    return results
