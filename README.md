## PrimeTrade


A premium Binance Futures Testnet trading dashboard built with Flask, SQLAlchemy, and Python-Binance. QuantumTrade provides a modern trading interface for testing futures strategies, managing positions, monitoring portfolio performance, and executing trades in a secure Binance Testnet environment.

## Features

* Binance Futures Testnet Integration
* Market Buy/Sell Order Execution
* Position Closing with `reduceOnly`
* Trade History Logging
* Leverage & Risk Management
* Real-Time Portfolio Tracking
* Open Position Monitoring
* SQLite Database Storage
* Modern Responsive UI with Tailwind CSS
* Flask-Based Backend Architecture

## Tech Stack

* Python
* Flask
* SQLAlchemy
* SQLite
* Python-Binance
* Tailwind CSS
* JavaScript

## Installation

Clone the repository:

```bash
git clone https://github.com/aftabakhan82/primetrade-test
cd primetrade-test
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Edit `.env` file in the project root:

```env
BINANCE_TESTNET_KEY=your_api_key
BINANCE_TESTNET_SECRET=your_secret_key
FLASK_SECRET_KEY=your_secret_key
```

## Run the Application

```bash
python app.py
```

Open your browser and visit:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
primetrade-test/
├── app.py
├── models.py
├── templates/
│   └── index.html
├── .env
└── requirements.txt
```

## Requirements

```text
Flask==3.0.2
Flask-SQLAlchemy==3.1.1
python-binance==1.0.19
python-dotenv==1.0.1
```

## Disclaimer

This project is intended for educational, research, and testing purposes only. It is designed to work with Binance Futures Testnet accounts and should not be used with real funds without implementing additional security, risk management, validation, and production-grade safeguards.


---

Developed with ❤️ using Flask, Binance API, and modern web technologies.
