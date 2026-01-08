/**
 * 프론트엔드 상수 정의
 */

/**
 * 로또 공 색상 (번호 범위별)
 */
export const BALL_COLORS = {
  '1-10': 'bg-yellow-500',
  '11-20': 'bg-blue-500',
  '21-30': 'bg-red-500',
  '31-40': 'bg-gray-500',
  '41-45': 'bg-green-500',
  'bonus': 'bg-orange-500',
};

/**
 * 번호에 해당하는 공 색상을 반환합니다.
 * @param {number} num - 로또 번호 (1-45)
 * @param {boolean} isBonus - 보너스 번호 여부
 * @returns {string} Tailwind CSS 클래스
 */
export function getBallColor(num, isBonus = false) {
  if (isBonus) return BALL_COLORS.bonus;
  if (num >= 1 && num <= 10) return BALL_COLORS['1-10'];
  if (num >= 11 && num <= 20) return BALL_COLORS['11-20'];
  if (num >= 21 && num <= 30) return BALL_COLORS['21-30'];
  if (num >= 31 && num <= 40) return BALL_COLORS['31-40'];
  return BALL_COLORS['41-45'];
}

/**
 * 탭 정의
 */
export const TABS = [
  { id: 'recommend', label: '번호 추천' },
  { id: 'analyze', label: '빈도 분석' },
  { id: 'history', label: '추첨 기록' },
  { id: 'weekly', label: '주간 통계' },
];

/**
 * 공 크기
 */
export const BALL_SIZES = {
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
};
