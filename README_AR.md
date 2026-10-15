
# Morsely 💙

بوت تيليجرام بسيط لتحويل النص إلى شفرة مورس وتحويل شفرة مورس إلى نص.

## المميزات

- تحويل النص إلى شفرة مورس
- تحويل شفرة مورس إلى نص
- اكتشاف اتجاه التحويل تلقائيًا
- واجهة بالإنجليزية والعربية والفرنسية
- إعدادات اللغة وتنسيق النص لسهولة النسخ
- خيارات التبرع، بما فيها العملات الرقمية

## المتطلبات

- Python 3
- رمز بوت تيليجرام من [@BotFather](https://t.me/BotFather)

## التثبيت

1. استنسخ المستودع:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd Morsely
   ```

2. أنشئ بيئة افتراضية وفعّلها (اختياري، لكنه مستحسن).

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

3. ثبّت المكتبات المطلوبة:

   ```bash
   pip install -r requirements.txt
   ```

4. أنشئ ملف `.env` داخل مجلد المشروع:

   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ```

5. تأكد من وجود `languages.json` و`donation/donations.json` في المسارات الصحيحة.

6. شغّل البوت:

   ```bash
   python bot.py
   ```

## الاستخدام

افتح البوت في تيليجرام وأرسل `/start`.

- أرسل نصًا عاديًا لتحويله إلى شفرة مورس.
- أرسل شفرة مورس لتحويلها إلى نص.
- استخدم القائمة للوصول إلى الإعدادات والمساعدة ومعلومات البوت وخيارات التبرع.

## بنية المشروع

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

## الأمان

- لا تشارك ملف `.env` أو رمز البوت.
- تحقق من عناوين العملات الرقمية والشبكات قبل إرسال الأموال.