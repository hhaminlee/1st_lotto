/**
 * 데이터 업데이트 탭
 */

export default function UpdateTab({ onUpdate, loading }) {
  return (
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
          onClick={onUpdate}
          disabled={loading}
          className="px-8 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors duration-200 disabled:opacity-50"
        >
          지금 업데이트
        </button>
      </div>

      <div className="mt-8 bg-gray-50 border border-gray-200 rounded-lg p-6">
        <h3 className="mb-4 text-lg font-semibold text-gray-900">
          업데이트 시 진행되는 작업
        </h3>
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
  );
}
