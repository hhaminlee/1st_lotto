/**
 * 추첨 기록 탭
 */

import LottoBall from '../common/LottoBall';

export default function HistoryTab({ 
  onFetch, 
  history,
  loading 
}) {
  return (
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
          onClick={onFetch}
          disabled={loading}
          className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50"
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
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {draw.draw_no}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-center gap-2">
                        {[draw.num1, draw.num2, draw.num3, draw.num4, draw.num5, draw.num6].map((num, i) => (
                          <LottoBall key={i} number={num} size="sm" />
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex justify-center">
                        <LottoBall number={draw.bonus} size="sm" isBonus />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
