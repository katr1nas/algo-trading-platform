if __name__ == "__main__":
    from app.services.backtest_service import BacktestEngine
    

    # Sample data
    sample_data = [
        {"timestamp": "2024-01-01 10:00", "open": 100, "high": 102, "low": 99, "close": 101, "volume": 1000},
        {"timestamp": "2024-01-01 11:00", "open": 101, "high": 103, "low": 100, "close": 98, "volume": 1100},
        {"timestamp": "2024-01-01 12:00", "open": 98, "high": 99, "low": 97, "close": 97, "volume": 1200},
        {"timestamp": "2024-01-01 13:00", "open": 97, "high": 98, "low": 96, "close": 105, "volume": 1300},
        {"timestamp": "2024-01-01 14:00", "open": 105, "high": 107, "low": 104, "close": 106, "volume": 1400},
    ]
    
    # Sample signals
    sample_signals = [
        {"index": 2, "type": "BUY", "price": 97},
        {"index": 4, "type": "SELL", "price": 106}
    ]
    
    # Run backtest
    engine = BacktestEngine(initial_capital=10000, commission=0.001)
    results = engine.run_backtest(sample_signals, sample_data)
    
    print("\n" + "="*60)
    print("BACKTEST RESULTS")
    print("="*60)
    print(f"Initial Capital: ${results['initial_capital']:,.2f}")
    print(f"Final Capital: ${results['final_capital']:,.2f}")
    print(f"Total P&L: ${results['total_pnl']:,.2f}")
    print(f"Return: {results['total_return_percent']:.2f}%")
    print(f"\nTotal Trades: {results['total_trades']}")
    print(f"Win Rate: {results['metrics']['win_rate']}%")
    print(f"Profit Factor: {results['metrics']['profit_factor']}")
    print(f"Max Drawdown: ${results['metrics']['max_drawdown']:,.2f} ({results['metrics']['max_drawdown_percent']}%)")
    print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']}")
    print("\n" + "="*60)