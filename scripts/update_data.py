#!/usr/bin/env python3
"""
Auto-refresh script for TEAM stock price data.
Run monthly via Bitbucket Pipelines — commits updated team_prices.json to repo.
"""

import json
import subprocess
import sys
from datetime import date

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    import yfinance as yf
except ImportError:
    install("yfinance")
    import yfinance as yf

print(f"Fetching TEAM stock prices... [{date.today()}]")

team = yf.Ticker('TEAM')
hist = team.history(start='2019-01-01', end=str(date.today()), interval='1d')

prices = {}
for year in range(2019, date.today().year + 1):
    yr = hist[hist.index.year == year]
    if yr.empty:
        continue

    peak_val = float(yr['High'].max())
    peak_date = yr['High'].idxmax().strftime('%Y-%m-%d')

    dec_data = yr[yr.index.month == 12]
    dec31_close = float(dec_data['Close'].iloc[-1]) if not dec_data.empty else None
    dec31_date  = dec_data.index[-1].strftime('%Y-%m-%d') if not dec_data.empty else None

    daily = {
        idx.strftime('%Y-%m-%d'): round(float(row['Close']), 2)
        for idx, row in yr.iterrows()
    }

    prices[year] = {
        'peak_price':  round(peak_val, 2),
        'peak_date':   peak_date,
        'dec31_close': round(dec31_close, 2) if dec31_close else None,
        'dec31_date':  dec31_date,
        'daily_close': daily,
    }
    print(f"  CY{year}: peak=${prices[year]['peak_price']} on {peak_date}, "
          f"dec31=${prices[year]['dec31_close']}")

output = {
    'ticker':       'TEAM',
    'company':      'Atlassian Corporation',
    'currency':     'USD',
    'generated_on': str(date.today()),
    'source':       'Yahoo Finance via yfinance (auto-updated monthly)',
    'annual':       prices,
}

out_path = 'data/team_prices.json'
with open(out_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Written {out_path}")
