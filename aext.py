#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import threading
import time
import re
import requests
import random
import os
import gc
import json
import hashlib
import string
import signal
import sys
import subprocess
from datetime import datetime
from io import BytesIO
from mimetypes import guess_type
from os.path import basename

# Auto install packages
def install_packages():
    packages = ['psutil']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Dang cai dat {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_packages()

try:
    import psutil
    USE_PSUTIL = True
except:
    USE_PSUTIL = False

# ==================== 7 MÀU CẦU VỒNG RGB ====================
RAINBOW_RGB = [
    (255, 0, 0),      # Đỏ
    (255, 127, 0),    # Cam
    (255, 255, 0),    # Vàng
    (0, 255, 0),      # Xanh lá
    (0, 255, 255),    # Cyan
    (0, 0, 255),      # Xanh dương
    (139, 0, 255)     # Tím
]

COLOR_SUCCESS = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_RESET = '\033[0m'
COLOR_CYAN = '\033[96m'
COLOR_YELLOW = '\033[93m'
COLOR_INFO = '\033[94m'
COLOR_RED = '\033[91m'
COLOR_WARNING = '\033[93m'

running = True
tasks = []
task_counter = 0
global_delay = 5.0

def rgb_gradient_text(text):
    output = ""
    length = len(text)
    for i, char in enumerate(text):
        if char == ' ' or char == '\n':
            output += char
            continue
        pos = i / length * (len(RAINBOW_RGB) - 1)
        idx = int(pos)
        frac = pos - idx
        if idx + 1 < len(RAINBOW_RGB):
            r = int(RAINBOW_RGB[idx][0] + (RAINBOW_RGB[idx+1][0] - RAINBOW_RGB[idx][0]) * frac)
            g = int(RAINBOW_RGB[idx][1] + (RAINBOW_RGB[idx+1][1] - RAINBOW_RGB[idx][1]) * frac)
            b = int(RAINBOW_RGB[idx][2] + (RAINBOW_RGB[idx+1][2] - RAINBOW_RGB[idx][2]) * frac)
        else:
            r, g, b = RAINBOW_RGB[idx]
        output += f"\033[38;2;{r};{g};{b}m{char}"
    return output + COLOR_RESET

def print_rainbow_banner():
    banner_lines = [
"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣾⠟⠓⣯⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⣾⠞⠳⣷⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣏⣿⠀⠀⠿⣾⠶⠾⠶⠶⠾⠷⠷⠭⢶⣶⣿⣇⠀⢀⣿⣿⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢠⣮⡏⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠈⢿⣕⢄⠀⠀⠀⠀
⠀⠀⠀⣠⣾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢷⣕⠄⠀⠀
⠀⠀⣴⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣤⣄⠀⠀⠀⠀⠀⠀⢀⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣾⡄⠀
⠀⢸⣿⠃⠀⠀⠀⠀⠀⠀⠀⢀⡴⠶⣤⡀⠀⠀⠀⠀⠀⠀⣠⠤⣄⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⡀
⠀⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⢺⣷⠴⢿⡇⠀⠀⠀⠀⠀⢸⣧⠤⢿⡆⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇
⢐⣿⡇⠀⠀⠀⠀⣰⣆⡇⣥⣢⡙⠒⠋⠀⠀⠀⣀⠀⠀⠈⠛⠒⢛⣄⣆⣒⢠⡀⠀⠀⠀⠀⣿⡁
⠀⣿⡇⠀⠀⠀⠀⠏⢸⠑⣏⠟⠀⠀⠀⠀⢦⣤⠿⣄⡴⠀⠀⠀⠸⠣⠏⠟⡼⠇⠀⠀⠀⢠⣿⡇
⠀⠹⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡟⠀  Dinh Xuan Thang - ZiaoLang
⠀⠀⠙⡿⣆⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡿⠋⠀⠀  ========================
⠀⠀⠀⠀⠉⣿⡶⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢫⣿⠁⠀⠀⠀  TREO MES PIDIPIU
⠀⠀⠀⠀⠀⣽⡇⢰⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⢘⣿⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢻⢧⣼⡃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣧⣸⡟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡿⠉⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⣿⠃⢸⣶⣦⣤⣤⣤⣄⣠⣀⣀⣠⣀⣤⣤⣤⣤⣶⠄⣿⡇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠘⡿⣆⣼⡞⠈⠁⠈⠉⠉⠙⠒⠚⠓⠉⠉⠉⠈⣽⣷⣠⣿⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠓⠁⠀⠀⠀⠀⠀"""

    ]
    for line in banner_lines:
        if line.strip():
            print(rgb_gradient_text(line))
        else:
            print()
        time.sleep(0.05)

def cprint(text, color_name):
    color_map = {
        'red': COLOR_RED, 'green': COLOR_SUCCESS, 'yellow': COLOR_YELLOW,
        'cyan': COLOR_CYAN, 'info': COLOR_INFO, 'warning': COLOR_WARNING, 'error': COLOR_ERROR
    }
    print(f"{color_map.get(color_name, COLOR_RESET)}{text}{COLOR_RESET}")

def show_help():
    print("\n" + "="*60)
    print(rgb_gradient_text("DANH SACH LENH DIEU KHIEN"))
    print("="*60)
    print(f"{COLOR_CYAN}add{COLOR_RESET}       - Them task moi")
    print(f"{COLOR_CYAN}list{COLOR_RESET}      - Liet ke task dang chay")
    print(f"{COLOR_CYAN}stop{COLOR_RESET}      - Dung task theo so")
    print(f"{COLOR_CYAN}stopall{COLOR_RESET}   - Dung tat ca task")
    print(f"{COLOR_CYAN}delay{COLOR_RESET}     - Thay doi delay mac dinh")
    print(f"{COLOR_CYAN}mem{COLOR_RESET}       - Hien thi RAM usage")
    print(f"{COLOR_CYAN}clean{COLOR_RESET}     - Don RAM thu cong")
    print(f"{COLOR_CYAN}help{COLOR_RESET}      - Hien thi tro giup")
    print(f"{COLOR_CYAN}exit{COLOR_RESET}      - Thoat")
    print("="*60 + "\n")

def get_uptime(start_time):
    elapsed = (datetime.now() - start_time).total_seconds()
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def get_memory_usage():
    try:
        if USE_PSUTIL and psutil:
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        return 0
    except:
        return 0

def clean_memory():
    gc.collect()
    if hasattr(gc, 'garbage'):
        gc.garbage.clear()
    cprint(f"[DON RAM] RAM: {get_memory_usage():.1f}MB", 'cyan')
    return get_memory_usage()

# ==================== CPU GUARD ====================
TARGET_CPU_PERCENT = 15.0
CHECK_INTERVAL = 1.0
MAX_SUSPEND_SECONDS = 30
MIN_SUSPEND_SECONDS = 0.05
PARENT_PID = os.getpid()
_CPU_GUARD_WATCHDOG = None

def _measure_process_cpu_percent_fallback(pid, interval):
    try:
        if pid != os.getpid():
            return 0.0
        t0 = time.perf_counter()
        cpu0 = time.process_time()
        time.sleep(interval)
        t1 = time.perf_counter()
        cpu1 = time.process_time()
        wall = t1 - t0
        if wall <= 0:
            return 0.0
        return ((cpu1 - cpu0) / wall) * 100.0
    except:
        return 0.0

def _suspend_process_unix(pid):
    try:
        os.kill(pid, signal.SIGSTOP)
        return True
    except:
        return False

def _resume_process_unix(pid):
    try:
        os.kill(pid, signal.SIGCONT)
        return True
    except:
        return False

def _suspend_process_psutil(p_proc):
    try:
        p_proc.suspend()
        return True
    except:
        return False

def _resume_process_psutil(p_proc):
    try:
        p_proc.resume()
        return True
    except:
        return False

def _watchdog_main():
    global _CPU_GUARD_WATCHDOG
    use_ps = USE_PSUTIL and (psutil is not None)
    if use_ps:
        try:
            p = psutil.Process(PARENT_PID)
        except:
            p = None
            use_ps = False
    else:
        p = None
    target = TARGET_CPU_PERCENT
    while True:
        try:
            if use_ps and p is not None:
                try:
                    usage = p.cpu_percent(interval=CHECK_INTERVAL)
                except:
                    usage = 0.0
            else:
                usage = _measure_process_cpu_percent_fallback(PARENT_PID, CHECK_INTERVAL)
            if usage > target:
                suspend_time = min(MAX_SUSPEND_SECONDS, max(MIN_SUSPEND_SECONDS, CHECK_INTERVAL * (usage / target - 1) * 2))
                cprint(f"[CPU Guard] CPU: {usage:.1f}% > {target}% - Suspend {suspend_time:.2f}s", 'yellow')
                suspended = False
                if use_ps and p is not None:
                    suspended = _suspend_process_psutil(p)
                else:
                    if hasattr(signal, "SIGSTOP"):
                        suspended = _suspend_process_unix(PARENT_PID)
                if suspended:
                    time.sleep(suspend_time)
                    if use_ps and p is not None:
                        _resume_process_psutil(p)
                    else:
                        if hasattr(signal, "SIGCONT"):
                            _resume_process_unix(PARENT_PID)
                    cprint(f"[CPU Guard] Resume", 'green')
                    time.sleep(0.5)
                else:
                    time.sleep(min(suspend_time, 1.0))
            else:
                time.sleep(CHECK_INTERVAL)
        except:
            time.sleep(1.0)

def start_cpu_guard():
    global _CPU_GUARD_WATCHDOG
    _CPU_GUARD_WATCHDOG = threading.Thread(target=_watchdog_main, daemon=True)
    _CPU_GUARD_WATCHDOG.start()
    cprint(f"[CPU Guard] Khoi dong - Gioi han CPU: {TARGET_CPU_PERCENT}%", 'green')

# ==================== AUTO CLEAN ====================
def auto_clean_memory_loop(stop_event):
    clean_count = 0
    while not stop_event.is_set():
        time.sleep(60)
        clean_count += 1
        memory_before = get_memory_usage()
        clean_memory()
        cprint(f"[AUTO CLEAN #{clean_count}] RAM: {memory_before:.1f}MB -> {get_memory_usage():.1f}MB", 'cyan')

def start_auto_cleaner():
    stop_event = threading.Event()
    cleaner_thread = threading.Thread(target=auto_clean_memory_loop, args=(stop_event,), daemon=True)
    cleaner_thread.start()
    cprint(f"[AUTO CLEAN] Khoi dong - Don RAM moi 60 giay", 'green')
    return stop_event

# ==================== CHUC NANG 1: get_uid_fbdtsg ====================
def get_uid_fbdtsg(ck):
    try:
        headers = {'Accept': 'text/html', 'Cookie': ck, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get('https://www.facebook.com/', headers=headers)
        html_content = response.text
        if "home_icon" not in html_content and '"USER_ID":"' not in html_content:
            return None, None, None, None, None, None
        user_id = re.search(r'"USER_ID":"(\d+)"', html_content)
        user_id = user_id.group(1) if user_id else None
        fb_dtsg_match = re.search(r'"f":"([^"]+)"', html_content)
        fb_dtsg = fb_dtsg_match.group(1) if fb_dtsg_match else None
        jazoest_match = re.search(r'jazoest=(\d+)', html_content)
        jazoest = jazoest_match.group(1) if jazoest_match else None
        revision_match = re.search(r'"server_revision":(\d+),"client_revision":(\d+)', html_content)
        rev = revision_match.group(1) if revision_match else ""
        a_match = re.search(r'__a=(\d+)', html_content)
        a = a_match.group(1) if a_match else "1"
        req = "1b"
        if not user_id or not fb_dtsg:
            return None, None, None, None, None, None
        return user_id, fb_dtsg, rev, req, a, jazoest
    except Exception as e:
        cprint(f"Loi get_uid_fbdtsg: {e}", 'red')
        return None, None, None, None, None, None

# ==================== CHUC NANG 2: parse_cookie_string ====================
def parse_cookie_string(cookie_string):
    cookie_dict = {}
    cookies = cookie_string.split(";")
    for cookie in cookies:
        if "=" in cookie:
            key, value = cookie.split("=", 1)
            try:
                cookie_dict[key.strip()] = value.strip()
            except:
                pass
    return cookie_dict

def get_user_id_from_cookie(cookie):
    try:
        match = re.search(r'c_user=(\d+)', cookie)
        return match.group(1) if match else "Unknown"
    except:
        return "Unknown"

# ==================== CHUC NANG 3: digitToChar, str_base ====================
def digitToChar(digit):
    if digit < 10:
        return str(digit)
    return chr(ord('a') + digit - 10)

def str_base(number, base):
    if number < 0:
        return "-" + str_base(-number, base)
    (d, m) = divmod(number, base)
    if d > 0:
        return str_base(d, base) + digitToChar(m)
    return digitToChar(m)

def base36encode(number, alphabet="0123456789abcdefghijklmnopqrstuvwxyz"):
    if not isinstance(number, int):
        raise TypeError("number must be an integer")
    base36 = ""
    sign = ""
    if number < 0:
        sign = "-"
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36

# ==================== CHUC NANG 4: dataSplit ====================
def dataSplit(string1, string2, numberSplit1=None, numberSplit2=None, HTML=None, amount=None, string3=None, numberSplit3=None, defaultValue=None):
    if defaultValue:
        numberSplit1, numberSplit2 = 1, 0
    if amount is None:
        return HTML.split(string1)[numberSplit1].split(string2)[numberSplit2]
    elif amount == 3:
        return HTML.split(string1)[numberSplit1].split(string2)[numberSplit2].split(string3)[numberSplit3]

# ==================== CHUC NANG 5: get_from ====================
def get_from(input_str, start_token, end_token):
    start = input_str.find(start_token) + len(start_token)
    if start < len(start_token):
        return ""
    last_half = input_str[start:]
    end = last_half.find(end_token)
    if end == -1:
        raise ValueError(f"Could not find endToken")
    return last_half[:end]

# ==================== CHUC NANG 6: generate_offline_threading_id ====================
def generate_offline_threading_id():
    ret = int(time.time() * 1000)
    value = random.randint(0, 4294967295)
    binary_str = format(value, "022b")[-22:]
    msgs = bin(ret)[2:] + binary_str
    return str(int(msgs, 2))

# ==================== CHUC NANG 7: generate_session_id, generate_client_id ====================
def generate_session_id():
    return random.randint(1, 2 ** 53)

def generate_client_id():
    def gen(length):
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return gen(8) + '-' + gen(4) + '-' + gen(4) + '-' + gen(4) + '-' + gen(12)

# ==================== CHUC NANG 8: json_minimal ====================
def json_minimal(data):
    return json.dumps(data, separators=(",", ":"))

# ==================== CHUC NANG 9: gen_threading_id ====================
def gen_threading_id():
    return str(int(format(int(time.time() * 1000), "b") + ("0000000000000000000000" + format(int(random.random() * 4294967295), "b"))[-22:], 2))

# ==================== CHUC NANG 10: get_headers ====================
def get_headers(url, options={}, ctx={}, customHeader={}):
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": "https://www.facebook.com/",
        "Host": url.replace("https://", "").split("/")[0],
        "Origin": "https://www.facebook.com",
        "User-Agent": "Mozilla/5.0 (Linux; Android 9; SM-G973U Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
        "Connection": "keep-alive",
    }
    if "user_agent" in options:
        headers["User-Agent"] = options["user_agent"]
    for key in customHeader:
        headers[key] = customHeader[key]
    if "region" in ctx:
        headers["X-MSGR-Region"] = ctx["region"]
    return headers

# ==================== CHUC NANG 11: Counter class ====================
class Counter:
    def __init__(self, initial_value=0):
        self.value = initial_value
    def increment(self):
        self.value += 1
        return self.value
    @property
    def counter(self):
        return self.value

# ==================== CHUC NANG 12: formAll ====================
_req_counter = Counter(0)

def formAll(dataFB, FBApiReqFriendlyName=None, docID=None, requireGraphql=None):
    global _req_counter
    __reg = _req_counter.increment()
    dataForm = {}
    if requireGraphql is None:
        dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
        dataForm["jazoest"] = dataFB["jazoest"]
        dataForm["__a"] = 1
        dataForm["__user"] = str(dataFB["FacebookID"])
        dataForm["__req"] = str_base(__reg, 36)
        dataForm["__rev"] = dataFB["clientRevision"]
        dataForm["av"] = dataFB["FacebookID"]
        dataForm["fb_api_caller_class"] = "RelayModern"
        dataForm["fb_api_req_friendly_name"] = FBApiReqFriendlyName
        dataForm["server_timestamps"] = "true"
        dataForm["doc_id"] = str(docID)
    else:
        dataForm["fb_dtsg"] = dataFB["fb_dtsg"]
        dataForm["jazoest"] = dataFB["jazoest"]
        dataForm["__a"] = 1
        dataForm["__user"] = str(dataFB["FacebookID"])
        dataForm["__req"] = str_base(__reg, 36)
        dataForm["__rev"] = dataFB["clientRevision"]
        dataForm["av"] = dataFB["FacebookID"]
    return dataForm

# ==================== CHUC NANG 13: mainRequests ====================
def mainRequests(url, data, cookies):
    if isinstance(url, str) and isinstance(data, dict):
        return {
            "url": url,
            "data": data,
            "headers": {
                "authority": "www.facebook.com",
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,vi;q=0.8",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://www.facebook.com",
                "referer": "https://www.facebook.com/",
                "user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            },
            "cookies": parse_cookie_string(cookies),
            "verify": True
        }
    else:
        return {
            "headers": Headers(cookies, data),
            "timeout": 5,
            "url": url,
            "data": data,
            "cookies": parse_cookie_string(cookies),
            "verify": True
        }

def Headers(setCookies, dataForm=None, Host=None):
    if Host is None:
        Host = "www.facebook.com"
    headers = {}
    headers["Host"] = Host
    headers["Connection"] = "keep-alive"
    if dataForm is not None:
        headers["Content-Length"] = str(len(dataForm))
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
    headers["Accept"] = "*/*"
    headers["Origin"] = "https://" + Host
    headers["Sec-Fetch-Site"] = "same-origin"
    headers["Sec-Fetch-Mode"] = "cors"
    headers["Sec-Fetch-Dest"] = "empty"
    headers["Referer"] = "https://" + Host
    headers["Accept-Language"] = "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7"
    return headers

# ==================== CHUC NANG 14: dataGetHome ====================
def dataGetHome(setCookies):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    ]
    dictValueSaved = {}
    try:
        c_user = re.search(r"c_user=(\d+)", setCookies)
        if c_user:
            dictValueSaved["FacebookID"] = c_user.group(1)
        else:
            dictValueSaved["FacebookID"] = None
    except:
        dictValueSaved["FacebookID"] = None
    
    headers = {
        'Cookie': setCookies,
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    sites_to_try = ['https://www.facebook.com', 'https://mbasic.facebook.com']
    fb_dtsg_found = False
    jazoest_found = False
    
    params_to_extract = {
        "fb_dtsg": None,
        "jazoest": None,
        "clientRevision": None
    }
    
    for site in sites_to_try:
        if fb_dtsg_found and jazoest_found:
            break
        try:
            response = requests.get(site, headers=headers)
            if not fb_dtsg_found:
                fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
                if not fb_dtsg_match:
                    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                if fb_dtsg_match:
                    params_to_extract["fb_dtsg"] = fb_dtsg_match.group(1)
                    fb_dtsg_found = True
            if not jazoest_found:
                jazoest_match = re.search(r'jazoest=(\d+)', response.text)
                if jazoest_match:
                    params_to_extract["jazoest"] = jazoest_match.group(1)
                    jazoest_found = True
            revision_match = re.search(r'client_revision":(\d+)', response.text)
            if revision_match:
                params_to_extract["clientRevision"] = revision_match.group(1)
        except:
            continue
    
    for param, value in params_to_extract.items():
        dictValueSaved[param] = value if value else None
    
    dictValueSaved["__rev"] = "1015919737"
    dictValueSaved["__req"] = "1b"
    dictValueSaved["__a"] = "1"
    dictValueSaved["cookieFacebook"] = setCookies
    
    return dictValueSaved

# ==================== CHUC NANG 15: fbTools class ====================
class fbTools:
    def __init__(self, dataFB, threadID="0"):
        self.threadID = threadID
        self.dataGet = None
        self.dataFB = dataFB
        self.ProcessingTime = None
        self.last_seq_id = None
    
    def getAllThreadList(self):
        randomNumber = gen_threading_id()
        dataForm = formAll(self.dataFB, requireGraphql=0)
        dataForm["queries"] = json.dumps({
            "o0": {
                "doc_id": "3336396659757871",
                "query_params": {
                    "limit": 20,
                    "before": None,
                    "tags": ["INBOX"],
                    "includeDeliveryReceipts": False,
                    "includeSeqID": True,
                }
            }
        })
        sendRequests = requests.post(**mainRequests("https://www.facebook.com/api/graphqlbatch/", dataForm, self.dataFB["cookieFacebook"]))
        response_text = sendRequests.text
        self.ProcessingTime = sendRequests.elapsed.total_seconds()
        if response_text.startswith("for(;;);"):
            response_text = response_text[9:]
        if not response_text.strip():
            return False
        try:
            response_parts = response_text.split("\n")
            first_part = response_parts[0]
            if first_part.strip():
                response_data = json.loads(first_part)
                self.dataGet = first_part
                if "o0" in response_data and "data" in response_data["o0"] and "viewer" in response_data["o0"]["data"] and "message_threads" in response_data["o0"]["data"]["viewer"]:
                    self.last_seq_id = response_data["o0"]["data"]["viewer"]["message_threads"]["sync_sequence_id"]
                    return True
            return False
        except:
            return False
    
    def getListThreadID(self):
        try:
            if self.dataGet is None:
                return {"ERR": "No data available"}
            data_to_parse = self.dataGet
            if data_to_parse.startswith("for(;;);"):
                data_to_parse = data_to_parse[9:]
            threadIDList = []
            threadNameList = []
            getData = json.loads(data_to_parse)["o0"]["data"]["viewer"]["message_threads"]["nodes"]
            for getThreadID in getData:
                thread_key = getThreadID.get("thread_key", {})
                thread_fbid = thread_key.get("thread_fbid")
                if thread_fbid is not None:
                    threadIDList.append(thread_fbid)
                    threadNameList.append(getThreadID.get("name", "No Name"))
            return {
                "threadIDList": threadIDList,
                "threadNameList": threadNameList,
                "countThread": len(threadIDList)
            }
        except Exception as errLog:
            return {"ERR": str(errLog)}
    
    def getThreadInfo(self):
        try:
            if self.dataGet is None:
                return None
            data_to_parse = self.dataGet
            if data_to_parse.startswith("for(;;);"):
                data_to_parse = data_to_parse[9:]
            data = json.loads(data_to_parse)
            return data.get("o0", {}).get("data", {}).get("viewer", {}).get("message_threads", {})
        except:
            return None

# ==================== CLASS MESSENGER ====================
class Messenger:
    def __init__(self, cookie, user_agents, thread_id):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.user_agents = user_agents
        self.user_agent = random.choice(user_agents) if user_agents else 'Mozilla/5.0'
        self.send_count = 0
        self.fail_count = 0
        self.thread_id = thread_id
        self.is_broken = False
        self.init_params()
    
    def id_user(self):
        try:
            return re.search(r'c_user=(\d+)', self.cookie).group(1)
        except:
            raise Exception('Cookie khong hop le')
    
    def refresh_fb_dtsg(self):
        self.fb_dtsg = None 
        try:
            self.init_params()
            return self.fb_dtsg is not None
        except Exception as e:
            cprint(f"[LOI LAM MOI] Cookie {self.user_id}: {str(e)}", 'red')
            return False
    
    def init_params(self):
        headers = {'Cookie': self.cookie, 'User-Agent': self.user_agent}
        try:
            resp = requests.get('https://www.facebook.com', headers=headers, timeout=10)
            match = re.search(r'"token":"(.*?)"', resp.text)
            if not match:
                resp = requests.get('https://mbasic.facebook.com', headers=headers, timeout=10)
                match = re.search(r'name="fb_dtsg" value="(.*?)"', resp.text)
            if match:
                self.fb_dtsg = match.group(1)
                resp.close()
            else:
                raise Exception('Khong the lay fb_dtsg')
        except Exception as e:
            raise Exception(f'Loi init: {str(e)}')
    
    def gui_tn(self, recipient_id, message):
        if self.is_broken:
            return False
        
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': recipient_id,
            'action_type': 'ma-type:user-generated-message',
            'body': message,
            'client': 'mercury',
            'author': f'fbid:{self.user_id}',
            'timestamp': timestamp,
            'source': 'source:chat:web',
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            '__user': self.user_id,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': self.fb_dtsg
        }
        headers = {
            'Cookie': self.cookie,
            'User-Agent': self.user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': f'https://www.facebook.com/messages/t/{recipient_id}',
        }
        for attempt in range(3):
            try:
                res = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers, timeout=10)
                if res.status_code == 200:
                    self.send_count += 1
                    res.close()
                    return True
                else:
                    res.close()
                    time.sleep(1)
            except:
                time.sleep(1)
        self.fail_count += 1
        return False

# ==================== CLASS MESSENGER TASK ====================
class MessengerTask:
    def __init__(self, task_id, cookie, recipient_id, message, delay):
        self.task_id = task_id
        self.cookie = cookie
        self.user_id = get_user_id_from_cookie(cookie)
        self.recipient_id = recipient_id
        self.message = message
        self.delay = delay
        self.running = True
        self.thread = None
        self.messenger = None
        self.send_count = 0
        self.fail_count = 0
        self.start_time = datetime.now()
        
    def start(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        
    def run(self):
        try:
            user_agents = load_user_agents('ua.txt')
            self.messenger = Messenger(self.cookie, user_agents, self.task_id)
        except Exception as e:
            cprint(f"[Task {self.task_id}] Loi khoi tao: {e}", 'red')
            return
        
        color_idx = self.task_id % len(RAINBOW_RGB)
        rgb = RAINBOW_RGB[color_idx]
        color_code = f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
        print(f"{color_code}[Task {self.task_id}] Started - UID: {self.user_id} -> ID: {self.recipient_id}{COLOR_RESET}")
        
        fail_streak = 0
        
        while self.running:
            try:
                actual_delay = self.delay + random.uniform(-0.5, 0.5)
                if actual_delay < 0.5:
                    actual_delay = 0.5
                
                success = self.messenger.gui_tn(self.recipient_id, self.message)
                
                if success:
                    fail_streak = 0
                    self.send_count = self.messenger.send_count
                else:
                    fail_streak += 1
                    self.fail_count = self.messenger.fail_count
                    if fail_streak >= 10:
                        cprint(f"[Task {self.task_id}] That bai 10 lan, dung task", 'red')
                        break
                
                uptime = get_uptime(self.start_time)
                status_color = COLOR_SUCCESS if success else COLOR_ERROR
                status_text = "✓" if success else "✗"
                print(f"{status_color}[Task {self.task_id}] {status_text} | To: {self.recipient_id} | OK:{self.send_count} FAIL:{self.fail_count} | Uptime:{uptime}{COLOR_RESET}".ljust(100), end='\r')
                time.sleep(actual_delay)
            except Exception as e:
                self.fail_count += 1
                time.sleep(self.delay)
        
        cprint(f"\n[Task {self.task_id}] Da dung - OK:{self.send_count} FAIL:{self.fail_count}", 'yellow')

# ==================== LOAD USER AGENTS ====================
def load_user_agents(file_path='ua.txt'):
    agents = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        agents.append(line)
            cprint(f"[OK] Da doc {len(agents)} User-Agent", 'green')
        else:
            agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]
            cprint(f"[!] Khong tim thay ua.txt, dung UA mac dinh", 'yellow')
    except:
        agents = []
    return agents

# ==================== TAO TASK TRUC TIEP ====================
def create_tasks_direct():
    global task_counter, global_delay
    
    print("\n" + "="*60)
    print(rgb_gradient_text("TAO TASK MESSENGER SPAM"))
    print("="*60)
    
    recipient_id = input(f"\n{COLOR_CYAN}[?] Nhap ID nhan tin: {COLOR_RESET}").strip()
    if not recipient_id:
        cprint("ID nhan khong duoc de trong!", 'red')
        return False
    
    print(f"\n{COLOR_CYAN}[?] Chon cach nhap tin nhan:{COLOR_RESET}")
    print("1. Nhap truc tiep")
    print("2. Doc tu file")
    choice = input("Lua chon (1/2): ").strip()
    
    message = ""
    if choice == "1":
        message = input(f"{COLOR_CYAN}[?] Nhap tin nhan: {COLOR_RESET}").strip()
    else:
        file_path = input(f"{COLOR_CYAN}[?] Nhap duong dan file: {COLOR_RESET}").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                message = f.read().strip()
            cprint(f"Da doc file: {len(message)} ky tu", 'green')
        except Exception as e:
            cprint(f"Loi doc file: {e}", 'red')
            return False
    
    if not message:
        cprint("Tin nhan khong duoc de trong!", 'red')
        return False
    
    try:
        delay_input = input(f"{COLOR_CYAN}[?] Nhap delay (giay, mac dinh {global_delay}): {COLOR_RESET}").strip()
        if delay_input:
            delay = max(0.5, float(delay_input))
        else:
            delay = global_delay
    except:
        delay = global_delay
    
    print("\n" + "="*60)
    print(rgb_gradient_text("NHAP DANH SACH COOKIE"))
    print("Moi cookie la 1 task rieng biet")
    print("Nhap 'done' de ket thuc")
    print("="*60)
    
    cookie_list = []
    count = 1
    while True:
        cookie = input(f"{COLOR_CYAN}Cookie #{count}{COLOR_RESET}> ").strip()
        if cookie.lower() == 'done':
            if count == 1:
                cprint("Chua nhap cookie nao!", 'red')
                continue
            break
        if cookie:
            if 'c_user' not in cookie:
                cprint("[!] Cookie co ve khong hop le (thieu c_user)", 'yellow')
            cookie_list.append(cookie)
            count += 1
    
    if not cookie_list:
        cprint("Khong co cookie nao duoc nhap!", 'red')
        return False
    
    cprint(f"\n[+] Dang tao {len(cookie_list)} task...", 'cyan')
    for cookie in cookie_list:
        task_counter += 1
        task = MessengerTask(task_counter, cookie, recipient_id, message, delay)
        task.start()
        tasks.append(task)
        time.sleep(0.1)
    
    cprint(f"\n[+] Da tao thanh cong {len(cookie_list)} task!", 'green')
    return True

# ==================== QUAN LY TASK ====================
def add_single_task():
    global task_counter, global_delay
    
    print("\n" + "="*50)
    print(rgb_gradient_text("THEM TASK MOI"))
    print("="*50)
    
    cookie = input("Nhap cookie: ").strip()
    if not cookie:
        cprint("Khong co cookie!", 'red')
        return
    
    recipient_id = input("Nhap ID nhan: ").strip()
    if not recipient_id:
        cprint("Khong co ID nhan!", 'red')
        return
    
    print("\n1. Nhap truc tiep\n2. Doc tu file")
    choice = input("Lua chon (1/2): ").strip()
    
    message = ""
    if choice == "1":
        message = input("Nhap tin nhan: ").strip()
    else:
        file_path = input("Nhap duong dan file: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                message = f.read().strip()
        except Exception as e:
            cprint(f"Loi doc file: {e}", 'red')
            return
    
    if not message:
        cprint("Tin nhan trong!", 'red')
        return
    
    try:
        delay_input = float(input(f"Nhap delay (giay, mac dinh {global_delay}): ").strip() or str(global_delay))
        delay = max(0.5, delay_input)
    except:
        delay = global_delay
    
    task_counter += 1
    task = MessengerTask(task_counter, cookie, recipient_id, message, delay)
    task.start()
    tasks.append(task)
    cprint(f"Da them Task {task_counter}", 'green')

def list_tasks():
    if not tasks:
        cprint("Khong co task nao dang chay!", 'yellow')
        return
    
    print("\n" + "="*80)
    print(rgb_gradient_text("DANH SACH TASK DANG CHAY"))
    print("="*80)
    print(f"{'STT':<4} {'Task ID':<8} {'UID':<15} {'To ID':<15} {'OK':<6} {'FAIL':<6} {'Delay':<8} {'Uptime':<12}")
    print("-"*80)
    
    for i, task in enumerate(tasks):
        uptime = get_uptime(task.start_time)
        print(f"{i+1:<4} {task.task_id:<8} {task.user_id:<15} {task.recipient_id:<15} {task.send_count:<6} {task.fail_count:<6} {task.delay:<8} {uptime:<12}")
    
    print("="*80)
    print(f"Tong task: {len(tasks)} | RAM: {get_memory_usage():.1f} MB")
    print("="*80 + "\n")

def stop_task():
    if not tasks:
        cprint("Khong co task nao!", 'yellow')
        return
    list_tasks()
    try:
        choice = int(input("Chon task de dung: ")) - 1
        if 0 <= choice < len(tasks):
            task = tasks[choice]
            task.stop()
            cprint(f"Da dung Task {task.task_id}", 'green')
            tasks.pop(choice)
        else:
            cprint("Lua chon khong hop le!", 'red')
    except ValueError:
        cprint("Nhap so!", 'red')

def stop_all_tasks():
    global tasks
    if not tasks:
        cprint("Khong co task nao!", 'yellow')
        return
    cprint(f"Dang dung {len(tasks)} task...", 'yellow')
    for task in tasks:
        task.stop()
    tasks.clear()
    cprint("Da dung tat ca task!", 'green')

def set_global_delay():
    global global_delay
    try:
        val = float(input(f"Nhap delay moi (hien tai {global_delay}): ").strip())
        if val < 0.5:
            val = 0.5
        global_delay = val
        cprint(f"Delay: {global_delay}s", 'green')
    except:
        cprint("Delay khong hop le!", 'red')

def show_memory():
    mem = get_memory_usage()
    cprint(f"RAM usage: {mem:.1f} MB", 'cyan')
    if tasks:
        total_ok = sum(t.send_count for t in tasks)
        total_fail = sum(t.fail_count for t in tasks)
        cprint(f"Tong tin nhan: {total_ok} OK, {total_fail} FAIL", 'info')

# ==================== MAIN ====================
def main():
    global running, global_delay
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print_rainbow_banner()
    start_cpu_guard()
    clean_stop_event = start_auto_cleaner()
    
    if not load_user_agents('ua.txt'):
        cprint("[!] Khong co User-Agent", 'red')
        return
    
    # Tao task ngay lap tuc
    create_tasks_direct()
    
    show_help()
    print(f"\n{COLOR_INFO}Tool dang chay. Nhap 'help' de xem lenh{COLOR_RESET}")
    print(f"{COLOR_CYAN}Delay hien tai: {global_delay}s{COLOR_RESET}\n")
    
    while running:
        try:
            cmd = input(f"{COLOR_YELLOW}[CMD]{COLOR_RESET} > ").strip().lower()
            
            if cmd == 'add':
                add_single_task()
            elif cmd == 'list':
                list_tasks()
            elif cmd == 'stop':
                stop_task()
            elif cmd == 'stopall':
                stop_all_tasks()
            elif cmd == 'delay':
                set_global_delay()
            elif cmd == 'mem':
                show_memory()
            elif cmd == 'clean':
                clean_memory()
            elif cmd == 'help':
                show_help()
            elif cmd == 'exit':
                cprint("Dang tat...", 'yellow')
                stop_all_tasks()
                running = False
            elif cmd == '':
                continue
            else:
                cprint("Lenh khong hop le! Go 'help'", 'red')
        except KeyboardInterrupt:
            print()
            cprint("\nDang tat...", 'yellow')
            stop_all_tasks()
            running = False
    
    clean_stop_event.set()
    clean_memory()
    print_rainbow_text("\nCam on ban da su dung tool!", 0.02)
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{COLOR_YELLOW}[!] Thoat{COLOR_RESET}")
        sys.exit(0)
