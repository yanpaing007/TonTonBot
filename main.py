import aiohttp
import asyncio
import random
import json
import sys
import logging
from colorama import Fore, Style, init
from typing import Tuple, Optional, List

import urllib

import requests

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
        "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/127.06533103 Mobile Safari/537.36",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "sec-fetch-site": "same-site",
        "pragma": "no-cache",
    }

    MAX_RETRIES = 3
    DEFAULT_TAP_DELAY_RANGE = (0.3, 0.5)
    DEFAULT_TAP_AMOUNT = (1, 10)
    SLEEP_DURATION_LOW_ENERGY = random.randint(40,60)  # 5 minutes
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
            encoded_data = self.token
            decoded_data = urllib.parse.unquote(encoded_data)

            # Parse the decoded string into components
            query_params = urllib.parse.parse_qs(decoded_data)

            # Extract the 'user' field
            user_data_encoded = query_params['user'][0]
            user_data_json = urllib.parse.unquote(user_data_encoded)
            user_data = json.loads(user_data_json)

            # Extract other fields
            auth_date = int(query_params['auth_date'][0])
            hash_value = query_params['hash'][0]

            # Extract relevant fields
            user_id = user_data['id']
            first_name = user_data['first_name']
            username = user_data['username']
            

            data = {
                "isTaskLogin": False,
                "source": "TELEGRAM",
                "isTmaTonAppUser": True,
                "user": { 
                    "auth_date": auth_date,
                    "first_name": first_name,
                    "hash": hash_value,
                    "id": user_id,
                    "username": username
                },
                "fingerprintId": None
            }
            
            print(data)

            # Make an async HTTP POST request using aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(self.GET_BEARER_URL, json=data) as response:
                    if response.status == 200:
                        try:
                            result = await response.json()  # Parse the JSON response
                            logging.debug(f"Response JSON: {result}")
                            print(response.headers.get('Authorization'))
                            return response.headers.get('Authorization')  # Get the token from headers
                        except aiohttp.ContentTypeError:
                            logging.error(f"Failed to parse JSON response: {await response.text()}")
                    else:
                        logging.error(f"Failed to fetch bearer token, status code: {response.status}")
                        return None
        except Exception as e:
            logging.error(f"Request failed during fetching bearer token: {e}")
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
            
    async def daily_login(self, session: aiohttp.ClientSession):
        try:
            async with session.get(self.DAILY_LOGIN_URL, headers=self.headers, proxy=self.proxy) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"Daily login success: {result}")
                else:
                    logging.warning(f"Daily login seems to have completed already!")
        except aiohttp.ClientError as e:
            logging.error(f"Request failed during daily login: {e}")
            
    async def schedule_daily_login(self, session: aiohttp.ClientSession, index: int):
        while True:
            logging.info(f"[Account {index}] Performing daily login.")
            await self.daily_login(session)
            logging.info(f"[Account {index}] Daily login completed, waiting 24 hours for the next login.")
            await asyncio.sleep(86400)  # Wait for 24 hours

    async def start_tapping(self, index: int):
        async with aiohttp.ClientSession() as session:
            self.bearer = await self.get_bearer_token()  # Use await here
            self.headers['Authorization'] = f"Bearer {self.bearer}"
            print(self.headers)
            logging.warning(f"[Account {index}] Proxy: {self.proxy}")
            logging.warning(f"[Account {index}] Tapping {self.tap_amount} times every {self.tap_delay:.2f} seconds.")
            logging.warning(f"[Account {index}] Starting in {self.random_delay:.2f} seconds.")
            await asyncio.sleep(self.random_delay)
            asyncio.create_task(self.schedule_daily_login(session, index))
            
            while True:
                current_energy, balance = await self.fetch_energy_info(session)
                print(current_energy,balance)
                if current_energy is not None and balance is not None:
                    logging.info(f"[Account {index}] Current energy: {current_energy}, Balance: {balance}")
                    
                    if current_energy < self.tap_amount + 30:
                        logging.warning(f"[Account {index}] Energy too low. Sleeping for {self.SLEEP_DURATION_LOW_ENERGY // 60} minutes.")
                        await asyncio.sleep(self.SLEEP_DURATION_LOW_ENERGY)
                        continue 
                    
                    await self.tap(session)
                    await asyncio.sleep(self.tap_delay)
                    current_energy, balance = await self.fetch_energy_info(session)
                    if current_energy is None:
                         logging.error(f"[Account {index}] Failed to retrieve updated energy or balance.")
                        
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
        logging.warning("Stopping bot due to user interruption...")
        sys.exit(0)