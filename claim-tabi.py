import requests
import json
import time
import sys
from datetime import datetime, timedelta
from colorama import init, Fore
import pytz
import urllib3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from tzlocal import get_localzone
import keyboard
import threading
import logging

# Initialize colorama
init(autoreset=True)

# Configure logging
logging.basicConfig(filename='http.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the URLs
login_url = 'https://app.tabibot.com/api/user/sign-in'
checkin_url = 'https://app.tabibot.com/api/user/check-in'
info_url = 'https://app.tabibot.com/api/mining/info'
claim_url = 'https://app.tabibot.com/api/mining/claim'

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read_data_file():
    try:
        with open('data.txt', 'r') as file:
            rawdata = file.read().strip()
            if not rawdata:
                raise ValueError("data.txt is empty. Please provide the necessary data.")
    except FileNotFoundError:
        print(f'{Fore.RED}[{get_timestamp()}] Error: data.txt file not found.{Fore.RED}')
        sys.exit(1)
    except ValueError as e:
        print(f'{Fore.RED}[{get_timestamp()}] Error: {str(e)}{Fore.RED}')
        sys.exit(1)
    return rawdata.splitlines()

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
    'Connection': 'keep-alive',
    'Content-Length': '0',
    'Content-Type': 'application/json',
    'Origin': 'https://app.tabibot.com',
    'Referer': 'https://app.tabibot.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
    'rawdata': read_data_file,  # Use the rawdata read from file
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126", "Microsoft Edge WebView2";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}

def log_http_request(url, method, headers, data=None):
    logging.info(f'Sending {method} request to {url}')
    logging.info(f'Headers: {headers}')
    if data:
        logging.info(f'Body: {json.dumps(data)}')

def log_http_response(response):
    logging.info(f'Response status: {response.status_code}')
    logging.info(f'Headers: {response.headers}')
    logging.info(f'Content: {response.text}')

def login_with_retry(headers, index):
    retry_count = 0
    max_retries = 5
    delay_seconds = 5
    data = {}

    hijau = Fore.GREEN
    putih = Fore.WHITE
    biru = Fore.BLUE
    merah = Fore.RED

    while retry_count < max_retries:
        try:
            log_http_request(login_url, 'POST', headers, data)
            response = requests.post(login_url, headers=headers, json=data, verify=False)
            log_http_response(response)

            if response.status_code == 200:
                response_json = response.json()
                if isinstance(response_json, dict):
                    user = response_json.get('user')
                    tgUserId = user.get('tgUserId')
                    name = user.get('name')
                    level = user.get('level')
                    balance = user.get('coins')
                    loginTime = convert_utc_to_local(user.get('loginTime'))
                    checkInDate = user.get('checkInDate')
                    hasCheckedIn = user.get('hasCheckedIn')
                    tabiAdress = user.get('tabiAddress')
                    streak = user.get('streak')
                    print(f'{biru}[{get_timestamp()}] {putih}=================================================={putih}')
                    print(f'{biru}[{get_timestamp()}] {hijau}+             AUTO CLAIM TABIZOO                 +{hijau}')
                    print(f'{biru}[{get_timestamp()}] {putih}=================================================={putih}')
                    print(f'{biru}[{get_timestamp()}] {hijau}ACCOUNT INDEX: {index}{hijau}')  # Print account index
                    print(f'{biru}[{get_timestamp()}] {hijau}TELEGRAM ID: {tgUserId}              {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}NAME: {name}                       {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}LEVEL: {level}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}BALANCE: {balance}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}LOGIN TIME: {loginTime}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}CHECK IN DATE: {checkInDate}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}HAS CHECKED IN DAILY?: {hasCheckedIn}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}CHECK IN STREAK: {streak}                            {hijau}')
                    print(f'{biru}[{get_timestamp()}] {hijau}CONNECT TO WALLET: {tabiAdress}                            {hijau}')
                    return True
                else:
                    print(f'{merah}[{get_timestamp()}] Error: Invalid response format{merah}')
            else:
                print(f'{merah}[{get_timestamp()}] Error: {response.status_code} - {response.text}{merah}')
                retry_count += 1
                time.sleep(delay_seconds)
        except Exception as e:
            print(f'{merah}[{get_timestamp()}] Exception: {e}{merah}')
            retry_count += 1
            time.sleep(delay_seconds)

    print(f'{merah}[{get_timestamp()}] Failed to login after {max_retries} attempts{merah}')
    return False

def check_in(headers):
    hijau = Fore.GREEN
    putih = Fore.WHITE
    biru = Fore.BLUE
    merah = Fore.RED
    try:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        log_http_request(checkin_url, 'POST', headers, {})
        response = requests.post(checkin_url, headers=headers, json={}, verify=False)
        log_http_response(response)

        if response.status_code == 200:
            response_json = response.json()
            # print(f'{biru}[{get_timestamp()}] Claim response JSON: {json.dumps(response_json)}')
            if isinstance(response_json, dict):
                check_in_status = response_json.get('success')
                if check_in_status:
                    print(f'{biru}[{get_timestamp()}] {hijau}Check-in successful!{hijau}')
                    return True
                else:
                    print(f'{biru}[{get_timestamp()}] {merah}Check-in failed! Already done check-in. Come back tomorrow!{merah}')
                    return False
            else:
                print(f'{biru}[{get_timestamp()}] {merah}Error: Invalid response format{merah}')
                return False
        else:
            print(f'{biru}[{get_timestamp()}] {merah}Error: {response.status_code} - {response.text}{merah}')
            return False
    except requests.exceptions.SSLError as ssl_err:
        print(f'{biru}[{get_timestamp()}] {merah}SSL Error: {ssl_err}{merah}')
        return False
    except Exception as e:
        print(f'{biru}[{get_timestamp()}] {merah}Exception: {e}{merah}')
        return False

def fetch_info(headers):
    try:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        log_http_request(info_url, 'GET', headers)
        response = requests.get(info_url, headers=headers, verify=False)
        log_http_response(response)

        if response.status_code == 200:
            response_json = response.json()
            if isinstance(response_json, dict):
                return response_json
            else:
                print(f'{Fore.RED}[{get_timestamp()}] Error: Invalid response format{Fore.RED}')
                return None
        else:
            print(f'{Fore.RED}[{get_timestamp()}] Error fetching info: {response.status_code} - {response.text}{Fore.RED}')
            return None
    except Exception as e:
        print(f'{Fore.RED}[{get_timestamp()}] Exception: {e}{Fore.RED}')
        return None

def claim_rewards(headers):
    hijau = Fore.GREEN
    putih = Fore.WHITE
    biru = Fore.BLUE
    merah = Fore.RED
    try:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        log_http_request(claim_url, 'POST', headers, {})
        response = requests.post(claim_url, headers=headers, json={}, verify=False)
        log_http_response(response)

        if response.status_code == 200:
            response_json = response.json()
            # print(f'{biru}[{get_timestamp()}] Claim response JSON: {json.dumps(response_json, indent=2)}')
            if isinstance(response_json, bool):
                if response_json:
                     print(f'{biru}[{get_timestamp()}]{hijau} Claim successful!')
                else:
                    print(f'{biru}[{get_timestamp()}]{merah} Claim failed! Not yet to claim.')
            else:
                print(f'{Fore.YELLOW}[{get_timestamp()}] Unexpected response format: {response.text}')
        else:
            print(f'{Fore.RED}[{get_timestamp()}] Error: {response.status_code} - {response.text}')
    except requests.exceptions.SSLError as ssl_err:
        print(f'{Fore.RED}[{get_timestamp()}] SSL Error: {ssl_err}')
    except Exception as e:
        print(f'{Fore.RED}[{get_timestamp()}] Exception: {e}')
def convert_utc_to_local(utc_time_str):
    try:
        if '.' in utc_time_str:
            utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        else:
            utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        
        utc_time = utc_time.replace(tzinfo=pytz.utc)
        local_timezone = get_localzone()  # Replace with your local timezone
        local_time = utc_time.astimezone(local_timezone)
        return local_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    except ValueError as e:
        print(f"Error parsing UTC time: {e}")
        return None

def exit_on_key_press():
    print(f"{Fore.YELLOW}Press 'q' to exit...")
    while True:
        if keyboard.is_pressed('q'):
            print(f"{Fore.YELLOW}Exiting program...")
            sys.exit()

def main():
    hijau = Fore.GREEN
    putih = Fore.WHITE
    biru = Fore.BLUE
    merah = Fore.RED
    kuning = Fore.YELLOW
    banner = f"""
    {hijau}AUTO CLAIM TABIZOO{biru} 
    {hijau}Github : {putih}https://github.com/foxxw0lf
    {hijau}Telegram : {putih}https://t.me/anggastwn
    
    {kuning}Modular Cosmos gaming L1 with any-VM-compatibility. 
    Driven by community, backed by @animocabrands & @BinanceLabs towards a billion-gamer future 🎮{kuning}

    {merah}NOT FOR SALE! | DYOR | This BOT is for study purposes only and cannot be used for commercial purposes{merah}
    """
    print(banner)
    urllib3.disable_warnings()
    # Suppress SSL warnings
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    # Start exit key listener in a separate thread
    keyboard_thread = threading.Thread(target=exit_on_key_press)
    keyboard_thread.daemon = True
    keyboard_thread.start()
    
    # Read accounts from data.txt
    accounts = read_data_file()
    num_accounts = len(accounts)
    
    for index, account_data in enumerate(accounts, start=1):
        print(f'{biru}[{get_timestamp()}] {hijau}Total Accounts in data.txt: {num_accounts}{hijau}')
        print(f'{biru}[{get_timestamp()}] {hijau}Processing Account Index: {index}/{num_accounts}{hijau}')
        headers['rawdata'] = account_data  # Update headers with account data
        if login_with_retry(headers, index):  # Pass index to login_with_retry function
            print(f'{Fore.BLUE}[{get_timestamp()}] Starting TabiZoo check-in process...')
            check_in(headers)
            info_data = fetch_info(headers)
            if info_data:
                rate = info_data.get('rate', 0)
                referral_rate = info_data.get('referralRate', 0)
                current = info_data.get('current', 0)
                top_limit = info_data.get('topLimit', 0)
                accumulated = info_data.get('accumulated', 0)
                nextClaimTimeInSecond = info_data.get('nextClaimTimeInSecond', 0)
                refreshTime = convert_utc_to_local(info_data.get('refreshTime'))
                nextClaimTime = convert_utc_to_local(info_data.get('nextClaimTime'))

                print(f'{biru}[{get_timestamp()}] {hijau}CURRENT BALANCE: {current}{hijau}')
                print(f'{biru}[{get_timestamp()}] {putih}REFRESH TIME: {refreshTime}{putih}')
                print(f'{biru}[{get_timestamp()}] {putih}NEXT CLAIM: {nextClaimTime}{putih}')
                print(f'{biru}[{get_timestamp()}] {hijau}NEXT CLAIM IN SECOND: {nextClaimTimeInSecond}{hijau}')
                
                print(f'{Fore.BLUE}[{get_timestamp()}] Starting TabiZoo claim process...')
                claim_rewards(headers)
                
                # Adding delay between account switches
                delay_seconds = 30  # Set the initial delay time
                print(f'{biru}[{get_timestamp()}] {kuning}Waiting for {delay_seconds} seconds before switching to the next account...{kuning}')
                time.sleep(delay_seconds)

                # Adding delay between account switches
                delay_seconds = 3600 # Set the initial delay time
                print(f'{biru}[{get_timestamp()}] {kuning}Sleep {delay_seconds} seconds before claim again...{kuning}')
                time.sleep(delay_seconds)

                login_with_retry(headers, index)
        
        
if __name__ == "__main__":
    main()
