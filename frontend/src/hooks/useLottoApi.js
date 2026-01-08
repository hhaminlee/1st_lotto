/**
 * 로또 API 커스텀 훅
 * API 호출과 상태 관리를 캡슐화합니다.
 */

import { useState, useCallback } from 'react';
import * as api from '../api/client';

export function useLottoApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState('');

  /**
   * 공통 API 호출 래퍼
   */
  const withLoading = useCallback(async (apiCall) => {
    setLoading(true);
    setError(null);
    setMessage('');
    
    try {
      const result = await apiCall();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * 역대 당첨 번호 조회
   */
  const fetchHistory = useCallback(() => 
    withLoading(api.fetchHistory), [withLoading]);

  /**
   * 빈도 분석 조회
   */
  const fetchAnalysis = useCallback(() => 
    withLoading(api.fetchAnalysis), [withLoading]);

  /**
   * 추천 번호 조회
   */
  const fetchRecommendation = useCallback((strategy) => 
    withLoading(() => api.fetchRecommendation(strategy)), [withLoading]);

  /**
   * 사용자 선택 저장
   */
  const saveSelection = useCallback(async (numbers, strategy) => {
    const result = await withLoading(() => api.saveSelection(numbers, strategy));
    if (result.success) {
      setMessage(`${result.message} (총 ${result.user_count}회 참여)`);
    }
    return result;
  }, [withLoading]);

  /**
   * 주간 통계 조회
   */
  const fetchWeeklyStats = useCallback(() => 
    withLoading(api.fetchWeeklyStats), [withLoading]);

  /**
   * 주간 통계 히스토리 조회
   */
  const fetchWeeklyHistory = useCallback(() => 
    withLoading(api.fetchWeeklyHistory), [withLoading]);

  /**
   * 상태 초기화
   */
  const clearState = useCallback(() => {
    setError(null);
    setMessage('');
  }, []);

  return {
    loading,
    error,
    message,
    fetchHistory,
    fetchAnalysis,
    fetchRecommendation,
    saveSelection,
    fetchWeeklyStats,
    fetchWeeklyHistory,
    clearState,
  };
}
