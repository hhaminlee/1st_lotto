import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from firebase_functions import https_fn

# --- Helper Functions ---
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

# --- Firebase Functions ---
@https_fn.on_request()
def lotto_api(req: https_fn.Request) -> https_fn.Response:
    import json
    
    path = req.path
    method = req.method
    
    if path == '/api/history' and method == 'GET':
        try:
            df = pd.read_csv("lotto_history.csv")
            return https_fn.Response(
                json.dumps(df.to_dict(orient="records")),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        except FileNotFoundError:
            return https_fn.Response(
                json.dumps({"error": "No data available"}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    elif path.startswith('/api/analyze') and method == 'GET':
        try:
            df = pd.read_csv("lotto_history.csv")
        except FileNotFoundError:
            return https_fn.Response(
                json.dumps({"error": "No data available"}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        freq = analyze_number_frequency(df)
        if freq is None:
            return https_fn.Response(
                json.dumps({"error": "Analysis failed"}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        strategy = req.args.get('strategy')
        if strategy == "top20":
            top_20 = freq.head(20)
            recommended_numbers = np.random.choice(top_20.index, 6, replace=False)
            recommended_numbers.sort()
            return https_fn.Response(
                json.dumps({"strategy": strategy, "numbers": recommended_numbers.tolist()}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        elif strategy == "bottom20":
            bottom_20 = freq.tail(20)
            recommended_numbers = np.random.choice(bottom_20.index, 6, replace=False)
            recommended_numbers.sort()
            return https_fn.Response(
                json.dumps({"strategy": strategy, "numbers": recommended_numbers.tolist()}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
        else:
            return https_fn.Response(
                json.dumps(freq.to_dict()),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )
    
    elif path == '/api/update' and method == 'POST':
        try:
            main_page_res = requests.get("https://www.dhlottery.co.kr/common.do?method=main", timeout=10)
            soup = BeautifulSoup(main_page_res.text, "html.parser")
            latest_no = int(soup.select_one('#lottoDrwNo').text)
        except Exception as e:
            return https_fn.Response(
                json.dumps({"error": f"Could not fetch latest draw number: {e}"}),
                content_type="application/json",
                headers={"Access-Control-Allow-Origin": "*"}
            )

        try:
            df = pd.read_csv("lotto_history.csv")
            last_saved_no = df['draw_no'].max()
        except FileNotFoundError:
            df = pd.DataFrame()
            last_saved_no = 0

        if last_saved_no < latest_no:
            new_draws = [get_lotto_win_numbers_api(i) for i in range(int(last_saved_no) + 1, latest_no + 1) if get_lotto_win_numbers_api(i) is not None]
            if new_draws:
                new_df = pd.DataFrame(new_draws)
                updated_df = pd.concat([df, new_df], ignore_index=True)
                updated_df.to_csv("lotto_history.csv", index=False, encoding='utf-8-sig')
                return https_fn.Response(
                    json.dumps({"message": f"Successfully updated from draw {last_saved_no + 1} to {latest_no}."}),
                    content_type="application/json",
                    headers={"Access-Control-Allow-Origin": "*"}
                )
        
        return https_fn.Response(
            json.dumps({"message": "Data is already up to date."}),
            content_type="application/json",
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    return https_fn.Response("Not Found", status=404)