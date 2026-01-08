"""
주간 통계 관리 모듈
사용자 참여 현황 및 당첨 결과 추적
"""

from datetime import datetime, timedelta
from typing import TypedDict, Optional, Any

from .constants import DRAW_DAY, DRAW_HOUR, DRAW_MINUTE, PRIZE_RANKS


class UserSelection(TypedDict):
    """사용자 번호 선택 타입"""

    user_id: str
    numbers: list[int]
    strategy: str
    timestamp: str


class PrizeResult(TypedDict):
    """당첨 결과 타입"""

    draw_no: int
    winning_numbers: list[int]
    bonus_number: int
    summary: dict[str, int]
    user_results: list[dict]
    total_users: int


class WeeklyStats(TypedDict):
    """주간 통계 타입"""

    users: list[UserSelection]
    current_week: str
    results: dict


def get_current_week() -> str:
    """
    현재 주차를 반환합니다 (로또 추첨일 기준: 토요일 오후 8시 45분)

    Returns:
        "연도-주차번호" 형식의 문자열 (예: "2024-52")
    """
    now = datetime.now()

    # 토요일 추첨시간 설정
    draw_time_saturday = now.replace(
        hour=DRAW_HOUR, minute=DRAW_MINUTE, second=0, microsecond=0
    )

    # 현재 요일 (0=월요일, 6=일요일)
    current_weekday = now.weekday()

    # 이번 주 토요일 추첨시간 계산
    days_to_saturday = (DRAW_DAY - current_weekday) % 7
    this_saturday_draw = draw_time_saturday + timedelta(days=days_to_saturday)

    # 현재 시각이 이번 주 토요일 추첨시간 이전이면 이전 주 기준
    if now < this_saturday_draw:
        reference_saturday = this_saturday_draw - timedelta(days=7)
    else:
        reference_saturday = this_saturday_draw

    # 해당 토요일이 속한 주의 월요일을 기준으로 주차 계산
    monday_of_week = reference_saturday - timedelta(days=5)
    return f"{monday_of_week.year}-{monday_of_week.strftime('%U')}"


def calculate_prize_rank(
    user_numbers: list[int], winning_numbers: list[int], bonus_number: int
) -> int:
    """
    사용자 번호와 당첨 번호를 비교하여 등수를 계산합니다.

    Args:
        user_numbers: 사용자가 선택한 6개 번호
        winning_numbers: 당첨 번호 6개
        bonus_number: 보너스 번호

    Returns:
        등수 (1~5) 또는 낙첨시 0
    """
    matching = len(set(user_numbers) & set(winning_numbers))
    has_bonus = bonus_number in user_numbers

    if matching == 6:
        return 1  # 1등: 6개 일치
    elif matching == 5 and has_bonus:
        return 2  # 2등: 5개 + 보너스
    elif matching == 5:
        return 3  # 3등: 5개 일치
    elif matching == 4:
        return 4  # 4등: 4개 일치
    elif matching == 3:
        return 5  # 5등: 3개 일치
    else:
        return 0  # 낙첨


class WeeklyStatsManager:
    """주간 통계 관리 클래스"""

    def __init__(self, db: Any = None):
        """
        Args:
            db: Firestore 클라이언트 (None이면 로컬 모드)
        """
        self.db = db
        self._stats: WeeklyStats = {"users": [], "current_week": "", "results": {}}

    @property
    def stats(self) -> WeeklyStats:
        return self._stats

    def load(self) -> None:
        """Firebase 또는 로컬에서 주간 통계를 로드합니다."""
        from .constants import COLLECTION_WEEKLY_STATS

        if self.db:
            try:
                doc_ref = self.db.collection(COLLECTION_WEEKLY_STATS).document(
                    "current"
                )
                doc = doc_ref.get()
                if doc.exists:
                    self._stats = doc.to_dict()
                    return
            except Exception as e:
                print(f"Firebase에서 주간 통계 로드 실패: {e}")

        # 기본값 설정
        self._stats = {"users": [], "current_week": get_current_week(), "results": {}}

    def save(self) -> None:
        """Firebase에 주간 통계를 저장합니다."""
        from .constants import COLLECTION_WEEKLY_STATS

        if self.db:
            try:
                doc_ref = self.db.collection(COLLECTION_WEEKLY_STATS).document(
                    "current"
                )
                doc_ref.set(self._stats)
            except Exception as e:
                print(f"Firebase에 주간 통계 저장 실패: {e}")

    def add_user_selection(
        self, numbers: list[int], strategy: str, user_id: Optional[str] = None
    ) -> dict:
        """
        사용자 번호 선택을 저장합니다.

        Returns:
            저장 결과 딕셔너리
        """
        self.check_and_reset_week()

        user_data: UserSelection = {
            "user_id": user_id or f"user_{len(self._stats['users'])}",
            "numbers": numbers,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
        }

        self._stats["users"].append(user_data)
        self.save()

        return {
            "success": True,
            "message": "선택이 저장되었습니다!",
            "user_count": len(self._stats["users"]),
        }

    def check_and_reset_week(self) -> None:
        """새로운 주가 시작되면 통계를 초기화합니다."""
        from .constants import COLLECTION_WEEKLY_HISTORY

        current_week = get_current_week()

        if self._stats.get("current_week") != current_week:
            # 이전 주 데이터 아카이브
            if self.db and self._stats.get("users") and self._stats.get("results"):
                try:
                    old_week = self._stats.get("current_week", "unknown")
                    results = self._stats.get("results", {})

                    history_summary = {
                        "week": old_week,
                        "period": f"{old_week} 주차",
                        "total_participants": len(self._stats.get("users", [])),
                        "draw_no": results.get("draw_no"),
                        "winning_numbers": results.get("winning_numbers"),
                        "bonus_number": results.get("bonus_number"),
                        "winners": results.get(
                            "summary",
                            {
                                "1등": 0,
                                "2등": 0,
                                "3등": 0,
                                "4등": 0,
                                "5등": 0,
                                "낙첨": 0,
                            },
                        ),
                        "archived_at": datetime.now().isoformat(),
                    }

                    backup_ref = self.db.collection(COLLECTION_WEEKLY_HISTORY).document(
                        old_week
                    )
                    backup_ref.set(history_summary)
                except Exception as e:
                    print(f"주간 히스토리 저장 실패: {e}")

            # 새로운 주 초기화
            self._stats = {"users": [], "current_week": current_week, "results": {}}
            self.save()

    def check_winners(self, latest_draw: dict) -> None:
        """
        최신 추첨 결과와 사용자 선택을 비교하여 당첨자를 확인합니다.

        Args:
            latest_draw: 최신 추첨 결과 딕셔너리
        """
        if not self._stats.get("users"):
            return

        winning_numbers = [
            int(latest_draw["num1"]),
            int(latest_draw["num2"]),
            int(latest_draw["num3"]),
            int(latest_draw["num4"]),
            int(latest_draw["num5"]),
            int(latest_draw["num6"]),
        ]
        bonus_number = int(latest_draw["bonus"])

        # 등수별 카운트
        results_summary = {"1등": 0, "2등": 0, "3등": 0, "4등": 0, "5등": 0, "낙첨": 0}
        user_results = []

        for user in self._stats["users"]:
            rank = calculate_prize_rank(user["numbers"], winning_numbers, bonus_number)
            rank_name = PRIZE_RANKS.get(rank, "낙첨")
            results_summary[rank_name] += 1

            user_results.append(
                {
                    "numbers": user["numbers"],
                    "strategy": user["strategy"],
                    "rank": rank,
                    "timestamp": user.get("timestamp", ""),
                }
            )

        self._stats["results"] = {
            "draw_no": int(latest_draw["draw_no"]),
            "winning_numbers": winning_numbers,
            "bonus_number": bonus_number,
            "summary": results_summary,
            "user_results": user_results,
            "total_users": len(self._stats["users"]),
        }

        self.save()

    def get_stats_summary(self) -> dict:
        """주간 통계 요약을 반환합니다."""
        self.check_and_reset_week()

        unique_participants = len(
            set(
                user.get("user_id", "")
                for user in self._stats["users"]
                if user.get("user_id")
            )
        )

        return {
            "current_week": self._stats["current_week"],
            "unique_participants": unique_participants,
            "total_selections": len(self._stats["users"]),
            "results": self._stats.get("results", {}),
            "has_results": bool(self._stats.get("results")),
        }

    def reset(self) -> None:
        """주간 통계를 강제 초기화합니다."""
        self._stats = {"users": [], "current_week": get_current_week(), "results": {}}
        self.save()

    def get_history(self, limit: int = 10) -> list[dict]:
        """
        저장된 주간 통계 히스토리를 가져옵니다.
        
        Args:
            limit: 가져올 최대 개수
            
        Returns:
            히스토리 리스트 (최신순)
        """
        if not self.db:
            return []
            
        try:
            from .constants import COLLECTION_WEEKLY_HISTORY
            
            collection_ref = self.db.collection(COLLECTION_WEEKLY_HISTORY)
            docs = collection_ref.order_by('week', direction='DESCENDING').limit(limit).get()
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append(data)
                
            return history
        except Exception as e:
            print(f"주간 히스토리 조회 실패: {e}")
            return []
