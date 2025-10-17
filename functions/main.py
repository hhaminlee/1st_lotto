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
    """현재 주차 반환 (YYYY-WW 형식)"""
    now = datetime.now()
    return f"{now.year}-{now.isocalendar()[1]:02d}"

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

# 데이터 초기 로드
load_data()
load_weekly_stats()

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
            # 주간 통계 계산
            current_week = get_current_week()
            unique_users = set()
            for user in weekly_stats.get("users", []):
                unique_users.add(user.get("user_id", ""))
            
            stats = {
                "current_week": current_week,
                "unique_participants": len(unique_users),
                "total_selections": len(weekly_stats.get("users", [])),
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