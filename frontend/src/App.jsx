import React, { useState } from 'react';

const API_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [history, setHistory] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [recommended, setRecommended] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updateMessage, setUpdateMessage] = useState('');

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
    <div className="bg-gray-100 min-h-screen font-sans text-gray-800">
      <header className="bg-blue-600 text-white p-6 shadow-md">
        <h1 className="text-4xl font-bold text-center">🍀 Lotto Number Analyzer 🍀</h1>
      </header>

      <main className="p-8">
        <div className="max-w-5xl mx-auto bg-white rounded-lg shadow-lg p-6">
          
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6 border-b pb-6">
            <button onClick={updateData} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Update Data
            </button>
            <button onClick={fetchHistory} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Load Full History
            </button>
            <button onClick={fetchAnalysis} className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Analyze Frequencies
            </button>
            <button onClick={() => fetchRecommendation('top20')} className="bg-purple-500 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Recommend (Top 20)
            </button>
            <button onClick={() => fetchRecommendation('bottom20')} className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded-lg transition duration-300">
              Recommend (Bottom 20)
            </button>
          </div>

          {loading && <p className="text-center text-blue-500">Loading...</p>}
          {error && <p className="text-center text-red-500 font-semibold">{error}</p>}
          {updateMessage && <p className="text-center text-green-600 font-semibold">{updateMessage}</p>}

          {recommended.length > 0 && (
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <h2 className="text-2xl font-semibold mb-2 text-center">Recommended Numbers</h2>
              <p className="text-3xl font-bold text-center text-green-600 tracking-widest">
                {recommended.join(', ')}
              </p>
            </div>
          )}

          {analysis && (
            <div className="mt-6 p-4 bg-indigo-50 rounded-lg">
              <h2 className="text-2xl font-semibold mb-2">Number Frequencies</h2>
              <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-7 gap-4">
                {Object.entries(analysis).sort((a,b) => b[1] - a[1]).map(([num, freq]) => (
                  <div key={num} className="p-2 bg-white rounded shadow text-center">
                    <span className="font-bold text-xl text-indigo-600">{num}</span>
                    <span className="text-gray-600">: {freq}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {history.length > 0 && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h2 className="text-2xl font-semibold mb-2">Lottery History (Latest 20)</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white shadow-md rounded-lg">
                  <thead className="bg-gray-200">
                    <tr>
                      <th className="py-3 px-4">Draw No.</th>
                      <th className="py-3 px-4">Numbers</th>
                      <th className="py-3 px-4">Bonus</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice().reverse().slice(0, 20).map((draw) => (
                      <tr key={draw.draw_no} className="border-b hover:bg-gray-50">
                        <td className="py-2 px-4 text-center font-medium">{draw.draw_no}</td>
                        <td className="py-2 px-4 text-center tracking-wider">{`${draw.num1}, ${draw.num2}, ${draw.num3}, ${draw.num4}, ${draw.num5}, ${draw.num6}`}</td>
                        <td className="py-2 px-4 text-center text-red-500 font-semibold">{draw.bonus}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      </main>
    </div>
  );
}

export default App;