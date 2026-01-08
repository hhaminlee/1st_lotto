/**
 * 번호 추천 탭
 */

import LottoBall from '../common/LottoBall';

export default function RecommendTab({ 
  onRecommend, 
  recommended,
  loading 
}) {
  return (
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
          onClick={() => onRecommend('top20')}
          disabled={loading}
          className="p-6 border border-gray-300 rounded-lg hover:border-black hover:shadow-lg transition-all duration-200 disabled:opacity-50"
        >
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900 mb-2">
              자주 나온 번호
            </div>
            <div className="text-sm text-gray-600">
              출현 빈도가 높은 번호들
            </div>
          </div>
        </button>

        <button
          onClick={() => onRecommend('bottom20')}
          disabled={loading}
          className="p-6 border border-gray-300 rounded-lg hover:border-black hover:shadow-lg transition-all duration-200 disabled:opacity-50"
        >
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900 mb-2">
              적게 나온 번호
            </div>
            <div className="text-sm text-gray-600">
              출현 빈도가 낮은 번호들
            </div>
          </div>
        </button>
      </div>

      {recommended.length > 0 && (
        <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-8">
          <h3 className="mb-6 text-center text-xl font-semibold text-gray-900">
            추천 번호
          </h3>
          <div className="flex flex-wrap justify-center gap-4">
            {recommended.map((num, index) => (
              <LottoBall key={index} number={num} size="lg" />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
