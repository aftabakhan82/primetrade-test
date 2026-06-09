import os
from flask import Flask, render_template, request, jsonify, redirect, url_for,flash
from models import db, BotConfig, TradeLog
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY']=os.getenv("FLASK_SECRET_KEY", "your_flask_secret_key")

db.init_app(app)

# Binance Testnet Credentials (Use environment variables or test keys)
BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_KEY", "your_testnet_api_key")
BINANCE_SECRET_KEY = os.getenv("BINANCE_TESTNET_SECRET", "your_testnet_secret_key")

# Initialize Binance Client pointing to Futures Testnet
binance_client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY, testnet=True)

# Ensure database tables exist and seed baseline configuration
with app.app_context():
    db.create_all()
    if not BotConfig.query.first():
        default_config = BotConfig(symbol="BTCUSDT", leverage=10, order_size=0.005, is_active=False)
        db.session.add(default_config)
        db.session.commit()

@app.route('/')
def dashboard():
    config = BotConfig.query.first()
    trade_logs = TradeLog.query.order_by(TradeLog.timestamp.desc()).limit(10).all()
    
    # Fetch real-time metrics from Binance Testnet safely
    try:
        account_info = binance_client.futures_account()
        total_balance = float(account_info.get('totalWalletBalance', 0.0))
        unrealized_pnl = float(account_info.get('totalUnrealizedProfit', 0.0))
        
        # Pull current open positions
        positions = [
            pos for pos in account_info.get('positions', []) 
            if float(pos.get('positionAmt', 0)) != 0
        ]
    except Exception as e:
        print(f"Error connecting to Binance Testnet: {e}")
        total_balance, unrealized_pnl, positions = 0.0, 0.0, []

    return render_template(
        'index.html', 
        config=config, 
        trade_logs=trade_logs, 
        balance=round(total_balance, 2), 
        pnl=round(unrealized_pnl, 2),
        positions=positions
    )

@app.route('/update_config', methods=['POST'])
def update_config():
    config = BotConfig.query.first()
    config.symbol = request.form.get('symbol').upper()
    config.leverage = int(request.form.get('leverage'))
    config.order_size = float(request.form.get('order_size'))
    db.session.commit()
    
    try:
        binance_client.futures_change_leverage(symbol=config.symbol, leverage=config.leverage)
        flash(f"System Reconfigured: {config.symbol} Matrix initialized at {config.leverage}x leverage.", "success")
    except BinanceAPIException as e:
        print(f"Leverage Change Error: {e.message}")
        flash(f"Binance Core Fault: Failed to change leverage. {e.message}", "error")
        
    return redirect(url_for('dashboard'))

@app.route('/execute_trade', methods=['POST'])
def execute_trade():
    side = request.form.get('side').upper()  # BUY or SELL
    config = BotConfig.query.first()
    
    try:
        # Market Order Execution on Futures Testnet
        order = binance_client.futures_create_order(
            symbol=config.symbol,
            side=side,
            type='MARKET',
            quantity=config.order_size
        )
        
        execution_price = float(order.get('avgPrice', 0.0) or binance_client.futures_symbol_ticker(symbol=config.symbol)['price'])
        
        # Log to Database
        log = TradeLog(
            symbol=config.symbol,
            side=side,
            quantity=config.order_size,
            price=execution_price
        )
        db.session.add(log)
        db.session.commit()
        
        # Premium success flash feedback
        flash(f"Order Executed Successfully: Opened {side} position for {config.order_size} {config.symbol} at ${execution_price:,.2f}.", "success")
        
    except BinanceAPIException as e:
        print(f"Trade Execution Error: {e.message}")
        # Capture the raw error from Binance and flash it to the terminal screen
        flash(f"Execution Failed: {e.message}", "error")
        
    return redirect(url_for('dashboard'))


@app.route('/close_position', methods=['POST'])
def close_position():
    symbol = request.form.get('symbol').upper()
    
    try:
        positions = binance_client.futures_position_information()
        target_pos = None
        for pos in positions:
            if pos['symbol'] == symbol:
                target_pos = pos
                break
        
        if not target_pos:
            flash(f"Liquidation Error: No active contract configuration found for {symbol}.", "error")
            return redirect(url_for('dashboard'))
            
        position_amount = float(target_pos.get('positionAmt', 0.0))
        
        if position_amount == 0.0:
            flash(f"Position Alert: There are no open contracts to close for {symbol}.", "error")
            return redirect(url_for('dashboard'))
            
        close_side = 'SELL' if position_amount > 0 else 'BUY'
        close_quantity = abs(position_amount)
        
        # Send Market Exit Order to Binance Testnet
        order = binance_client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type='MARKET',
            quantity=close_quantity,
            reduceOnly=True
        )
        
        exit_price = float(order.get('avgPrice', 0.0) or binance_client.futures_symbol_ticker(symbol=symbol)['price'])
        
        # Log transaction history into SQLite local logs
        log = TradeLog(
            symbol=symbol,
            side=f"CLOSE_{close_side}",
            quantity=close_quantity,
            price=exit_price
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f"Position Closed: Liquidated {close_quantity} {symbol} contracts via Market Exit at ${exit_price:,.2f}.", "success")
        
    except BinanceAPIException as e:
        print(f"Liquidation Error: {e.message}")
        flash(f"Market Exit Failed: {e.message}", "error")
    except Exception as e:
        print(f"Internal Engine Error: {str(e)}")
        flash(f"System Matrix Error: Unable to complete position closure.", "error")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)