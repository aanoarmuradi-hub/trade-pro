from .models import Trade
from decimal import Decimal


def calculate_profit_loss(trade):

    if not trade.entry_price or not trade.exit_price:
        return Decimal("0.00")

    symbol = str(trade.symbol).upper().strip()

    lot = Decimal(str(trade.lot_size or 1))

    pip_size_map = {
        "EURUSD": Decimal("0.0001"),
        "GBPUSD": Decimal("0.0001"),
        "USDJPY": Decimal("0.01"),
        "XAUUSD": Decimal("0.1")
    }

    pip_value_map = {
        "EURUSD": Decimal("10"),
        "GBPUSD": Decimal("10"),
        "USDJPY": Decimal("10"),
        "XAUUSD": Decimal("1")
    }

    pip_size = pip_size_map.get(symbol, Decimal("0.0001"))
    pip_value = pip_value_map.get(symbol, Decimal("10"))

    entry = Decimal(str(trade.entry_price))
    exit = Decimal(str(trade.exit_price))
    lot = Decimal(str(trade.lot_size or 1))

    symbol = str(trade.symbol).upper().strip()

    # GOLD FIX
    if symbol == "XAUUSD":
        price_diff = exit - entry if trade.trade_type == "BUY" else entry - exit
        profit = price_diff * Decimal("100") * lot
        return float(profit.quantize(Decimal("0.01")))

    # FX NORMAL MODE
    pip_size = pip_size_map.get(symbol, Decimal("0.0001"))
    pip_value = pip_value_map.get(symbol, Decimal("10"))

    price_diff = exit - entry if trade.trade_type == "BUY" else entry - exit
    pips = price_diff / pip_size
    profit = pips * pip_value * lot

    return float(profit.quantize(Decimal("0.01")))

def safe_profit(t):
    return float(t.profit_loss or 0)

def get_summary(user):

    trades = Trade.objects.filter(user=user)

    total_profit = sum(safe_profit(t) for t in trades)
    total_trades = trades.count()
    win_trades = sum(1 for t in trades if safe_profit(t) > 0)

    win_rate = (win_trades / total_trades * 100) if total_trades else 0

    return {
        "total_profit": round(total_profit, 2),
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
    }


def get_streaks(trades):

    win_streak = 0
    loss_streak = 0
    max_win_streak = 0
    max_loss_streak = 0

    for t in trades:
        if safe_profit(t) > 0:
            win_streak += 1
            loss_streak = 0
        else:
            loss_streak += 1
            win_streak = 0

        max_win_streak = max(max_win_streak, win_streak)
        max_loss_streak = max(max_loss_streak, loss_streak)

    return {
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
    }


def get_equity_curve(trades):

    trades = trades.order_by("created_at")

    equity = 0
    curve = []

    for t in trades:
        equity += safe_profit(t)

        curve.append({
            "date": t.created_at.strftime("%Y-%m-%d"),
            "equity": round(equity, 2)
        })

    return curve


def risk_check(trades):

    warnings = sum(1 for t in trades if t.risk_percent and t.risk_percent > 2)

    return {
        "high_risk_trades": warnings
    }


def get_trading_score(summary, streaks, risk):

    score = 50  # پایه

    # Profit
    if summary["total_profit"] > 0:
        score += 20
    else:
        score -= 10

    # Win rate
    if summary["win_rate"] >= 55:
        score += 15
    else:
        score -= 10

    # Streaks
    if streaks["max_win_streak"] >= 3:
        score += 10

    if streaks["max_loss_streak"] >= 3:
        score -= 10

    # Risk control
    if risk["high_risk_trades"] == 0:
        score += 10
    else:
        score -= 10

    # clamp
    score = max(0, min(100, score))

    return score