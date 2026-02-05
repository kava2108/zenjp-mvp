import { ScoreData } from './types';

const API_BASE_URL =
  typeof window !== 'undefined'
    ? `http://${window.location.hostname}:8000`
    : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchScore(stockCode: string): Promise<ScoreData> {
  const response = await fetch(`${API_BASE_URL}/api/score/${stockCode}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error(`銘柄コード ${stockCode} のスコアが見つかりません`);
    } else if (response.status === 400) {
      throw new Error(`無効な銘柄コードです: ${stockCode}`);
    } else {
      throw new Error(`APIエラー: ${response.status}`);
    }
  }

  const data: ScoreData = await response.json();
  return data;
}

export async function fetchMultipleScores(stockCodes: string[]): Promise<ScoreData[]> {
  const promises = stockCodes.map((code) => fetchScore(code));
  return Promise.all(promises);
}

export function formatScore(score: number | null): string {
  if (score === null || score === undefined) return 'N/A';
  return score.toFixed(1);
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('ja-JP', {
      timeZone: 'Asia/Tokyo',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    }).format(date);
  } catch {
    return dateString;
  }
}

export function getRankColor(rank: string): string {
  const colorMap: { [key: string]: string } = {
    'A': 'text-green-600',
    'B+': 'text-blue-600',
    'B': 'text-blue-500',
    'C+': 'text-yellow-600',
    'C': 'text-yellow-500',
    'D': 'text-red-600'
  };
  return colorMap[rank] || 'text-gray-600';
}

export function getRankBackgroundColor(rank: string): string {
  const colorMap: { [key: string]: string } = {
    'A': 'bg-green-100',
    'B+': 'bg-blue-100',
    'B': 'bg-blue-50',
    'C+': 'bg-yellow-100',
    'C': 'bg-yellow-50',
    'D': 'bg-red-100'
  };
  return colorMap[rank] || 'bg-gray-100';
}
