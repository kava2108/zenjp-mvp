'use client';

import { STOCKS } from '@/lib/types';

interface StockSelectorProps {
  selectedCode: string;
  onSelect: (code: string) => void;
}

export default function StockSelector({ selectedCode, onSelect }: StockSelectorProps) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
      <h3 className="text-lg font-semibold mb-4 text-gray-800">銘柄選択</h3>

      <div className="flex flex-col sm:flex-row gap-3">
        {STOCKS.map((stock) => (
          <button
            key={stock.code}
            onClick={() => onSelect(stock.code)}
            className={`flex-1 py-4 px-6 rounded-xl font-semibold transition-all duration-200 ${
              selectedCode === stock.code
                ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <div className="text-sm mb-1 opacity-75">{stock.code}</div>
            <div className="text-base">{stock.name}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
