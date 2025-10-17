import React, { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updateMessage, setUpdateMessage] = useState('');
  const [activeTab, setActiveTab] = useState('recommend');
  const [weeklyStats, setWeeklyStats] = useState(null);
  const [selectedNumbers, setSelectedNumbers] = useState(null);

  const fetchHistory = () => {
    setLoading(true);
    setError(null);
    setUpdateMessage('');
    fetch(`${API_BASE_URL}/api/history`)
      .then(res => res.json())
      .then(data => {
        setHistory(data);
        setLoading(false);
      })
      .catch(err => {
        setError('이력 데이터를 불러오는데 실패했습니다');
        setLoading(false);
      });
  };

  const fetchAnalysis = () => {
    setLoading(true);
    setError(null);
    setUpdateMessage('');
    fetch(`${API_BASE_URL}/api/analyze`)
      .then(res => res.json())
      .then(data => {
        setAnalysis(data);
        setRecommended([]);
        setLoading(false);
      })
      .catch(err => {
        setError('분석 데이터를 불러오는데 실패했습니다');
        setLoading(false);
      });
  };

  const fetchRecommendation = (strategy) => {
    setLoading(true);
    setError(null);
    setUpdateMessage('');
    fetch(`${API_BASE_URL}/api/analyze?strategy=${strategy}`)
      .then(res => res.json())
      .then(data => {
        const numbers = data.numbers || [];
        setRecommended(numbers);
        setAnalysis(null);
        setLoading(false);
        
        // 자동으로 사용자 선택 저장
        if (numbers.length > 0) {
          saveUserSelection(numbers, strategy);
        }
      })
      .catch(err => {
        setError('추천 번호를 불러오는데 실패했습니다');
        setLoading(false);
      });
  };

  const updateData = () => {
    setLoading(true);
    setError(null);
    setUpdateMessage('');
    fetch(`${API_BASE_URL}/api/update`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        setUpdateMessage(data.message || data.error);
        setLoading(false);
        fetchHistory();
      })
      .catch(err => {
        setError('데이터 업데이트에 실패했습니다');
        setLoading(false);
      });
  };

  const saveUserSelection = (numbers, strategy) => {
    fetch(`${API_BASE_URL}/api/save-selection`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        numbers: numbers,
        strategy: strategy
      })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setSelectedNumbers({ numbers, strategy });
          setUpdateMessage(`${data.message} (총 ${data.user_count}회 참여)`);
        }
      })
      .catch(err => {
        setError('선택 저장에 실패했습니다');
      });
  };

  const fetchWeeklyStats = () => {
    setLoading(true);
    setError(null);
    setUpdateMessage('');
    fetch(`${API_BASE_URL}/api/weekly-stats`)
      .then(res => res.json())
      .then(data => {
        setWeeklyStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError('주간 통계를 불러오는데 실패했습니다');
        setLoading(false);
      });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-black text-white">
        <div className="px-6 py-16 text-center">
          <div className="mx-auto max-w-4xl">
            <h1 className="mb-4 text-5xl font-bold tracking-tight">
              🍀 스마트 로또 추첨기 🍀
            </h1>
            <p className="text-xl text-gray-300">
              AI 기반 로또 번호 분석 및 추첨 시스템
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
                {[
                  { id: 'recommend', label: '번호 추천' },
                  { id: 'analyze', label: '빈도 분석' },
                  { id: 'history', label: '추첨 기록' },
                  { id: 'weekly', label: '주간 통계' },
                  { id: 'update', label: '데이터 업데이트' }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
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
            {updateMessage && (
              <div className="rounded-lg bg-green-50 px-6 py-4 border border-green-200">
                <div className="flex items-center">
                  <span className="mr-2 text-green-600">✓</span>
                  <span className="text-green-700">{updateMessage}</span>
                </div>
              </div>
            )}
          </div>

          {/* Content Based on Active Tab */}
          {activeTab === 'recommend' && (
            <div className="bg-white rounded-lg border p-8">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-2xl font-bold text-gray-900">
                  번호 추천
                </h2>
                <p className="text-gray-600">
                  과거 데이터를 기반으로 한 AI 추천 번호를 받아보세요
                </p>
              </div>

              <div className="grid gap-6 sm:grid-cols-2">
                <button
                  onClick={() => fetchRecommendation('top20')}
                  className="p-6 border border-gray-300 rounded-lg hover:border-black hover:shadow-lg transition-all duration-200"
                >
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900 mb-2">자주 나온 번호</div>
                    <div className="text-sm text-gray-600">출현 빈도가 높은 번호들</div>
                  </div>
                </button>

                <button
                  onClick={() => fetchRecommendation('bottom20')}
                  className="p-6 border border-gray-300 rounded-lg hover:border-black hover:shadow-lg transition-all duration-200"
                >
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-900 mb-2">적게 나온 번호</div>
                    <div className="text-sm text-gray-600">출현 빈도가 낮은 번호들</div>
                  </div>
                </button>
              </div>

              {recommended.length > 0 && (
                <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-8">
                  <h3 className="mb-6 text-center text-xl font-semibold text-gray-900">
                    추천 번호
                  </h3>
                  <div className="flex flex-wrap justify-center gap-4">
                    {recommended.map((num, index) => {
                      let ballColor = '';
                      if (num >= 1 && num <= 10) ballColor = 'bg-yellow-500';
                      else if (num >= 11 && num <= 20) ballColor = 'bg-blue-500';
                      else if (num >= 21 && num <= 30) ballColor = 'bg-red-500';
                      else if (num >= 31 && num <= 40) ballColor = 'bg-gray-500';
                      else if (num >= 41 && num <= 45) ballColor = 'bg-green-500';
                      
                      return (
                        <div
                          key={index}
                          className={`flex h-12 w-12 items-center justify-center rounded-full ${ballColor} font-semibold text-white border-2 border-gray-300`}
                        >
                          {num}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analyze' && (
            <div className="bg-white rounded-lg border p-8">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-2xl font-bold text-gray-900">
                  빈도 분석
                </h2>
                <p className="text-gray-600">
                  번호별 출현 빈도를 분석해보세요
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchAnalysis}
                  className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  전체 번호 분석
                </button>
              </div>

              {analysis && (
                <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
                  <h3 className="mb-6 text-center text-xl font-semibold text-gray-900">
                    번호별 출현 빈도
                  </h3>
                  <div className="grid grid-cols-3 gap-3 sm:grid-cols-5 md:grid-cols-7 lg:grid-cols-9">
                    {Object.entries(analysis)
                      .sort((a, b) => b[1] - a[1])
                      .map(([num, freq], index) => {
                        const isHot = index < 15;
                        const isCold = index >= Object.keys(analysis).length - 15;
                        return (
                          <div
                            key={num}
                            className={`p-3 text-center rounded-lg border transition-transform duration-200 hover:scale-105 ${
                              isHot 
                                ? 'bg-black text-white border-black'
                                : isCold 
                                ? 'bg-gray-100 text-gray-700 border-gray-300'
                                : 'bg-white text-gray-900 border-gray-200'
                            }`}
                          >
                            <div className="text-lg font-bold">{num}</div>
                            <div className="text-xs">{freq}회</div>
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="bg-white rounded-lg border p-8">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-2xl font-bold text-gray-900">
                  추첨 기록
                </h2>
                <p className="text-gray-600">
                  최근 로또 추첨 결과를 확인해보세요
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchHistory}
                  className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  기록 불러오기
                </button>
              </div>

              {history.length > 0 && (
                <div className="mt-8 overflow-hidden rounded-lg border border-gray-200">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-4 text-left font-semibold text-gray-900">회차</th>
                          <th className="px-6 py-4 text-center font-semibold text-gray-900">당첨번호</th>
                          <th className="px-6 py-4 text-center font-semibold text-gray-900">보너스</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.slice().reverse().slice(0, 20).map((draw, index) => (
                          <tr
                            key={draw.draw_no}
                            className={`border-t border-gray-200 hover:bg-gray-50 ${
                              index % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                            }`}
                          >
                            <td className="px-6 py-4 font-medium text-gray-900">{draw.draw_no}</td>
                            <td className="px-6 py-4">
                              <div className="flex justify-center gap-2">
                                {[draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6].map((num, i) => {
                                  let ballColor = '';
                                  if (num >= 1 && num <= 10) ballColor = 'bg-yellow-500';
                                  else if (num >= 11 && num <= 20) ballColor = 'bg-blue-500';
                                  else if (num >= 21 && num <= 30) ballColor = 'bg-red-500';
                                  else if (num >= 31 && num <= 40) ballColor = 'bg-gray-500';
                                  else if (num >= 41 && num <= 45) ballColor = 'bg-green-500';
                                  
                                  return (
                                    <span
                                      key={i}
                                      className={`flex h-8 w-8 items-center justify-center rounded-full ${ballColor} text-sm font-semibold text-white`}
                                    >
                                      {num}
                                    </span>
                                  );
                                })}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="flex h-8 w-8 mx-auto items-center justify-center rounded-full bg-orange-500 text-sm font-semibold text-white">
                                {draw.bonus}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'weekly' && (
            <div className="bg-white rounded-lg border p-8">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-2xl font-bold text-gray-900">
                  주간 통계
                </h2>
                <p className="text-gray-600">
                  이번 주 사용자들의 번호 선택과 당첨 결과를 확인하세요
                </p>
              </div>

              <div className="text-center mb-6">
                <button
                  onClick={fetchWeeklyStats}
                  className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  주간 통계 조회
                </button>
              </div>

              {weeklyStats && (
                <div className="space-y-6">
                  {/* 기본 정보 */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">이번 주 현황</h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">{weeklyStats.total_selections}회</div>
                        <div className="text-sm text-gray-600">참여 횟수</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">{weeklyStats.current_week}</div>
                        <div className="text-sm text-gray-600">현재 주차</div>
                      </div>
                    </div>
                  </div>

                  {/* 당첨 결과 */}
                  {weeklyStats.has_results && weeklyStats.results ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">당첨 결과 (제{weeklyStats.results.draw_no}회)</h3>
                      
                      {/* 당첨 번호 */}
                      <div className="mb-6">
                        <div className="text-sm text-gray-600 mb-2">당첨 번호</div>
                        <div className="flex justify-center gap-3 mb-4">
                          {weeklyStats.results.winning_numbers.map((num, i) => {
                            let ballColor = '';
                            if (num >= 1 && num <= 10) ballColor = 'bg-yellow-500';
                            else if (num >= 11 && num <= 20) ballColor = 'bg-blue-500';
                            else if (num >= 21 && num <= 30) ballColor = 'bg-red-500';
                            else if (num >= 31 && num <= 40) ballColor = 'bg-gray-500';
                            else if (num >= 41 && num <= 45) ballColor = 'bg-green-500';
                            
                            return (
                              <span
                                key={i}
                                className={`flex h-10 w-10 items-center justify-center rounded-full ${ballColor} text-sm font-semibold text-white`}
                              >
                                {num}
                              </span>
                            );
                          })}
                          <span className="text-gray-400 mx-2">+</span>
                          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-500 text-sm font-semibold text-white">
                            {weeklyStats.results.bonus_number}
                          </span>
                        </div>
                      </div>

                      {/* 당첨 통계 */}
                      <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
                        {Object.entries(weeklyStats.results.summary).map(([rank, count]) => (
                          <div key={rank} className="text-center p-3 bg-white rounded-lg border">
                            <div className="text-lg font-bold text-gray-900">{count}</div>
                            <div className="text-sm text-gray-600">{rank}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                      <div className="text-yellow-700">
                        아직 이번 주 추첨 결과가 발표되지 않았습니다.
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {activeTab === 'update' && (
            <div className="bg-white rounded-lg border p-8">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-2xl font-bold text-gray-900">
                  데이터 업데이트
                </h2>
                <p className="text-gray-600">
                  최신 로또 결과와 동기화합니다
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={updateData}
                  className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200"
                >
                  지금 업데이트
                </button>
              </div>

              <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
                <h3 className="mb-4 text-lg font-semibold text-gray-900">업데이트 시 진행되는 작업</h3>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-center">
                    <span className="mr-3 text-green-600">✓</span>
                    공식 소스에서 최신 추첨 번호를 가져옵니다
                  </li>
                  <li className="flex items-center">
                    <span className="mr-3 text-green-600">✓</span>
                    새로운 데이터로 분석 데이터베이스를 업데이트합니다
                  </li>
                  <li className="flex items-center">
                    <span className="mr-3 text-green-600">✓</span>
                    최신 정보로 예측 정확도를 향상시킵니다
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;