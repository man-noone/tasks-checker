## Tasks checker Telegram bot

### Installation

#### Clone repo
    git clone https://github.com/man-noone/tasks-checker.git
    pip install -r requirements.txt

#### Create new environment variables (Linux):
 - TELEGRAM_TOKEN
 - DEVMAN_TOKEN

1. Open your .bashrc, e.g.
    ~~~
    vim ~/.bashrc
    ~~~
2. Add to the .bashrc these two lines:
    ~~~
    export TELEGRAM_TOKEN=your_telegram_api_token_here
    export DEVMAN_TOKEN=your_devman_api_token_here
    ~~~
3. Restart .bashrc with:
    ~~~
    source ~/.bashrc
    ~~~

### Start

To start the bot use:

    python main.py
