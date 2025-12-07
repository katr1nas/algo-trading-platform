import numpy as np
from typing import List, Dict, Optional
from datetime import datetime

class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 10000.0,
        commission: float = 0.001,  # 0.1% commission per trade
        position_size: float = 1.0   # Trade size as fraction of capital
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.position_size = position_size
    
    def run_backtest(
        self, 
        signals: List[Dict], 
        data: List[Dict]
    ) -> Dict:
        capital = self.initial_capital
        position = None  # Current position (None, or dict with entry details)
        trades = []
        equity_curve = [self.initial_capital]
        
        # Create a map of index to signal for quick lookup
        signal_map = {signal['index']: signal for signal in signals}
        
        for i, candle in enumerate(data):
            if i in signal_map:
                signal = signal_map[i]
                
                if signal['type'] == 'BUY' and position is None:
                    # Open long position
                    entry_price = candle['close']
                    shares = (capital * self.position_size) / entry_price
                    commission_paid = (shares * entry_price) * self.commission
                    
                    position = {
                        'type': 'LONG',
                        'entry_price': entry_price,
                        'entry_time': candle['timestamp'],
                        'entry_index': i,
                        'shares': shares,
                        'commission_paid': commission_paid
                    }
                
                elif signal['type'] == 'SELL' and position is not None:
                    # Close position
                    exit_price = candle['close']
                    exit_commission = (position['shares'] * exit_price) * self.commission
                    
                    # Calculate P&L
                    gross_pnl = (exit_price - position['entry_price']) * position['shares']
                    net_pnl = gross_pnl - position['commission_paid'] - exit_commission
                    
                    # Update capital
                    capital += net_pnl
                    
                    # Record trade
                    trade = {
                        'entry_time': position['entry_time'],
                        'exit_time': candle['timestamp'],
                        'entry_price': position['entry_price'],
                        'exit_price': exit_price,
                        'shares': position['shares'],
                        'pnl': net_pnl,
                        'pnl_percent': (net_pnl / (position['entry_price'] * position['shares'])) * 100,
                        'holding_bars': i - position['entry_index'],
                        'commission_total': position['commission_paid'] + exit_commission
                    }
                    trades.append(trade)
                    
                    # Clear position
                    position = None
            
            # Update equity curve
            if position is not None:
                # Mark-to-market
                current_value = capital + (candle['close'] - position['entry_price']) * position['shares']
                equity_curve.append(current_value)
            else:
                equity_curve.append(capital)
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades, equity_curve)
        
        return {
            'initial_capital': self.initial_capital,
            'final_capital': capital,
            'total_pnl': capital - self.initial_capital,
            'total_return_percent': ((capital - self.initial_capital) / self.initial_capital) * 100,
            'trades': trades,
            'total_trades': len(trades),
            'equity_curve': equity_curve,
            'metrics': metrics,
            'parameters': {
                'commission': self.commission,
                'position_size': self.position_size
            }
        }
    
    def _calculate_metrics(self, trades: List[Dict], equity_curve: List[float]) -> Dict:
        """Calculate performance metrics"""
        if not trades:
            return {
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'max_drawdown_percent': 0,
                'sharpe_ratio': 0,
                'total_wins': 0,
                'total_losses': 0
            }
        
        # Separate winning and losing trades
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        # Win rate
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        
        # Average win/loss
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Maximum drawdown
        peak = equity_curve[0]
        max_dd = 0
        max_dd_percent = 0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = peak - value
            dd_percent = (dd / peak) * 100 if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_percent = dd_percent
        
        # Sharpe ratio (simplified - assumes daily returns)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        return {
            'win_rate': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_dd, 2),
            'max_drawdown_percent': round(max_dd_percent, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'total_wins': len(winning_trades),
            'total_losses': len(losing_trades),
            'largest_win': round(max([t['pnl'] for t in winning_trades]), 2) if winning_trades else 0,
            'largest_loss': round(min([t['pnl'] for t in losing_trades]), 2) if losing_trades else 0,
            'avg_holding_bars': round(np.mean([t['holding_bars'] for t in trades]), 1) if trades else 0
        }