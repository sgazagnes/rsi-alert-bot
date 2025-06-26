# RSI Alert Telegram Bot

A Python-based Telegram bot that monitors large-cap stocks for significant drops in their hourly Relative Strength Index (RSI). Designed to help identify potential buying opportunities by sending real-time alerts and technical charts through Telegram.

> ⚠️ **Important:** This tool does not run continuously or on a schedule — it responds to user commands that trigger checks on hourly data.

## 📈 What is RSI?

The **Relative Strength Index (RSI)** is a momentum oscillator that measures the speed and change of price movements. Values range from 0 to 100:

- **RSI > 70:** Stock might be **overbought**
- **RSI < 30:** Stock might be **oversold**

### Alert Conditions

This bot notifies you when:
- The current hourly RSI drops below 30, **OR**
- RSI falls by more than 25 points compared to the previous hour

These signals might indicate oversold conditions and — if confirmed by other indicators — could represent a buying opportunity.

## 🚀 Features

- **Multi-Market Support:** Monitors tickers from **NASDAQ-100**, **S&P 500**, **CAC 40**, and **DAX**
- **Technical Analysis:** Uses `yfinance` and `ta` libraries for comprehensive analysis
- **Telegram Alerts:** Sends notifications with:
  - 📊 4-panel technical chart (Candlestick, OBV, MACD, RSI)
  - 📰 Recent news headlines about the stock
- **Command-Based Interface:** Responds to specific Telegram commands for different markets

## 💬 Available Commands

- `/rsi_nasdaq` – Check RSI for NASDAQ-100 stocks
- `/rsi_sp500` – Check RSI for S&P 500 stocks
- `/rsi_cac` – Check RSI for CAC 40 stocks
- `/rsi_dax` – Check RSI for DAX stocks
- `/rsi_all` – Check RSI for all markets combined

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sgazagnes/rsi-alert-bot.git
cd rsi-alert-bot
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Save the bot token provided

### 4. Get Your Telegram Chat ID

1. Start a conversation with your bot
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Look for `"chat":{"id":...}` in the response — that's your chat ID

### 5. Set Up Environment Variables

Create the `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BOT_TOKEN=your_bot_token_here
CHAT_ID=your_chat_id_here
```


### 6. Run the Bot

```bash
python rsi_bot.py
```

The bot will start polling Telegram for messages and respond to your commands.


## 🗂️ Project Structure

```
rsi-alert-bot/
├── rsi_bot.py                   # Main bot logic and handlers
├── .env.example             # Template for environment variables
├── .env                     # Your actual environment variables (not in git)
├── ticker_lists/            # Market-specific ticker lists
│   ├── nasdaq100_tickers.txt
│   ├── sp500_tickers.txt
│   ├── cac40_tickers.txt
│   └── dax_tickers.txt
├── temp_plots/              # Temporary storage for generated charts
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore              # Git ignore rules
```

## 🔧 Dependencies

The bot relies on these Python packages:

- `python-telegram-bot` - Telegram API wrapper
- `yfinance` - Financial data from Yahoo Finance
- `ta` - Technical analysis indicators
- `matplotlib` - Chart generation
- `pandas` - Data manipulation
- `python-dotenv` - Environment variable management

## 📝 Usage Notes

- **Manual Operation:** The bot responds to commands rather than running automatically
- **Data Source:** RSI is computed using hourly candles 
- **Chart Storage:** Generated charts are temporarily stored in `temp_plots/` folder

## 🤖 Automation Options

To run the bot on a schedule, consider:

- **Cron Jobs** (Linux/macOS)
- **Task Scheduler** (Windows)
- **Cloud Functions** (AWS Lambda, Google Cloud Functions)
- **GitHub Actions** with scheduled workflows

## 🔍 Technical Details

- **RSI Period:** 14 periods (standard)
- **Timeframe:** 1-hour candles
- **Lookback:** Past 30 days of data
- **Alert Thresholds:**
  - RSI below 30 (oversold)
  - RSI drop of 25+ points from previous hour

## ⚠️ Important Disclaimers

- **Not Financial Advice:** This tool is for informational purposes only
- **No Guarantees:** RSI-based strategies are analytical tools, not investment guarantees
- **Risk Warning:** All trading and investing involves risk of loss
- **Due Diligence:** Always consider technical, fundamental, and personal factors before making investment decisions
- **Use at Your Own Risk:** The author is not responsible for any financial losses

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding:** Check your bot token and chat ID
2. **No data for ticker:** Verify ticker symbols in your lists
3. **Chart generation fails:** Ensure `temp_plots/` directory exists
4. **Rate limiting:** Yahoo Finance may limit requests; add delays if needed

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify all environment variables are set correctly
3. Ensure ticker files contain valid symbols
4. Test with a single command first (e.g., `/rsi_nasdaq`)

## 📄 License

This project is open source. 

## 🤝 Contributing

Contributions are welcome! 

---

*Happy trading! 📈*