import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from firebase_functions import https_fn
import json
import os
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase 초기화
def initialize_firebase():
    try:
        # Firebase 앱이 이미 초기화되어 있는지 확인
        if not firebase_admin._apps:
            # Firebase Functions 환경에서는 자동으로 인증됨
            firebase_admin.initialize_app()
        
        return firestore.client()
    except Exception as e:
        print(f"Firebase 초기화 실패: {e}")
        return None

# Firestore 클라이언트
db = initialize_firebase()

# 전역 변수
lotto_history_df = pd.DataFrame()
weekly_stats = {"users": [], "current_week": "", "results": {}}

# --- Helper Functions ---
def get_current_week():
    """현재 주차를 반환 (로또 추첨일 기준: 토요일 오후 8시 45분)"""
    now = datetime.now()
    
    # 토요일 추첨시간 (오후 8시 45분)
    draw_time_saturday = now.replace(hour=20, minute=45, second=0, microsecond=0)
    
    # 현재 요일 (0=월요일, 6=일요일)
    current_weekday = now.weekday()
    
    # 이번 주 토요일 추첨시간 계산 (5 = 토요일)
    days_to_saturday = (5 - current_weekday) % 7
    this_saturday_draw = draw_time_saturday + timedelta(days=days_to_saturday)
    
    # 현재 시각이 이번 주 토요일 추첨시간 이전이면 이전 주 기준
    if now < this_saturday_draw:
        # 이전 주 토요일을 기준으로 주차 계산
        reference_saturday = this_saturday_draw - timedelta(days=7)
    else:
        # 이번 주 토요일을 기준으로 주차 계산
        reference_saturday = this_saturday_draw
    
    # 해당 토요일이 속한 주의 월요일을 기준으로 주차 계산
    monday_of_week = reference_saturday - timedelta(days=5)  # 토요일에서 5일 전이 월요일
    return f"{monday_of_week.year}-{monday_of_week.strftime('%U')}"

def load_data():
    """로또 역대 당첨 번호 데이터 로드 (Firebase 우선, CSV 백업)"""
    global lotto_history_df, db
    try:
        if db:
            # Firebase에서 데이터 로드 시도
            collection_ref = db.collection('lotto_history')
            docs = collection_ref.order_by('draw_no').get()
            
            if docs:
                # Firebase 데이터를 DataFrame으로 변환
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
                print(f"Firebase에서 로또 데이터 로드 완료: {len(firebase_data)}회차")
                return
            else:
                print("Firebase에 로또 데이터가 없음, CSV 파일에서 로드 시도")
        
        # Firebase 실패시 CSV 파일에서 로드 (백업)
        lotto_history_df = pd.read_csv("lotto_history.csv")
        print(f"CSV에서 로또 데이터 로드 완료: {len(lotto_history_df)}회차")
        
    except FileNotFoundError:
        lotto_history_df = pd.DataFrame()
        print("로또 데이터 파일을 찾을 수 없음")
    except Exception as e:
        lotto_history_df = pd.DataFrame()
        print(f"로또 데이터 로드 실패: {e}")

def load_weekly_stats():
    """주간 통계 로드 (Firebase 우선)"""
    global weekly_stats, db
    try:
        if db:
            doc_ref = db.collection('weekly_stats').document('current')
            doc = doc_ref.get()
            
            if doc.exists:
                weekly_stats = doc.to_dict()
                print("Firebase에서 주간 통계 로드 완료")
                return
        
        # Firebase 실패시 로컬 파일에서 로드
        with open("weekly_stats.json", "r", encoding="utf-8") as f:
            weekly_stats = json.load(f)
        print("로컬 파일에서 주간 통계 로드 완료")
    except FileNotFoundError:
        weekly_stats = {"users": [], "current_week": get_current_week(), "results": {}}
        print("주간 통계 파일이 없어 새로 생성")
    except Exception as e:
        weekly_stats = {"users": [], "current_week": get_current_week(), "results": {}}
        print(f"주간 통계 로드 실패: {e}")

def save_weekly_stats():
    """주간 통계 저장 (Firebase 우선)"""
    global weekly_stats, db
    try:
        if db:
            doc_ref = db.collection('weekly_stats').document('current')
            doc_ref.set(weekly_stats)
            print("Firebase에 주간 통계 저장 완료")
        else:
            # Firebase 실패시 로컬 파일에 저장
            with open("weekly_stats.json", "w", encoding="utf-8") as f:
                json.dump(weekly_stats, f, ensure_ascii=False, indent=2)
            print("로컬 파일에 주간 통계 저장 완료")
    except Exception as e:
        print(f"주간 통계 저장 실패: {e}")

def get_lotto_win_numbers_api(draw_no):
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('returnValue') != 'success':
            return None
        return {
            "draw_no": data.get('drwNo'),
            "num1": data.get('drwtNo1'), "num2": data.get('drwtNo2'),
            "num3": data.get('drwtNo3'), "num4": data.get('drwtNo4'),
            "num5": data.get('drwtNo5'), "num6": data.get('drwtNo6'),
            "bonus": data.get('bnusNo')
        }
    except requests.exceptions.RequestException:
        return None

def analyze_number_frequency(df):
    if df.empty:
        return None
    win_numbers_only = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']]
    all_numbers = win_numbers_only.values.flatten()
    return pd.Series(all_numbers).value_counts()

def calculate_prize_rank(user_numbers, winning_numbers, bonus_number):
    """당첨 등수 계산"""
    matching = len(set(user_numbers) & set(winning_numbers))
    has_bonus = bonus_number in user_numbers
    
    if matching == 6:
        return 1  # 1등
    elif matching == 5 and has_bonus:
        return 2  # 2등
    elif matching == 5:
        return 3  # 3등
    elif matching == 4:
        return 4  # 4등
    elif matching == 3:
        return 5  # 5등
    else:
        return 0  # 낙첨

def check_weekly_winner():
    """최신 추첨 결과와 사용자 선택을 비교하여 당첨자 확인"""
    global weekly_stats, lotto_history_df
    
    if lotto_history_df.empty or not weekly_stats.get("users"):
        return
    
    # 최신 추첨 결과 가져오기
    latest_draw = lotto_history_df.iloc[-1]
    winning_numbers = [int(latest_draw['num1']), int(latest_draw['num2']), int(latest_draw['num3']), 
                      int(latest_draw['num4']), int(latest_draw['num5']), int(latest_draw['num6'])]
    bonus_number = int(latest_draw['bonus'])
    
    # 각 사용자의 등수 계산
    results = {"1등": 0, "2등": 0, "3등": 0, "4등": 0, "5등": 0, "낙첨": 0}
    user_results = []
    
    for user in weekly_stats["users"]:
        rank = calculate_prize_rank(user["numbers"], winning_numbers, bonus_number)
        if rank == 1:
            results["1등"] += 1
        elif rank == 2:
            results["2등"] += 1
        elif rank == 3:
            results["3등"] += 1
        elif rank == 4:
            results["4등"] += 1
        elif rank == 5:
            results["5등"] += 1
        else:
            results["낙첨"] += 1
        
        user_results.append({
            "numbers": user["numbers"],
            "strategy": user["strategy"],
            "rank": rank,
            "timestamp": user.get("timestamp", "")
        })
    
    weekly_stats["results"] = {
        "draw_no": int(latest_draw['draw_no']),
        "winning_numbers": winning_numbers,
        "bonus_number": bonus_number,
        "summary": results,
        "user_results": user_results,
        "total_users": len(weekly_stats["users"])
    }
    
    save_weekly_stats()

def reset_weekly_stats():
    """주간 통계 초기화 (Firebase 기반, 최적화된 히스토리 저장)"""
    global weekly_stats, db
    current_week = get_current_week()
    
    # 새로운 주가 시작되면 초기화
    if weekly_stats.get("current_week") != current_week:
        # 이전 주 데이터가 있고 당첨 결과가 있으면 요약본만 저장
        if db and weekly_stats.get("users") and weekly_stats.get("results"):
            try:
                old_week = weekly_stats.get("current_week", "unknown")
                results = weekly_stats.get("results", {})
                
                # 최소한의 통계 데이터만 저장 (int 타입 변환)
                history_summary = {
                    "week": old_week,
                    "period": f"{old_week} 주차",
                    "total_participants": len(weekly_stats.get("users", [])),
                    "draw_no": int(results.get("draw_no", 0)) if results.get("draw_no") else None,
                    "winning_numbers": results.get("winning_numbers"),
                    "bonus_number": int(results.get("bonus_number", 0)) if results.get("bonus_number") else None,
                    "winners": results.get("summary", {
                        "1등": 0, "2등": 0, "3등": 0, "4등": 0, "5등": 0, "낙첨": 0
                    }),
                    "archived_at": datetime.now().isoformat()
                }
                
                # history 컬렉션에 요약 저장 (개인 번호는 저장하지 않음)
                backup_ref = db.collection('weekly_history').document(old_week)
                backup_ref.set(history_summary)
                print(f"주간 통계 요약 저장 완료: {old_week} ({history_summary['total_participants']}명 참여)")
                
            except Exception as e:
                print(f"주간 히스토리 저장 실패: {e}")
        
        # 새로운 주 초기화 (개인 데이터 완전 삭제)
        weekly_stats = {
            "users": [],
            "current_week": current_week,
            "results": {}
        }
        save_weekly_stats()
        print(f"주간 통계 초기화 완료: {current_week} (개인 데이터 삭제됨)")

# 데이터 초기 로드
load_data()
load_weekly_stats()
reset_weekly_stats()

# --- Firebase Functions ---
@https_fn.on_request()
def lotto_api(req: https_fn.Request) -> https_fn.Response:
    global lotto_history_df, weekly_stats
    
    # CORS 헤더
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }
    
    # OPTIONS 요청 처리 (CORS preflight)
    if req.method == 'OPTIONS':
        return https_fn.Response("", headers=headers)
    
    path = req.path
    method = req.method
    
    try:
        # API 라우팅
        if path == '/api/history' and method == 'GET':
            if lotto_history_df.empty:
                load_data()
            return https_fn.Response(
                json.dumps(lotto_history_df.to_dict(orient="records")),
                headers=headers
            )
        
        elif path == '/api/analyze' and method == 'GET':
            if lotto_history_df.empty:
                load_data()
            
            strategy = req.args.get('strategy')
            freq = analyze_number_frequency(lotto_history_df)
            
            if freq is None:
                return https_fn.Response(
                    json.dumps({"error": "No data available"}),
                    status=500,
                    headers=headers
                )
            
            if strategy == 'top20':
                top_numbers = freq.head(20).index.tolist()
                recommended_numbers = np.random.choice(top_numbers, size=6, replace=False)
                recommended_numbers.sort()
                return https_fn.Response(
                    json.dumps({"strategy": strategy, "numbers": recommended_numbers.tolist()}),
                    headers=headers
                )
            elif strategy == 'bottom20':
                bottom_numbers = freq.tail(20).index.tolist()
                recommended_numbers = np.random.choice(bottom_numbers, size=6, replace=False)
                recommended_numbers.sort()
                return https_fn.Response(
                    json.dumps({"strategy": strategy, "numbers": recommended_numbers.tolist()}),
                    headers=headers
                )
            else:
                return https_fn.Response(
                    json.dumps(freq.to_dict()),
                    headers=headers
                )
        
        elif path == '/api/save-selection' and method == 'POST':
            try:
                body = req.get_json()
                numbers = body.get('numbers', [])
                strategy = body.get('strategy', 'unknown')
                user_id = body.get('user_id', f'user_{len(weekly_stats["users"]) + 1}')
                
                # 주차 확인 및 필요시 초기화
                reset_weekly_stats()
                
                # 사용자 선택 저장
                user_data = {
                    "user_id": user_id,
                    "numbers": numbers,
                    "strategy": strategy,
                    "timestamp": datetime.now().isoformat()
                }
                
                weekly_stats["users"].append(user_data)
                save_weekly_stats()
                
                return https_fn.Response(
                    json.dumps({
                        "success": True,
                        "message": "선택이 저장되었습니다!",
                        "user_count": len(weekly_stats["users"])
                    }),
                    headers=headers
                )
            except Exception as e:
                return https_fn.Response(
                    json.dumps({"success": False, "error": str(e)}),
                    status=500,
                    headers=headers
                )
        
        elif path == '/api/weekly-stats' and method == 'GET':
            # 주차 확인
            reset_weekly_stats()
            
            # 고유 참여자 수 계산 (user_id 기준)
            unique_participants = len(set(user.get("user_id", "") for user in weekly_stats["users"] if user.get("user_id")))
            total_selections = len(weekly_stats["users"])
            
            stats = {
                "current_week": weekly_stats["current_week"],
                "unique_participants": unique_participants,
                "total_selections": total_selections,
                "results": weekly_stats.get("results", {}),
                "has_results": bool(weekly_stats.get("results"))
            }
            
            return https_fn.Response(
                json.dumps(stats),
                headers=headers
            )
        
        elif path == '/api/update' and method == 'POST':
            try:
                # 최신 회차 번호 가져오기
                main_page_res = requests.get("https://www.dhlottery.co.kr/common.do?method=main", timeout=10)
                soup = BeautifulSoup(main_page_res.text, "html.parser")
                latest_no = int(soup.select_one('#lottoDrwNo').text)
                
                last_saved_no = 0
                if not lotto_history_df.empty:
                    last_saved_no = lotto_history_df['draw_no'].max()
                
                if last_saved_no < latest_no:
                    new_draws = []
                    for i in range(int(last_saved_no) + 1, latest_no + 1):
                        draw_data = get_lotto_win_numbers_api(i)
                        if draw_data:
                            new_draws.append(draw_data)
                    
                    if new_draws and db:
                        # Firebase에 새로운 회차 데이터 저장
                        batch = db.batch()
                        collection_ref = db.collection('lotto_history')
                        
                        for draw_data in new_draws:
                            doc_ref = collection_ref.document(str(draw_data['draw_no']))
                            batch.set(doc_ref, draw_data)
                        
                        batch.commit()
                        
                        # 데이터 다시 로드
                        load_data()
                        
                        # 새로운 추첨 결과가 있으면 주간 당첨자 확인
                        check_weekly_winner()
                        
                        return https_fn.Response(
                            json.dumps({"message": f"Successfully updated from draw {last_saved_no + 1} to {latest_no}."}),
                            headers=headers
                        )
                
                return https_fn.Response(
                    json.dumps({"message": "Data is already up to date."}),
                    headers=headers
                )
            except Exception as e:
                return https_fn.Response(
                    json.dumps({"error": f"Update failed: {str(e)}"}),
                    status=500,
                    headers=headers
                )
        
        elif path == '/api/check-winners' and method == 'POST':
            # 수동으로 당첨자 확인 (테스트용)
            check_weekly_winner()
            return https_fn.Response(
                json.dumps({"message": "당첨자 확인이 완료되었습니다.", "results": weekly_stats.get("results", {})}),
                headers=headers
            )
        
        elif path == '/api/reset-week' and method == 'POST':
            # 수동으로 주간 통계 초기화 (관리자용)
            weekly_stats = {
                "users": [],
                "current_week": get_current_week(),
                "results": {}
            }
            save_weekly_stats()
            return https_fn.Response(
                json.dumps({"message": "주간 통계가 초기화되었습니다."}),
                headers=headers
            )
        
        else:
            return https_fn.Response(
                json.dumps({"error": "Endpoint not found"}),
                status=404,
                headers=headers
            )
    
    except Exception as e:
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers=headers
        )