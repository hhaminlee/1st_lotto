"""
로또 번호 추천 시스템 - Firebase Functions
"""

import sys
import os

# shared 모듈 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import json
from firebase_functions import https_fn, scheduler_fn, options

from shared.constants import COLLECTION_LOTTO_HISTORY
from shared.lotto_api import get_lotto_win_numbers, get_latest_draw_number
from shared.analysis import analyze_number_frequency, get_recommended_numbers
from shared.weekly_stats import WeeklyStatsManager
from shared.firebase_client import get_firestore_client_for_functions

# Firestore 클라이언트
db = get_firestore_client_for_functions()

# 주간 통계 매니저
stats_manager = WeeklyStatsManager(db)

# 로또 데이터 DataFrame
lotto_history_df = pd.DataFrame()


def load_lotto_data() -> pd.DataFrame:
    """Firebase에서 로또 데이터를 로드합니다."""
    global lotto_history_df
    
    try:
        if db:
            collection_ref = db.collection(COLLECTION_LOTTO_HISTORY)
            docs = collection_ref.order_by('draw_no').get()
            
            if docs:
                firebase_data = []
                for doc in docs:
                    data = doc.to_dict()
                    firebase_data.append({
                        'draw_no': data['draw_no'],
                        'num1': data['num1'], 'num2': data['num2'],
                        'num3': data['num3'], 'num4': data['num4'],
                        'num5': data['num5'], 'num6': data['num6'],
                        'bonus': data['bonus']
                    })
                lotto_history_df = pd.DataFrame(firebase_data)
                return lotto_history_df
    except Exception as e:
        print(f"로또 데이터 로드 실패: {e}")
    
    return pd.DataFrame()


def create_response(data, status: int = 200) -> https_fn.Response:
    """JSON 응답을 생성합니다."""
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    return https_fn.Response(json.dumps(data), status=status, headers=headers)


@https_fn.on_request()
def lotto_api(req: https_fn.Request) -> https_fn.Response:
    """로또 API 메인 엔드포인트"""
    global lotto_history_df
    
    # CORS preflight
    if req.method == 'OPTIONS':
        return create_response({})
    
    path = req.path
    method = req.method
    
    try:
        # /api/history - 역대 당첨번호 조회
        if path == '/api/history' and method == 'GET':
            if lotto_history_df.empty:
                load_lotto_data()
            return create_response(lotto_history_df.to_dict(orient="records"))
        
        # /api/analyze - 빈도 분석 및 추천
        elif path == '/api/analyze' and method == 'GET':
            if lotto_history_df.empty:
                load_lotto_data()
            
            strategy = req.args.get('strategy')
            freq = analyze_number_frequency(lotto_history_df)
            
            if freq is None:
                return create_response({"error": "분석 실패"}, 500)
            
            if strategy in ['top20', 'bottom20']:
                recommended = get_recommended_numbers(freq, strategy)
                return create_response({"strategy": strategy, "numbers": recommended})
            
            return create_response(freq.to_dict())
        
        # /api/save-selection - 사용자 선택 저장
        elif path == '/api/save-selection' and method == 'POST':
            body = req.get_json()
            numbers = body.get('numbers', [])
            strategy = body.get('strategy', 'unknown')
            user_id = body.get('user_id')
            
            stats_manager.load()
            result = stats_manager.add_user_selection(numbers, strategy, user_id)
            return create_response(result)
        
        # /api/weekly-stats - 주간 통계 조회
        elif path == '/api/weekly-stats' and method == 'GET':
            stats_manager.load()
            return create_response(stats_manager.get_stats_summary())

        # /api/weekly-history - 주간 통계 히스토리 조회 (NEW)
        elif path == '/api/weekly-history' and method == 'GET':
            return create_response(stats_manager.get_history())
        
        # /api/update - 데이터 업데이트 (수동 트리거용)
        elif path == '/api/update' and method == 'POST':
            result = update_lotto_data_logic()
            return create_response(result)
        
        # /api/check-winners - 당첨자 확인
        elif path == '/api/check-winners' and method == 'POST':
            if lotto_history_df.empty:
                load_lotto_data()
            
            if not lotto_history_df.empty:
                latest_draw = lotto_history_df.iloc[-1].to_dict()
                stats_manager.load()
                stats_manager.check_winners(latest_draw)
            
            return create_response({
                "message": "당첨자 확인 완료",
                "results": stats_manager.stats.get("results", {})
            })
        
        # /api/reset-week - 주간 통계 초기화
        elif path == '/api/reset-week' and method == 'POST':
            stats_manager.load()
            stats_manager.reset()
            return create_response({"message": "주간 통계가 초기화되었습니다."})
        
        else:
            return create_response({"error": "Endpoint not found"}, 404)
    
    except Exception as e:
        return create_response({"error": str(e)}, 500)


def update_lotto_data_logic() -> dict:
    """로또 데이터 업데이트 핵심 로직"""
    global lotto_history_df
    
    try:
        latest_no = get_latest_draw_number()
        if latest_no is None:
            return {"error": "최신 회차 정보를 가져올 수 없습니다"}
        
        if lotto_history_df.empty:
            load_lotto_data()
        
        last_saved_no = 0
        if not lotto_history_df.empty:
            last_saved_no = int(lotto_history_df['draw_no'].max())
        
        if last_saved_no >= latest_no:
            return {"message": "데이터가 이미 최신 상태입니다."}
        
        # 새로운 회차 데이터 가져오기
        new_draws = []
        for i in range(last_saved_no + 1, latest_no + 1):
            draw_data = get_lotto_win_numbers(i)
            if draw_data:
                new_draws.append(draw_data)
        
        if new_draws and db:
            batch = db.batch()
            collection_ref = db.collection(COLLECTION_LOTTO_HISTORY)
            
            for draw_data in new_draws:
                doc_ref = collection_ref.document(str(draw_data['draw_no']))
                batch.set(doc_ref, draw_data)
            
            batch.commit()
            load_lotto_data()
            
            # 당첨자 확인
            stats_manager.load()
            stats_manager.check_winners(new_draws[-1])
        
        return {
            "message": f"{last_saved_no + 1}회부터 {latest_no}회까지 업데이트 완료",
            "count": len(new_draws)
        }
    except Exception as e:
        return {"error": f"업데이트 실패: {str(e)}"}


# 매주 토요일 오후 9시에 실행되는 스케줄러 함수
@scheduler_fn.on_schedule(
    schedule="0 21 * * 6",  # 매주 토요일 21:00 (KST 기준 아님, UTC 기준 유의 필요. 한국 시간 21시는 UTC 12시)
    timezone=scheduler_fn.Timezone("Asia/Seoul"),
)
def scheduled_lotto_update(event: scheduler_fn.ScheduledEvent) -> None:
    """자동 업데이트 스케줄러"""
    print(f"자동 업데이트 시작: {event.schedule_time}")
    result = update_lotto_data_logic()
    print(f"자동 업데이트 결과: {json.dumps(result, ensure_ascii=False)}")
