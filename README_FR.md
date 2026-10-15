
# Morsely 💙

Un bot Telegram simple qui convertit le texte en code Morse et le code Morse en texte.

## Fonctionnalités

- Conversion du texte en code Morse
- Conversion du code Morse en texte
- Détection automatique du sens de conversion
- Interface en anglais, arabe et français
- Paramètres de langue et de format du texte à copier
- Options de don, y compris les cryptomonnaies

## Prérequis

- Python 3
- Un token de bot Telegram obtenu auprès de [@BotFather](https://t.me/BotFather)

## Installation

1. Clonez le dépôt :

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd Morsely
   ```

2. Créez et activez un environnement virtuel (facultatif, mais recommandé).

   Windows :

   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Linux/macOS :

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Installez les dépendances :

   ```bash
   pip install -r requirements.txt
   ```

4. Créez un fichier `.env` dans le dossier du projet :

   ```env
   BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
   ```

5. Vérifiez que `languages.json` et `donation/donations.json` se trouvent aux bons emplacements.

6. Lancez le bot :

   ```bash
   python bot.py
   ```

## Utilisation

Ouvrez votre bot sur Telegram et envoyez `/start`.

- Envoyez du texte normal pour le convertir en code Morse.
- Envoyez du code Morse pour le convertir en texte.
- Utilisez le menu pour accéder aux paramètres, à l'aide, aux informations et aux options de don.

## Structure du projet

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

## Sécurité

- Ne partagez jamais votre fichier `.env` ni votre token Telegram.
- Vérifiez les adresses et les réseaux des cryptomonnaies avant tout envoi.
