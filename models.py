from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class BotConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), default="BTCUSDT")
    leverage = db.Column(db.Integer, default=10)
    order_size = db.Column(db.Float, default=0.01)
    is_active = db.Column(db.Boolean, default=False)

class TradeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    symbol = db.Column(db.String(20), nullable=False)
    side = db.Column(db.String(10), nullable=False) 
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="FILLED")