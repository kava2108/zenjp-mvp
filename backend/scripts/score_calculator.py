"""
スコア計算ロジック
ZenJP MVP - PHASE3

このファイルには、スコア計算の全ロジックが含まれています。
- Valueスコア（PER, PBR, 配当）
- Growthスコア（売上成長率）
- Momentumスコア（RSI, 出来高）
- 総合スコア計算とランク判定
"""

from typing import Dict, Tuple, Optional
import pandas as pd
import numpy as np
from scripts.constants import (
    # Value
    PER_BASELINE, PER_PERFECT_THRESHOLD, PER_MAX_THRESHOLD,
    PBR_PERFECT_THRESHOLD, PBR_MAX_THRESHOLD,
    DIVIDEND_MULTIPLIER, DIVIDEND_MAX_SCORE,
    # Growth
    GROWTH_PERFECT_THRESHOLD, GROWTH_BASELINE, GROWTH_MIN_THRESHOLD,
    GROWTH_RATE_FIXED,
    # Momentum
    RSI_PERIOD, RSI_IDEAL_MIN, RSI_IDEAL_MAX, RSI_OVERSOLD, RSI_OVERBOUGHT,
    VOLUME_SHORT_PERIOD, VOLUME_LONG_PERIOD, VOLUME_INCREASE_MULTIPLIER, VOLUME_MAX_SCORE,
    # Weights
    WEIGHT_VALUE, WEIGHT_GROWTH, WEIGHT_MOMENTUM,
    SECTOR_WEIGHTS, DEFAULT_WEIGHTS,
    # Ranks
    RANK_THRESHOLDS
)


# ============================================================
# Valueスコア計算
# ============================================================

def calculate_per_score(per: float) -> float:
    """
    PERスコアを計算（0-100点）
    
    改善版：より広い評価範囲、業界標準に近い評価
    
    ロジック:
    - PER <= 10.0 → 100点（優秀）
    - PER == 15.0 → 70点（良好）
    - PER == 25.0 → 0点（割高）
    - PER > 25.0 → 0点（割高）
    - 上記の間は線形補間
    
    実績：
    - トヨタ（PER 8.19）→ 100点
    - ソニー（PER 9.07）→ 100点
    - ソフトバンク（PER 18.74）→ 約30点
    
    Args:
        per: PER（株価収益率）
    
    Returns:
        スコア（0-100）
    """
    if per <= 0:
        return 0.0
    
    if per <= PER_PERFECT_THRESHOLD:
        # PER <= 10.0 は100点
        return 100.0
    elif per <= PER_BASELINE:
        # 10.0 → 100点、15.0 → 70点の線形補間
        return 100.0 - ((per - PER_PERFECT_THRESHOLD) / 
                        (PER_BASELINE - PER_PERFECT_THRESHOLD) * 30.0)
    elif per <= PER_MAX_THRESHOLD:
        # 15.0 → 70点、25.0 → 0点の線形補間
        return 70.0 - ((per - PER_BASELINE) / 
                       (PER_MAX_THRESHOLD - PER_BASELINE) * 70.0)
    else:
        # PER > 25.0 は0点
        return 0.0


def calculate_pbr_score(pbr: float) -> float:
    """
    PBRスコアを計算（0-100点）
    
    ロジック:
    - PBR <= 1.0 → 100点
    - PBR >= 3.0 → 0点
    - 上記の間は線形補間
    
    Args:
        pbr: PBR（株価純資産倍率）
    
    Returns:
        スコア（0-100）
    """
    if pbr <= 0:
        return 0.0
    
    if pbr <= PBR_PERFECT_THRESHOLD:
        return 100.0
    elif pbr <= PBR_MAX_THRESHOLD:
        # 1.0 → 100点、3.0 → 0点の線形補間
        return 100.0 - ((pbr - PBR_PERFECT_THRESHOLD) / 
                        (PBR_MAX_THRESHOLD - PBR_PERFECT_THRESHOLD) * 100.0)
    else:
        return 0.0


def calculate_dividend_score(dividend_yield: float) -> float:
    """
    配当スコアを計算（0-100点）
    
    ロジック:
    - 配当利回り × 20 = スコア
    - 上限100点
    
    Args:
        dividend_yield: 配当利回り（%）
    
    Returns:
        スコア（0-100）
    """
    if dividend_yield < 0:
        return 0.0
    
    score = dividend_yield * DIVIDEND_MULTIPLIER
    return min(score, DIVIDEND_MAX_SCORE)


def calculate_value_score(per: float, pbr: float, dividend_yield: float) -> Tuple[float, Dict[str, float]]:
    """
    Valueスコアを計算（PER + PBR + 配当の平均）
    
    Args:
        per: PER（株価収益率）
        pbr: PBR（株価純資産倍率）
        dividend_yield: 配当利回り（%）
    
    Returns:
        (総合Valueスコア, 内訳辞書)
    """
    per_score = calculate_per_score(per)
    pbr_score = calculate_pbr_score(pbr)
    dividend_score = calculate_dividend_score(dividend_yield)
    
    # 3つの平均
    value_score = (per_score + pbr_score + dividend_score) / 3.0
    
    breakdown = {
        'per_score': per_score,
        'pbr_score': pbr_score,
        'dividend_score': dividend_score
    }
    
    return value_score, breakdown


# ============================================================
# Growthスコア計算
# ============================================================

def calculate_growth_score(growth_rate: Optional[float] = None) -> float:
    """
    Growthスコアを計算（0-100点）
    
    ロジック:
    - 成長率 >= 20% → 100点
    - 成長率 == 10% → 50点
    - 成長率 <= -5% → 0点
    - 上記の間は線形補間
    
    MVP版では固定値（10%）を使用
    
    Args:
        growth_rate: 売上成長率（%）。Noneの場合は固定値を使用
    
    Returns:
        スコア（0-100）
    """
    if growth_rate is None:
        growth_rate = GROWTH_RATE_FIXED
    
    if growth_rate >= GROWTH_PERFECT_THRESHOLD:
        return 100.0
    elif growth_rate >= GROWTH_BASELINE:
        # 10% → 50点、20% → 100点の線形補間
        return 50.0 + ((growth_rate - GROWTH_BASELINE) / 
                       (GROWTH_PERFECT_THRESHOLD - GROWTH_BASELINE) * 50.0)
    elif growth_rate >= GROWTH_MIN_THRESHOLD:
        # -5% → 0点、10% → 50点の線形補間
        return ((growth_rate - GROWTH_MIN_THRESHOLD) / 
                (GROWTH_BASELINE - GROWTH_MIN_THRESHOLD) * 50.0)
    else:
        return 0.0


# ============================================================
# Momentumスコア計算
# ============================================================

def calculate_rsi(prices: pd.Series, period: int = RSI_PERIOD) -> float:
    """
    RSI（相対力指数）を計算
    
    Args:
        prices: 価格データ（新しい順）
        period: 計算期間（デフォルト14日）
    
    Returns:
        RSI値（0-100）
    """
    if len(prices) < period + 1:
        return 50.0  # データ不足の場合は中立値
    
    # 価格差分を計算
    delta = prices.diff()
    
    # 上昇と下降を分離
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    # 平均を計算
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    # RSを計算
    rs = avg_gain / avg_loss
    
    # RSIを計算
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    # 最新のRSI値を返す
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0


def calculate_rsi_score(rsi: float) -> float:
    """
    RSIスコアを計算（0-100点）
    
    ロジック:
    - RSI 40-70 → 高評価（線形で100点に近づく）
    - RSI < 30 → 売られすぎ（低評価）
    - RSI > 70 → 買われすぎ（低評価）
    
    Args:
        rsi: RSI値（0-100）
    
    Returns:
        スコア（0-100）
    """
    if RSI_IDEAL_MIN <= rsi <= RSI_IDEAL_MAX:
        # 理想範囲内: 40-70
        # 中心（55）で100点、端で80点
        center = (RSI_IDEAL_MIN + RSI_IDEAL_MAX) / 2.0  # 55
        distance_from_center = abs(rsi - center)
        max_distance = (RSI_IDEAL_MAX - RSI_IDEAL_MIN) / 2.0  # 15
        return 100.0 - (distance_from_center / max_distance * 20.0)
    elif rsi < RSI_IDEAL_MIN:
        # 40未満: 売られすぎ
        if rsi <= RSI_OVERSOLD:
            return 30.0  # 30以下は低評価
        else:
            # 30-40の間は線形で評価
            return 30.0 + ((rsi - RSI_OVERSOLD) / (RSI_IDEAL_MIN - RSI_OVERSOLD) * 50.0)
    else:
        # 70超: 買われすぎ
        if rsi >= RSI_OVERBOUGHT:
            return 30.0  # 70以上は低評価
        else:
            # このケースは理論上ないが、念のため
            return 80.0


def calculate_volume_change_rate(volumes: pd.Series) -> float:
    """
    出来高変化率を計算
    
    Args:
        volumes: 出来高データ（新しい順）
    
    Returns:
        変化率（%）: (直近7日平均 / 過去30日平均 - 1) * 100
    """
    if len(volumes) < VOLUME_LONG_PERIOD:
        return 0.0  # データ不足
    
    # 直近7日平均
    recent_avg = volumes.iloc[:VOLUME_SHORT_PERIOD].mean()
    
    # 過去30日平均
    long_avg = volumes.iloc[:VOLUME_LONG_PERIOD].mean()
    
    if long_avg == 0:
        return 0.0
    
    change_rate = ((recent_avg / long_avg) - 1.0) * 100.0
    return change_rate


def calculate_volume_score(volume_change_rate: float) -> float:
    """
    出来高スコアを計算（0-100点）
    
    ロジック:
    - 出来高増加率 × 5 = スコア
    - 上限100点、下限20点（マイナスでも最低20点を保証）
    
    Args:
        volume_change_rate: 出来高変化率（%）
    
    Returns:
        スコア（20-100）
    """
    score = 50.0 + (volume_change_rate * VOLUME_INCREASE_MULTIPLIER)
    return max(20.0, min(score, VOLUME_MAX_SCORE))


def calculate_momentum_score(prices: pd.Series, volumes: pd.Series) -> Tuple[float, Dict[str, float]]:
    """
    Momentumスコアを計算（RSI + 出来高の平均）
    
    Args:
        prices: 価格データ（新しい順）
        volumes: 出来高データ（新しい順）
    
    Returns:
        (総合Momentumスコア, 内訳辞書)
    """
    # RSI計算
    rsi = calculate_rsi(prices)
    rsi_score = calculate_rsi_score(rsi)
    
    # 出来高変化率計算
    volume_change = calculate_volume_change_rate(volumes)
    volume_score = calculate_volume_score(volume_change)
    
    # 2つの平均
    momentum_score = (rsi_score + volume_score) / 2.0
    
    breakdown = {
        'rsi': rsi,
        'rsi_score': rsi_score,
        'volume_change_rate': volume_change,
        'volume_score': volume_score
    }
    
    return momentum_score, breakdown


# ============================================================
# 総合スコア計算
# ============================================================

def calculate_total_score(value_score: float, growth_score: float, momentum_score: float, sector_name: str = None) -> float:
    """
    総合スコアを計算（加重平均）
    
    業種別の重みを適用：
    - 輸送用機器: Value(40%) + Growth(30%) + Momentum(30%)
    - 電気機器: Value(30%) + Growth(45%) + Momentum(25%)
    - 情報・通信業: Value(25%) + Growth(50%) + Momentum(25%)
    
    Args:
        value_score: Valueスコア（0-100）
        growth_score: Growthスコア（0-100）
        momentum_score: Momentumスコア（0-100）
        sector_name: 業種名（オプション）
    
    Returns:
        総合スコア（0-100）
    """
    # 業種別の重みを取得
    if sector_name and sector_name in SECTOR_WEIGHTS:
        weights = SECTOR_WEIGHTS[sector_name]
    else:
        weights = DEFAULT_WEIGHTS
    
    total = (value_score * weights['value'] + 
             growth_score * weights['growth'] + 
             momentum_score * weights['momentum'])
    return total


def determine_rank(total_score: float) -> str:
    """
    総合スコアからランクを判定
    
    Args:
        total_score: 総合スコア（0-100）
    
    Returns:
        ランク（A, B+, B, C+, C, D）
    """
    for rank, threshold in RANK_THRESHOLDS.items():
        if total_score >= threshold:
            return rank
    return 'D'


# ============================================================
# メイン計算関数
# ============================================================

def calculate_stock_score(
    stock_code: str,
    current_price: float,
    eps: float,
    bps: float,
    dividend: float,
    prices_df: pd.DataFrame,
    growth_rate: Optional[float] = None,
    sector_name: str = None
) -> Dict:
    """
    銘柄のスコアを計算（すべてのスコアを算出）
    
    Args:
        stock_code: 銘柄コード
        current_price: 現在株価
        eps: 1株当たり利益
        bps: 1株当たり純資産
        dividend: 1株当たり配当
        prices_df: 株価・出来高データ（date降順）
        growth_rate: 売上成長率（%）。Noneの場合は固定値
        sector_name: 業種名（オプション。指定時は業種別の重みを適用）
    
    Returns:
        スコア辞書
    """
    # PER, PBR, 配当利回り計算
    per = current_price / eps if eps > 0 else 0
    pbr = current_price / bps if bps > 0 else 0
    dividend_yield = (dividend / current_price * 100.0) if current_price > 0 else 0
    
    # Valueスコア
    value_score, value_breakdown = calculate_value_score(per, pbr, dividend_yield)
    
    # Growthスコア
    growth_score = calculate_growth_score(growth_rate)
    
    # Momentumスコア
    prices = prices_df['close'].reset_index(drop=True)
    volumes = prices_df['volume'].reset_index(drop=True)
    momentum_score, momentum_breakdown = calculate_momentum_score(prices, volumes)
    
    # 総合スコア（業種別の重みを適用）
    total_score = calculate_total_score(value_score, growth_score, momentum_score, sector_name)
    rank = determine_rank(total_score)
    
    return {
        'stock_code': stock_code,
        'total_score': round(total_score, 2),
        'rank': rank,
        'value_score': round(value_score, 2),
        'growth_score': round(growth_score, 2),
        'momentum_score': round(momentum_score, 2),
        # 詳細
        'per': round(per, 2),
        'pbr': round(pbr, 2),
        'dividend_yield': round(dividend_yield, 2),
        'per_score': round(value_breakdown['per_score'], 2),
        'pbr_score': round(value_breakdown['pbr_score'], 2),
        'dividend_score': round(value_breakdown['dividend_score'], 2),
        'rsi': round(momentum_breakdown['rsi'], 2),
        'rsi_score': round(momentum_breakdown['rsi_score'], 2),
        'volume_change_rate': round(momentum_breakdown['volume_change_rate'], 2),
        'volume_score': round(momentum_breakdown['volume_score'], 2)
    }
