import aiohttp
import asyncio
import random
import json
import sys
import logging
from colorama import Fore, Style, init
from typing import Tuple, Optional, List

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.msg = f"{log_color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.basicConfig(level=logging.INFO, handlers=[handler])

class TonTonBot:
    API_URL = "https://api.intract.io/api/qv1/tma/tap"
    ENERGY_URL = "https://api.intract.io/api/qv1/auth/get-super-user"
    HEADERS_TEMPLATE = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "id,en-US;q=0.9,en;q=0.8,id-ID;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.intract.io",
        "referer": "https://www.intract.io/",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/127.06533103 Mobile Safari/537.36",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "sec-fetch-site": "same-site",
        "pragma": "no-cache",
    }

    def __init__(self, config_file: str, token: str, proxy: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.token = token
        self.proxy = proxy if self.config.get('use_proxy', False) else None
        self.tap_delay = random.uniform(0.1, 0.2)
        self.random_delay = random.uniform(3, 5)
        self.tap_amount = self.config.get('tap', 3)
        self.validate_config()
        self.url = self.API_URL
        self.headers = self.build_headers()

    def load_config(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load configuration: {e}")
            raise

    def validate_config(self):
        if not isinstance(self.tap_delay, (int, float)) or self.tap_delay <= 0:
            raise ValueError("Invalid tap_delay in configuration. It must be a positive number.")
        if not (1 <= self.tap_amount <= 10):
            raise ValueError("Invalid tap amount in configuration. It must be between 1 and 10.")

    def build_headers(self) -> dict:
        headers = self.HEADERS_TEMPLATE.copy()
        headers["authorization"] = f"Bearer {self.token}"
        return headers
    
    
    async def check_proxy(self):
        test_url = "http://httpbin.org/ip"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(test_url, proxy=self.proxy) as response:
                    if response.status == 200:
                        logging.warning(f"Proxy {self.proxy} is working.")
                    else:
                        logging.error(f"Proxy {self.proxy} failed with status code: {response.status}")
                        self.proxy = None
        except aiohttp.ClientError as e:
            logging.error(f"Proxy {self.proxy} failed with error: {e}")
            self.proxy = None
    

    async def get_energy(self, session: aiohttp.ClientSession) -> Tuple[Optional[int], Optional[int]]:
        try:
            async with session.get(self.ENERGY_URL, headers=self.headers, proxy=self.proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    current_energy = result.get('tapDetails', {}).get('energyLeft', None)
                    balance = result.get('totalTxps', None)
                    return current_energy, balance
                else:
                    logging.error(f"Failed to fetch energy, status code: {response.status}")
                    return None, None
        except aiohttp.ClientError as e:
            logging.error(f"Request failed during fetching energy: {e}")
            return None, None

    async def tap(self, session: aiohttp.ClientSession):
        payload = {"userTaps": self.tap_amount}
        try:
            async with session.post(self.url, json=payload, headers=self.headers, proxy=self.proxy) as response:
                if response.status != 200:
                    logging.error(f"Tap failed, status code: {response.status}")
                    
        except aiohttp.ClientError as e:
            logging.error(f"Request failed during tap: {e}")

    async def start_tapping(self, index: int):
        async with aiohttp.ClientSession() as session:  
            logging.debug(f"[Account {index}] Starting session.")
            if self.proxy:
                logging.warning(f"[Account {index}] Proxy: {self.proxy}")
                await self.check_proxy()
                
            await self.tap(session)  # Initial tap
            logging.warning(f"[Account {index}] Tapping {self.tap_amount} times every {self.tap_delay:.2f} seconds.")
            logging.warning(f"[Account {index}] starting in {self.random_delay:.2f} seconds.")
            await asyncio.sleep(self.random_delay)
            while True:
                current_energy, balance = await self.get_energy(session)
                if current_energy is not None and balance is not None:
                    logging.info(f"[Account {index}] Current energy: {current_energy}, Balance: {balance}")
                    if current_energy < self.tap_amount:
                        logging.warning(f"[Account {index}] Energy too low. Sleeping for 15 minutes.")
                        await asyncio.sleep(300)  # Sleep for 15 minutes
                    else:
                        await self.tap(session)
                        await asyncio.sleep(self.tap_delay)
                else:
                    logging.error(f"[Account {index}] Failed to retrieve energy or balance.")

def print_banner():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("#############################################")
    print("#                                           #")
    print("#          TonTon Bot by YAN                #")
    print("#                                           #")
    print("#############################################")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}")
    print("#  Press Ctrl+C to stop the bot safely...   #")
    print("#############################################\n")
    
    
async def main():
    print_banner()
    config_file = 'config.json'
    tokens_file = 'token.txt'
    proxy_file = 'proxy.txt'

    try:
        with open(tokens_file, 'r') as tf:
            tokens = [line.strip() for line in tf if line.strip()]
    except FileNotFoundError:
        logging.error(f"Tokens file '{tokens_file}' not found.")
        return
    except Exception as e:
        logging.error(f"Error reading tokens file: {e}")
        return

    try:
        with open(proxy_file, 'r') as pf:
            proxies = [line.strip() for line in pf if line.strip()]
    except FileNotFoundError:
        logging.error(f"Proxy file '{proxy_file}' not found.")
        return
    except Exception as e:
        logging.error(f"Error reading proxy file: {e}")
        return

    tasks = []
    for index, (token, proxy) in enumerate(zip(tokens, proxies), start=1):
        bot = TonTonBot(config_file, token, proxy)
        tasks.append(bot.start_tapping(index))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopping betting loop due to user interruption...")
        sys.exit(0)