
import os
import json
import html
import sqlite3
import logging
from pathlib import Path

from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
LANGUAGES_FILE = BASE_DIR / "languages.json"
DB_PATH = BASE_DIR / "morsely.db"

DONATION_DIR = BASE_DIR / "donation"
DONATIONS_FILE = DONATION_DIR / "donations.json"
IMAGES_DIR = DONATION_DIR / "images"

EMAIL = "kacemlabs.store@gmail.com"
TELEGRAM_USERNAME = "kacem_la"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("Morsely")


# =========================================================
# LOAD DONATION CONFIGURATION
# =========================================================

def load_donations():
    with open(DONATIONS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data.get("crypto"), dict):
        raise ValueError(
            "donations.json must contain a 'crypto' object."
        )

    return data


DONATIONS = load_donations()


def get_crypto():
    return DONATIONS.get("crypto", {})


def get_crypto_currency(currency_key):
    return get_crypto().get(currency_key)


def get_currency_name(currency_key, currency_data):
    return currency_data.get("name", currency_key.upper())


# =========================================================
# LANGUAGES
# =========================================================

def load_languages():
    with open(LANGUAGES_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    for code in ("en", "ar", "fr"):
        if code not in data:
            raise ValueError(
                f"Missing language '{code}' in languages.json"
            )

    return data


LANGUAGES = load_languages()


def t(language, key, **kwargs):
    language = language if language in LANGUAGES else "en"

    message = LANGUAGES[language].get(
        key,
        LANGUAGES["en"].get(key, key),
    )

    return message.format(**kwargs)


# =========================================================
# DATABASE
# =========================================================

def init_db():
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                user_id INTEGER PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'en',
                copied_text INTEGER NOT NULL DEFAULT 1
            )
        """)
        connection.commit()


def get_preferences(user_id):
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO preferences (user_id)
            VALUES (?)
            """,
            (user_id,),
        )
        connection.commit()

        row = connection.execute(
            """
            SELECT language, copied_text
            FROM preferences
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    return row[0], bool(row[1])


def set_preference(user_id, column, value):
    if column not in ("language", "copied_text"):
        raise ValueError("Invalid preference")

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            f"UPDATE preferences SET {column} = ? WHERE user_id = ?",
            (value, user_id),
        )
        connection.commit()


# =========================================================
# KEYBOARD HELPERS
# =========================================================

def button(text, callback):
    return InlineKeyboardButton(
        text=text,
        callback_data=callback,
    )


def main_menu_keyboard(language):
    return InlineKeyboardMarkup([
        [
            button(t(language, "settings"), "settings"),
            button(t(language, "help"), "help"),
        ],
        [
            button(t(language, "about"), "about"),
            button(t(language, "donate"), "donate"),
        ],
        [
            button(t(language, "support"), "support"),
        ],
    ])


def back_home_keyboard(language, back_callback="home"):
    return InlineKeyboardMarkup([
        [
            button(t(language, "back"), back_callback),
            button(t(language, "home"), "home"),
        ]
    ])


def support_keyboard(language):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📧 Email",
                url=(
                    "https://mail.google.com/mail/"
                    "?view=cm&fs=1&to=kacemlabs.store%40gmail.com"
                ),
            )
        ],
        [
            InlineKeyboardButton(
                "💬 Telegram",
                url="https://t.me/kacem_la",
            )
        ],
        [
            button(t(language, "back"), "home"),
            button(t(language, "home"), "home"),
        ],
    ])


def settings_keyboard(language, copied_text):
    status = (
        t(language, "on")
        if copied_text
        else t(language, "off")
    )

    return InlineKeyboardMarkup([
        [
            button(t(language, "language"), "language"),
        ],
        [
            button(
                f"{t(language, 'copied')}: {status}",
                "toggle_copied",
            )
        ],
        [
            button(t(language, "home"), "home"),
        ],
    ])


def language_keyboard(current_language):
    options = [
        ("en", "🇬🇧 English"),
        ("ar", "🇩🇿 العربية"),
        ("fr", "🇫🇷 Français"),
    ]

    rows = []

    for code, label in options:
        if code == current_language:
            label += t(current_language, "selected")

        rows.append([
            button(label, f"setlang_{code}")
        ])

    rows.append([
        button(t(current_language, "back"), "settings"),
        button(t(current_language, "home"), "home"),
    ])

    return InlineKeyboardMarkup(rows)


def donation_keyboard(language):
    return InlineKeyboardMarkup([
        [button("💛 Binance Pay", "pay_binance")],
        [button("❤️ RedotPay", "pay_redotpay")],
        [button("☕ Ko-fi", "pay_kofi")],
        [button(t(language, "paypal_button"), "pay_paypal")],
        [button("₿ Crypto", "crypto")],
        [
            button(t(language, "back"), "home"),
            button(t(language, "home"), "home"),
        ],
    ])


# =========================================================
# DYNAMIC CRYPTO KEYBOARDS
# =========================================================

def crypto_currency_keyboard(language):
    rows = []

    for currency_key, currency_data in get_crypto().items():
        emoji = currency_data.get("emoji", "💰")
        name = currency_data.get("name", currency_key.upper())

        rows.append([
            button(
                f"{emoji} {name}",
                f"coin_{currency_key}",
            )
        ])

    rows.append([
        button(t(language, "back"), "donate"),
        button(t(language, "home"), "home"),
    ])

    return InlineKeyboardMarkup(rows)


def crypto_network_keyboard(language, currency_key):
    currency_data = get_crypto_currency(currency_key)

    if not currency_data:
        return back_home_keyboard(language, "crypto")

    networks = currency_data.get("networks", {})
    rows = []

    for network_name in networks:
        rows.append([
            button(
                network_name,
                f"net_{currency_key}_{network_name}",
            )
        ])

    rows.append([
        button(t(language, "back"), "crypto"),
        button(t(language, "home"), "home"),
    ])

    return InlineKeyboardMarkup(rows)


def crypto_address_keyboard(language, currency_key):
    return InlineKeyboardMarkup([
        [
            button(
                t(language, "back"),
                f"coin_{currency_key}",
            ),
        ],
        [
            button(t(language, "home"), "home"),
        ],
    ])


# =========================================================
# MESSAGE NAVIGATION
# =========================================================

async def replace_text(query, text, keyboard=None):
    message = query.message

    try:
        await message.edit_text(
            text=text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
        return

    except BadRequest as error:
        if "message is not modified" in str(error).lower():
            return

        logger.info(
            "Message edit unavailable; sending replacement: %s",
            error,
        )

    # Send the new message before deleting the old one.
    await message.chat.send_message(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )

    try:
        await message.delete()
    except Exception as error:
        logger.warning(
            "Could not delete previous message: %s",
            error,
        )


async def replace_photo(query, filename, caption, keyboard):
    message = query.message
    image_path = IMAGES_DIR / filename

    if image_path.exists():
        with open(image_path, "rb") as photo:
            await message.chat.send_photo(
                photo=photo,
                caption=caption,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
            )
    else:
        logger.warning("Donation image not found: %s", image_path)

        await message.chat.send_message(
            text=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

    try:
        await message.delete()
    except Exception as error:
        logger.warning(
            "Could not delete previous message: %s",
            error,
        )


# =========================================================
# COMMANDS
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    language, _ = get_preferences(user.id)
    name = html.escape(user.first_name or "there")

    await update.message.reply_text(
        t(language, "welcome", name=name),
        reply_markup=main_menu_keyboard(language),
        parse_mode=ParseMode.HTML,
    )


async def settings_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    language, copied_text = get_preferences(
        update.effective_user.id
    )

    await update.message.reply_text(
        t(language, "choose_language"),
        reply_markup=settings_keyboard(language, copied_text),
        parse_mode=ParseMode.HTML,
    )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    language, _ = get_preferences(update.effective_user.id)

    await update.message.reply_text(
        t(language, "help_text"),
        reply_markup=back_home_keyboard(language),
        parse_mode=ParseMode.HTML,
    )


async def about_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    language, _ = get_preferences(update.effective_user.id)

    await update.message.reply_text(
        t(language, "about_text"),
        reply_markup=back_home_keyboard(language),
        parse_mode=ParseMode.HTML,
    )


async def donate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    language, _ = get_preferences(update.effective_user.id)

    await update.message.reply_text(
        t(language, "donation_text"),
        reply_markup=donation_keyboard(language),
        parse_mode=ParseMode.HTML,
    )


async def support_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    language, _ = get_preferences(update.effective_user.id)

    await update.message.reply_text(
        t(language, "support_text"),
        reply_markup=support_keyboard(language),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# =========================================================
# MORSE CONVERSION
# =========================================================

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..",
    "E": ".", "F": "..-.", "G": "--.", "H": "....",
    "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.",
    "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
    "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---",
    "3": "...--", "4": "....-", "5": ".....",
    "6": "-....", "7": "--...", "8": "---..",
    "9": "----.",
    ".": ".-.-.-", ",": "--..--", "?": "..--..",
    "'": ".----.", "!": "-.-.--", "/": "-..-.",
    "(": "-.--.", ")": "-.--.-", "&": ".-...",
    ":": "---...", ";": "-.-.-.", "=": "-...-",
    "+": ".-.-.", "-": "-....-", "_": "..--.-",
    '"': ".-..-.", "$": "...-..-", "@": ".--.-.",
}

REVERSE_MORSE = {
    code: character
    for character, code in MORSE.items()
}


def looks_like_morse(text):
    stripped = text.strip()

    return (
        bool(stripped)
        and any(character in ".-" for character in stripped)
        and all(
            character in ".-/ \t\n"
            for character in stripped
        )
    )


def text_to_morse(text):
    converted_words = []

    for word in text.upper().split():
        letters = [
            MORSE[character]
            for character in word
            if character in MORSE
        ]

        if letters:
            converted_words.append(" ".join(letters))

    return " / ".join(converted_words)


def morse_to_text(text):
    decoded_words = []

    for word in text.strip().split("/"):
        letters = word.strip().split()

        decoded = "".join(
            REVERSE_MORSE.get(letter, "?")
            for letter in letters
        )

        if decoded:
            decoded_words.append(decoded)

    return " ".join(decoded_words)


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user
    language, copied_text = get_preferences(user.id)
    incoming = update.message.text.strip()

    if not incoming:
        await update.message.reply_text(t(language, "empty"))
        return

    if looks_like_morse(incoming):
        result = morse_to_text(incoming)
    else:
        result = text_to_morse(incoming)

    if not result:
        await update.message.reply_text(t(language, "empty"))
        return

    if copied_text:
        result = f"<pre>{html.escape(result)}</pre>"

    await update.message.reply_text(
        result,
        parse_mode=ParseMode.HTML if copied_text else None,
    )


# =========================================================
# CALLBACK HANDLER
# =========================================================

async def callback_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    language, copied_text = get_preferences(user_id)
    data = query.data

    try:
        if data == "home":
            name = html.escape(
                query.from_user.first_name or "there"
            )

            await replace_text(
                query,
                t(language, "welcome", name=name),
                main_menu_keyboard(language),
            )

        elif data == "settings":
            await replace_text(
                query,
                t(language, "choose_language"),
                settings_keyboard(language, copied_text),
            )

        elif data == "language":
            await replace_text(
                query,
                t(language, "choose_language"),
                language_keyboard(language),
            )

        elif data.startswith("setlang_"):
            new_language = data.split("_", 1)[1]

            if new_language in LANGUAGES:
                set_preference(
                    user_id,
                    "language",
                    new_language,
                )

            language, copied_text = get_preferences(user_id)

            await replace_text(
                query,
                t(language, "language_saved")
                + "\n\n"
                + t(language, "choose_language"),
                settings_keyboard(language, copied_text),
            )

        elif data == "toggle_copied":
            new_value = 0 if copied_text else 1

            set_preference(
                user_id,
                "copied_text",
                new_value,
            )

            language, copied_text = get_preferences(user_id)

            await replace_text(
                query,
                t(language, "choose_language"),
                settings_keyboard(language, copied_text),
            )

        elif data == "help":
            await replace_text(
                query,
                t(language, "help_text"),
                back_home_keyboard(language),
            )

        elif data == "about":
            await replace_text(
                query,
                t(language, "about_text"),
                back_home_keyboard(language),
            )

        elif data == "support":
            await replace_text(
                query,
                t(language, "support_text"),
                support_keyboard(language),
            )

        elif data == "donate":
            await replace_text(
                query,
                t(language, "donation_text"),
                donation_keyboard(language),
            )

        elif data == "pay_binance":
            await replace_photo(
                query,
                DONATIONS.get("binance_image", "binance.png"),
                t(
                    language,
                    "binance_text",
                    binance_id=DONATIONS["binance_id"],
                ),
                back_home_keyboard(language, "donate"),
            )

        elif data == "pay_redotpay":
            await replace_photo(
                query,
                DONATIONS.get("redotpay_image", "redotpay.jpg"),
                t(
                    language,
                    "redotpay_text",
                    redotpay_id=DONATIONS["redotpay_id"],
                ),
                back_home_keyboard(language, "donate"),
            )

        elif data == "pay_kofi":
            await replace_text(
                query,
                t(language, "kofi_text"),
                InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "☕ Open Ko-fi",
                            url=DONATIONS["kofi_url"],
                        )
                    ],
                    [
                        button(t(language, "back"), "donate"),
                        button(t(language, "home"), "home"),
                    ],
                ]),
            )

        elif data == "pay_paypal":
            await replace_text(
                query,
                t(language, "paypal_text"),
                back_home_keyboard(language, "donate"),
            )

        elif data == "crypto":
            await replace_text(
                query,
                t(language, "crypto_text"),
                crypto_currency_keyboard(language),
            )

        elif data.startswith("coin_"):
            currency_key = data[len("coin_"):]
            currency_data = get_crypto_currency(currency_key)

            if not currency_data or not currency_data.get("networks"):
                await replace_text(
                    query,
                    t(language, "crypto_unavailable"),
                    back_home_keyboard(language, "crypto"),
                )
                return

            currency_name = get_currency_name(
                currency_key,
                currency_data,
            )

            await replace_text(
                query,
                t(
                    language,
                    "choose_network",
                    currency=html.escape(currency_name),
                ),
                crypto_network_keyboard(language, currency_key),
            )

        elif data.startswith("net_"):
            # Currency keys must not contain underscores.
            # Network names may contain underscores.
            remainder = data[len("net_"):]
            currency_key, separator, network_name = remainder.partition("_")

            if not separator:
                await replace_text(
                    query,
                    t(language, "crypto_unavailable"),
                    back_home_keyboard(language, "crypto"),
                )
                return

            currency_data = get_crypto_currency(currency_key)
            networks = (
                currency_data.get("networks", {})
                if currency_data
                else {}
            )
            address = networks.get(network_name)

            if not address:
                await replace_text(
                    query,
                    t(language, "crypto_unavailable"),
                    back_home_keyboard(language, "crypto"),
                )
                return

            currency_name = get_currency_name(
                currency_key,
                currency_data,
            )

            # This uses the existing translated long message in
            # languages.json, filling its currency, network, and
            # address placeholders automatically.
            await replace_text(
                query,
                t(
                    language,
                    "crypto_address",
                    currency=html.escape(currency_name),
                    network=html.escape(network_name),
                    address=html.escape(address),
                ),
                crypto_address_keyboard(language, currency_key),
            )

    except Exception:
        logger.exception(
            "Failed handling callback %r from user %s",
            data,
            user_id,
        )


# =========================================================
# MAIN
# =========================================================

def main():
    load_dotenv(BASE_DIR / ".env")

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError(
            "BOT_TOKEN is missing. Add it to your .env file."
        )

    init_db()

    application = (
        Application.builder()
        .token(token)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("donate", donate_command))
    application.add_handler(CommandHandler("support", support_command))

    application.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text,
        )
    )

    print("Morsely is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
