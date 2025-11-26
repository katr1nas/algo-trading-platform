from fastapi import APIRouter
import numpy as np

router = APIRouter()

@router.post("/backtest")
def backtest(ohlc: list[dict], signals: list[dict]):
    equity = 1000
    balance_curve = [equity]
    positions = []
    trades = []

    current_position = None

    for sig in signals:
        idx = sig["index"]
        price = ohlc[idx]["close"]

        if sig["type"] == "BUY":
            if current_position is None:
                current_position = {"entry": price, "index": idx}
            elif sig["type"] == "SELL":
                if current_position is not None:
                    profit = price = current_position["entry"]
                    trades.append({"entry": current_position["entry"],
                                  "exit": price,
                                  "profit": profit})
                    equity += profit
                    balance_curve.append(equity)
                    current_position = None
                
    profits = [t["profut"] for t in trades]
    winrate = sum(1 for p in profits if p > 0) / len(profits) * 100 if profits else 0
    total_profit = sum(profits) if profits else 0
    max_dd = float(np.min([0] + [b - max(balance_curve[:i+1]) for i, b in enumerate(balance_curve)]))

    return {
        "balance_curve": balance_curve,
        "trades": trades,
        "winrate": winrate,
        "total_profit": total_profit,
        "max_drawdown": max_dd
        }
