/**
 * 로또 번호 추천 시스템 - 메인 앱
 */

import { useState } from 'react';
import { TABS } from './constants';
import { useLottoApi } from './hooks/useLottoApi';

// 탭 컴포넌트
import RecommendTab from './components/tabs/RecommendTab';
import AnalysisTab from './components/tabs/AnalysisTab';
import HistoryTab from './components/tabs/HistoryTab';
import WeeklyStatsTab from './components/tabs/WeeklyStatsTab';
import UpdateTab from './components/tabs/UpdateTab';

export default function App() {
  // 상태
  const [activeTab, setActiveTab] = useState('recommend');
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [weeklyStats, setWeeklyStats] = useState(null);

  // API 훅
  const {
    loading,
    error,
    message,
    fetchHistory,
    fetchAnalysis,
    fetchRecommendation,
    saveSelection,
    fetchWeeklyStats,
    updateData,
    clearState,
  } = useLottoApi();

  // 핸들러
  const handleFetchHistory = async () => {
    clearState();
    try {
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) {
      // 에러는 훅에서 처리
    }
  };

  const handleFetchAnalysis = async () => {
    clearState();
    try {
      const data = await fetchAnalysis();
      setAnalysis(data);
      setRecommended([]);
    } catch (e) {
      // 에러는 훅에서 처리
    }
  };

  const handleRecommend = async (strategy) => {
    clearState();
    try {
      const data = await fetchRecommendation(strategy);
      const numbers = data.numbers || [];
      setRecommended(numbers);
      setAnalysis(null);
      
      // 자동으로 선택 저장
      if (numbers.length > 0) {
        await saveSelection(numbers, strategy);
      }
    } catch (e) {
      // 에러는 훅에서 처리
    }
  };

  const handleFetchWeeklyStats = async () => {
    clearState();
    try {
      const data = await fetchWeeklyStats();
      setWeeklyStats(data);
    } catch (e) {
      // 에러는 훅에서 처리
    }
  };

  const handleUpdate = async () => {
    clearState();
    try {
      await updateData();
      // 업데이트 후 기록 새로고침
      const data = await fetchHistory();
      setHistory(data);
    } catch (e) {
      // 에러는 훅에서 처리
    }
  };

  // 현재 탭 렌더링
  const renderTab = () => {
    switch (activeTab) {
      case 'recommend':
        return (
          <RecommendTab
            onRecommend={handleRecommend}
            recommended={recommended}
            loading={loading}
          />
        );
      case 'analyze':
        return (
          <AnalysisTab
            onAnalyze={handleFetchAnalysis}
            analysis={analysis}
            loading={loading}
          />
        );
      case 'history':
        return (
          <HistoryTab
            onFetch={handleFetchHistory}
            history={history}
            loading={loading}
          />
        );
      case 'weekly':
        return (
          <WeeklyStatsTab
            onFetch={handleFetchWeeklyStats}
            stats={weeklyStats}
            loading={loading}
          />
        );
      case 'update':
        return (
          <UpdateTab
            onUpdate={handleUpdate}
            loading={loading}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-black text-white">
        <div className="px-6 py-16 text-center">
          <div className="mx-auto max-w-4xl">
            <h1 className="mb-4 text-5xl font-bold tracking-tight">
              스마트 로또 추첨기
            </h1>
            <p className="text-xl text-gray-300">
              AI 기반 로또 번호 분석 및 추천 시스템
            </p>
          </div>
        </div>
      </header>

      <main className="px-4 py-8">
        <div className="mx-auto max-w-6xl">
          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="border-b border-gray-200">
              <div className="flex justify-center space-x-8">
                {TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => {
                      setActiveTab(tab.id);
                      clearState();
                    }}
                    className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors duration-200 ${
                      activeTab === tab.id
                        ? 'border-black text-black'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Status Messages */}
          <div className="mb-6 space-y-3">
            {loading && (
              <div className="flex items-center justify-center rounded-lg bg-gray-50 px-6 py-4 border">
                <div className="mr-3 h-5 w-5 animate-spin rounded-full border-2 border-gray-300 border-t-black"></div>
                <span className="text-gray-700">요청을 처리하고 있습니다...</span>
              </div>
            )}
            {error && (
              <div className="rounded-lg bg-red-50 px-6 py-4 border border-red-200">
                <div className="flex items-center">
                  <span className="mr-2 text-red-600">⚠</span>
                  <span className="text-red-700">{error}</span>
                </div>
              </div>
            )}
            {message && (
              <div className="rounded-lg bg-green-50 px-6 py-4 border border-green-200">
                <div className="flex items-center">
                  <span className="mr-2 text-green-600">✓</span>
                  <span className="text-green-700">{message}</span>
                </div>
              </div>
            )}
          </div>

          {/* Tab Content */}
          {renderTab()}
        </div>
      </main>
    </div>
  );
}
