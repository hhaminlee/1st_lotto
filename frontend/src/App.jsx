import React, { useState } from 'react';

const API_BASE_URL = '';

function App() {
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updateMessage, setUpdateMessage] = useState('');
  const [activeTab, setActiveTab] = useState('recommend');

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
        setRecommended(data.numbers || []);
        setAnalysis(null);
        setLoading(false);
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
        // Refresh history after update
        fetchHistory();
      })
      .catch(err => {
        setError('데이터 업데이트에 실패했습니다');
        setLoading(false);
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-900 via-red-900 to-purple-900">
      {/* Header */}
      <header className="relative overflow-hidden bg-gradient-to-r from-yellow-500 to-orange-500 shadow-2xl">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10 px-6 py-8 text-center">
          <div className="mx-auto max-w-4xl">
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-white/20 p-3 backdrop-blur-sm">
                <div className="text-4xl">🎰</div>
              </div>
            </div>
            <h1 className="mb-2 text-5xl font-bold tracking-tight text-white">
              스마트 로또 분석기
            </h1>
            <p className="text-xl text-amber-100">
              AI 기반 로또 번호 분석 및 예측 시스템
            </p>
          </div>
        </div>
        <div className="absolute -bottom-1 left-0 right-0 h-6 bg-gradient-to-br from-amber-900 via-red-900 to-purple-900"></div>
      </header>

      <main className="px-4 py-8">
        <div className="mx-auto max-w-6xl">
          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="flex flex-wrap justify-center gap-2 rounded-xl bg-white/10 p-2 backdrop-blur-sm">
              {[
                { id: 'recommend', label: '🎯 번호 추천', icon: '🔮' },
                { id: 'analyze', label: '📊 빈도 분석', icon: '📈' },
                { id: 'history', label: '📋 추첨 기록', icon: '🗂️' },
                { id: 'update', label: '🔄 데이터 업데이트', icon: '⚡' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-lg px-6 py-3 font-semibold transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-amber-900 shadow-lg'
                      : 'text-white hover:bg-gradient-to-r hover:from-yellow-500/20 hover:to-orange-500/20'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Status Messages */}
          <div className="mb-6 space-y-2">
            {loading && (
              <div className="flex items-center justify-center rounded-xl bg-yellow-500/20 px-6 py-4 text-yellow-100 backdrop-blur-sm">
                <div className="mr-3 h-5 w-5 animate-spin rounded-full border-2 border-yellow-300 border-t-transparent"></div>
                <span className="font-medium">요청을 처리하고 있습니다...</span>
              </div>
            )}
            {error && (
              <div className="rounded-xl bg-red-500/30 px-6 py-4 text-red-100 backdrop-blur-sm border border-red-400/30">
                <div className="flex items-center">
                  <span className="mr-2 text-xl">⚠️</span>
                  <span className="font-medium">{error}</span>
                </div>
              </div>
            )}
            {updateMessage && (
              <div className="rounded-xl bg-emerald-500/30 px-6 py-4 text-emerald-100 backdrop-blur-sm border border-emerald-400/30">
                <div className="flex items-center">
                  <span className="mr-2 text-xl">✅</span>
                  <span className="font-medium">{updateMessage}</span>
                </div>
              </div>
            )}
          </div>

          {/* Content Based on Active Tab */}
          {activeTab === 'recommend' && (
            <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-3xl font-bold text-white">
                  🎯 행운의 번호 생성기
                </h2>
                <p className="text-lg text-gray-300">
                  과거 데이터를 기반으로 한 AI 추천 번호를 받아보세요
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <button
                  onClick={() => fetchRecommendation('top20')}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-red-500 to-pink-600 p-6 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-red-400/30"
                >
                  <div className="relative z-10 text-center">
                    <div className="mb-2 text-3xl">🔥</div>
                    <div className="text-xl font-bold">핫 넘버</div>
                    <div className="text-sm opacity-90">가장 자주 나온 번호들</div>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-pink-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>

                <button
                  onClick={() => fetchRecommendation('bottom20')}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 p-6 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-blue-400/30"
                >
                  <div className="relative z-10 text-center">
                    <div className="mb-2 text-3xl">❄️</div>
                    <div className="text-xl font-bold">콜드 넘버</div>
                    <div className="text-sm opacity-90">가장 적게 나온 번호들</div>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {recommended.length > 0 && (
                <div className="mt-8 rounded-xl bg-gradient-to-r from-yellow-400/30 to-orange-500/30 p-8 backdrop-blur-sm border border-yellow-400/40">
                  <h3 className="mb-6 text-center text-2xl font-bold text-white">
                    🎉 당신의 행운 번호
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
                          className={`flex h-16 w-16 items-center justify-center rounded-full ${ballColor} font-bold text-2xl text-white shadow-lg transition-transform duration-300 hover:scale-110 border-2 border-white`}
                          style={{ animationDelay: `${index * 0.1}s` }}
                        >
                          {num}
                        </div>
                      );
                    })}
                  </div>
                  <div className="mt-4 text-center">
                    <span className="text-lg text-gray-300">
                      번호: {recommended.join(' - ')}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'analyze' && (
            <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-3xl font-bold text-white">
                  📊 빈도 분석
                </h2>
                <p className="text-lg text-gray-300">
                  번호 패턴과 출현 빈도를 분석해보세요
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchAnalysis}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 to-green-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-emerald-400/30"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">🔍</span>
                    <span className="text-xl font-bold">전체 번호 분석</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-green-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {analysis && (
                <div className="mt-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                  <h3 className="mb-6 text-center text-xl font-bold text-white">
                    번호별 출현 빈도 분포
                  </h3>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8">
                    {Object.entries(analysis)
                      .sort((a, b) => b[1] - a[1])
                      .map(([num, freq]) => (
                        <div
                          key={num}
                          className="rounded-lg bg-gradient-to-br from-yellow-400/20 to-orange-500/20 p-3 text-center backdrop-blur-sm transition-transform duration-300 hover:scale-105 border border-yellow-400/30"
                        >
                          <div className="text-2xl font-bold text-white">{num}</div>
                          <div className="text-xs text-gray-300">{freq}회</div>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'history' && (
            <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-3xl font-bold text-white">
                  📋 추첨 기록
                </h2>
                <p className="text-lg text-gray-300">
                  최근 로또 추첨 결과를 확인해보세요
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchHistory}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-500 to-violet-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-purple-400/30"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">📚</span>
                    <span className="text-xl font-bold">기록 불러오기</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-violet-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {history.length > 0 && (
                <div className="mt-8 overflow-hidden rounded-xl bg-white/10 backdrop-blur-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-white/20">
                        <tr>
                          <th className="px-6 py-4 text-left font-semibold text-white">회차</th>
                          <th className="px-6 py-4 text-center font-semibold text-white">당첨번호</th>
                          <th className="px-6 py-4 text-center font-semibold text-white">보너스</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.slice().reverse().slice(0, 20).map((draw, index) => (
                          <tr
                            key={draw.draw_no}
                            className={`border-t border-white/10 transition-colors hover:bg-white/10 ${
                              index % 2 === 0 ? 'bg-white/5' : ''
                            }`}
                          >
                            <td className="px-6 py-4 font-medium text-white">{draw.draw_no}</td>
                            <td className="px-6 py-4">
                              <div className="flex flex-wrap justify-center gap-2">
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
                                      className={`flex h-8 w-8 items-center justify-center rounded-full ${ballColor} text-sm font-bold text-white border border-white/30 shadow-md`}
                                    >
                                      {num}
                                    </span>
                                  );
                                })}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="flex h-8 w-8 mx-auto items-center justify-center rounded-full bg-orange-500 text-sm font-bold text-white border border-white/30 shadow-md">
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

          {activeTab === 'update' && (
            <div className="rounded-2xl bg-white/10 p-8 backdrop-blur-lg">
              <div className="mb-8 text-center">
                <h2 className="mb-4 text-3xl font-bold text-white">
                  🔄 데이터베이스 업데이트
                </h2>
                <p className="text-lg text-gray-300">
                  최신 로또 결과와 동기화합니다
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={updateData}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-amber-400/30"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">⚡</span>
                    <span className="text-xl font-bold">지금 업데이트</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-amber-600 to-yellow-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              <div className="mt-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                <h3 className="mb-4 text-lg font-semibold text-white">업데이트 시 진행되는 작업</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
                    공식 소스에서 최신 추첨 번호를 가져옵니다
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
                    새로운 데이터로 분석 데이터베이스를 업데이트합니다
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
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