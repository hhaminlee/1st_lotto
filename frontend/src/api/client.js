/**
 * API 클라이언트
 * 백엔드 API와 통신하는 함수들
 */

// Vite 프록시(개발) 또는 Firebase Rewrite(배포)가 /api 요청을 처리하므로
// 항상 상대 경로를 사용합니다.
const API_BASE_URL = '';

/**
 * API 요청을 수행합니다.
 * @param {string} endpoint - API 엔드포인트
 * @param {Object} options - fetch 옵션
 * @returns {Promise<any>} 응답 데이터
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  const response = await fetch(url, config);
  
  if (!response.ok) {
    throw new Error(`API 요청 실패: ${response.status}`);
  }
  
  return response.json();
}

/**
 * 로또 역대 당첨 번호 조회
 */
export async function fetchHistory() {
  return request('/api/history');
}

/**
 * 번호 빈도 분석 조회
 */
export async function fetchAnalysis() {
  return request('/api/analyze');
}

/**
 * 추천 번호 조회
 * @param {'top20' | 'bottom20'} strategy - 추천 전략
 */
export async function fetchRecommendation(strategy) {
  return request(`/api/analyze?strategy=${strategy}`);
}

/**
 * 사용자 선택 저장
 * @param {number[]} numbers - 선택한 번호들
 * @param {string} strategy - 사용한 전략
 */
export async function saveSelection(numbers, strategy) {
  return request('/api/save-selection', {
    method: 'POST',
    body: JSON.stringify({ numbers, strategy }),
  });
}

/**
 * 주간 통계 조회
 */
export async function fetchWeeklyStats() {
  return request('/api/weekly-stats');
}

/**
 * 주간 통계 히스토리 조회
 */
export async function fetchWeeklyHistory() {
  return request('/api/weekly-history');
}
