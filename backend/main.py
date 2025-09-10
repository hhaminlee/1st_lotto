from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from typing import Optional
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Global variable for the DataFrame
lotto_history_df = pd.DataFrame()

def load_data():
    global lotto_history_df
    try:
        lotto_history_df = pd.read_csv("lotto_history.csv")
    except FileNotFoundError:
        lotto_history_df = pd.DataFrame()

# Initial data load
load_data()

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
            return {"message": f"Successfully updated from draw {last_saved_no + 1} to {latest_no}."}
    
    return {"message": "Data is already up to date."}