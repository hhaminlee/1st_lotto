import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import time
import os

# ==============================================================================
# 섹션 1: 데이터 수집 및 관리 (이전과 동일)
# ==============================================================================

def get_lotto_win_numbers_api(draw_no):
    """JSON API를 사용하여 특정 회차의 당첨 번호를 가져옵니다."""
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

def update_and_load_data(file_path='lotto_history.csv'):
    """데이터 파일을 확인하고 최신 버전으로 업데이트한 후 DataFrame을 반환합니다."""
    try:
        main_page_res = requests.get("https://www.dhlottery.co.kr/common.do?method=main", timeout=10)
        soup = BeautifulSoup(main_page_res.text, "html.parser")
        latest_no = int(soup.select_one('#lottoDrwNo').text)
    except Exception as e:
        print(f"최신 회차 정보를 가져올 수 없습니다: {e}")
        return pd.read_csv(file_path) if os.path.exists(file_path) else pd.DataFrame()

    if not os.path.exists(file_path):
        print(f"'{file_path}' 파일이 없어 전체 이력을 다운로드합니다.")
        all_draws = [get_lotto_win_numbers_api(i) for i in range(1, latest_no + 1) if get_lotto_win_numbers_api(i) is not None]
        df = pd.DataFrame(all_draws)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
    else:
        df = pd.read_csv(file_path)
        last_saved_no = df['draw_no'].max()
        if last_saved_no < latest_no:
            print(f"{last_saved_no + 1}회부터 {latest_no}회까지 데이터를 업데이트합니다.")
            new_draws = [get_lotto_win_numbers_api(i) for i in range(int(last_saved_no) + 1, latest_no + 1) if get_lotto_win_numbers_api(i) is not None]
            if new_draws:
                new_df = pd.DataFrame(new_draws)
                new_df.to_csv(file_path, mode='a', header=False, index=False, encoding='utf-8-sig')
                df = pd.concat([df, new_df], ignore_index=True)
    
    print("데이터가 최신 상태입니다.")
    return df

# ==============================================================================
# 섹션 2: 데이터 분석 (이전과 동일)
# ==============================================================================

def analyze_number_frequency(df):
    """DataFrame에서 번호별 출현 빈도를 분석합니다."""
    if df.empty:
        return None
    win_numbers_only = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']]
    all_numbers = win_numbers_only.values.flatten()
    return pd.Series(all_numbers).value_counts()

# ==============================================================================
# ✨ 섹션 3: 번호 생성 로직 (옵션별로 함수 분리) ✨
# ==============================================================================

def generate_from_top_20(freq):
    """가장 많이 나온 상위 20개 번호에서 6개를 생성합니다."""
    print("\n--- 가장 많이 나온 번호 Top 20 기반 추천 ---")
    top_20 = freq.head(20)
    recommended_numbers = np.random.choice(top_20.index, 6, replace=False)
    recommended_numbers.sort()
    print("🍀 추천 번호:", recommended_numbers)

def generate_from_bottom_20(freq):
    """가장 적게 나온 하위 20개 번호에서 6개를 생성합니다."""
    print("\n--- 가장 적게 나온 번호 Top 20 기반 추천 ---")
    bottom_20 = freq.tail(20)
    recommended_numbers = np.random.choice(bottom_20.index, 6, replace=False)
    recommended_numbers.sort()
    print("🍀 추천 번호:", recommended_numbers)

def generate_from_custom_numbers():
    """사용자가 직접 입력한 번호 목록에서 지정된 개수만큼 생성합니다."""
    print("\n--- 사용자 지정 번호 기반 추천 ---")
    while True:
        try:
            # 1. 사용자에게 번호 목록 입력받기
            custom_input = input("원하는 번호들을 띄어쓰기로 구분하여 입력하세요 (예: 1 7 15 22 30 41): ")
            # 입력값을 숫자 리스트로 변환 (중복 제거 및 정렬)
            custom_list = sorted(list(set([int(n) for n in custom_input.split()])))
            
            if len(custom_list) < 6:
                print("오류: 최소 6개 이상의 서로 다른 번호를 입력해야 합니다.")
                continue

            # 2. 몇 개를 뽑을지 입력받기
            num_to_select_str = input(f"총 {len(custom_list)}개의 번호를 입력했습니다. 이 중에서 몇 개를 뽑을까요? (기본값 6): ")
            # 입력이 없으면 기본값 6 사용
            num_to_select = int(num_to_select_str) if num_to_select_str else 6

            if len(custom_list) < num_to_select:
                print(f"오류: 입력한 번호의 개수({len(custom_list)}개)보다 더 많은 수를 뽑을 수 없습니다.")
                continue

            # 3. 최종 번호 추천
            recommended_numbers = np.random.choice(custom_list, num_to_select, replace=False)
            recommended_numbers.sort()
            print("🍀 추천 번호:", recommended_numbers)
            break
        except ValueError:
            print("잘못된 입력입니다. 숫자만 입력해주세요.")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            break

# ==============================================================================
# ✨ 섹션 4: 메인 메뉴 및 실행 로직 (새로 추가된 부분) ✨
# ==============================================================================

def main_menu(freq):
    """메인 메뉴를 표시하고 사용자 입력을 받아 해당 기능을 실행합니다."""
    while True:
        print("\n" + "="*40)
        print("          🍀 로또 번호 생성기 🍀")
        print("="*40)
        print("1. 가장 많이 나온 번호 Top 20에서 생성")
        print("2. 가장 적게 나온 번호 Top 20에서 생성")
        print("3. 내가 직접 입력한 번호 목록에서 생성")
        print("4. 프로그램 종료")
        print("="*40)
        
        choice = input("원하는 기능의 번호를 선택하세요 (1-4): ")

        if choice == '1':
            generate_from_top_20(freq)
        elif choice == '2':
            generate_from_bottom_20(freq)
        elif choice == '3':
            generate_from_custom_numbers()
        elif choice == '4':
            print("프로그램을 종료합니다. 행운을 빌어요!")
            break
        else:
            print("잘못된 선택입니다. 1에서 4 사이의 숫자를 입력해주세요.")

if __name__ == "__main__":
    # 1. 데이터 준비 (필요 시 업데이트)
    lotto_df = update_and_load_data()
    
    # 2. 데이터 분석
    if lotto_df is not None and not lotto_df.empty:
        number_freq = analyze_number_frequency(lotto_df)
        
        # 3. 메인 메뉴 보여주기
        if number_freq is not None:
            main_menu(number_freq)
    else:
        print("로또 데이터를 불러올 수 없습니다. 프로그램을 종료합니다.")