> [!WARNING]
> This project is an MVP and contains the initial verson of the project code

# Speed Reading Telegram Bot

A Telegram bot designed to help users improve their speed reading skills. The bot contains texts of different levels of complexity, allows to process user voice messages and gives feedback. With the feedback bot calculates the speed of reading.

## Features

- Provides speed reading exercises with different difficulty of texts.
- Tracks user reading aloud and provides personalized feedback.
- Simple and intuitive interface with easy-to-use buttons.
- Provides statistics and progress tracking.
- Recommendations work through Chat GPT and Speech Recognition

## Getting Started

Follow the instructions below to set up and run the bot on your local machine.

### Prerequisites

Make sure you have the following installed:

- Python 3.7+
- [Telegram Bot API Token](https://core.telegram.org/bots#creating-a-new-bot) (You can get this by creating a new bot with [BotFather](https://t.me/BotFather))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/speed-reading-telegram-bot.git
   cd speed-reading-telegram-bot
   ```
2. **Install the required dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
3. **Set up environment variables:**
   Create a `.env` file in the root directory or change the value of the variables in the `config.py`.Add your Telegram Bot API token, OpenAI API token:
  ```env
  TELEGRAM_TOKEN=your_telegram_bot_token
  OPEN_AI_TOKEN=your_openai_token
  ```
4. **Run the bot:**
  ```python
  python main.py
  ```
## Usage
Once the bot is running, open Telegram and find your bot by its username. Start a conversation by typing `/start`. The bot will guide you through the available commands and exercises.

## Available Commands
/start - Start interacting with the bot and get a list of texts.
Further interaction takes place through the buttons.
