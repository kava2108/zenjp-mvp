'use client';

import { useState, useEffect } from 'react';
import { STOCKS } from '@/lib/types';
import type { ScoreData } from '@/lib/types';
import { fetchMultipleScores } from '@/lib/api';
import ScoreCard from '@/components/ScoreCard';
import CategoryBar from '@/components/CategoryBar';
import DetailTable from '@/components/DetailTable';

export default function Home() {
  const [scores, setScores] = useState<ScoreData[]>([]);
  const [selectedStock, setSelectedStock] = useState<ScoreData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadScores();
  }, []);

  async function loadScores() {
    setLoading(true);
    setError(null);
    try {
      const targetCodes = STOCKS.map((stock) => stock.code);
      const data = await fetchMultipleScores(targetCodes);
      setScores(data);
      setSelectedStock(data.length > 0 ? data[0] : null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">ZenJP MVP</h1>
          <p className="text-gray-600">日本株スコアリングシステム - Value/Growth/Momentumの3軸で評価</p>
        </div>

        {loading && (
          <div className="text-center py-12">
            <div className="inline-block">
              <div className="animate-spin">
                <svg
                  className="h-12 w-12 text-blue-600"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
              </div>
              <p className="text-gray-600 mt-4">読み込み中...</p>
            </div>
          </div>
        )}

        {error && !loading && (
          <div className="bg-red-50 border-l-4 border-red-600 rounded-lg p-6 mb-6">
            <div className="flex items-start">
              <svg
                className="h-6 w-6 text-red-600 mt-0.5 mr-4 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4v.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="flex-1">
                <h3 className="text-red-900 font-semibold mb-1">エラーが発生しました</h3>
                <p className="text-red-800 text-sm mb-3">{error}</p>
                <button
                  onClick={loadScores}
                  className="text-red-600 hover:text-red-800 font-medium text-sm underline"
                >
                  再度読み込み
                </button>
              </div>
            </div>
          </div>
        )}

        {!loading && scores.length > 0 && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {scores.map((score) => (
                <button
                  key={score.stock_code}
                  onClick={() => setSelectedStock(score)}
                  className={`text-left transition-all ${
                    selectedStock?.stock_code === score.stock_code
                      ? 'ring-2 ring-blue-500 rounded-2xl'
                      : 'hover:shadow-md'
                  }`}
                >
                  <ScoreCard data={score} />
                </button>
              ))}
            </div>

            {selectedStock && (
              <div className="space-y-6">
                <CategoryBar data={selectedStock} />
                <DetailTable data={selectedStock} />
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

