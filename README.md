# TonTon Bot

TonTon Bot is a script designed to automate certain tasks using multiple tokens and optional proxies. This README provides instructions on how to set up and run the script on both Windows and Mac/Linux systems.

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

    - **[config.json]()**: Configuration file for the bot.
    - **[token.txt]()**: File containing tokens, one per line.
    - **[proxy.txt]()**: (Optional) File containing proxies, one per line.
## Obtaining Tokens

To obtain the tokens required for [token.txt](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Ftoken.txt%22%2C%22path%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Ftoken.txt%22%2C%22scheme%22%3A%22file%22%7D%7D), follow these steps:

1. **Open your browser and navigate to the game.**
2. **Open Developer Tools:**
    - **Chrome:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
    - **Firefox:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
3. **Go to the Network tab.**
4. **Start the game and look for a network request named [`get-super-user`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A21%2C%22character%22%3A32%7D%7D%5D%2C%22d8ec5ac9-1633-4cb8-a273-9bf8729fdfa8%22%5D "Go to definition").**
5. **Click on the [`get-super-user`](command:_github.copilot.openSymbolFromReferences?%5B%22%22%2C%5B%7B%22uri%22%3A%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Fmain.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22pos%22%3A%7B%22line%22%3A21%2C%22character%22%3A32%7D%7D%5D%2C%22d8ec5ac9-1633-4cb8-a273-9bf8729fdfa8%22%5D "Go to definition") request and go to the Headers tab.**
6. **Find the `Authorization` header and copy the Bearer token.**
7. **Paste the token into [token.txt](http://_vscodecontentref_/#%7B%22uri%22%3A%7B%22%24mid%22%3A1%2C%22fsPath%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Ftoken.txt%22%2C%22path%22%3A%22%2FUsers%2Fyan%2FTgBot%2FTonTon%2Ftoken.txt%22%2C%22scheme%22%3A%22file%22%7D%7D), one token per line.**

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
