from fastapi import FastAPI, HTTPException, Form, APIRouter
from pydantic import BaseModel
import MetaTrader5 as mt5
from datetime import datetime

meta_router = APIRouter(prefix="/meta")


# Request model
class MT5Request(BaseModel):
    account_number: int
    password: str
    server: str

# Function to calculate daily drawdown
def calculate_daily_drawdown(current_equity):
    today = datetime.now().date()
    trades_today = mt5.history_deals_get(datetime(today.year, today.month, today.day), datetime.now())
    
    if not trades_today:
        return None  # No trades today, so no drawdown
    
    max_equity = current_equity
    for trade in trades_today:
        max_equity = max(max_equity, trade.profit + current_equity)
    
    drawdown = (max_equity - current_equity) / max_equity * 100
    return drawdown if drawdown > 0 else None

# Endpoint to fetch account details, total trades, and daily drawdown
@meta_router.post("/fetch_account_details")
async def fetch_account_details(
    account_number: int = Form(...),
    password: str = Form(...),
    server: str = Form(...)
):
    # Initialize MetaTrader5
    if not mt5.initialize():
        raise HTTPException(status_code=500, detail="MetaTrader5 initialization failed")
    
    # Login to MetaTrader5 account
    if not mt5.login(account_number, password=password, server=server):
        mt5.shutdown()
        raise HTTPException(status_code=401, detail="Login failed. Check your credentials and server.")
    
    # Fetch account information
    account_info = mt5.account_info()
    if account_info is None:
        mt5.shutdown()
        raise HTTPException(status_code=500, detail="Failed to retrieve account information.")
    
    # Gather account details
    account_details = {
        "balance": account_info.balance,
        "equity": account_info.equity,
        "margin": account_info.margin,
        "free_margin": account_info.margin_free,
        "currency": account_info.currency,
        "leverage": account_info.leverage,
        "name": account_info.name,
    }
    
    # Fetch total closed trades
    closed_trades = mt5.history_deals_get(datetime(2000, 1, 1), datetime.now())
    total_trades = len(closed_trades) if closed_trades else 0

    # Calculate total profit/loss
    total_pnl = 0
    
    # Fetch trade details
    trade_details = []
    if closed_trades:
        for trade in closed_trades:
            total_pnl += trade.profit
            # Convert timestamp to date string
            trade_date = datetime.fromtimestamp(trade.time).strftime('%Y-%m-%d')
            # Map trade type number to descriptive string
            trade_type = "Buy" if trade.type == 0 else "Sell" if trade.type == 1 else str(trade.type)
            trade_details.append({
                "ticket": trade.ticket,
                "time": trade.time,
                "date": trade_date,
                "type": trade.type,
                "trade_type": trade_type,
                "volume": trade.volume,
                "price": trade.price,
                "profit": trade.profit,
                "symbol": trade.symbol,
            })

    # Calculate daily drawdown
    drawdown = calculate_daily_drawdown(account_info.equity)

    # Shutdown MetaTrader5
    mt5.shutdown()

    # Return response
    return {
        "account_details": account_details,
        "total_closed_trades": total_trades,
        "trade_details": trade_details,
        "daily_drawdown": drawdown,
        "total_profit_loss": total_pnl
    }
