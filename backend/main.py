"""
로또 번호 추천 시스템 - FastAPI 백엔드
"""

import sys
import os

# shared 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

from shared.constants import COLLECTION_LOTTO_HISTORY
from shared.lotto_api import get_lotto_win_numbers, get_latest_draw_number
from shared.analysis import analyze_number_frequency, get_recommended_numbers
from shared.weekly_stats import WeeklyStatsManager
from shared.firebase_client import initialize_firebase

# 환경변수 로드
load_dotenv()

# Firebase 초기화
db = initialize_firebase(use_env=True)

# 주간 통계 매니저
stats_manager = WeeklyStatsManager(db)
stats_manager.load()

# 로또 데이터 DataFrame
lotto_history_df = pd.DataFrame()


def load_lotto_data() -> pd.DataFrame:
    """Firebase 또는 CSV에서 로또 데이터를 로드합니다."""
    global lotto_history_df

    try:
        if db:
            collection_ref = db.collection(COLLECTION_LOTTO_HISTORY)
            docs = collection_ref.order_by("draw_no").get()

            if docs:
                firebase_data = []
                for doc in docs:
                    data = doc.to_dict()
                    firebase_data.append(
                        {
                            "draw_no": data["draw_no"],
                            "num1": data["num1"],
                            "num2": data["num2"],
                            "num3": data["num3"],
                            "num4": data["num4"],
                            "num5": data["num5"],
                            "num6": data["num6"],
                            "bonus": data["bonus"],
                        }
                    )
                lotto_history_df = pd.DataFrame(firebase_data)
                print(f"Firebase에서 로또 데이터 로드 완료: {len(firebase_data)}회차")
                return lotto_history_df

        # Firebase 실패 시 CSV 백업
        csv_path = os.path.join(os.path.dirname(__file__), "lotto_history.csv")
        if os.path.exists(csv_path):
            lotto_history_df = pd.read_csv(csv_path)
            print(f"CSV에서 로또 데이터 로드 완료: {len(lotto_history_df)}회차")

    except Exception as e:
        print(f"로또 데이터 로드 실패: {e}")
        lotto_history_df = pd.DataFrame()

    return lotto_history_df


# 초기 데이터 로드
load_lotto_data()

# FastAPI 앱 생성
app = FastAPI(
    title="로또 번호 추천 API",
    description="AI 기반 로또 번호 분석 및 추천 시스템",
    version="2.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic 모델
class UserSelection(BaseModel):
    numbers: List[int]
    strategy: str
    user_id: Optional[str] = None


# API 엔드포인트
@app.get("/")
def read_root():
    return {"message": "로또 번호 추천 API", "version": "2.0.0"}


@app.get("/api/history")
def get_history():
    """로또 역대 당첨 번호 조회"""
    if lotto_history_df.empty:
        load_lotto_data()

    if not lotto_history_df.empty:
        return lotto_history_df.to_dict(orient="records")
    return {"error": "데이터를 불러올 수 없습니다"}


@app.get("/api/analyze")
def get_analysis(strategy: Optional[str] = None):
    """번호 빈도 분석 및 추천"""
    if lotto_history_df.empty:
        load_lotto_data()

    if lotto_history_df.empty:
        return {"error": "데이터를 불러올 수 없습니다"}

    freq = analyze_number_frequency(lotto_history_df)
    if freq is None:
        return {"error": "분석에 실패했습니다"}

    # 전략별 추천
    if strategy in ["top20", "bottom20"]:
        recommended = get_recommended_numbers(freq, strategy)
        return {"strategy": strategy, "numbers": recommended}

    # 전체 빈도 반환
    return freq.to_dict()


@app.post("/api/update")
def update_history():
    """최신 로또 데이터 업데이트"""
    global lotto_history_df

    try:
        latest_no = get_latest_draw_number()
        if latest_no is None:
            return {"error": "최신 회차 정보를 가져올 수 없습니다"}

        last_saved_no = 0
        if not lotto_history_df.empty:
            last_saved_no = int(lotto_history_df["draw_no"].max())

        if last_saved_no >= latest_no:
            return {"message": "데이터가 이미 최신 상태입니다."}

        # 새로운 회차 데이터 가져오기
        new_draws = []
        for i in range(last_saved_no + 1, latest_no + 1):
            draw_data = get_lotto_win_numbers(i)
            if draw_data:
                new_draws.append(draw_data)

        if new_draws and db:
            # Firebase에 저장
            batch = db.batch()
            collection_ref = db.collection(COLLECTION_LOTTO_HISTORY)

            for draw_data in new_draws:
                doc_ref = collection_ref.document(str(draw_data["draw_no"]))
                batch.set(doc_ref, draw_data)

            batch.commit()
            print(f"Firebase에 새로운 회차 저장 완료: {len(new_draws)}개 회차")

        # 데이터 다시 로드
        load_lotto_data()

        # 당첨자 확인
        if new_draws:
            stats_manager.check_winners(new_draws[-1])

        return {"message": f"{last_saved_no + 1}회부터 {latest_no}회까지 업데이트 완료"}

    except Exception as e:
        return {"error": f"업데이트 실패: {str(e)}"}


@app.post("/api/save-selection")
def save_user_selection(selection: UserSelection):
    """사용자 번호 선택 저장"""
    result = stats_manager.add_user_selection(
        numbers=selection.numbers,
        strategy=selection.strategy,
        user_id=selection.user_id,
    )
    return result


@app.get("/api/weekly-stats")
def get_weekly_stats():
    """주간 통계 조회"""
    return stats_manager.get_stats_summary()


@app.post("/api/check-winners")
def manual_check_winners():
    """수동 당첨자 확인 (테스트용)"""
    if not lotto_history_df.empty:
        latest_draw = lotto_history_df.iloc[-1].to_dict()
        stats_manager.check_winners(latest_draw)
    return {
        "message": "당첨자 확인 완료",
        "results": stats_manager.stats.get("results", {}),
    }


@app.post("/api/reset-week")
def manual_reset_week():
    """주간 통계 초기화 (관리자용)"""
    stats_manager.reset()
    return {"message": "주간 통계가 초기화되었습니다."}
