import aiohttp
import asyncio
import random
import json
import sys
import logging
from colorama import Fore, Style, init
from typing import Tuple, Optional, List
import urllib

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
    API_URL = "https://gcpapilb.intract.io/api/qv1/tma/tap"
    ENERGY_URL = "https://gcpapilb.intract.io/api/qv1/auth/get-super-user"
    TASK_ID_URL = "https://gcpapilb.intract.io/api/qv1/search/results"
    DAILY_LOGIN_URL = "https://gcpapilb.intract.io/api/qv1/auth/gm-streak"
    GET_BEARER_URL = "https://gcpapilb.intract.io/api/qv1/auth/telegram"
    HEADERS_TEMPLATE = {
        "authority": "gcpapilb.intract.io",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "id,en-US;q=0.9,en;q=0.8,id-ID;q=0.7",
        "content-type": "application/json",
        "origin": "https://www.intract.io",
        "referer": "https://www.intract.io/",
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K)",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "sec-fetch-site": "same-site",
        "pragma": "no-cache",
    }

    MAX_RETRIES = 3
    DEFAULT_TAP_DELAY_RANGE = (0.3, 0.5)
    SLEEP_DURATION_LOW_ENERGY = random.randint(200, 300)  
    SLEEP_DURATION_RETRY = 60  # 1 minute

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
        self.bearer = None
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

    async def get_bearer_token(self):
        try:
            decoded_data = urllib.parse.unquote(self.token)
            query_params = urllib.parse.parse_qs(decoded_data)
            user_data = json.loads(urllib.parse.unquote(query_params['user'][0]))
            auth_date = int(query_params['auth_date'][0])
            hash_value = query_params['hash'][0]

            data = {
                "isTaskLogin": False,
                "source": "TELEGRAM",
                "isTmaTonAppUser": True,
                "user": {
                    "auth_date": auth_date,
                    "first_name": user_data['first_name'],
                    "hash": hash_value,
                    "id": user_data['id'],
                    "username": user_data['username'],
                },
                "fingerprintId": None
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.GET_BEARER_URL, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return response.headers.get('Authorization')
                    else:
                        logging.error(f"Failed to fetch bearer token, status code: {response.status}")
        except Exception as e:
            logging.error(f"Error fetching bearer token: {e}")
        return None

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
                logging.error(f"Error fetching energy info: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(5)
        return None, None

    async def fetch_tasks(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.TASK_ID_URL, headers=self.headers, proxy=self.proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    ids = [item['id'] for item in result.get('data', []) if not item.get('isStopped', True) and item.get('isMultiplierQuest', False)]
                    logging.info(f"Extracted IDs: {ids}")
                    return ids
                logging.error(f"Failed to fetch tasks, status code: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching tasks: {e}")
        return None

    async def tap(self, session: aiohttp.ClientSession):
        payload = {"userTaps": self.tap_amount}
        try:
            async with session.post(self.API_URL, json=payload, headers=self.headers, proxy=self.proxy) as response:
                if response.status != 200:
                    logging.error(f"Tap failed, status code: {response.status}")
        except aiohttp.ClientError as e:
            logging.error(f"Error during tap: {e}")

    async def daily_login(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.DAILY_LOGIN_URL, headers=self.headers, proxy=self.proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"Daily login success: {result}")
                else:
                    logging.warning(f"Daily login may already be completed.")
        except aiohttp.ClientError as e:
            logging.error(f"Error during daily login: {e}")

    async def schedule_daily_login(self, session: aiohttp.ClientSession, index: int):
        while True:
            logging.info(f"[Account {index}] Performing daily login.")
            await self.daily_login(session)
            logging.info(f"[Account {index}] Waiting 24 hours for next daily login.")
            await asyncio.sleep(86400)  # 24 hours

    async def start_tapping(self, index: int):
        async with aiohttp.ClientSession() as session:
            self.bearer = await self.get_bearer_token()
            self.headers['Authorization'] = f"Bearer {self.bearer}"
            logging.info(f"[Account {index}] Proxy: {self.proxy}")
            await asyncio.sleep(self.random_delay)

            asyncio.create_task(self.schedule_daily_login(session, index))
            await self.tap(session)  # making sure to get latest energy
            while True:
                current_energy, balance = await self.fetch_energy_info(session)
                if current_energy is not None and balance is not None:
                    logging.info(f"[Account {index}] Current energy: {current_energy}, Balance: {balance}")
                    if current_energy < self.tap_amount + 30:
                        logging.warning(f"[Account {index}] Low energy, waiting {self.SLEEP_DURATION_LOW_ENERGY} seconds.")
                        await asyncio.sleep(self.SLEEP_DURATION_LOW_ENERGY)
                        await self.tap(session)  # making sure to get latest energy
                        continue
                    
                    await self.tap(session)
                    logging.info(f"[Account {index}] Sleeping for {self.tap_delay:.2f} seconds.")
                    await asyncio.sleep(self.tap_delay)
                else:
                    logging.warning(f"[Account {index}] Could not retrieve energy information, retrying in {self.SLEEP_DURATION_RETRY} seconds.")
    
                    await asyncio.sleep(self.SLEEP_DURATION_RETRY)
def load_file_lines(file_path: str) -> Optional[List[str]]:
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File '{file_path}' not found.")
    except Exception as e:
        logging.error(f"Error reading file '{file_path}': {e}")
    return None

async def main():
    config_file = 'config.json'
    tokens_file = 'token.txt'
    proxy_file = 'proxy.txt'

    tokens = load_file_lines(tokens_file)
    if tokens is None:
        return

    proxies = load_file_lines(proxy_file)
    if proxies is None:
        return

    # Ensure that tokens and proxies match
    tasks = [
        TonTonBot(config_file, token, proxies[index - 1] if index <= len(proxies) else None).start_tapping(index)
        for index, token in enumerate(tokens, start=1)
    ]

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
