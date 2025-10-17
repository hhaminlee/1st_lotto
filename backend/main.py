from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional, List
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# 환경변수 로드
load_dotenv()

# Firebase 초기화
def initialize_firebase():
    try:
        # 환경변수에서 Firebase 설정 가져오기
        firebase_config = {
            "type": "service_account",
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
        }
        
        # Firebase 앱이 이미 초기화되어 있는지 확인
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
        
        return firestore.client()
    except Exception as e:
        print(f"Firebase 초기화 실패: {e}")
        return None

# Firestore 클라이언트 초기화
db = initialize_firebase()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variables
lotto_history_df = pd.DataFrame()
weekly_stats = {"users": [], "current_week": None, "results": {}}

# Pydantic models
class UserSelection(BaseModel):
    numbers: List[int]
    strategy: str
    user_id: str = None

def load_data():
    global lotto_history_df
    try:
        lotto_history_df = pd.read_csv("lotto_history.csv")
    except FileNotFoundError:
        lotto_history_df = pd.DataFrame()

def load_weekly_stats():
    global weekly_stats, db
    try:
        if db:
            # Firestore에서 주간 통계 로드
            doc_ref = db.collection('weekly_stats').document('current')
            doc = doc_ref.get()
            if doc.exists:
                weekly_stats = doc.to_dict()
            else:
                weekly_stats = {"users": [], "current_week": None, "results": {}}
        else:
            # Firebase 연결 실패시 로컬 JSON 파일 사용 (백업)
            if os.path.exists("weekly_stats.json"):
                with open("weekly_stats.json", "r", encoding="utf-8") as f:
                    weekly_stats = json.load(f)
            else:
                weekly_stats = {"users": [], "current_week": None, "results": {}}
    except Exception as e:
        print(f"주간 통계 로드 실패: {e}")
        weekly_stats = {"users": [], "current_week": None, "results": {}}

def save_weekly_stats():
    global weekly_stats, db
    try:
        if db:
            # Firestore에 주간 통계 저장
            doc_ref = db.collection('weekly_stats').document('current')
            doc_ref.set(weekly_stats)
        else:
            # Firebase 연결 실패시 로컬 JSON 파일에 저장 (백업)
            with open("weekly_stats.json", "w", encoding="utf-8") as f:
                json.dump(weekly_stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"주간 통계 저장 실패: {e}")
        # 백업으로 로컬 파일에 저장
        try:
            with open("weekly_stats.json", "w", encoding="utf-8") as f:
                json.dump(weekly_stats, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

def get_current_week():
    """현재 주차를 반환 (로또 추첨일 기준)"""
    now = datetime.now()
    # 로또는 매주 토요일 추첨 (6 = 토요일)
    days_since_saturday = (now.weekday() + 2) % 7  # 토요일을 기준으로 계산
    last_saturday = now - timedelta(days=days_since_saturday)
    return last_saturday.strftime("%Y-%W")

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
    
    if lotto_history_df.empty or not weekly_stats["users"]:
        return
    
    # 최신 추첨 결과 가져오기
    latest_draw = lotto_history_df.iloc[-1]
    winning_numbers = [latest_draw['num1'], latest_draw['num2'], latest_draw['num3'], 
                      latest_draw['num4'], latest_draw['num5'], latest_draw['num6']]
    bonus_number = latest_draw['bonus']
    
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
        "draw_no": latest_draw['draw_no'],
        "winning_numbers": winning_numbers,
        "bonus_number": bonus_number,
        "summary": results,
        "user_results": user_results,
        "total_users": len(weekly_stats["users"])
    }
    
    save_weekly_stats()

def reset_weekly_stats():
    """주간 통계 초기화"""
    global weekly_stats
    current_week = get_current_week()
    
    # 새로운 주가 시작되면 초기화
    if weekly_stats["current_week"] != current_week:
        weekly_stats = {
            "users": [],
            "current_week": current_week,
            "results": {}
        }
        save_weekly_stats()

# Initial data load
load_data()
load_weekly_stats()
reset_weekly_stats()

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

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/history")
def get_history():
    if not lotto_history_df.empty:
        return lotto_history_df.to_dict(orient="records")
    return {"error": "No data available"}

@app.get("/api/analyze")
def get_analysis(strategy: Optional[str] = None):
    if lotto_history_df.empty:
        return {"error": "No data available"}
    freq = analyze_number_frequency(lotto_history_df)
    if freq is None:
        return {"error": "Analysis failed"}
    if strategy == "top20":
        top_20 = freq.head(20)
        recommended_numbers = np.random.choice(top_20.index, 6, replace=False)
        recommended_numbers.sort()
        return {"strategy": strategy, "numbers": recommended_numbers.tolist()}
    elif strategy == "bottom20":
        bottom_20 = freq.tail(20)
        recommended_numbers = np.random.choice(bottom_20.index, 6, replace=False)
        recommended_numbers.sort()
        return {"strategy": strategy, "numbers": recommended_numbers.tolist()}
    else:
        return freq.to_dict()

@app.post("/api/update")
def update_history():
    global lotto_history_df
    try:
        main_page_res = requests.get("https://www.dhlottery.co.kr/common.do?method=main", timeout=10)
        soup = BeautifulSoup(main_page_res.text, "html.parser")
        latest_no = int(soup.select_one('#lottoDrwNo').text)
    except Exception as e:
        return {"error": f"Could not fetch latest draw number: {e}"}

    last_saved_no = 0
    if not lotto_history_df.empty:
        last_saved_no = lotto_history_df['draw_no'].max()

    if last_saved_no < latest_no:
        new_draws = [get_lotto_win_numbers_api(i) for i in range(int(last_saved_no) + 1, latest_no + 1) if get_lotto_win_numbers_api(i) is not None]
        if new_draws:
            new_df = pd.DataFrame(new_draws)
            new_df.to_csv("lotto_history.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
            load_data() # Reload the data
            
            # 새로운 추첨 결과가 있으면 주간 당첨자 확인
            check_weekly_winner()
            
            return {"message": f"Successfully updated from draw {last_saved_no + 1} to {latest_no}."}
    
    return {"message": "Data is already up to date."}

@app.post("/api/save-selection")
def save_user_selection(selection: UserSelection):
    """사용자의 번호 선택을 저장"""
    global weekly_stats
    reset_weekly_stats()  # 주차 확인 및 필요시 초기화
    
    user_data = {
        "numbers": selection.numbers,
        "strategy": selection.strategy,
        "timestamp": datetime.now().isoformat(),
        "user_id": selection.user_id or f"user_{len(weekly_stats['users'])}"
    }
    
    weekly_stats["users"].append(user_data)
    save_weekly_stats()
    
    return {
        "success": True, 
        "message": "선택이 저장되었습니다!",
        "user_count": len(weekly_stats["users"])
    }

@app.get("/api/weekly-stats")
def get_weekly_stats():
    """주간 통계 조회"""
    global weekly_stats
    reset_weekly_stats()  # 주차 확인
    
    # 고유 참여자 수 계산 (user_id 기준)
    unique_participants = len(set(user.get("user_id", "") for user in weekly_stats["users"] if user.get("user_id")))
    total_selections = len(weekly_stats["users"])
    
    return {
        "current_week": weekly_stats["current_week"],
        "unique_participants": unique_participants,
        "total_selections": total_selections,
        "results": weekly_stats.get("results", {}),
        "has_results": bool(weekly_stats.get("results"))
    }

@app.post("/api/check-winners")
def manual_check_winners():
    """수동으로 당첨자 확인 (테스트용)"""
    check_weekly_winner()
    return {"message": "당첨자 확인이 완료되었습니다.", "results": weekly_stats.get("results", {})}

@app.post("/api/reset-week")
def manual_reset_week():
    """수동으로 주간 통계 초기화 (관리자용)"""
    global weekly_stats
    weekly_stats = {
        "users": [],
        "current_week": get_current_week(),
        "results": {}
    }
    save_weekly_stats()
    return {"message": "주간 통계가 초기화되었습니다."}