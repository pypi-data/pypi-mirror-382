import requests,re,sys,base64
import time,hashlib,random,string
from datetime import datetime

def _update_cookies(old_cookie_str: str, response: requests.Response) -> str:
    cookies_dict = {}
    for part in old_cookie_str.split(";"):
        part = part.strip()
        if "=" in part:
            k, v = part.split("=", 1)
            cookies_dict[k.strip()] = v.strip()
    for c in response.cookies:
        cookies_dict[c.name] = c.value 
    return "; ".join([f"{k}={v}" for k, v in cookies_dict.items()])   
def _make_client_nonce(length=16):
    chars = string.ascii_letters + string.digits + "-_"
    return "".join(random.choice(chars) for _ in range(length))
def _decode_b64(s):
    s = s.replace("%3D", "=") 
    return base64.urlsafe_b64decode(s)
def _get_sapisidhash(cookies, origin="https://www.youtube.com"):
    sapisid = None
    for p in cookies.split(";"):
        p = p.strip()
        if p.startswith("__Secure-3PAPISID="):
            sapisid = p.split("=",1)[1]
            break
        elif p.startswith("SAPISID="):
            sapisid = p.split("=",1)[1]
            break
    if not sapisid:
        return False

    timestamp = int(time.time())
    to_hash = f"{timestamp} {sapisid} {origin}"
    sha1_hash = hashlib.sha1(to_hash.encode("utf-8")).hexdigest()
    return f"SAPISIDHASH {timestamp}_{sha1_hash}"
def _GETURL(url):
    if '?' in url:
        return url.split("?")[0]
    else:
        return url
def _Rotate_cookies(cookies,x_browser_validation="XPdmRdCCj2OkELQ2uovjJFk6aKA=",x_client_data="CJW2yQEIpbbJAQipncoBCLyKywEIlaHLAQiFoM0BCO6EzwEIz4XPAQiAiM8BCIaKzwE=",user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"):
    current_year = datetime.now().year
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'priority': 'u=0, i',
        'referer': 'https://www.youtube.com/',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-form-factors': '"Desktop"',
        'sec-ch-ua-full-version': '"139.0.7258.157"',
        'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.157", "Chromium";v="139.0.7258.157"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-site',
        'upgrade-insecure-requests': '1',
        'user-agent': user_agent,
        'x-browser-channel': 'stable',
        'x-browser-copyright': f'Copyright {str(current_year)} Google LLC. All rights reserved.',
        'x-browser-validation': x_browser_validation,
        'x-browser-year': str(current_year),
        'x-client-data': x_client_data,
        'cookie': cookies,
    }
    try:
        r = requests.get("https://accounts.youtube.com/RotateCookiesPage?origin=https://www.youtube.com&yt_pid=1",headers=headers)
        if r.status_code ==200:
            pattern = r"init\('(-?\d+)'"
            match = re.search(pattern, r.text)
            if match:
                init =  match.group(1)
            else: return False
        else:
            return False
    except KeyboardInterrupt:
        sys.exit(0)    
    except Exception as e:
        print(e)
    headers2 = {
        'accept': '*/*',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'content-type': 'application/json',
        'origin': 'https://accounts.youtube.com',
        'priority': 'u=1, i',
        'referer': 'https://accounts.youtube.com/RotateCookiesPage?origin=https://www.youtube.com&yt_pid=1',
        'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-bitness': '"64"',
        'sec-ch-ua-form-factors': '"Desktop"',
        'sec-ch-ua-full-version': '"139.0.7258.157"',
        'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.157", "Chromium";v="139.0.7258.157"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"15.0.0"',
        'sec-ch-ua-wow64': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'same-origin',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'x-browser-channel': 'stable',
        'x-browser-copyright': f'Copyright {str(current_year)} Google LLC. All rights reserved.',
        'x-browser-validation': x_browser_validation,
        'x-browser-year': str(current_year),
        'x-client-data': x_client_data,
        'cookie': cookies
    }

    json_data = [
        None,
        str(init),
        1,
    ]
    try:
        response = requests.post('https://accounts.youtube.com/RotateCookies', headers=headers2, json=json_data)
        if response.status_code == 200:
            merged_cookie = _update_cookies(cookies, response)
            return merged_cookie
        else:
            return False
    except KeyboardInterrupt:
        sys.exit(0)    
    except Exception as e:
        print(e)
def _GETDATA(cookies,x_browser_validation="XPdmRdCCj2OkELQ2uovjJFk6aKA=",x_client_data = "CJW2yQEIpbbJAQipncoBCLyKywEIlKHLAQjNo8sBCIWgzQEIk4HPAQjuhM8BCLWFzwEIz4XPAQiAiM8BGOntzgEYzYLPARjYhs8B",x_goog_visitor_id="Cgt5dXpraW1JNGpwbyj71urFBjIKCgJWThIEGgAgXw%3D%3D",user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"):
    current_year = datetime.now().year
    headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'authorization': _get_sapisidhash(cookies),
            'content-type': 'application/json',
            'origin': 'https://www.youtube.com',
            'priority': 'u=1, i',
            'referer': 'https://www.youtube.com/@nhacnghetrenbar.',
            'sec-ch-ua': '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"139.0.7258.157"',
            'sec-ch-ua-full-version-list': '"Not;A=Brand";v="99.0.0.0", "Google Chrome";v="139.0.7258.157", "Chromium";v="139.0.7258.157"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': user_agent,
            'x-browser-channel': 'stable',
            'x-browser-copyright': f'Copyright {str(current_year)} Google LLC. All rights reserved.',
            'x-browser-validation': x_browser_validation,
            'x-browser-year': str(current_year),
            'x-client-data': x_client_data,
            'x-goog-authuser': '0',
            'x-goog-visitor-id': x_goog_visitor_id,
            'x-origin': 'https://www.youtube.com',
            'x-youtube-bootstrap-logged-in': 'true',
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20250904.01.00',
            'cookie': cookies,
        }
    
    data = requests.get("https://www.youtube.com/",headers=headers)
    if data.status_code ==200:
        match = re.search(r'"USER_ACCOUNT_NAME"\s*:\s*"([^"]+)"', data.text)
        if match:
            return True
        else:
            return False
    else:
        return False