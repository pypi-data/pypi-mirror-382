import requests,re,sys,base64
import time,hashlib,random,string
from datetime import datetime
from typing import Literal
from .utils import _update_cookies,_make_client_nonce,_decode_b64,_get_sapisidhash,_GETURL,_Rotate_cookies,_GETDATA
class YouTube_Api():
    def __init__(self,cookies:str,x_browser_validation="XPdmRdCCj2OkELQ2uovjJFk6aKA=",x_client_data = "CJW2yQEIpbbJAQipncoBCLyKywEIlKHLAQjNo8sBCIWgzQEIk4HPAQjuhM8BCLWFzwEIz4XPAQiAiM8BGOntzgEYzYLPARjYhs8B",x_goog_visitor_id="Cgt5dXpraW1JNGpwbyj71urFBjIKCgJWThIEGgAgXw%3D%3D",user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"):
        self.current_year = datetime.now().year
        self.cookies = cookies
        self.x_browser_validation= x_browser_validation
        self.x_client_data = x_client_data
        self.x_goog_visitor_id = x_goog_visitor_id
        self.user_agent = user_agent
    def Subscribe(self,url:str):
        if _get_sapisidhash(self.cookies) == False:
            return 0
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'authorization': _get_sapisidhash(self.cookies),
                'content-type': 'application/json',
                'origin': 'https://www.youtube.com',
                'priority': 'u=1, i',
                'referer': url,
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
                'user-agent': self.user_agent,
                'x-browser-channel': 'stable',
                'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
                'x-browser-validation': self.x_browser_validation,
                'x-browser-year': str(self.current_year),
                'x-client-data': self.x_client_data,
                'x-goog-authuser': '0',
                'x-goog-visitor-id': self.x_goog_visitor_id,
                'x-origin': 'https://www.youtube.com',
                'x-youtube-bootstrap-logged-in': 'true',
                'x-youtube-client-name': '1',
                'x-youtube-client-version': '2.20250904.01.00',
                'cookie': self.cookies,
            }
            data = requests.get(url,headers=headers).text

            clickTrackingParams_raw = r'"buttonText":"Subscribe".*?"clickTrackingParams":"([^"]+)"'
            clickTrackingParam = re.findall(clickTrackingParams_raw, data, flags=re.DOTALL)
            # channelIds_raw = r'"channelIds"\s*:\s*\[\s*"([^"]+)"\s*\]'
            channelIds_raw = r'channel_id=([A-Za-z0-9_-]+)'
            channelIds = re.findall(channelIds_raw, data)
            unique_ids = list(set(channelIds))
            params = {
                'prettyPrint': 'false',
            }

            json_data = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:5296:239d:5db:e7a2:97a0:9d70',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': self.x_goog_visitor_id,
                        'userAgent': self.user_agent,
                        'clientName': 'WEB',
                        'clientVersion': '2.20250904.01.00',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': url,
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'COzY68UGEPyyzhwQxcPPHBCZjbEFEOevzxwQndfPHBCKgoATELOQzxwQjbjPHBC9mbAFEKKvzxwQuOTOHBD6888cEIKPzxwQ7MbPHBDM364FEJT-sAUQ4tSuBRDw488cEJ7QsAUQvbauBRDL0bEFENuvrwUQgc3OHBCQwc8cEOmIzxwQppqwBRC72c4cEMXWzxwQq_jOHBDtqIATEJmYsQUQh6zOHBDo5M8cELfq_hIQ79zPHBDJ968FEJGM_xIQtenPHBDa984cEJi5zxwQibDOHBCrnc8cEInorgUQiIewBRDN0bEFENPhrwUQjcywBRDe6c8cEK7WzxwQ3rzOHBC52c4cEIXnzxwQ4M2xBRC9irAFEParsAUQh-rPHBDXwbEFEOLozxwQ-7TPHBDtws8cEJjczxwQn-fPHBC1288cENOdzxwqSENBTVNNUlVxb0wyd0ROSGtCcmlVRXJQUTVndVA5QTd2LXdiVl9BQzF6QWFIVERLZ3JBUURqSVVHdUk0R3YwbTZDNEFWSFFjPTAA',
                            'coldConfigData': 'COzY68UGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQpL6xBRDXwbEFEK-nzhwQkbHOHBD2ss4cEPyyzhwQzeLOHBCvlM8cEKudzxwQ053PHBCir88cEPK2zxwQkMHPHBDtws8cENzEzxwQ7MbPHBD5xs8cEKXKzxwQ29PPHBCd188cEJ_XzxwQg9nPHBDi2c8cEILazxwQ-trPHBCY3M8cEM_gzxwQseHPHBDY4s8cEN_izxwQ5OLPHBCB5c8cEPzlzxwQ9OjPHBC16c8cGjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUSIyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHcqiAFDQU1TWVEwZ3VOMjNBcVFabHgtb0tyVUVzaENEaFpvUXZRRFpEUGtPN2dBVXF4M2FFZjRqekFQVEFyWURGVEdac2JjZmhhUUZrWndGdUlBQ0JLWFNCcUdvQkpPTkJaOTc5SWdHeUZxX1JiZ0x2Y0FHTXJjb2tOOEcyYVFHQTVYeEJwVTQ5Uzg9',
                            'coldHashData': 'COzY68UGEhQxMTUwNjIwMzQzMjc4OTE3MjM1MBjs2OvFBjIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QogBQ0FNU1lRMGd1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2UURaRFBrTzdnQVVxeDNhRWY0anpBUFRBcllERlRHWnNiY2ZoYVFGa1p3RnVJQUNCS1hTQnFHb0JKT05CWjk3OUlnR3lGcV9SYmdMdmNBR01yY29rTjhHMmFRR0E1WHhCcFU0OVM4PQ%3D%3D',
                            'hotHashData': 'COzY68UGEhQxMzM2MDgwNjA5MDE3OTY3OTU5NBjs2OvFBiiU5PwSKKXQ_RIo2pn-EijIyv4SKLfq_hIowYP_EiiRjP8SKMeAgBMoioKAEyj3kIATKOWUgBMotZuAEyjkooATKM6kgBMopKaAEyjvp4ATKO2ogBMyMkFPakZveDFtT1VkZmNiTFhuWFhIMmxMTVdaZHViNXBnWWZvalVnVXBad3IwcnJQclJROjJBT2pGb3gyTjRhQ2lKekNjMEUzYUplQ29QZllxNVBBSjhGLWFGSTViSjMzUWljbmpMd0JIQ0FNU01BMFdvdGY2RmE3QkJwTk44Z3E1Qk0wM2hBUVZITjNQd2d6SzRRXzB2dVlMMk0wSnBjQUYxbGVXeFEtczhnYlJTQT09',
                        },
                        'screenDensityFloat': 1.25,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '139.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUwTmpZd05EQTNOakF5TURNeU5qTTVOZz09EOzY68UGGOzY68UG',
                        'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMYjreP2aXBjwM%3D',
                        'screenWidthPoints': 770,
                        'screenHeightPoints': 730,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': url,
                            'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'internalExperimentFlags': [],
                        'consistencyTokenJars': [],
                    },
                    'clientScreenNonce': _make_client_nonce(),
                    'clickTracking': {
                        'clickTrackingParams': clickTrackingParam[0],
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1757079365698',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '0',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '10',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '730',
                            },
                            {
                                'key': 'biw',
                                'value': '755',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,770,730',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                        'bid': 'ANyPxKr06FW0qz5MNEpOkr8CBbSbjYDRYwYzdwlQ_mwR-iiwAPEJpJydCDclV_k6UJqI6pI8skkHuVUjNHg1EI6Wz4PWM-p_iw',
                    },
                },
                'channelIds': [
                channelIds[0],
                ],
                'params': 'EgIIAhgA',
            }
            response = requests.post(
                'https://www.youtube.com/youtubei/v1/subscription/subscribe',
                params=params,
                headers=headers,
                json=json_data,
            )
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(e)
        except KeyboardInterrupt:
            sys.exit(0)
    def Comment(self,url:str,cmt:str,type_video:Literal["short", "video","live"]):
        if type_video=="video":
            headers = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'authorization': _get_sapisidhash(self.cookies),
                'content-type': 'application/json',
                'origin': 'https://www.youtube.com',
                'priority': 'u=1, i',
                'referer': url,
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
                'user-agent': self.user_agent,
                'x-browser-channel': 'stable',
                'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
                'x-browser-validation': self.x_browser_validation,
                'x-browser-year': str(self.current_year),
                'x-client-data': self.x_client_data,
                'x-goog-authuser': '0',
                'x-goog-visitor-id': self.x_goog_visitor_id,
                'x-origin': 'https://www.youtube.com',
                'x-youtube-bootstrap-logged-in': 'true',
                'x-youtube-client-name': '1',
                'x-youtube-client-version': '2.20250910.00.00',
                'cookie': self.cookies,
            }
            data = requests.get(url,headers=headers).text
            section_match = re.search(r'"sectionIdentifier":"comment-item-section".{0,5000}', data)
            if not section_match:
                return False
            section_text = section_match.group(0)
            section_match2 = r'youtubei/v1/next.*?"continuationCommand":\{"token":"([^"]+)"'
            match = re.search(r'"clickTrackingParams"\s*:\s*"([^"]+)"', section_text)
            if match:
                clickTrackingParams =  match.group(1)
            else:
                return False
            matches = re.findall(section_match2, data)
            if matches:
                tokens = [item for item in matches if item.startswith("Eg")]
                
            else:
                return False
            pattern = r'(?:clickTrackingParams|trackingParams)"\s*:\s*"(?P<token>CM[^"]*?)"'
            matches2 = re.findall(pattern, data)
            if matches2:
                tokens2 = [item for item in matches2 if item.startswith("CM")]
            else:
                return False
            params = {
                'prettyPrint': 'false',
            }
            json_data = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:2f05:1827:e5ff:ee5f:d1b2:d354',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': self.x_goog_visitor_id,
                        'userAgent': self.user_agent,
                        'clientName': 'WEB',
                        'clientVersion': '2.20250910.00.00',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': url,
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'CNPZkMYGEPu0zxwQ8czPHBCRjP8SEKn3zxwQibDOHBCBzc4cEJmNsQUQ4ujPHBDN0bEFELOQzxwQxcPPHBCF588cEParsAUQk_LPHBDv3M8cEMXWzxwQ4tSuBRC2q4ATEL22rgUQ4M2xBRCHrM4cEInorgUQmLnPHBC45M4cEJ7QsAUQjOnPHBCIh7AFEO2ogBMQtsnPHBDF988cEJT-sAUQ6OTPHBDnr88cELfq_hIQy9GxBRDXwbEFELnZzhwQ4enPHBC34K4FEIqCgBMQ8OPPHBCCj88cENPhrwUQ6YjPHBD8ss4cENuvrwUQndfPHBCrnc8cEJmYsQUQu9nOHBC9irAFEK7WzxwQ7MbPHBCmmrAFEL2ZsAUQ2vfOHBDM364FEN68zhwQi_fPHBCRwc8cEN7pzxwQq_jOHBCNzLAFEMn3rwUQmNzPHBC1288cEO3CzxwQ2e_PHBDpy88cEJ_nzxwqSENBTVNNUlVxb0wyd0ROSGtCcmlVRXJQUTVndVA5QTY4X3c2MXpBYUhUREtnckFRRGpJVUd1STRHdjBtNkM0QVZ5N2NHSFFjPTAA',
                            'coldConfigData': 'CNPZkMYGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQpL6xBRDXwbEFEK-nzhwQkbHOHBD2ss4cEPyyzhwQzeLOHBCvlM8cEKudzxwQ8rbPHBCRwc8cEO3CzxwQ7MbPHBD5xs8cEKXKzxwQ6cvPHBDb088cEJ3XzxwQn9fPHBCD2s8cEJjczxwQz97PHBDP4M8cELLhzxwQ3-LPHBDk4s8cEPzlzxwQjOjPHBCO6M8cEPTozxwQjOnPHBDZ788cEJPyzxwQ8vPPHBCG9s8cEKn3zxwQxffPHBoyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlEiMkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3KoQBQ0FNU1hRMGl1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2UURaRFBrTzdnQVVxeDNhRWY0anB3MjJBeFV6bWJHM0g0V2tCWkdjQmJpQUFnU2wwZ2FocUFTVGpRV2ZlX1NJQnNoYXYwVzRDNzNBQmpLM0tKRGZCdG1rQmdPaXNnWDFMdz09',
                            'coldHashData': 'CPfikMYGEhQxMzMwNjMzOTY3NzUyMjg0ODYwOBj34pDGBjIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QoQBQ0FNU1hRMGl1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2UURaRFBrTzdnQVVxeDNhRWY0anB3MjJBeFV6bWJHM0g0V2tCWkdjQmJpQUFnU2wwZ2FocUFTVGpRV2ZlX1NJQnNoYXYwVzRDNzNBQmpLM0tKRGZCdG1rQmdPaXNnWDFMdz09',
                            'hotHashData': 'CPfikMYGEhQxMzM2MDgwNjA5MDE3OTY3OTU5NBj34pDGBiiU5PwSKKXQ_RIo2pn-EijIyv4SKLfq_hIowYP_EiiRjP8SKMeAgBMoioKAEyjYi4ATKPeQgBMo5ZSAEyi1m4ATKISkgBMopKaAEyjvp4ATKO2ogBMo8qqAEyiUq4ATMjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUToyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHdCNENBTVNJUTBLb3RmNkZhN0JCcE5OOGdxNUJCVVgzY19DRE1hbjdRdll6UW1sd0FYV1Z3PT0%3D',
                        },
                        'screenDensityFloat': 1.125,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '139.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUwT1RJd09ERTJNVFUyTXpNeU9UTTJNUT09ENPZkMYGGNPZkMYG',
                        'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMYrv_l24nTjwM%3D',
                        'screenWidthPoints': 856,
                        'screenHeightPoints': 811,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': url,
                            'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'internalExperimentFlags': [],
                        'consistencyTokenJars': [],
                    },
                    'clickTracking': {
                        'clickTrackingParams': tokens2[0] ,
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1757686996207',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '0',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '4',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '811',
                            },
                            {
                                'key': 'biw',
                                'value': '839',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,856,811',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                        'bid': 'ANyPxKrUo3y4wPthxzcHFkP7YjvVkp0Goo2ufRhoTFmj797VFJ-3RzXcFyEWhq8slJHoS_s3A_Nelz7iCkwLS155uVg2UUnKXA',
                    },
                },
                'continuation': tokens[0],
            }
            try:
                response = requests.post('https://www.youtube.com/youtubei/v1/next', params=params, headers=headers, json=json_data)
                pattern = r'"createCommentParams"\s*:\s*"([^"]+)"'
                match3 = re.search(pattern, response.text)
                if match3:
                    createCommentParams = match3.group(1)
                else:
                    return False
            except KeyboardInterrupt:
                sys.exit(0)    
            except Exception as e:
                print(e)
            json_data2 = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:2f05:1827:2c39:8420:284:74a4',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': self.x_goog_visitor_id,
                        'userAgent': self.user_agent,
                        'clientName': 'WEB',
                        'clientVersion': '2.20250910.00.00',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': url,
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'CIL-j8YGEIqCgBMQndfPHBDnr88cEOLozxwQq_jOHBDh6c8cELfgrgUQ18GxBRDM364FEN7pzxwQuOTOHBCJ6K4FENPhrwUQ7aiAExDo5M8cEParsAUQ8OPPHBC9tq4FELnZzhwQyfevBRDv3M8cEJi5zxwQ3rzOHBCrnc8cELfq_hIQgo_PHBCp988cEJPyzxwQxcPPHBCL988cEIHNzhwQ_LLOHBCF588cEI3MsAUQntCwBRCu1s8cEIiHsAUQmZixBRDpiM8cEMvRsQUQxdbPHBC72c4cEIzpzxwQkYz_EhDF988cELOQzxwQibDOHBCHrM4cEM3RsQUQkcHPHBDa984cEL2KsAUQ4tSuBRD7tM8cENuvrwUQtauAExDgzbEFEL2ZsAUQlP6wBRCZjbEFEKaasAUQ7MbPHBC1288cEOnLzxwQ2e_PHBCf588cEO3CzxwQmNzPHCpIQ0FNU01SVXFvTDJ3RE5Ia0JyaVVFclBRNWd1UDlBNjhfdzYxekFhSFRES2dyQVFEaklVR3VJNEd2MG02QzRBVnk3Y0dIUWM9MAA%3D',
                            'coldConfigData': 'CIL-j8YGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQpL6xBRDXwbEFEK-nzhwQkbHOHBD2ss4cEPyyzhwQzeLOHBCvlM8cEKudzxwQ8rbPHBCRwc8cEO3CzxwQ7MbPHBD5xs8cEKXKzxwQ6cvPHBDb088cEJ3XzxwQn9fPHBCD2s8cEJjczxwQz97PHBDP4M8cELLhzxwQ3-LPHBDk4s8cEPzlzxwQjOjPHBCO6M8cEPTozxwQjOnPHBDZ788cEJPyzxwQ8vPPHBCG9s8cEKn3zxwQxffPHBoyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlEiMkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3KoQBQ0FNU1hRMGl1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2UURaRFBrTzdnQVVxeDNhRWY0anB3MjJBeFV6bWJHM0g0V2tCWkdjQmJpQUFnU2wwZ2FocUFTVGpRV2ZlX1NJQnNoYXYwVzRDNzNBQmpLM0tKRGZCdG1rQmdPaXNnWDFMdz09',
                            'coldHashData': 'CIL-j8YGEhMzNzUyMjgxMzUyMDk5NjIyMjQxGIL-j8YGMjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUToyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHdChAFDQU1TWFEwaXVOMjNBcVFabHgtb0tyVUVzaENEaFpvUXZRRFpEUGtPN2dBVXF4M2FFZjRqcHcyMkF4VXptYkczSDRXa0JaR2NCYmlBQWdTbDBnYWhxQVNUalFXZmVfU0lCc2hhdjBXNEM3M0FCakszS0pEZkJ0bWtCZ09pc2dYMUx3PT0%3D',
                            'hotHashData': 'CIL-j8YGEhQxMzM2MDgwNjA5MDE3OTY3OTU5NBiC_o_GBiiU5PwSKKXQ_RIo2pn-EijIyv4SKLfq_hIowYP_EiiRjP8SKMeAgBMoioKAEyj3kIATKOWUgBMotZuAEyiEpIATKKSmgBMo76eAEyjtqIATKPKqgBMolKuAEzIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QjRDQU1TSVEwS290ZjZGYTdCQnBOTjhncTVCQlVYM2NfQ0RNYW43UXZZelFtbHdBWFdWdz09',
                        },
                        'screenDensityFloat': 1.25,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '139.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUwT1RFMU56YzROVFExTmpFMk1EZzVOZz09EIL-j8YGGIL-j8YG',
                        'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMYrv_l24nTjwM%3D',
                        'screenWidthPoints': 770,
                        'screenHeightPoints': 730,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': url,
                            'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'internalExperimentFlags': [],
                        'consistencyTokenJars': [],
                    },
                    'clientScreenNonce': _make_client_nonce(),
                    'clickTracking': {
                        'clickTrackingParams': clickTrackingParams,
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1757675266534',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '0',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '3',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '730',
                            },
                            {
                                'key': 'biw',
                                'value': '755',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,770,730',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                        'bid': 'ANyPxKq1ZROqr6EzEq-GWVr5hzIhMBuJrkmDEoLQC2x5cXGfTDwY6WwiHF_y1ZyGaH3IaXVIQLETizTwCWhQagyNRzJb2N9eng',
                    },
                },
                'createCommentParams': createCommentParams,
                'commentText': cmt,
            }

            response = requests.post(
                'https://www.youtube.com/youtubei/v1/comment/create_comment',
                params=params,
                headers=headers,
                json=json_data2,
            )
            if response.status_code == 200:
                return True
            else:
                return False
        elif type_video=="short":
            headers = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'authorization': _get_sapisidhash(self.cookies),
                'content-type': 'application/json',
                'origin': 'https://www.youtube.com',
                'priority': 'u=1, i',
                'referer': url,
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
                'user-agent': self.user_agent,
                'x-browser-channel': 'stable',
                'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
                'x-browser-validation': 'XPdmRdCCj2OkELQ2uovjJFk6aKA=',
                'x-browser-year': str(self.current_year),
                'x-client-data': self.x_client_data,
                'x-goog-authuser': '0',
                'x-goog-visitor-id': self.x_goog_visitor_id,
                'x-origin': 'https://www.youtube.com',
                'x-youtube-bootstrap-logged-in': 'true',
                'x-youtube-client-name': '1',
                'x-youtube-client-version': '2.20250910.00.00',
                'cookie': self.cookies,
            }
            data = requests.get(url,headers=headers).text
            section_match = re.search(r'"sectionIdentifier":"comment-item-section".{0,5000}', data)
            if not section_match:
                return False
            section_text = section_match.group(0)
            section_match2 = r'youtubei/v1/browse.*?"continuationCommand":\{"token":"([^"]+)"'
            match = re.search(r'"clickTrackingParams"\s*:\s*"([^"]+)"', section_text)
            if match:
                clickTrackingParams =  match.group(1)
            else:
                return False
            matches = re.findall(section_match2, data)
            if matches:
                tokens = [item for item in matches if item.startswith("4q")]
                
            else:
                return False
            pattern = r'(?:clickTrackingParams|trackingParams)"\s*:\s*"(?P<token>CD[^"]*?)"'
            matches2 = re.findall(pattern, data)
            if matches2:
                tokens2 = [item for item in matches2 if item.startswith("CDA")]
            else:
                return False
        

            params = {
                'prettyPrint': 'false',
            }

            json_data = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:71bf:a742:2073:99d6:c1a6:efaf',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': self.x_goog_visitor_id,
                        'userAgent': self.user_agent,
                        'clientName': 'WEB',
                        'clientVersion': '2.20250911.00.00',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': url,
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'CLLXk8YGEO_czxwQ0-GvBRDg6c8cEL22rgUQkcHPHBCd0LAFEJmYsQUQ6OTPHBC9mbAFEJi5zxwQ4M2xBRDklbAFEPDjzxwQmejOHBD2q7AFEO2ogBMQxcPPHBDxnLAFEN68zhwQ56_PHBDe6c8cEJmNsQUQyfevBRCRjP8SEKv4zhwQmcrPHBCIh7AFEMb3zxwQrtbPHBDXwbEFEOzGzxwQt-r-EhDxzM8cELfJzxwQ2vfOHBCU_rAFELjkzhwQgc3OHBDA988cEImwzhwQh6zOHBCzkM8cELWrgBMQk_LPHBDL0bEFEMXWzxwQjPfPHBCLgoATEPyyzhwQ6YjPHBCNzLAFEPu0zxwQudnOHBCmmrAFEKudzxwQvoqwBRDi1K4FENuvrwUQzN-uBRCJ6K4FELvZzhwQgo_PHBCc188cENzrzxwQi-nPHBDi6M8cEM3RsQUQvaaAExD_qoATEJCpgBMQp6vOHCpAQ0FNU0toVWhvTDJ3RE5Ia0JzZVVFclRRNWd1UDlBNjhfdzYxekFhSFRES2dyQVFEekl3Ri1Xdk10d1lkQnc9PTAA',
                            'coldConfigData': 'CLLXk8YGEPG6rQUQvbauBRDi1K4FEL6KsAUQ5JWwBRDxnLAFEJ3QsAUQz9KwBRDj-LAFEKS-sQUQ18GxBRCvp84cEKerzhwQ_LLOHBDL4s4cEJnozhwQq53PHBDyts8cEJHBzxwQtcbPHBDsxs8cEPjGzxwQmcrPHBClys8cENvTzxwQnNfPHBCD2s8cEM_ezxwQz-DPHBCy4c8cEIzozxwQjujPHBCL6c8cENzrzxwQk_LPHBDM888cEPLzzxwQ1PbPHBDx9s8cEMb3zxwQmPnPHBoyQU9qRm94MEVjeGFZcUR0OXVCWmpMS0h2ZVE1eHljWU1jUEtWbXlqVnZTcWx2NGc3QmciMkFPakZveDNJRVZJUXg2b1Qzb20xQmpTRmY2eUlKUjlyMjkzWDYtOXFSYWpWeW9CcDhnKogBQ0FNU1lnMGd1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2d0RuRFBrTzdnQVVxeDNhRWY0anB3MjJBODBKRlRDWnNiY2ZoYVFGa1p3RnVJQUNCS1hTQnFHb0JKT05CWkI3ODRnR3lGcV9SYmdMdmNBR01yY29rTjhHMmFRR0E2S3lCZlV2azVjRw%3D%3D',
                            'coldHashData': 'CLLXk8YGEhQxMzgxNDI3MDAyMzMzMzAyNjc4MBiy15PGBjIyQU9qRm94MEVjeGFZcUR0OXVCWmpMS0h2ZVE1eHljWU1jUEtWbXlqVnZTcWx2NGc3Qmc6MkFPakZveDNJRVZJUXg2b1Qzb20xQmpTRmY2eUlKUjlyMjkzWDYtOXFSYWpWeW9CcDhnQogBQ0FNU1lnMGd1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2d0RuRFBrTzdnQVVxeDNhRWY0anB3MjJBODBKRlRDWnNiY2ZoYVFGa1p3RnVJQUNCS1hTQnFHb0JKT05CWkI3ODRnR3lGcV9SYmdMdmNBR01yY29rTjhHMmFRR0E2S3lCZlV2azVjRw%3D%3D',
                            'hotHashData': 'CLLXk8YGEhQxMzM2MDgwNjA5MDE3OTY3OTU5NBiy15PGBiiU5PwSKKXQ_RIonpH-Eii36v4SKOft_hIowIP_EiiRjP8SKM3z_xIox4CAEyiLgoATKPeQgBMotZuAEyiGnoATKIOkgBMopKaAEyi9poATKO-ngBMo7aiAEyiQqYATKO2qgBMo8qqAEyj_qoATKMyrgBMyMkFPakZveDBFY3hhWXFEdDl1QlpqTEtIdmVRNXh5Y1lNY1BLVm15alZ2U3FsdjRnN0JnOjJBT2pGb3gzSUVWSVF4Nm9UM29tMUJqU0ZmNnlJSlI5cjI5M1g2LTlxUmFqVnlvQnA4Z0I0Q0FNU0lRMEtvdGY2RmE3QkJwTk44Z3E1QkJVWDNjX0NETWFuN1F2WXpRbWx3QVhXVnc9PQ%3D%3D',
                        },
                        'screenDensityFloat': 1.125,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '139.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUwT1RReE9EQXlOVEk1TWpreU56TXlOQT09ELLXk8YGGLLXk8YG',
                        'rolloutToken': 'CNvQvZylr87SKhCRp6KskbSLAxivwMKxydOPAw%3D%3D',
                        'screenWidthPoints': 892,
                        'screenHeightPoints': 811,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': url,
                            'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'consistencyTokenJars': [
                            {
                            },
                        ],
                        'internalExperimentFlags': [],
                    },
                    'clickTracking': {
                        'clickTrackingParams': tokens2[0],
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1757735859969',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '0',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '6',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '811',
                            },
                            {
                                'key': 'biw',
                                'value': '892',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,892,811',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                        'bid': 'ANyPxKo7J2itnYt9dq6Kr9dyg0SgBuo8fHj351uYoa81n1kefn0IG71BAYzkeCwpbvEhZ80z28gL',
                    },
                },
                'continuation': tokens[0],
            }
            try:
                response = requests.post('https://www.youtube.com/youtubei/v1/browse', params=params, headers=headers, json=json_data)
                pattern = r'"createCommentParams"\s*:\s*"([^"]+)"'
                match3 = re.search(pattern, response.text)
                if match3:
                    createCommentParams = match3.group(1)

                else:
                    return False
            except KeyboardInterrupt:
                sys.exit(0)    
            except Exception as e:
                print(e)
            json_data2 = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:2f05:1827:2c39:8420:284:74a4',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': 'Cgt5dXpraW1JNGpwbyiC_o_GBjIKCgJWThIEGgAgXw%3D%3D',
                        'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36,gzip(gfe)',
                        'clientName': 'WEB',
                        'clientVersion': '2.20250910.00.00',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': url,
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'CIL-j8YGEIqCgBMQndfPHBDnr88cEOLozxwQq_jOHBDh6c8cELfgrgUQ18GxBRDM364FEN7pzxwQuOTOHBCJ6K4FENPhrwUQ7aiAExDo5M8cEParsAUQ8OPPHBC9tq4FELnZzhwQyfevBRDv3M8cEJi5zxwQ3rzOHBCrnc8cELfq_hIQgo_PHBCp988cEJPyzxwQxcPPHBCL988cEIHNzhwQ_LLOHBCF588cEI3MsAUQntCwBRCu1s8cEIiHsAUQmZixBRDpiM8cEMvRsQUQxdbPHBC72c4cEIzpzxwQkYz_EhDF988cELOQzxwQibDOHBCHrM4cEM3RsQUQkcHPHBDa984cEL2KsAUQ4tSuBRD7tM8cENuvrwUQtauAExDgzbEFEL2ZsAUQlP6wBRCZjbEFEKaasAUQ7MbPHBC1288cEOnLzxwQ2e_PHBCf588cEO3CzxwQmNzPHCpIQ0FNU01SVXFvTDJ3RE5Ia0JyaVVFclBRNWd1UDlBNjhfdzYxekFhSFRES2dyQVFEaklVR3VJNEd2MG02QzRBVnk3Y0dIUWM9MAA%3D',
                            'coldConfigData': 'CIL-j8YGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQpL6xBRDXwbEFEK-nzhwQkbHOHBD2ss4cEPyyzhwQzeLOHBCvlM8cEKudzxwQ8rbPHBCRwc8cEO3CzxwQ7MbPHBD5xs8cEKXKzxwQ6cvPHBDb088cEJ3XzxwQn9fPHBCD2s8cEJjczxwQz97PHBDP4M8cELLhzxwQ3-LPHBDk4s8cEPzlzxwQjOjPHBCO6M8cEPTozxwQjOnPHBDZ788cEJPyzxwQ8vPPHBCG9s8cEKn3zxwQxffPHBoyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlEiMkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3KoQBQ0FNU1hRMGl1TjIzQXFRWmx4LW9LclVFc2hDRGhab1F2UURaRFBrTzdnQVVxeDNhRWY0anB3MjJBeFV6bWJHM0g0V2tCWkdjQmJpQUFnU2wwZ2FocUFTVGpRV2ZlX1NJQnNoYXYwVzRDNzNBQmpLM0tKRGZCdG1rQmdPaXNnWDFMdz09',
                            'coldHashData': 'CIL-j8YGEhMzNzUyMjgxMzUyMDk5NjIyMjQxGIL-j8YGMjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUToyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHdChAFDQU1TWFEwaXVOMjNBcVFabHgtb0tyVUVzaENEaFpvUXZRRFpEUGtPN2dBVXF4M2FFZjRqcHcyMkF4VXptYkczSDRXa0JaR2NCYmlBQWdTbDBnYWhxQVNUalFXZmVfU0lCc2hhdjBXNEM3M0FCakszS0pEZkJ0bWtCZ09pc2dYMUx3PT0%3D',
                            'hotHashData': 'CIL-j8YGEhQxMzM2MDgwNjA5MDE3OTY3OTU5NBiC_o_GBiiU5PwSKKXQ_RIo2pn-EijIyv4SKLfq_hIowYP_EiiRjP8SKMeAgBMoioKAEyj3kIATKOWUgBMotZuAEyiEpIATKKSmgBMo76eAEyjtqIATKPKqgBMolKuAEzIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QjRDQU1TSVEwS290ZjZGYTdCQnBOTjhncTVCQlVYM2NfQ0RNYW43UXZZelFtbHdBWFdWdz09',
                        },
                        'screenDensityFloat': 1.25,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '139.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUwT1RFMU56YzROVFExTmpFMk1EZzVOZz09EIL-j8YGGIL-j8YG',
                        'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMYrv_l24nTjwM%3D',
                        'screenWidthPoints': 770,
                        'screenHeightPoints': 730,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': url,
                            'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'internalExperimentFlags': [],
                        'consistencyTokenJars': [],
                    },
                    'clientScreenNonce': _make_client_nonce(),
                    'clickTracking': {
                        'clickTrackingParams': clickTrackingParams,
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1757675266534',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '0',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '3',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '730',
                            },
                            {
                                'key': 'biw',
                                'value': '755',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,770,730',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                        'bid': 'ANyPxKq1ZROqr6EzEq-GWVr5hzIhMBuJrkmDEoLQC2x5cXGfTDwY6WwiHF_y1ZyGaH3IaXVIQLETizTwCWhQagyNRzJb2N9eng',
                    },
                },
                'createCommentParams': createCommentParams,
                'commentText': cmt,
            }
            try:
                response = requests.post(
                    'https://www.youtube.com/youtubei/v1/comment/create_comment',
                    params=params,
                    headers=headers,
                    json=json_data2,
                )
                if response.status_code ==200:
                    return True
                else:
                    return False
            except KeyboardInterrupt:
                sys.exit(0)    
            except Exception as e:
                print(e)
        else:
            headers = {
                'accept': '*/*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'authorization': _get_sapisidhash(self.cookies),
                'content-type': 'application/json',
                'origin': 'https://www.youtube.com',
                'priority': 'u=1, i',
                'referer': url,
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
                'user-agent': self.user_agent,
                'x-browser-channel': 'stable',
                'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
                'x-browser-validation': self.x_browser_validation,
                'x-browser-year': str(self.current_year),
                'x-client-data': self.x_client_data,
                'x-goog-authuser': '0',
                'x-goog-visitor-id': self.x_goog_visitor_id,
                'x-origin': 'https://www.youtube.com',
                'x-youtube-bootstrap-logged-in': 'true',
                'x-youtube-client-name': '1',
                'x-youtube-client-version': '2.20250910.00.00',
                'cookie': self.cookies,
            }
            data = requests.get(url,headers=headers).text
            section_match = re.search(r'"sectionIdentifier":"sid-wn-chips".{0,5000}', data,re.S)
            if not section_match:
                return False
            section_text = section_match.group(0)
            section_match2 = r'"liveChatRenderer".*?"continuation":"([^"]+)"'
            match = re.search(r'"clickTrackingParams"\s*:\s*"([^"]+)"', section_text)
            if match:
                clickTrackingParams =  match.group(1)
            else:
                return False
            matches = re.findall(section_match2, data)
            if matches:
                tokens = [item for item in matches if item.startswith("0of")]
            params = {
                'continuation': tokens[0],
                'dark_theme': 'true',
                'authuser': '0',
            }
            try:
                response = requests.get('https://www.youtube.com/live_chat', params=params, headers=headers)
                if response.status_code == 200:
                    pattern = r'"sendLiveChatMessageEndpoint"\s*:\s*{[^}]*"params":"([^"]+)"[^}]*"clickTrackingParams":"([^"]+)"'
                    match = re.search(pattern, response.text, re.S)
                    if match:
                        paramsID = match.group(1)
                        click = match.group(2)
                    else:
                        return False
                    pmatches = re.findall(r'"addChatItemAction"\s*:\s*{[\s\S]*?"clientId"\s*:\s*"([^"]+)"', response.text, re.S)
                    if pmatches:
                        clientId = [item for item in pmatches if item.startswith("CO")]
                    else:
                        return False
                    
                else:
                    return False
            
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(e)
            params = {
                'prettyPrint': 'false',
            }

            json_data = {
                'context': {
                    'client': {
                        'hl': 'en',
                        'gl': 'VN',
                        'remoteHost': '2401:d800:b4:f83d:d86f:59:a8d5:c49a',
                        'deviceMake': '',
                        'deviceModel': '',
                        'visitorData': self.x_goog_visitor_id,
                        'userAgent': self.user_agent,
                        'clientName': 'WEB',
                        'clientVersion': '2.20250927.00.01',
                        'osName': 'Windows',
                        'osVersion': '10.0',
                        'originalUrl': f'https://www.youtube.com/live_chat?continuation={tokens[0]}&dark_theme=true&authuser=0',
                        'screenPixelDensity': 1,
                        'platform': 'DESKTOP',
                        'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                        'configInfo': {
                            'appInstallData': 'CKyN-sYGEKudzxwQq_jOHBCD588cEL76zxwQieiuBRC35M8cEMXDzxwQppqwBRDJ968FELOQzxwQxPTPHBCIh7AFEN7pzxwQqejPHBCV988cEIv3zxwQ-v_PHBC72c4cEPyyzhwQh6zOHBCRjP8SEK_4zxwQgo_PHBDEgtAcEMzfrgUQmLnPHBC9irAFEK7WzxwQtquAExCBzc4cEParsAUQmZixBRDm4M8cELjkzhwQqYbQHBDa984cEIzpzxwQjcywBRC36v4SEM3RsQUQ4M2xBRDT4a8FEJSD0BwQibDOHBDXwbEFEOLUrgUQovvPHBCU_rAFEL6pgBMQlPLPHBDevM4cEMvRsQUQvbauBRDy6M8cENDWzxwQmY2xBRCwg9AcEOevzxwQre_PHBD7tM8cEMfqzxwQ-YnQHBCe0LAFEL2ZsAUQ4enPHBCW288cEPiqgBMQpvnPHBCB988cEJ3XzxwQudnOHBDtws8cEJ_nzxwQj4LQHBDpy88cEJOI0BwqSENBTVNNUlVxLVpxLURMaVVFdkFFdTlUbUM4UHNGTFhNQm9kTU1xQ3NCQVBMdmdYeUs0QVZrRlBoTnNvdG1pR0NPS2czSFFjPTAA',
                        },
                        'screenDensityFloat': 1.125,
                        'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                        'timeZone': 'Asia/Bangkok',
                        'browserName': 'Chrome',
                        'browserVersion': '140.0.0.0',
                        'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'deviceExperimentId': 'ChxOelUxTmpZeU5USTVPVFEyTWpVd05qTXhPUT09EKyN-sYGGKyN-sYG',
                        'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMYiMyQ2c2FkAM%3D',
                        'screenWidthPoints': 400,
                        'screenHeightPoints': 595,
                        'utcOffsetMinutes': 420,
                        'connectionType': 'CONN_CELLULAR_4G',
                        'memoryTotalKbytes': '8000000',
                        'mainAppWebInfo': {
                            'graftUrl': f'https://www.youtube.com/live_chat?continuation={tokens[0]}&dark_theme=true&authuser=0',
                            'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                            'isWebNativeShareAvailable': True,
                        },
                    },
                    'user': {
                        'lockedSafetyMode': False,
                    },
                    'request': {
                        'useSsl': True,
                        'internalExperimentFlags': [],
                        'consistencyTokenJars': [],
                    },
                    'clickTracking': {
                        'clickTrackingParams': click,
                    },
                    'adSignalsInfo': {
                        'params': [
                            {
                                'key': 'dt',
                                'value': '1759413933226',
                            },
                            {
                                'key': 'flash',
                                'value': '0',
                            },
                            {
                                'key': 'frm',
                                'value': '1',
                            },
                            {
                                'key': 'u_tz',
                                'value': '420',
                            },
                            {
                                'key': 'u_his',
                                'value': '3',
                            },
                            {
                                'key': 'u_h',
                                'value': '864',
                            },
                            {
                                'key': 'u_w',
                                'value': '1536',
                            },
                            {
                                'key': 'u_ah',
                                'value': '816',
                            },
                            {
                                'key': 'u_aw',
                                'value': '1536',
                            },
                            {
                                'key': 'u_cd',
                                'value': '24',
                            },
                            {
                                'key': 'bc',
                                'value': '31',
                            },
                            {
                                'key': 'bih',
                                'value': '811',
                            },
                            {
                                'key': 'biw',
                                'value': '1280',
                            },
                            {
                                'key': 'brdim',
                                'value': '0,0,0,0,1536,0,1536,816,400,595',
                            },
                            {
                                'key': 'vis',
                                'value': '1',
                            },
                            {
                                'key': 'wgl',
                                'value': 'true',
                            },
                            {
                                'key': 'ca_type',
                                'value': 'image',
                            },
                        ],
                    },
                },
                'params': paramsID,
                'clientMessageId': clientId[0],
                'richMessage': {
                    'textSegments': [
                        {
                            'text': cmt,
                        },
                    ],
                },
            }
            try:
                response = requests.post(
                    'https://www.youtube.com/youtubei/v1/live_chat/send_message',params=params,headers=headers,json=json_data,)
                if response.status_code == 200:
                    return True
                else:
                    return False
            except KeyboardInterrupt:
                sys.exit(0)
            except Exception as e:
                print(e)
    def Like(self,url:str):
        headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'authorization': _get_sapisidhash(self.cookies),
            'content-type': 'application/json',
            'device-memory': '8',
            'origin': 'https://www.youtube.com',
            'priority': 'u=1, i',
            'referer': url,
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"140.0.7339.210"',
            'sec-ch-ua-full-version-list': '"Chromium";v="140.0.7339.210", "Not=A?Brand";v="24.0.0.0", "Google Chrome";v="140.0.7339.210"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
            'x-browser-channel': 'stable',
            'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
            'x-browser-validation': self.x_browser_validation,
            'x-browser-year': str(self.current_year),
            'x-client-data': self.x_client_data,
            'x-goog-authuser': '0',
            'x-goog-visitor-id': self.x_goog_visitor_id,
            'x-origin': 'https://www.youtube.com',
            'x-youtube-bootstrap-logged-in': 'true',
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20251006.01.00',
            'cookie': self.cookies
        }
        try:
            r = requests.get(url,headers=headers)
            if r.status_code == 200:
                pattern = r'"innertubeCommand"\s*:\s*{\s*"clickTrackingParams"\s*:\s*"([A-Za-z0-9+/=]+)"[^}]+?"apiUrl"\s*:\s*"/youtubei/v1/like/like"'
                match = re.search(pattern, r.text, re.DOTALL)
                if match:
                    clickTrackingParams =  match.group(1)
                else:
                    raise ValueError("Do not find the clickTrackingParams")
                pattern1 = r'"likeEndpoint"\s*:\s*{\s*"status"\s*:\s*"LIKE".*?"likeParams"\s*:\s*"([^"]+)"'
                match2 = re.search(pattern1, r.text, re.DOTALL)

                if match2:
                    likeParams = match2.group(1)
                else:
                    raise ValueError("Do not find likeParams")
                params = {
                    'prettyPrint': 'false',
                }
                match_videoId = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)", url)
                json_data = {
                    'context': {
                        'client': {
                            'hl': 'en',
                            'gl': 'VN',
                            'remoteHost': '2401:d800:d2:406c:1c23:3b4a:ecad:ed3f',
                            'deviceMake': '',
                            'deviceModel': '',
                            'visitorData': self.x_goog_visitor_id,
                            'userAgent': self.user_agent,
                            'clientName': 'WEB',
                            'clientVersion': '2.20251006.01.00',
                            'osName': 'Windows',
                            'osVersion': '10.0',
                            'originalUrl': 'https://www.youtube.com/',
                            'screenPixelDensity': 1,
                            'platform': 'DESKTOP',
                            'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                            'configInfo': {
                                'appInstallData': 'CPmolMcGEL22rgUQntCwBRCZmLEFEIiHsAUQndfPHBDU688cEODpzxwQg-fPHBD2q7AFEK7WzxwQ8ejPHBDa984cENPhrwUQyfevBRDi1K4FEKnozxwQpvnPHBDFw88cEI3MsAUQ3rzOHBD8ss4cENDWzxwQy9GxBRDm4M8cEJuI0BwQi_fPHBC52c4cEJmNsQUQxPTPHBCmmrAFEIH3zxwQt-TPHBCCj88cEM3RsQUQ96qAExCU_rAFEKudzxwQre_PHBD7tM8cEJSD0BwQu9nOHBCBzc4cEKv4zhwQh6zOHBDZjdAcEImwzhwQxILQHBCv-M8cEMzfrgUQmLnPHBC--s8cEPr_zxwQlLGAExC36v4SEL6pgBMQtquAExCJ6K4FEJX3zxwQlPLPHBCzkM8cEJGM_xIQuOTOHBC9mbAFEODNsQUQvYqwBRC-idAcENjGzxwQjOnPHBDe6c8cENfBsQUQltvPHBCphtAcEJ_nzxwQ7cLPHBCDjdAcEI-C0BwQk4jQHCpIQ0FNU01SVXEtWnEtRExpVUV2d0V2OVRtQzhQc0ZMWE1Cb2RNTXFDc0JBUEx2Z1h5SzRBVmtGUGhOc290cEdMMkRyb2hIUWM9MAA%3D',
                                'coldConfigData': 'CPmolMcGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQ18GxBRCvp84cEJGxzhwQ9rLOHBD8ss4cEM3izhwQr5TPHBCrnc8cEOy2zxwQ573PHBDtws8cENjGzxwQ-cbPHBDb088cEJ3XzxwQn9fPHBDH2s8cEM_gzxwQt-TPHBDQ5c8cEPzlzxwQg-fPHBCp6M8cEPHozxwQr_PPHBDy9s8cEKb5zxwQz_zPHBD7_M8cEKb-zxwQ4v7PHBDo_s8cEOn-zxwQ-v_PHBCUg9AcENWD0BwQk4jQHBCbiNAcEL6J0BwQg43QHBDZjdAcGjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUSIyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHcqeENBTVNWZzBtdU4yM0FxUVpseC1mVDRPRm1oQzlBTmtNLVE3dUFCU05OdjRqcHczYUNab0RGVGFac2JjZmhhUUZrWndGNGRzQm9hZ0VrNDBGbjN2MGlBYklXcjlGdUF1OXdBWXl6NEFGMmFRR0E2S3lCYnVRQnN3bQ%3D%3D',
                                'coldHashData': 'CPmolMcGEhMyMzQzMTg5NzY5MzM1ODE5OTEyGPmolMcGMjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUToyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHdCeENBTVNWZzBtdU4yM0FxUVpseC1mVDRPRm1oQzlBTmtNLVE3dUFCU05OdjRqcHczYUNab0RGVGFac2JjZmhhUUZrWndGNGRzQm9hZ0VrNDBGbjN2MGlBYklXcjlGdUF1OXdBWXl6NEFGMmFRR0E2S3lCYnVRQnN3bQ%3D%3D',
                                'hotHashData': 'CPmolMcGEhM4Mjk5MjUyMDc1NDgzMjQ5MTIzGPmolMcGKJTk_BIopdD9Eijamf4SKMjK_hIot-r-EiiRjP8SKMeAgBMo95CAEyjLkYATKOWUgBMotZuAEyippIATKL6pgBMo26qAEyj3qoATKJusgBMo2LCAEyiUsYATMjJBT2pGb3gxbU9VZGZjYkxYblhYSDJsTE1XWmR1YjVwZ1lmb2pVZ1VwWndyMHJyUHJSUToyQU9qRm94Mk40YUNpSnpDYzBFM2FKZUNvUGZZcTVQQUo4Ri1hRkk1YkozM1FpY25qTHdCOENBTVNKZzBJb3RmNkZhN0JCcE5OOGdxNUJOb19GUlRkejhJTTJPc1A1clRtQzlqTkNhWEFCZFpY',
                            },
                            'screenDensityFloat': 1.125,
                            'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                            'timeZone': 'Asia/Bangkok',
                            'browserName': 'Chrome',
                            'browserVersion': '140.0.0.0',
                            'memoryTotalKbytes': '8000000',
                            'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'deviceExperimentId': 'ChxOelUxT0RRM01EQTFPVFUzTURJek9UQXlNQT09EPmolMcGGPmolMcG',
                            'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMY852Y3ZeSkAM%3D',
                            'screenWidthPoints': 812,
                            'screenHeightPoints': 811,
                            'utcOffsetMinutes': 420,
                            'connectionType': 'CONN_CELLULAR_4G',
                            'mainAppWebInfo': {
                                'graftUrl': url,
                                'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                                'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                                'isWebNativeShareAvailable': True,
                            },
                        },
                        'user': {
                            'lockedSafetyMode': False,
                        },
                        'request': {
                            'useSsl': True,
                            'internalExperimentFlags': [],
                            'consistencyTokenJars': [],
                        },
                        'clickTracking': {
                            'clickTrackingParams': clickTrackingParams,
                        },
                        'adSignalsInfo': {
                            'params': [
                                {
                                    'key': 'dt',
                                    'value': '1759843455914',
                                },
                                {
                                    'key': 'flash',
                                    'value': '0',
                                },
                                {
                                    'key': 'frm',
                                    'value': '0',
                                },
                                {
                                    'key': 'u_tz',
                                    'value': '420',
                                },
                                {
                                    'key': 'u_his',
                                    'value': '3',
                                },
                                {
                                    'key': 'u_h',
                                    'value': '864',
                                },
                                {
                                    'key': 'u_w',
                                    'value': '1536',
                                },
                                {
                                    'key': 'u_ah',
                                    'value': '816',
                                },
                                {
                                    'key': 'u_aw',
                                    'value': '1536',
                                },
                                {
                                    'key': 'u_cd',
                                    'value': '24',
                                },
                                {
                                    'key': 'bc',
                                    'value': '31',
                                },
                                {
                                    'key': 'bih',
                                    'value': '811',
                                },
                                {
                                    'key': 'biw',
                                    'value': '795',
                                },
                                {
                                    'key': 'brdim',
                                    'value': '0,0,0,0,1536,0,1536,816,812,811',
                                },
                                {
                                    'key': 'vis',
                                    'value': '1',
                                },
                                {
                                    'key': 'wgl',
                                    'value': 'true',
                                },
                                {
                                    'key': 'ca_type',
                                    'value': 'image',
                                },
                            ],
                            'bid': 'ANyPxKoT1orJsKgUa1Qt16wyIkiV74J1it8Y-SqrX6Wdjg6DfZ0Y6YHXERh6B2u8FmVFlruBfnE3NNuk0bCOksbsW5RIbOm1eA',
                        },
                    },
                    'target': {
                        
                        'videoId': match_videoId.group(1),
                    },
                    'params': likeParams,
                }

                response = requests.post(
                    'https://www.youtube.com/youtubei/v1/like/like',
                    params=params,
                    headers=headers,
                    json=json_data,
                )
                if response.status_code == 200:
                    return True
                else:
                    return False
            else:
                return False
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(e)
    def Dislike(self,url):
        headers = {
            'accept': '*/*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'authorization': _get_sapisidhash(self.cookies),
            'content-type': 'application/json',
            'device-memory': '8',
            'origin': 'https://www.youtube.com',
            'priority': 'u=1, i',
            'referer': url,
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-form-factors': '"Desktop"',
            'sec-ch-ua-full-version': '"140.0.7339.210"',
            'sec-ch-ua-full-version-list': '"Chromium";v="140.0.7339.210", "Not=A?Brand";v="24.0.0.0", "Google Chrome";v="140.0.7339.210"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-ua-wow64': '?0',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'same-origin',
            'sec-fetch-site': 'same-origin',
            'user-agent': self.user_agent,
            'x-browser-channel': 'stable',
            'x-browser-copyright': f'Copyright {str(self.current_year)} Google LLC. All rights reserved.',
            'x-browser-validation': self.x_browser_validation,
            'x-browser-year': str(self.current_year),
            'x-client-data': self.x_client_data,
            'x-goog-authuser': '0',
            'x-goog-visitor-id': self.x_goog_visitor_id,
            'x-origin': 'https://www.youtube.com',
            'x-youtube-bootstrap-logged-in': 'true',
            'x-youtube-client-name': '1',
            'x-youtube-client-version': '2.20251006.01.00',
            'cookie': self.cookies
        }
        try:
            r = requests.get(url,headers=headers)
            if r.status_code == 200:
                pattern = r'"innertubeCommand"\s*:\s*{\s*"clickTrackingParams"\s*:\s*"([A-Za-z0-9+/=]+)"[^}]+?"apiUrl"\s*:\s*"/youtubei/v1/like/dislike"'
                match = re.search(pattern, r.text, re.DOTALL)
                if match:
                    clickTrackingParams =  match.group(1)
                else:
                    raise ValueError("Do not find the clickTrackingParams")
                pattern2 = r'"likeEndpoint"\s*:\s*{\s*"status"\s*:\s*"DISLIKE".*?"dislikeParams"\s*:\s*"([^"]+)"'
                match2 = re.search(pattern2, r.text, re.DOTALL)

                if match2:
                    dislikeparam = match2.group(1)
                else:
                    raise ValueError("Do not find likeParams")
                params = {
                    'prettyPrint': 'false',
                }
                match_videoId = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:\?|&|$)", url)
                json_data = {
                    'context': {
                        'client': {
                            'hl': 'en',
                            'gl': 'VN',
                            'remoteHost': '2401:d800:d2:406c:1c23:3b4a:ecad:ed3f',
                            'deviceMake': '',
                            'deviceModel': '',
                            'visitorData': self.x_goog_visitor_id,
                            'userAgent': self.user_agent,
                            'clientName': 'WEB',
                            'clientVersion': '2.20251006.01.00',
                            'osName': 'Windows',
                            'osVersion': '10.0',
                            'originalUrl': url,
                            'screenPixelDensity': 1,
                            'platform': 'DESKTOP',
                            'clientFormFactor': 'UNKNOWN_FORM_FACTOR',
                            'configInfo': {
                                'appInstallData': 'CIu0lMcGEM3RsQUQre_PHBDgzbEFEJuI0BwQgffPHBCrnc8cEJbbzxwQntCwBRC9mbAFEParsAUQu9nOHBC35M8cEIeszhwQ8ejPHBDE9M8cEK7WzxwQt-r-EhC-idAcELnZzhwQqYbQHBCUsYATELOQzxwQ2Y3QHBCZmLEFEODpzxwQieiuBRDJ968FEIPnzxwQtquAExDm4M8cEN68zhwQ0NbPHBD3qoATEJT-sAUQ-7TPHBC--s8cEOLUrgUQibDOHBD8ss4cEI3MsAUQ3unPHBDT4a8FEKnozxwQuOTOHBCBzc4cEKb5zxwQ8MzPHBC3yc8cEMzfrgUQ2vfOHBCV988cEJTyzxwQ4rjPHBDL0bEFEIv3zxwQvYqwBRCv-M8cEL6pgBMQjOnPHBD6_88cEKv4zhwQxILQHBC9tq4FEJGM_xIQgo_PHBDYxs8cEJi5zxwQ1OvPHBCIh7AFEKaasAUQmY2xBRCUg9AcENfBsQUQndfPHBDFw88cEION0BwQ7cLPHBCTiNAcEI-C0BwQn-fPHCpMQ0FNU014VW8tWnEtRExpVUV2d0V2OVRtQzhQc0ZMWE1Cb2RNTXFDc0JBUEx2Z1h5SzRBVmtGUGhOc290cEdMMkRyb2gyZ0lkQnc9PTAA',
                                'coldConfigData': 'CIu0lMcGEO-6rQUQvbauBRDi1K4FEL2KsAUQntCwBRDP0rAFEOP4sAUQ18GxBRCvp84cEJGxzhwQ9rLOHBD8ss4cEM3izhwQr5TPHBCrnc8cEOy2zxwQ4rjPHBDnvc8cEO3CzxwQ2MbPHBD5xs8cENvTzxwQndfPHBCf188cEMfazxwQz-DPHBC35M8cENDlzxwQ_OXPHBCD588cEKnozxwQ8ejPHBCa688cEK3vzxwQr_PPHBDy9s8cEIH3zxwQpvnPHBDP_M8cEPv8zxwQpv7PHBDi_s8cEOn-zxwQ-v_PHBDEgtAcEJSD0BwQ1YPQHBDZhtAcEJOI0BwQm4jQHBoyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlEiMkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3KnhDQU1TVmcwbXVOMjNBcVFabHgtZlQ0T0ZtaEM5QU5rTS1RN3VBQlNOTnY0anB3M2FDWm9ERlRhWnNiY2ZoYVFGa1p3RjRkc0JvYWdFazQwRm4zdjBpQWJJV3I5RnVBdTl3QVl5ejRBRjJhUUdBNkt5QmJ1UUJzd20%3D',
                                'coldHashData': 'CIu0lMcGEhQxNTI4MDUwNjE5MDYxMTQ5MTE5MhiLtJTHBjIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QnhDQU1TVmcwbXVOMjNBcVFabHgtZlQ0T0ZtaEM5QU5rTS1RN3VBQlNOTnY0anB3M2FDWm9ERlRhWnNiY2ZoYVFGa1p3RjRkc0JvYWdFazQwRm4zdjBpQWJJV3I5RnVBdTl3QVl5ejRBRjJhUUdBNkt5QmJ1UUJzd20%3D',
                                'hotHashData': 'CIu0lMcGEhM4Mjk5MjUyMDc1NDgzMjQ5MTIzGIu0lMcGKJTk_BIopdD9Eijamf4SKMjK_hIot-r-EiiRjP8SKMeAgBMo95CAEyjllIATKLWbgBMoqaSAEyi-qYATKNuqgBMo96qAEyibrIATKNiwgBMolLGAEzIyQU9qRm94MW1PVWRmY2JMWG5YWEgybExNV1pkdWI1cGdZZm9qVWdVcFp3cjByclByUlE6MkFPakZveDJONGFDaUp6Q2MwRTNhSmVDb1BmWXE1UEFKOEYtYUZJNWJKMzNRaWNuakx3QjhDQU1TSmcwSW90ZjZGYTdCQnBOTjhncTVCTm9fRlJUZHo4SU0yT3NQNXJUbUM5ak5DYVhBQmRaWA%3D%3D',
                            },
                            'screenDensityFloat': 1.125,
                            'userInterfaceTheme': 'USER_INTERFACE_THEME_DARK',
                            'timeZone': 'Asia/Bangkok',
                            'browserName': 'Chrome',
                            'browserVersion': '140.0.0.0',
                            'memoryTotalKbytes': '8000000',
                            'acceptHeader': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                            'deviceExperimentId': 'ChxOelUxT0RRM05qRTRORFkwTmpVMk9URXhPUT09EIu0lMcGGIu0lMcG',
                            'rolloutToken': 'CISt5qaP0dupzwEQ8MHc57G3jgMY852Y3ZeSkAM%3D',
                            'screenWidthPoints': 812,
                            'screenHeightPoints': 811,
                            'utcOffsetMinutes': 420,
                            'connectionType': 'CONN_CELLULAR_4G',
                            'mainAppWebInfo': {
                                'graftUrl': url,
                                'pwaInstallabilityStatus': 'PWA_INSTALLABILITY_STATUS_CAN_BE_INSTALLED',
                                'webDisplayMode': 'WEB_DISPLAY_MODE_BROWSER',
                                'isWebNativeShareAvailable': True,
                            },
                        },
                        'user': {
                            'lockedSafetyMode': False,
                        },
                        'request': {
                            'useSsl': True,
                            'consistencyTokenJars': [
                                {
                                   
                                },
                            ],
                            'internalExperimentFlags': [],
                        },
                        'clickTracking': {
                            'clickTrackingParams': clickTrackingParams,
                        },
                        'adSignalsInfo': {
                            'params': [
                                {
                                    'key': 'dt',
                                    'value': '1759844878205',
                                },
                                {
                                    'key': 'flash',
                                    'value': '0',
                                },
                                {
                                    'key': 'frm',
                                    'value': '0',
                                },
                                {
                                    'key': 'u_tz',
                                    'value': '420',
                                },
                                {
                                    'key': 'u_his',
                                    'value': '3',
                                },
                                {
                                    'key': 'u_h',
                                    'value': '864',
                                },
                                {
                                    'key': 'u_w',
                                    'value': '1536',
                                },
                                {
                                    'key': 'u_ah',
                                    'value': '816',
                                },
                                {
                                    'key': 'u_aw',
                                    'value': '1536',
                                },
                                {
                                    'key': 'u_cd',
                                    'value': '24',
                                },
                                {
                                    'key': 'bc',
                                    'value': '31',
                                },
                                {
                                    'key': 'bih',
                                    'value': '811',
                                },
                                {
                                    'key': 'biw',
                                    'value': '795',
                                },
                                {
                                    'key': 'brdim',
                                    'value': '0,0,0,0,1536,0,1536,816,812,811',
                                },
                                {
                                    'key': 'vis',
                                    'value': '1',
                                },
                                {
                                    'key': 'wgl',
                                    'value': 'true',
                                },
                                {
                                    'key': 'ca_type',
                                    'value': 'image',
                                },
                            ],
                            'bid': 'ANyPxKoIH2jTMYqEMyaPo8FNstfMMrZCx2_u93VarBwKLa3Mih5PQ95cA00ryHi5UzKIFZgjdroFHqZKo4VROQGv4ooDxLIOzg',
                        },
                    },
                    'target': {
                        'videoId': match_videoId.group(0),
                    },
                    'params': dislikeparam,
                }

                response = requests.post(
                    'https://www.youtube.com/youtubei/v1/like/dislike',
                    params=params,
                    headers=headers,
                    json=json_data,
                )

                if response.status_code == 200:
                    return True
                else:
                    return False
            else:
                return False
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(e)
    def Rotate_cookies(self):
        new_cookies = _Rotate_cookies(self.cookies,self.x_browser_validation,self.x_client_data,self.user_agent)
        return new_cookies
