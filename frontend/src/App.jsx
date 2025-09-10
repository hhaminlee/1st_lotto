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
        setError('Failed to fetch history');
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
        setError('Failed to fetch analysis');
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
        setError('Failed to fetch recommendation');
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
        setError('Failed to update data');
        setLoading(false);
      });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="relative overflow-hidden bg-gradient-to-r from-emerald-600 to-cyan-600 shadow-2xl">
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10 px-6 py-8 text-center">
          <div className="mx-auto max-w-4xl">
            <div className="mb-4 flex justify-center">
              <div className="rounded-full bg-white/20 p-3 backdrop-blur-sm">
                <div className="text-4xl">🎰</div>
              </div>
            </div>
            <h1 className="mb-2 text-5xl font-bold tracking-tight text-white">
              Smart Lotto Analyzer
            </h1>
            <p className="text-xl text-emerald-100">
              AI-Powered Lottery Number Analysis & Prediction
            </p>
          </div>
        </div>
        <div className="absolute -bottom-1 left-0 right-0 h-6 bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900"></div>
      </header>

      <main className="px-4 py-8">
        <div className="mx-auto max-w-6xl">
          {/* Tab Navigation */}
          <div className="mb-8">
            <div className="flex flex-wrap justify-center gap-2 rounded-xl bg-white/10 p-2 backdrop-blur-sm">
              {[
                { id: 'recommend', label: '🎯 Number Recommendations', icon: '🔮' },
                { id: 'analyze', label: '📊 Frequency Analysis', icon: '📈' },
                { id: 'history', label: '📋 Draw History', icon: '🗂️' },
                { id: 'update', label: '🔄 Update Data', icon: '⚡' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-lg px-6 py-3 font-semibold transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-white text-indigo-900 shadow-lg'
                      : 'text-white hover:bg-white/20'
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
              <div className="flex items-center justify-center rounded-xl bg-blue-500/20 px-6 py-4 text-blue-100 backdrop-blur-sm">
                <div className="mr-3 h-5 w-5 animate-spin rounded-full border-2 border-blue-300 border-t-transparent"></div>
                <span className="font-medium">Processing your request...</span>
              </div>
            )}
            {error && (
              <div className="rounded-xl bg-red-500/20 px-6 py-4 text-red-100 backdrop-blur-sm">
                <div className="flex items-center">
                  <span className="mr-2 text-xl">⚠️</span>
                  <span className="font-medium">{error}</span>
                </div>
              </div>
            )}
            {updateMessage && (
              <div className="rounded-xl bg-green-500/20 px-6 py-4 text-green-100 backdrop-blur-sm">
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
                  🎯 Lucky Number Generator
                </h2>
                <p className="text-lg text-gray-300">
                  Get AI-powered recommendations based on historical data
                </p>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <button
                  onClick={() => fetchRecommendation('top20')}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 p-6 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                >
                  <div className="relative z-10 text-center">
                    <div className="mb-2 text-3xl">🔥</div>
                    <div className="text-xl font-bold">Hot Numbers</div>
                    <div className="text-sm opacity-90">Most frequent numbers</div>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-teal-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>

                <button
                  onClick={() => fetchRecommendation('bottom20')}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-purple-500 to-pink-600 p-6 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                >
                  <div className="relative z-10 text-center">
                    <div className="mb-2 text-3xl">❄️</div>
                    <div className="text-xl font-bold">Cold Numbers</div>
                    <div className="text-sm opacity-90">Least frequent numbers</div>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {recommended.length > 0 && (
                <div className="mt-8 rounded-xl bg-gradient-to-r from-yellow-400/20 to-orange-500/20 p-8 backdrop-blur-sm">
                  <h3 className="mb-6 text-center text-2xl font-bold text-white">
                    🎉 Your Lucky Numbers
                  </h3>
                  <div className="flex flex-wrap justify-center gap-4">
                    {recommended.map((num, index) => (
                      <div
                        key={index}
                        className="flex h-16 w-16 items-center justify-center rounded-full bg-white font-bold text-2xl text-indigo-900 shadow-lg transition-transform duration-300 hover:scale-110"
                        style={{ animationDelay: `${index * 0.1}s` }}
                      >
                        {num}
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 text-center">
                    <span className="text-lg text-gray-300">
                      Numbers: {recommended.join(' - ')}
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
                  📊 Frequency Analysis
                </h2>
                <p className="text-lg text-gray-300">
                  Analyze number patterns and frequencies
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchAnalysis}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">🔍</span>
                    <span className="text-xl font-bold">Analyze All Numbers</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {analysis && (
                <div className="mt-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                  <h3 className="mb-6 text-center text-xl font-bold text-white">
                    Number Frequency Distribution
                  </h3>
                  <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8">
                    {Object.entries(analysis)
                      .sort((a, b) => b[1] - a[1])
                      .map(([num, freq]) => (
                        <div
                          key={num}
                          className="rounded-lg bg-white/20 p-3 text-center backdrop-blur-sm transition-transform duration-300 hover:scale-105"
                        >
                          <div className="text-2xl font-bold text-white">{num}</div>
                          <div className="text-xs text-gray-300">{freq} times</div>
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
                  📋 Draw History
                </h2>
                <p className="text-lg text-gray-300">
                  Browse recent lottery results
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={fetchHistory}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-teal-500 to-cyan-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">📚</span>
                    <span className="text-xl font-bold">Load History</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-teal-600 to-cyan-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              {history.length > 0 && (
                <div className="mt-8 overflow-hidden rounded-xl bg-white/10 backdrop-blur-sm">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-white/20">
                        <tr>
                          <th className="px-6 py-4 text-left font-semibold text-white">Draw #</th>
                          <th className="px-6 py-4 text-center font-semibold text-white">Winning Numbers</th>
                          <th className="px-6 py-4 text-center font-semibold text-white">Bonus</th>
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
                                {[draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6].map((num, i) => (
                                  <span
                                    key={i}
                                    className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500 text-sm font-bold text-white"
                                  >
                                    {num}
                                  </span>
                                ))}
                              </div>
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className="flex h-8 w-8 mx-auto items-center justify-center rounded-full bg-red-500 text-sm font-bold text-white">
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
                  🔄 Update Database
                </h2>
                <p className="text-lg text-gray-300">
                  Sync with the latest lottery results
                </p>
              </div>

              <div className="text-center">
                <button
                  onClick={updateData}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-orange-500 to-red-600 px-8 py-4 text-white transition-all duration-300 hover:scale-105 hover:shadow-2xl"
                >
                  <div className="relative z-10 flex items-center">
                    <span className="mr-2 text-xl">⚡</span>
                    <span className="text-xl font-bold">Update Now</span>
                  </div>
                  <div className="absolute inset-0 bg-gradient-to-r from-orange-600 to-red-700 opacity-0 transition-opacity duration-300 group-hover:opacity-100"></div>
                </button>
              </div>

              <div className="mt-8 rounded-xl bg-white/10 p-6 backdrop-blur-sm">
                <h3 className="mb-4 text-lg font-semibold text-white">What happens when you update?</h3>
                <ul className="space-y-2 text-gray-300">
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
                    Fetches the latest draw numbers from official sources
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
                    Updates the analysis database with new data
                  </li>
                  <li className="flex items-center">
                    <span className="mr-2 text-green-400">✓</span>
                    Improves prediction accuracy with fresh information
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