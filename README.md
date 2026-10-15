
# Morsely 💙

A simple Telegram bot that converts text to Morse code and Morse code to text.

## Features

- Text to Morse code conversion
- Morse code to text conversion
- Automatic conversion direction detection
- English, Arabic, and French interface
- Settings for language and copied-text formatting
- Donation options, including cryptocurrency

## Requirements

- Python 3
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Installation

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd Morsely
   ```

2. Create and activate a virtual environment (optional but recommended).

   Windows:

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Linux/macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project folder:

   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ```

5. Make sure `languages.json` and `donation/donations.json` are in the correct locations.

6. Start the bot:

   ```bash
   python bot.py
   ```

## Usage

Open your bot on Telegram and send `/start`.

- Send normal text to convert it to Morse code.
- Send Morse code to convert it to text.
- Use the menu to access settings, help, information, and donation options.

## Project Structure

```text
Morsely/
├── bot.py
├── languages.json
├── requirements.txt
├── .env
├── .gitignore
└── donation/
    ├── donations.json
    └── images/
        ├── binance.png
        └── redotpay.jpg
```

## Security

- Never share your `.env` file or Telegram bot token.
- Check cryptocurrency addresses and networks before sending funds.
