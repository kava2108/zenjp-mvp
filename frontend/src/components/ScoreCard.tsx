'use client';

import { ScoreData } from '@/lib/types';
import { getRankColor, formatDate } from '@/lib/api';
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';

interface ScoreCardProps {
  data: ScoreData;
}

export default function ScoreCard({ data }: ScoreCardProps) {
  const scoreMotion = useMotionValue(0);
  const scoreDisplay = useTransform(scoreMotion, (latest) => latest.toFixed(1));

  useEffect(() => {
    const controls = animate(scoreMotion, data.total_score, {
      duration: 1.5,
      ease: 'easeOut'
    });
    return () => controls.stop();
  }, [data.total_score, scoreMotion]);

  return (
    <div data-testid="score-card" className="bg-white rounded-2xl shadow-lg p-8 mb-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        {data.stock_name} <span className="text-gray-500">({data.stock_code})</span>
      </h2>

      <div className="flex flex-col sm:flex-row items-start sm:items-end justify-between mb-6">
        <div className="mb-6 sm:mb-0">
          <div className="text-6xl font-bold text-gray-900 mb-2">
            <motion.span>{scoreDisplay}</motion.span>
            <span className="text-3xl text-gray-500 ml-2">点</span>
          </div>
          <div className={`text-2xl font-semibold ${getRankColor(data.rank)}`}>
            ランク: {data.rank}
          </div>
        </div>

        <div className="text-right w-full sm:w-auto">
          <div className="text-sm text-gray-600 mb-1">市場平均との差</div>
          <div
            className={`text-3xl font-bold ${
              data.market_comparison.total_diff >= 0 ? 'text-green-600' : 'text-red-600'
            }`}
          >
            {data.market_comparison.total_diff >= 0 ? '+' : ''}
            {data.market_comparison.total_diff.toFixed(1)}
          </div>
        </div>
      </div>

      <div className="text-sm text-gray-500 text-right border-t pt-4">
        更新: {formatDate(data.updated_at)}
      </div>
    </div>
  );
}
