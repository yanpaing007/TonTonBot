# TonTon Bot

TonTon Bot is a script designed to tap nonstop for farming coins using multiple tokens and optional proxies. This bot supports multiple accounts and can run simultaneously.

Check out the bot here: [TonTon Bot](https://t.me/tonton_intract_bot?startapp=eyJyZWZlcnJhbENvZGUiOiJ2UHNCWGgiLCJyZWZlcnJhbFNvdXJjZSI6IlRFTEVHUkFNX01JTklfQVBQIiwicmVmZXJyYWxMaW5rIjoiaHR0cHM6Ly93d3cuaW50cmFjdC5pby90bWEvcmV3YXJkcz90YWI9cmVmZXJyYWxzIn0=&text=Check%20out%20this%20awesome%20mini%20app!)
- Top 10 users can get up to $100 daily!!

## Prerequisites

- Python 3.7 or higher
- `pip` (Python package installer)
- `git` [Git Download](https://git-scm.com/downloads) (if you want to easily update your code )(Without git every time your want to get latest version of code you have to manually download the zip file)
## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yanpaing007/TonTonBot.git
    cd TonTonBot
    cp token-example.txt token.txt 
    copy token-example.txt token.txt #For windows
    cp proxy-example.txt proxy.txt
    copy token-example.txt token.txt #For windows
    ```
- For token.txt enter your telegram bot query_id line by line for multi-account
- For proxy.txt if you want to use proxy,set it true in config.json,and put your proxy in proxy.txt line by line.Get free proxy here free [Webshare](https://proxy2.webshare.io/) or [Proxyscrape](https://dashboard.proxyscrape.com/)

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
    - **[token.txt](https://github.com/yanpaing007/TonTonBot/blob/main/token-example.txt)**: File containing query_id, one per line.
    - **[proxy.txt](https://github.com/yanpaing007/TonTonBot/blob/main/proxy-example.txt)**: (Optional) File containing proxies, one per line.
## Obtaining Tokens

To obtain the tokens required for [token.txt](https://github.com/yanpaing007/TonTonBot/blob/main/token.txt), follow these steps:

1. **Open your browser and open TonTon game bot.**
2. **Open Developer Tools:**
    - **Chrome:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
    - **Firefox:** Press `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac).
3. **Paste this command in console(if it said paste not allowed type "allow pasting" without ""**
```
copy(document.querySelector("iframe")?.src || "No iframe found.");
```
4.**After typing above command paste it in the token.txt done**


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

### [config.json](https://github.com/yanpaing007/TonTonBot/blob/main/config.json)

Example configuration:

```json
{
    "tap": 3, #Number of tap amount between 1 to 5 for safety purpose
    "use_proxy": true # If you want to use proxy set it true otherwise false
}
