/**
 * 로또 공 컴포넌트
 * 번호에 따른 색상이 자동으로 적용됩니다.
 */

import { getBallColor, BALL_SIZES } from '../../constants';

/**
 * @param {Object} props
 * @param {number} props.number - 로또 번호 (1-45)
 * @param {boolean} [props.isBonus=false] - 보너스 번호 여부
 * @param {'sm' | 'md' | 'lg'} [props.size='md'] - 공 크기
 * @param {string} [props.className] - 추가 CSS 클래스
 */
export default function LottoBall({ 
  number, 
  isBonus = false, 
  size = 'md',
  className = ''
}) {
  const colorClass = getBallColor(number, isBonus);
  const sizeClass = BALL_SIZES[size] || BALL_SIZES.md;

  return (
    <span
      className={`flex items-center justify-center rounded-full font-semibold text-white ${colorClass} ${sizeClass} ${className}`}
    >
      {number}
    </span>
  );
}
