/**
 * 빈도 분석 탭
 */

export default function AnalysisTab({ 
  onAnalyze, 
  analysis,
  loading 
}) {
  return (
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
          onClick={onAnalyze}
          disabled={loading}
          className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50"
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
                const total = Object.keys(analysis).length;
                const isHot = index < 15;
                const isCold = index >= total - 15;
                
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
  );
}
