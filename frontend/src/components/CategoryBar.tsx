'use client';

import { ScoreData } from '@/lib/types';
import { motion } from 'framer-motion';

interface CategoryBarProps {
  data: ScoreData;
}

export default function CategoryBar({ data }: CategoryBarProps) {
  const categories = [
    {
      name: 'Value',
      score: data.value_score,
      diff: data.market_comparison.value_diff,
      color: 'bg-blue-500'
    },
    {
      name: 'Growth',
      score: data.growth_score,
      diff: data.market_comparison.growth_diff,
      color: 'bg-green-500'
    },
    {
      name: 'Momentum',
      score: data.momentum_score,
      diff: data.market_comparison.momentum_diff,
      color: 'bg-purple-500'
    }
  ];

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
      <h3 className="text-xl font-bold mb-6 text-gray-800">カテゴリ別スコア</h3>

      <div className="space-y-6">
        {categories.map((cat, index) => (
          <div key={cat.name}>
            <div className="flex flex-col sm:flex-row justify-between mb-2">
              <span className="font-semibold text-gray-700 mb-2 sm:mb-0">{cat.name}</span>
              <div className="flex items-center gap-3">
                <span className="text-xl font-bold text-gray-900">{cat.score.toFixed(1)}</span>
                <span
                  className={`text-sm font-semibold ${
                    cat.diff >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  ({cat.diff >= 0 ? '+' : ''}{cat.diff.toFixed(1)})
                </span>
              </div>
            </div>

            <div className="relative h-8 bg-gray-200 rounded-full overflow-hidden">
              <div className="absolute h-full w-0.5 bg-gray-400" style={{ left: '50%' }} />
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min(cat.score, 100)}%` }}
                transition={{
                  duration: 1,
                  ease: 'easeOut',
                  delay: index * 0.2
                }}
                className={`h-full ${cat.color}`}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
