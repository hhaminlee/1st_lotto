"""
상수 정의 모듈
모든 하드코딩된 값들을 중앙 집중 관리
"""

# 동행복권 API URLs
DHLOTTERY_BASE_URL = "https://www.dhlottery.co.kr/common.do"
DHLOTTERY_MAIN_URL = f"{DHLOTTERY_BASE_URL}?method=main"
DHLOTTERY_API_URL = f"{DHLOTTERY_BASE_URL}?method=getLottoNumber&drwNo="

# Firebase 컬렉션 이름
COLLECTION_LOTTO_HISTORY = "lotto_history"
COLLECTION_WEEKLY_STATS = "weekly_stats"
COLLECTION_WEEKLY_HISTORY = "weekly_history"

# 로또 추첨 시간 설정 (토요일 오후 8시 45분)
DRAW_DAY = 5  # 토요일 (0=월요일, 6=일요일)
DRAW_HOUR = 20
DRAW_MINUTE = 45

# API 타임아웃 설정
DEFAULT_TIMEOUT = 10

# 번호 범위별 색상 (프론트엔드 참조용)
BALL_COLOR_RANGES = {
    (1, 10): "yellow",
    (11, 20): "blue",
    (21, 30): "red",
    (31, 40): "gray",
    (41, 45): "green",
}

# 당첨 등수 정의
PRIZE_RANKS = {
    1: "1등",  # 6개 일치
    2: "2등",  # 5개 + 보너스
    3: "3등",  # 5개 일치
    4: "4등",  # 4개 일치
    5: "5등",  # 3개 일치
    0: "낙첨",  # 2개 이하
}
