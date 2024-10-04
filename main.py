import aiohttp
import asyncio
import random
import json
import sys
import logging
from colorama import Fore, Style, init
from typing import Tuple, Optional, List

init(autoreset=True)

# Logging configuration
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
    TASK_ID_URL = "https://gcpapilb.intract.io/api/qv1/search/results"
    HEADERS_TEMPLATE = {
        "authority": "gcpapilb.intract.io",
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

    MAX_RETRIES = 3
    DEFAULT_TAP_DELAY_RANGE = (0.6, 0.8)
    DEFAULT_TAP_AMOUNT = (1, 10)
    SLEEP_DURATION_LOW_ENERGY = 300  # 5 minutes
    SLEEP_DURATION_RETRY = 60         # 1 minute

    def __init__(self, config_file: str, token: str, proxy: Optional[str] = None):
        self.config = self.load_config(config_file)
        self.token = token
        self.proxy = proxy if self.config.get('use_proxy', False) else None
        self.tap_delay = random.uniform(*self.DEFAULT_TAP_DELAY_RANGE)
        self.tap_amount = self.config.get('tap', 3)
        self.random_delay = random.uniform(0, 5)
        self.validate_config()
        self.headers = self.build_headers()
        self.loop = asyncio.get_event_loop()
        if self.proxy:
            asyncio.create_task(self.check_proxy())
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
                        logging.info(f"Proxy {self.proxy} is working.")
                    else:
                        logging.error(f"Proxy {self.proxy} failed with status code: {response.status}")
                        self.proxy = None
        except aiohttp.ClientError as e:
            logging.error(f"Proxy {self.proxy} failed with error: {e}")
            self.proxy = None

    async def fetch_energy_info(self, session: aiohttp.ClientSession) -> Tuple[Optional[int], Optional[int]]:
        for attempt in range(self.MAX_RETRIES):
            try:
                async with session.get(self.ENERGY_URL, headers=self.headers, proxy=self.proxy, timeout=10) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('tapDetails', {}).get('energyLeft'), result.get('totalTxps')
                    logging.error(f"Failed to fetch energy, status code: {response.status}")
                    return None, None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logging.error(f"Request failed during fetching energy: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    logging.warning(f"Retrying... ({attempt + 1}/{self.MAX_RETRIES})")
                    await asyncio.sleep(5)
                else:
                    return None, None
                
    async def fetch_tasks(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.TASK_ID_URL, headers=self.headers, proxy=self.proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    ids = self.extract_ids(result)
                    logging.info(f"Extracted IDs: {ids}")
                    return ids
                logging.error(f"Failed to fetch tasks, status code: {response.status}")
                return None
        except aiohttp.ClientError as e:
            logging.error(f"Request failed during fetching tasks: {e}")
            return None
            
    def extract_ids(self, data):
        return [
            item.get('id') for item in data.get('data', [])
            if not item.get('isStopped', True) and item.get('isMultiplierQuest', False)
        ]

    async def tap(self, session: aiohttp.ClientSession):
        payload = {"userTaps": self.tap_amount}
        try:
            async with session.post(self.API_URL, json=payload, headers=self.headers, proxy=self.proxy) as response:
                if response.status != 200:
                    logging.error(f"Tap failed, status code: {response.status}")
                    
        except aiohttp.ClientError as e:
            logging.error(f"Request failed during tap: {e}")

    async def start_tapping(self, index: int):
        async with aiohttp.ClientSession() as session:
            logging.warning(f"[Account {index}] Proxy: {self.proxy}")
            logging.warning(f"[Account {index}] Tapping {self.tap_amount} times every {self.tap_delay:.2f} seconds.")
            logging.warning(f"[Account {index}] Starting in {self.random_delay:.2f} seconds.")
            await asyncio.sleep(self.random_delay)
            
            await self.tap(session)
            current_energy, balance = await self.fetch_energy_info(session)  # Initial tap
            await asyncio.sleep(self.tap_delay)
            
            while True:
                current_energy, balance = await self.fetch_energy_info(session)
                if current_energy is not None and balance is not None:
                    logging.info(f"[Account {index}] Current energy: {current_energy}, Balance: {balance}")
                    if current_energy < self.tap_amount + 30:
                        random_pause_minutes = random.randint(5, 30)
                        random_pause_seconds = random.randint(0, 59)
                        random_long_pause = random_pause_minutes * 60 + random_pause_seconds

                        logging.warning(
                            f"[Account {index}] Energy too low. Taking a break for {random_pause_minutes} minutes and {random_pause_seconds} seconds.")
                        await asyncio.sleep(random_long_pause)
                    else:
                        await self.tap(session)
                        await asyncio.sleep(self.tap_delay)
                else:
                    logging.error(f"[Account {index}] Failed to retrieve energy or balance.")
                    logging.warning(f"[Account {index}] Sleeping for {self.SLEEP_DURATION_RETRY // 60} minutes before retrying.")
                    await asyncio.sleep(self.SLEEP_DURATION_RETRY)

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

    tokens = load_file_lines(tokens_file)
    if tokens is None:
        return

    proxies = load_file_lines(proxy_file)
    if proxies is None:
        return

    tasks = [
        TonTonBot(config_file, token, proxies[index - 1] if index <= len(proxies) else None).start_tapping(index)
        for index, token in enumerate(tokens, start=1)
    ]

    await asyncio.gather(*tasks)

def load_file_lines(file_path: str) -> Optional[List[str]]:
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
    except Exception as e:
        logging.error(f"Error reading file '{file_path}': {e}")
    return None

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Stopping bot due to user interruption...")
        sys.exit(0)