import requests
import pandas as pd
import time

def get_lotto_win_numbers_api(draw_no):
    """
    JSON API를 사용하여 지정된 회차의 로또 당첨 번호를 가져오는 함수 (개선된 버전)
    """
    url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={draw_no}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json() # HTML 파싱 대신 JSON으로 바로 변환

        # API 응답이 성공이 아닌 경우 None 반환
        if data.get('returnValue') != 'success':
            print(f"{draw_no}회차 데이터를 가져오는 데 실패했습니다.")
            return None

        return {
            "draw_no": data.get('drwNo'),
            "num1": data.get('drwtNo1'),
            "num2": data.get('drwtNo2'),
            "num3": data.get('drwtNo3'),
            "num4": data.get('drwtNo4'),
            "num5": data.get('drwtNo5'),
            "num6": data.get('drwtNo6'),
            "bonus": data.get('bnusNo')
        }
    except requests.exceptions.RequestException as e:
        print(f"{draw_no}회차 조회 중 오류 발생: {e}")
        return None
    except ValueError: # response.json() 실패 시
        print(f"{draw_no}회차에서 유효한 JSON 데이터를 받지 못했습니다.")
        return None

# ----- 이하 로직은 거의 동일 -----

# (가져오는 함수 이름만 변경됨)
def scrape_and_save_all_draws(file_path='lotto_history.csv'):
    # 최신 회차 번호는 여전히 웹페이지에서 가져오는 것이 간편합니다.
    try:
        main_page_res = requests.get("https://www.dhlottery.co.kr/common.do?method=main")
        soup = BeautifulSoup(main_page_res.text, "html.parser")
        latest_no = int(soup.select_one('#lottoDrwNo').text)
    except Exception as e:
        print(f"최신 회차 번호를 가져오는 데 실패했습니다: {e}")
        return
        
    all_draws = []

    print(f"1회부터 {latest_no}회까지 모든 당첨 번호 수집을 시작합니다 (API 사용)...")
    
    for i in range(1, latest_no + 1):
        # BeautifulSoup을 사용하는 대신 새로 만든 API 함수를 호출
        draw_data = get_lotto_win_numbers_api(i)
        if draw_data:
            all_draws.append(draw_data)
            print(f"{i}회차 데이터 수집 완료.")
        time.sleep(0.1)

    df = pd.DataFrame(all_draws)
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
    print(f"\n총 {len(all_draws)}회차의 데이터를 '{file_path}' 파일로 성공적으로 저장했습니다.")

# --- 메인 실행 로직 ---
if __name__ == "__main__":
    # BeautifulSoup 라이브러리가 최신 회차를 가져올 때만 필요합니다.
    from bs4 import BeautifulSoup
    scrape_and_save_all_draws()