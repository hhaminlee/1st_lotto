# 🍀 로또 번호 분석 및 추천 웹 애플리케이션

## 📖 프로젝트 설명

이 프로젝트는 동행복권 사이트의 역대 로또 당첨 번호 데이터를 기반으로, 다양한 통계 분석과 번호 추천 기능을 제공하는 웹 애플리케이션입니다.

기존 Python 스크립트로 구현되었던 로컬 분석 기능을 FastAPI 백엔드와 Vite+React 프론트엔드로 마이그레이션하여 사용자가 웹 환경에서 쉽고 편리하게 상호작용할 수 있도록 구축되었습니다.

## ✨ 주요 기능

-   **데이터 업데이트:** 동행복권 사이트에서 최신 회차까지의 당첨 번호를 스크래핑하여 데이터를 최신 상태로 유지합니다.
-   **역대 당첨 기록 조회:** 전체 로또 당첨 번호 이력을 테이블 형태로 조회할 수 있습니다. (최신 20개 표시)
-   **번호별 출현 빈도 분석:** 모든 회차에 걸쳐 각 번호가 몇 번 출현했는지 통계를 제공합니다.
-   **번호 추천 기능:**
    -   가장 많이 출현한 번호 20개 중에서 6개 조합 추천
    -   가장 적게 출현한 번호 20개 중에서 6개 조합 추천

## 🛠️ 기술 스택

### 백엔드 (Backend)

-   **Python 3**
-   **FastAPI:** API 서버 구축
-   **Pandas:** 데이터 처리 및 분석
-   **Requests & BeautifulSoup4:** 웹 스크래핑
-   **Uvicorn:** ASGI 서버

### 프론트엔드 (Frontend)

-   **Vite**
-   **React.js**
-   **Tailwind CSS:** UI 스타일링

## 📂 프로젝트 구조

```
.
├── backend/              # FastAPI 백엔드 서버
│   ├── main.py           # API 로직
│   ├── requirements.txt  # Python 의존성
│   └── lotto_history.csv # 로또 데이터
├── frontend/             # Vite+React 프론트엔드
│   ├── src/
│   │   └── App.jsx       # 메인 애플리케이션 컴포넌트
│   ├── package.json      # Node.js 의존성
│   └── ...
└── README.md             # 프로젝트 설명 파일
```

## 🚀 설치 및 실행 방법

이 프로젝트를 실행하기 위해서는 두 개의 터미널이 필요합니다.

### 1. 백엔드 서버 실행

```bash
# 1. 백엔드 디렉토리로 이동
cd backend

# 2. (최초 1회) 필요한 Python 패키지 설치
pip install -r requirements.txt

# 3. FastAPI 서버 실행
uvicorn main:app --reload
```

> 백엔드 서버는 `http://127.0.0.1:8000`에서 실행됩니다.

### 2. 프론트엔드 서버 실행

```bash
# 1. 프론트엔드 디렉토리로 이동
cd frontend

# 2. (최초 1회) 필요한 Node.js 패키지 설치
npm install

# 3. Vite 개발 서버 실행
npm run dev
```

> 프론트엔드 서버는 `http://localhost:5173` (또는 다른 포트)에서 실행됩니다. 터미널에 표시되는 주소로 접속하세요.
