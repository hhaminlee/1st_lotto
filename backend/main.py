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
                
                # 최소한의 통계 데이터만 저장
                history_summary = {
                    "week": old_week,
                    "period": f"{old_week} 주차",
                    "total_participants": len(weekly_stats.get("users", [])),
                    "draw_no": results.get("draw_no"),
                    "winning_numbers": results.get("winning_numbers"),
                    "bonus_number": results.get("bonus_number"),
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
    """로또 역대 당첨 번호 업데이트 (Firebase 우선 저장)"""
    global lotto_history_df, db
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
            # Firebase에 새로운 회차 데이터 저장
            if db:
                try:
                    batch = db.batch()
                    collection_ref = db.collection('lotto_history')
                    
                    for draw_data in new_draws:
                        doc_ref = collection_ref.document(str(draw_data['draw_no']))
                        batch.set(doc_ref, draw_data)
                    
                    batch.commit()
                    print(f"Firebase에 새로운 회차 저장 완료: {len(new_draws)}개 회차")
                    
                except Exception as e:
                    print(f"Firebase 저장 실패, CSV 백업 저장: {e}")
                    # Firebase 실패시 CSV 백업 저장
                    new_df = pd.DataFrame(new_draws)
                    new_df.to_csv("lotto_history.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
            else:
                # Firebase 연결이 없으면 CSV에 저장
                new_df = pd.DataFrame(new_draws)
                new_df.to_csv("lotto_history.csv", mode='a', header=False, index=False, encoding='utf-8-sig')
                print("Firebase 연결 없음, CSV에 저장")
            
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

@app.post("/api/migrate-local-data")
def migrate_local_data():
    """로컬 JSON 데이터를 Firebase로 이식 (일회성 마이그레이션)"""
    global weekly_stats, db
    try:
        # 로컬 JSON 파일 읽기
        if os.path.exists("weekly_stats.json"):
            with open("weekly_stats.json", "r", encoding="utf-8") as f:
                local_data = json.load(f)
            
            if db:
                # Firebase에 직접 저장
                doc_ref = db.collection('weekly_stats').document('current')
                doc_ref.set(local_data)
                
                # 글로벌 변수도 업데이트
                weekly_stats = local_data
                
                return {
                    "success": True,
                    "message": f"로컬 데이터가 Firebase로 성공적으로 이식되었습니다. (사용자: {len(local_data.get('users', []))}명)",
                    "migrated_users": len(local_data.get("users", [])),
                    "current_week": local_data.get("current_week")
                }
            else:
                return {"success": False, "message": "Firebase 연결이 실패했습니다."}
        else:
            return {"success": False, "message": "로컬 데이터 파일이 존재하지 않습니다."}
    except Exception as e:
        return {"success": False, "message": f"마이그레이션 실패: {str(e)}"}

@app.post("/api/migrate-lotto-history")
def migrate_lotto_history():
    """로또 역대 당첨 번호 CSV를 Firebase로 이식"""
    global lotto_history_df, db
    try:
        if lotto_history_df.empty:
            return {"success": False, "message": "로또 히스토리 데이터가 없습니다."}
        
        if not db:
            return {"success": False, "message": "Firebase 연결이 실패했습니다."}
        
        # DataFrame을 딕셔너리 리스트로 변환
        history_records = lotto_history_df.to_dict('records')
        
        # 배치로 Firebase에 저장 (효율성을 위해)
        batch = db.batch()
        collection_ref = db.collection('lotto_history')
        
        # 기존 데이터 확인
        existing_docs = collection_ref.limit(1).get()
        if existing_docs:
            return {"success": False, "message": "로또 히스토리 데이터가 이미 Firebase에 존재합니다."}
        
        # 배치로 저장 (500개씩 제한)
        for i, record in enumerate(history_records):
            doc_ref = collection_ref.document(str(record['draw_no']))
            batch.set(doc_ref, {
                'draw_no': int(record['draw_no']),
                'num1': int(record['num1']), 'num2': int(record['num2']),
                'num3': int(record['num3']), 'num4': int(record['num4']),
                'num5': int(record['num5']), 'num6': int(record['num6']),
                'bonus': int(record['bonus']),
                'migrated_at': datetime.now().isoformat()
            })
            
            # 500개마다 배치 커밋
            if (i + 1) % 500 == 0:
                batch.commit()
                batch = db.batch()
        
        # 남은 데이터 커밋
        if len(history_records) % 500 != 0:
            batch.commit()
        
        return {
            "success": True,
            "message": f"로또 역대 당첨번호 {len(history_records)}회차가 Firebase로 성공적으로 이식되었습니다.",
            "migrated_records": len(history_records),
            "latest_draw": int(lotto_history_df['draw_no'].max()) if not lotto_history_df.empty else 0
        }
        
    except Exception as e:
        return {"success": False, "message": f"로또 히스토리 마이그레이션 실패: {str(e)}"}