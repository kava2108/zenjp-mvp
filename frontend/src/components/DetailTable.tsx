'use client';

import { ScoreData } from '@/lib/types';

interface DetailTableProps {
  data: ScoreData;
}

export default function DetailTable({ data }: DetailTableProps) {
  const details = data.details;

  const rows = [
    {
      label: 'PER（株価収益率）',
      value: details.per ? `${details.per.toFixed(2)}倍` : 'N/A',
      score: details.per_score
    },
    {
      label: 'PBR（株価純資産倍率）',
      value: details.pbr ? `${details.pbr.toFixed(2)}倍` : 'N/A',
      score: details.pbr_score
    },
    {
      label: '配当利回り',
      value: details.dividend_yield ? `${details.dividend_yield.toFixed(2)}%` : 'N/A',
      score: details.dividend_score
    },
    {
      label: 'RSI（相対力指数）',
      value: details.rsi ? details.rsi.toFixed(1) : 'N/A',
      score: details.rsi_score
    },
    {
      label: '出来高変化率',
      value: details.volume_change_rate ? `${details.volume_change_rate.toFixed(1)}%` : 'N/A',
      score: details.volume_change_score
    }
  ].filter((row) => row.score !== null);

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h3 className="text-xl font-bold mb-6 text-gray-800">詳細指標</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">指標</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">値</th>
              <th className="text-right py-3 px-4 font-semibold text-gray-700">スコア</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-gray-700">{row.label}</td>
                <td className="py-3 px-4 text-right font-semibold text-gray-900">{row.value}</td>
                <td className="py-3 px-4 text-right font-bold text-blue-600">
                  {row.score ? row.score.toFixed(1) : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
