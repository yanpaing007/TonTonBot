# TonTon Bot

TonTon Bot is a script designed to tap nonstop for farming coins using multiple tokens and optional proxies. It supports multiple accounts and can run simultaneously.

Check out the bot here: [TonTon Bot](https://t.me/tonton_intract_bot?startapp=eyJyZWZlcnJhbENvZGUiOiJ2UHNCWGgiLCJyZWZlcnJhbFNvdXJjZSI6IlRFTEVHUkFNX01JTklfQVBQIiwicmVmZXJyYWxMaW5rIjoiaHR0cHM6Ly93d3cuaW50cmFjdC5pby90bWEvcmV3YXJkcz90YWI9cmVmZXJyYWxzIn0=&text=Check%20out%20this%20awesome%20mini%20app!)
- Top 10 users can get up to $100 daily!!

## Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)
- `virtualenv` (optional but recommended)

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/tonton-bot.git
    cd tonton-bot
    ```

2. **Create a virtual environment:**

    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    - **Windows:**

        ```bat
        venv\Scripts\activate
        ```

    - **Mac/Linux:**

        ```sh
        source venv/bin/activate
        ```

4. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

5. **Prepare configuration files:**

    - **[config.json](https://github.com/yanpaing007/TonTonBot/blob/main/config.json)**: Configuration file for the bot.
    - **[token.txt](https://github.com/yanpaing007/TonTonBot/blob/main/token.txt)**: File containing tokens, one per line.
    - **[proxy.txt](https://github.com/yanpaing007/TonTonBot/blob/main/proxy.txt)**: (Optional) File containing proxies, one per line.
## Obtaining Tokens

To obtain the tokens required for [token.txt](https://github.com/yanpaing007/TonTonBot/blob/main/token.txt), follow these steps:

1. **Open your browser and navigate to the game.**
2. **Open Developer Tools:**
    - **Chrome:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
    - **Firefox:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
3. **Go to the Network tab.**
4. **Start the game and look for a network request named [`get-super-user`].**
5. **Click on the [`get-super-user`] request and go to the Headers tab.**
6. **Find the `Authorization` header and copy the Bearer token.**
7. **Paste the token into [token.txt](), one token per line.**

## Running the Script

### Windows

1. **Run the script using `run.bat`:**

    ```bat
    run.bat
    ```

### Mac/Linux

1. **Run the script using [run.sh]():**

    ```sh
    ./run.sh
    ```

## Configuration

### [config.json]()

Example configuration:

```json
{
    "tap": 3,
    "use_proxy": true
}
