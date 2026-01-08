/**
 * 주간 통계 탭
 */

import LottoBall from '../common/LottoBall';

export default function WeeklyStatsTab({ 
  onFetch, 
  stats,
  loading 
}) {
  return (
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
          onClick={onFetch}
          disabled={loading}
          className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50"
        >
          주간 통계 조회
        </button>
      </div>

      {stats && (
        <div className="space-y-6">
          {/* 기본 정보 */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">이번 주 현황</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.total_selections}회
                </div>
                <div className="text-sm text-gray-600">참여 횟수</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.current_week}
                </div>
                <div className="text-sm text-gray-600">현재 주차</div>
              </div>
            </div>
          </div>

          {/* 당첨 결과 */}
          {stats.has_results && stats.results ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                당첨 결과 (제{stats.results.draw_no}회)
              </h3>
              
              {/* 당첨 번호 */}
              <div className="mb-6">
                <div className="text-sm text-gray-600 mb-2">당첨 번호</div>
                <div className="flex justify-center gap-3 mb-4">
                  {stats.results.winning_numbers.map((num, i) => (
                    <LottoBall key={i} number={num} />
                  ))}
                  <span className="text-gray-400 mx-2 self-center">+</span>
                  <LottoBall number={stats.results.bonus_number} isBonus />
                </div>
              </div>

              {/* 당첨 통계 */}
              <div className="grid grid-cols-3 gap-4 sm:grid-cols-6">
                {Object.entries(stats.results.summary).map(([rank, count]) => (
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
  );
}
