from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import MACD
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import mplfinance as mpf
from matplotlib.gridspec import GridSpec
import requests
import os
import glob
from dotenv import load_dotenv
import os

# Load from .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise RuntimeError("Missing BOT_TOKEN or CHAT_ID in .env file")


def plot_stock_figure(ticker):
    df = yf.download(ticker, period="1mo", interval="1h", progress=False)
    df.dropna(inplace=True)

    # Format data for mplfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df["RSI"] = RSIIndicator(close=df["Close"].squeeze(), window=14).rsi()
    x = range(len(df))
    rsi = df["RSI"].values
    timestamps = df.index.strftime('%m-%d %H:%M')  # Format timestamps
    df["OBV"] = OnBalanceVolumeIndicator(close=df["Close"].squeeze(), volume=df["Volume"].squeeze()).on_balance_volume()

    macd = MACD(close=df["Close"].squeeze(), window_slow=26, window_fast=12, window_sign=9)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()


    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(4, 1, height_ratios=[3, 1, 1, 1], hspace=0.2)

    # --- 1. Candlestick chart using mplfinance ---
    ax1 = fig.add_subplot(gs[0])

    # Prepare the OHLCV DataFrame
    df_candle = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    mpf.plot(
        df_candle,
        type='candle',
        ax=ax1,
        volume=False,
        show_nontrading=False,
        datetime_format='%m-%d %H:%M',
        xrotation=0,
        style='charles',
    )

    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_ylabel("Price")
    ax1.set_title(f"{ticker} - Hourly Candlestick + Indicators")
    ax1.tick_params(labelbottom=False)

    # --- Shared x-axis range ---
    x = range(len(df))
    timestamps = df.index.strftime('%m-%d %H:%M')
    # 2. OBV
    # --- 2. OBV ---
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    ax2.plot(x, df["OBV"], label="OBV", color="blue")
    ax2.set_ylabel("OBV")
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.tick_params(labelbottom=False)

    # --- 3. MACD ---
    ax3 = fig.add_subplot(gs[2], sharex=ax1)
    ax3.plot(x, df["MACD"], label="MACD", color="purple", drawstyle='steps-mid')
    ax3.plot(x, df["MACD_signal"], label="Signal", color="orange", linestyle="--")
    ax3.axhline(0, linestyle="--", color="gray", linewidth=1)
    ax3.set_ylabel("MACD")
    ax3.legend(loc="upper left")
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.tick_params(labelbottom=False)
    # --- 4. RSI ---
    ax4 = fig.add_subplot(gs[3], sharex=ax1)
    ax4.plot(x, df["RSI"], label="RSI", color="green", drawstyle='steps-mid')
    ax4.axhline(30, linestyle='--', color='gray', linewidth=1)
    ax4.axhline(70, linestyle='--', color='gray', linewidth=1)
    ax4.set_ylabel("RSI")
    ax4.set_ylim(0, 100)
    ax4.legend(loc="upper left")
    ax4.grid(True, linestyle=':', alpha=0.6)

    # --- X-axis ticks and labels ---
    ax4.set_xticks(x[::3])
    ax4.set_xticklabels(timestamps[::3], rotation=45, fontsize=8)
    ax4.set_xlabel("Time")
    name = get_company_name(ticker)
    plt.suptitle(f"{name} - Hourly Technical Indicators (Midstep Style)", fontsize=14)
    filename = f'temp_plots/{ticker}_tech_plot.png'
    fig.savefig(filename, dpi=150)
    return filename

def get_latest_news(ticker, count=3):
    try:
        news = yf.Ticker(ticker).news
        return [f"📰 {item['content']['title']} — {item['content']['provider']['displayName']} ({item['content']['pubDate']})\n{item['content']['clickThroughUrl']['url']}" for item in news[:count]]
    except:
        return ["No news found."]
    
def get_company_name(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("shortName", ticker)
    except:
        return ticker  # fallback

def check_rsi_conditions(ticker):
    df = yf.download(ticker, period="5d", interval="1h", progress=False)
    df.dropna(inplace=True)

    # Format data for mplfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    if df.empty or len(df) < 14 + 2:
        return None

    rsi = RSIIndicator(close=df["Close"], window=14).rsi().dropna()
    if len(rsi) < 2:
        return None

    if rsi.iloc[-1] < 30 or (rsi.iloc[-2] - rsi.iloc[-1] > 25):
        return {
            "Ticker": ticker,
            "RSI_now": round(rsi.iloc[-1], 2),
            "RSI_prev": round(rsi.iloc[-2], 2)
        }
    return None


def send_telegram_message(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

def send_telegram_image(bot_token, chat_id, image_path, caption=""):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(image_path, 'rb') as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id, "caption": caption}
        requests.post(url, files=files, data=data)

def handle_triggered_ticker(ticker):

    result = check_rsi_conditions(ticker)
    if(result is None):
        return 0
    
    image_path = plot_stock_figure(ticker)
    # Get news
    headlines = get_latest_news(ticker)
    news_text = "\n\n".join(headlines)

    # Send to Telegram
    caption = f"⚠️ RSI Alert for {ticker}\n\n{news_text}"
    send_telegram_image(BOT_TOKEN, CHAT_ID,image_path, caption=caption)    
    return 1

# --- Helper to load tickers ---
def load_tickers(filepath):
    with open(filepath, "r") as f:
        return [line.strip().upper() for line in f if line.strip()]


async def rsi_command(update: Update, context: ContextTypes.DEFAULT_TYPE, list_name: str, file_path: str):
    await update.message.reply_text(f"Running RSI check for {list_name}...")
    tickers = load_tickers(file_path)

    n_tickers_found = 0
    for ticker in tickers:
        try:
            n_tickers_found += handle_triggered_ticker(ticker)
        except Exception as e:
            print(f"Error checking {ticker}: {e}")

    await update.message.reply_text(f"✅ Done! {n_tickers_found} tickers in {list_name} met the criteria.")

def cleanup_temp_plots(directory="temp_plots"):
    if not os.path.exists(directory):
        return
    files = glob.glob(os.path.join(directory, "*"))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Failed to remove {f}: {e}")


# --- Command-specific wrappers ---
async def rsi_nasdaq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rsi_command(update, context, "NASDAQ-100", "ticker_lists/nasdaq100_tickers.txt")
    cleanup_temp_plots()
async def rsi_sp500(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rsi_command(update, context, "S&P 500", "ticker_lists/sp500_tickers.txt")
    cleanup_temp_plots()
async def rsi_cac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rsi_command(update, context, "CAC 40", "ticker_lists/cac40_tickers.txt")
    cleanup_temp_plots()
async def rsi_dax(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rsi_command(update, context, "DAX", "ticker_lists/dax_tickers.txt")
    cleanup_temp_plots()
async def rsi_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Running RSI check for Nasdaq, Cac40, DAX markets...")
    tickers = (
        load_tickers("ticker_lists/nasdaq100_tickers.txt") +
        load_tickers("ticker_lists/cac40_tickers.txt") +
        load_tickers("ticker_lists/dax_tickers.txt")
    )

    n_tickers_found = 0
    for ticker in tickers:
        try:
            n_tickers_found += handle_triggered_ticker(ticker)
        except Exception as e:
            print(f"Error checking {ticker}: {e}")

    await update.message.reply_text(f"✅ Done! {n_tickers_found} tickers across all lists met the criteria.")
    cleanup_temp_plots()

# --- Register commands ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("rsi_nasdaq", rsi_nasdaq))
app.add_handler(CommandHandler("rsi_sp500", rsi_nasdaq))
app.add_handler(CommandHandler("rsi_cac", rsi_cac))
app.add_handler(CommandHandler("rsi_dax", rsi_dax))
app.add_handler(CommandHandler("rsi_all", rsi_all))
app.run_polling()