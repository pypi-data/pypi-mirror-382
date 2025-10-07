
import requests
from user_agent import generate_user_agent
from hashlib import md5
import random
from bs4 import BeautifulSoup
import pycountry
import time
from datetime import datetime
from secrets import token_hex
from uuid import uuid4
from mnemonic import Mnemonic
from time import sleep

API_RanaGPT = "http://sii3.moayman.top"

MODELS_DEEP_INFRA = [
    "deepseekv3", "innova", "aicode", "Image4o","deepseekv3x", "deepseekr1", "deepseekr1base",
    "deepseekr1turbo", "deepseekr1llama", "deepseekr1qwen",
    "deepseekprover", "qwen235", "qwen30", "qwen32", "qwen14",
    "mav", "scout", "phi-plus", "guard", "qwq", "gemma27",
    "gemma12", "llama31", "llama332", "llama337", "mixtral24",
    "phi4", "phi-multi", "wizard822", "wizard27", "qwen2572",
    "qwen272", "dolphin26", "dolphin29", "airo70", "lzlv70",
    "mixtral822"
]

MODELS_31 = [
    "grok", "grok-2", "grok-2-1212", "grok-2-mini", "openai",
    "evil", "gpt-4o-mini", "gpt-4-1-nano", "gpt-4", "gpt-4o",
    "gpt-4-1", "gpt-4-1-mini", "o4-mini", "command-r-plus",
    "gemini-2-5-flash", "gemini-2-0-flash-thinking",
    "qwen-2-5-coder-32b", "llama-3-3-70b", "llama-4-scout",
    "llama-4-scout-17b", "mistral-small-3-1-24b",
    "deepseek-r1", "deepseek-r1-distill-llama-70b",
    "deepseek-r1-distill-qwen-32b", "phi-4", "qwq-32b",
    "deepseek-v3", "deepseek-v3-0324", "openai-large",
    "openai-reasoning", "searchgpt"
]

MODELS_BLACKBOX = [
    "blackbox", "gpt-4-1", "gpt-4-1-n", "gpt-4", "gpt-4o",
    "gpt-4o-m", "python", "html", "builder", "java", "js",
    "react", "android", "flutter", "nextjs", "angularjs",
    "swift", "mongodb", "pytorch", "xcode", "azure",
    "bitbucket", "digitalocean", "docker", "electron",
    "erlang", "fastapi", "firebase", "flask", "git",
    "gitlab", "go", "godot", "googlecloud", "heroku"
]

VOICES = ["alloy", "coral", "echo", "shimmer", "verse", "onyx"]
STYLES = ["friendly", "calm", "noir_detective", "cowboy"]


class VoiceAi:
    @staticmethod
    def openai(text: str, voice: str = "alloy", style: str = None, method: str = "GET") -> dict:
        if voice not in VOICES:
            return {
                "status": "Error",
                "error": f"This form '{voice}' does not exist. "
                         f"These are the supported forms for the provider: {VOICES}"
            }
        if style and style not in STYLES:
            return {
                "status": "Error",
                "error": f"This form '{style}' does not exist. "
                         f"These are the supported forms for the provider: {STYLES}"
            }

        params = {"text": text, "voice": voice}
        if style:
            params["style"] = style

        url = f"{API_RanaGPT}/Tofey/voice.php"
        resp = requests.post(url, data=params) if method.upper() == "POST" else requests.get(url, params=params)
        body = resp.text
        status = "ok" if "audio_url" in body else "Bad"
        return {"status": status, "result": body, "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return VOICES

    @staticmethod
    def styles() -> list:
        return STYLES


class TextAi:
    @staticmethod
    def DeepInfra(text: str, model: str) -> dict:
        if model not in MODELS_DEEP_INFRA:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_DEEP_INFRA}"
            }
        try:
            resp = requests.get(f"{API_RanaGPT}/api/DeepInfra.php", params={model: text})
            res = resp.json()
            if "response" in res:
                return {"status": "OK", "result": res["response"], "Tofey": "@qqxqqv"}
            else:
                return {"status": "Bad", "result": res, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return MODELS_DEEP_INFRA


class WormGpt:
    @staticmethod
    def DarkGPT(text: str) -> dict:
        res = requests.get(f"{API_RanaGPT}/Tofey/api2/Darkgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def Worm(text: str) -> dict:
        res = requests.get(f"{API_RanaGPT}/Tofey/api/wormgpt.php", params={"text": text}).json()
        return {"status": "OK", "result": res.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return []


class ModelDeepInfra:
    @staticmethod
    def models() -> list:
        return MODELS_DEEP_INFRA


class Model31:
    @staticmethod
    def Modl(text: str, model: str) -> dict:
        if model not in MODELS_31:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_31}"
            }
        return requests.get(f"{API_RanaGPT}/api/gpt.php", params={model: text}).json()

    @staticmethod
    def models() -> list:
        return MODELS_31


class BlackBox:
    @staticmethod
    def Models(text: str, model: str) -> dict:
        if model not in MODELS_BLACKBOX:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {MODELS_BLACKBOX}"
            }
        data = requests.get(f"{API_RanaGPT}/api/black.php", params={model: text}).json()
        return {"status": "OK", "result": data.get("response"), "Tofey": "@qqxqqv"}

    @staticmethod
    def models() -> list:
        return MODELS_BLACKBOX


class Developers:
    @staticmethod
    def Tofey() -> str:
        return (
            "Name ➝ ➞ #Tofey\n\n"
            "My user = @qqxqqv\n\n"
            "ʀᴀɴᴅᴏᴍ ǫᴜᴏᴛᴇ ➛ ➜ ➝\n"
            "    ˛ I have you, that's all I need 𓍲 ."
        )

    @staticmethod
    def models() -> list:
        return []


class ImageAi:
    SUPPORTED_MODELS = [
        "fluex-pro", "flux", "schnell", "imger-12", "deepseek",
        "gemini-2-5-pro", "blackbox", "redux", "RanaGPT-7-i",
        "r1", "gpt-4-1"
    ]

    @staticmethod
    def generate(prompt: str, model: str = "RanaGPT-7-i") -> dict:
        if model not in ImageAi.SUPPORTED_MODELS:
            return {
                "status": "Error",
                "error": f"This form '{model}' does not exist. "
                         f"These are the supported forms for the provider: {ImageAi.SUPPORTED_MODELS}"
            }
        resp = requests.get(f"{API_RanaGPT}/api/img.php", params={model: prompt})
        try:
            return resp.json()
        except:
            return {"status": "OK", "result": resp.text}

    @staticmethod
    def models() -> list:
        return ImageAi.SUPPORTED_MODELS


class ChatAi:
    @staticmethod
    def ask(prompt: str) -> dict:
        return requests.get(f"{API_RanaGPT}/api/chat/gpt-3.5.php", params={"ai": prompt}).json()

    @staticmethod
    def models() -> list:
        return []


class AzkarApi:
    @staticmethod
    def today() -> dict:
        try:
            return requests.get(f"{API_RanaGPT}/api/azkar.php").json()
        except:
            return {"status": "OK", "result": ""}

    @staticmethod
    def models() -> list:
        return []


class DeepSeekT1:
    @staticmethod
    def codeify(text: str) -> dict:
        url = f"{API_RanaGPT}/api/DeepSeek/DeepSeek.php"
        resp = requests.get(url, params={"text": text})
        body = resp.text
        try:
            data = resp.json()

            if isinstance(data, dict):
                if "result" in data:
                    return {"status": "OK", "result": data["result"]}
                if "response" in data:
                    return {"status": "OK", "result": data["response"]}

            return {"status": "OK", "result": str(data)}
        except ValueError:

            return {"status": "OK", "result": body}

    @staticmethod
    def models() -> list:
        return []


class GeminiApi:
    @staticmethod
    def ask(prompt: str) -> dict:
        try:
            return requests.get(f"{API_RanaGPT}/Tofey/gemini.php", params={"text": prompt}).json()
        except:
            return {"status": "OK", "result": ""}

    @staticmethod
    def models() -> list:
        return []


def innova(prompt):
    url = "https://tofey.serv00.net/api/chatgpt3.5.php"
    params = {"text": prompt}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response found.")
    except Exception as e:
        return f"Error: {e}"
        
        
def aicode(prompt):
    url = "https://tofey.serv00.net/api/aicode.php"
    params = {"text": prompt}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {e}"
        

import requests

class Image4o:
    @staticmethod
    def generate(prompt: str):
        try:
            url = "http://185.158.132.66:2010/api/tnt/tnt-black-image"
            params = {"text": prompt}
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            print("Raw API response:", data)
            if "الصور" in data:
                return data["الصور"]
            elif "images" in data:
                return data["images"]
            else:
                return data
        except Exception as e:
            return {"status": "Error", "message": str(e)}


import requests

class simongpt:
    @staticmethod
    def generate(prompt: str):
        try:
            url = "https://tofey.serv00.net/ai.php"
            params = {"text": prompt}
            resp = requests.get(url, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            print("Raw API response:", data)
            if "الصور" in data:
                return data["الصور"]
            elif "images" in data:
                return data["images"]
            else:
                return data
        except Exception as e:
            return {"status": "Error", "message": str(e)}
            
            
import requests

class SusanGPT:
    @staticmethod
    def edit(txt: str, url: str):
        try:
            api = f"https://api.dfkz.xo.je/apis/v2/gemini-img.php?text={requests.utils.quote(txt)}&link={requests.utils.quote(url)}"
            res = requests.get(api, timeout=1000).json()
            
            if "image" in res:
                return {"status": "OK", "result": res["image"]}
            elif "url" in res:
                return {"status": "OK", "result": res["url"]}
            else:
                return {"status": "OK", "result": res}
        except Exception as e:
            return {"status": "Error", "message": str(e)}
            
            
            
import requests

class download:
    @staticmethod
    def get(url: str) -> dict:
        try:
            api_url = f"https://sii3.moayman.top/api/do.php"
            resp = requests.get(api_url, params={"url": url}, timeout=10000)
            resp.raise_for_status()
            data = resp.json()

            if "links" in data:
                return {
                    "status": "OK",
                    "title": data.get("title", ""),
                    "date": data.get("date", ""),
                    "links": data["links"],  
                    "dev": data.get("dev", "")
                }
            else:
                return {"status": "Bad", "result": data}

        except Exception as e:
            return {"status": "Error", "message": str(e)}
            
            
            
class Turkish:
    BASE_URL = "https://api.dfkz.xo.je/Turkish"

    @staticmethod
    def latest_series(page: int = 1) -> dict:
        """جلب آخر المسلسلات (50 مسلسل لكل صفحة)"""
        try:
            url = f"{Turkish.BASE_URL}/"
            if page != 1:
                url += f"?page={page}"
            resp = requests.get(url, timeout=1000)
            resp.raise_for_status()
            data = resp.json()
            return {"status": "OK", "result": data, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def episode_servers(episode_id: str) -> dict:
        """جلب سيرفرات الحلقة باستخدام ID الحلقة (من ep.php)"""
        try:
            resp = requests.get(
                f"{Turkish.BASE_URL}/ep.php",
                params={"id": episode_id},
                timeout=30
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "error" in data:
                return {"status": "Bad", "error": data["error"], "Tofey": "@qqxqqv"}
            return {"status": "OK", "result": data, "Tofey": "@qqxqqv"}
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                return {
                    "status": "Error",
                    "error": "الخادم أعاد خطأ داخلي (500). تأكد من صحة الـ ID.",
                    "Tofey": "@qqxqqv"
                }
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def episode_servers_epid(episode_id: str) -> dict:
        """جلب سيرفرات الحلقة باستخدام ID الحلقة (من epid.php)"""
        try:
            url = f"{Turkish.BASE_URL}/epid.php"
            resp = requests.get(url, params={"id": episode_id}, timeout=1000)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "error" in data:
                return {"status": "Bad", "error": data["error"], "Tofey": "@qqxqqv"}
            return {"status": "OK", "result": data, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def latest_episodes(page: int = 1) -> dict:
        """جلب آخر الحلقات المضافة"""
        try:
            url = f"{Turkish.BASE_URL}/lastep.php"
            if page != 1:
                url += f"?page={page}"
            resp = requests.get(url, timeout=1000)
            resp.raise_for_status()
            data = resp.json()
            return {"status": "OK", "result": data, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}

    @staticmethod
    def search(query: str, page: int = 1) -> dict:
        """البحث عن مسلسل أو فيلم باستخدام كلمة مفتاحية"""
        try:
            url = f"{Turkish.BASE_URL}/search.php"
            params = {"q": query}
            if page != 1:
                params["page"] = page
            resp = requests.get(url, params=params, timeout=1000)
            resp.raise_for_status()
            data = resp.json()
            return {"status": "OK", "result": data, "Tofey": "@qqxqqv"}
        except Exception as e:
            return {"status": "Error", "error": str(e), "Tofey": "@qqxqqv"}
            
            
import requests

class VEO3:
    @staticmethod
    def generate(prompt: str, image_url: str):
        api_url = "https://tofey.serv00.net/api/veo3.php"

        try:
            # تجربة POST أولاً
            response = requests.post(api_url, data={"text": prompt, "link": image_url}, timeout=1000)
            if response.status_code == 1000 and response.text.strip():
                try:
                    res = response.json()
                    if "video" in res:
                        return {"status": "OK", "result": res["video"]}
                    elif "url" in res:
                        return {"status": "OK", "result": res["url"]}
                    elif "image" in res:
                        return {"status": "OK", "result": res["image"]}
                except ValueError:
                    # لو JSON غير صالح
                    pass

            # تجربة GET إذا POST فشل أو JSON غير صالح
            response = requests.get(f"{api_url}?text={requests.utils.quote(prompt)}&link={requests.utils.quote(image_url)}", timeout=1000)
            if response.status_code == 1000 and response.text.strip():
                try:
                    res = response.json()
                    if "video" in res:
                        return {"status": "OK", "result": res["video"]}
                    elif "url" in res:
                        return {"status": "OK", "result": res["url"]}
                    elif "image" in res:
                        return {"status": "OK", "result": res["image"]}
                except ValueError:
                    return {"status": "Error", "message": "Server returned invalid JSON"}

            return {"status": "Error", "message": "No valid response from server"}

        except Exception as e:
            return {"status": "Error", "message": str(e)}
            
            
import requests
import json

class xngpt:
    @staticmethod
    def generate(prompt: str, links: list = None):
        try:
            api_url = "https://tofey.serv00.net/api/gemini.php"
            data = {"text": prompt}

            if links:
                if isinstance(links, list):
                    links = ",".join(links[:10])
                data["links"] = links

            res = requests.post(api_url, data=data, timeout=10000)

            # لو الرد 200 → ناجح
            if res.status_code == 200:
                try:
                    decoded = res.json()  # حاول نفك JSON
                except Exception:
                    # لو JSON كسلسلة نصية
                    try:
                        decoded = json.loads(res.text)
                    except Exception:
                        return {"success": True, "raw": res.text}

                return {"success": True, "result": decoded}

            # أي حالة ثانية
            return {"success": False, "status_code": res.status_code, "message": res.text}

        except Exception as e:
            return {"success": False, "error": str(e)}
            
            
            
            
import requests

class info:
    _my_channel = "@T66TD"  # ← حط هنا قناتك

    @staticmethod
    def instagram(username: str):
        try:
            url = f"https://zecora0.serv00.net/info.php?ins={username}"
            res = requests.get(url, timeout=20)
            res.raise_for_status()
            data = res.json()
            # استبدال dev
            if "dev" in data:
                data["dev"] = f"Dont forget to support the channel {info._my_channel}"
            return data
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def tiktok(username: str):
        try:
            url = f"https://zecora0.serv00.net/info.php?tak={username}"
            res = requests.get(url, timeout=20)
            res.raise_for_status()
            data = res.json()
            if "dev" in data:
                data["dev"] = f"Dont forget to support the channel {info._my_channel}"
            return data
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def youtube(channel: str):
        try:
            url = f"https://zecora0.serv00.net/info.php?yt={channel}"
            res = requests.get(url, timeout=20)
            res.raise_for_status()
            data = res.json()
            if "dev" in data:
                data["dev"] = f"Dont forget to support the channel {info._my_channel}"
            return data
        except Exception as e:
            return {"success": False, "error": str(e)}
            
            
import requests

class Tofey:
    def __init__(self):
        # البيانات مخفية داخل المكتبة
        self.device_id = '52CAB9370AEBB1ED'
        self.application_id = 'com.smartwidgetlabs.chatgpt'
        self.auth_token_static = 'Lhee9Yb9VhLLV/vAZsOdKSRc7/m9Jc2IlEV0nnPLEMh+AnkGsk9p6QnTO2zqSs0mTxNW4SMZvQWQff2Nyu4/it7qHZU7i7MSRaXhXe30ZnFxGMwInrxQnWHjIkfKhN0yEJZiwOaUXyVAJaZ6quroAS6Kvycz6OeXYG0u3AM7/9g='
        self.access_token = None
        self.system_message = "اذا سئلك احد عن مطورك قول له مطوري توفي وهاذه يوزر توفي في تطبيق اشور @xxx"

    def _get_access_token(self):
        auth_payload = {
            'device_id': self.device_id,
            'order_id': '', 'product_id': '', 'purchase_token': '', 'subscription_id': '',
        }
        headers = {
            "Host": "api.vulcanlabs.co",
            "X-Vulcan-Application-Id": self.application_id,
            "Accept": "application/json",
            "User-Agent": "Chat Smith Android, Version 3.9.27(949)",
            "Content-Type": "application/json; charset=utf-8",
        }
        response = requests.post("https://api.vulcanlabs.co/smith-auth/api/v1/token", headers=headers, json=auth_payload)
        data = response.json()
        if "AccessToken" in data:
            self.access_token = data["AccessToken"]
        else:
            raise Exception("فشل في الحصول على AccessToken")

    def set_training(self, training_message: str):
        self.system_message = training_message

    def ask(self, user_text: str) -> str:
        if not self.access_token:
            self._get_access_token()

        payload = {
            'usage_model': {'provider': 'openai', 'model': 'gpt-4o'},
            'user': self.device_id,
            'messages': [
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': user_text}
            ],
            'nsfw_check': True,
        }

        headers = {
            "Host": "api.vulcanlabs.co",
            "Authorization": f"Bearer {self.access_token}",
            "X-Auth-Token": self.auth_token_static,
            "X-Vulcan-Application-Id": self.application_id,
            "Accept": "application/json",
            "User-Agent": "Chat Smith Android, Version 3.9.27(949)",
            "Content-Type": "application/json; charset=utf-8",
        }

        response = requests.post("https://api.vulcanlabs.co/smith-v2/api/v7/chat_android", headers=headers, json=payload)
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["Message"]["content"]
        else:
            raise Exception("لم يتم الحصول على رد")


import requests
import json

class gpt_oss:
    mmo = "@T66TD"  # ← قناتك
    BASE_URL = "https://sii3.top/api/gpt-oss.php"

    def __init__(self, system_message=None):
        self.system_message = system_message or f"اذا سئلك احد عن مطورك قول له مطوري رنا وهاذه يوزر {gpt_oss.mmo}"

    def set_training(self, training_message: str):
        """تغيير رسالة التدريب"""
        self.system_message = training_message

    def ask(self, prompt: str) -> dict:
        try:
            headers = {"Content-Type": "application/json"}
            # ندمج التدريب + رسالة المستخدم
            final_prompt = f"{self.system_message}\n\nUser: {prompt}"

            payload = {"text": final_prompt}

            resp = requests.post(gpt_oss.BASE_URL, headers=headers, data=json.dumps(payload), timeout=60)
            resp.raise_for_status()

            try:
                data = resp.json()
                return {"status": "OK", "result": data}
            except ValueError:
                return {"status": "OK", "result": resp.text}

        except Exception as e:
            return {"status": "Error", "error": str(e)}

    @staticmethod
    def models() -> list:
        return ["gpt-oss"]
        
        
import os
import sys
import re
import requests

class ToolEditor:
    def __init__(self):
        # معلومات ثابتة داخل المكتبة
        self.device_id = '52CAB9370AEBB1ED'
        self.application_id = 'com.smartwidgetlabs.chatgpt'
        self.auth_token_static = (
            'Lhee9Yb9VhLLV/vAZsOdKSRc7/m9Jc2IlEV0nnPLEMh+AnkGsk9p6QnTO2zqSs0mTxNW4SMZvQWQff2Nyu4/it7qHZU7i7MSRaXhXe30ZnFxGMwInrxQnWHjIkfKhN0yEJZiwOaUXyVAJaZ6quroAS6Kvycz6OeXYG0u3AM7/9g='
        )
        self.access_token = None
        self.system_message = "انت محرر أدوات، وظيفتك تعدل الأكواد حسب المطلوب اعمل حسب طلب بدون اضافه اي كلام زائد فقط قم باضافه الكود"

    # -----------------------------
    # داخليات المكتبة
    # -----------------------------

    def _get_access_token(self):
        payload = {
            'device_id': self.device_id,
            'order_id': '',
            'product_id': '',
            'purchase_token': '',
            'subscription_id': '',
        }
        headers = {
            "Host": "api.vulcanlabs.co",
            "X-Vulcan-Application-Id": self.application_id,
            "Accept": "application/json",
            "User-Agent": "Chat Smith Android, Version 3.9.27(949)",
            "Content-Type": "application/json; charset=utf-8",
        }
        r = requests.post("https://api.vulcanlabs.co/smith-auth/api/v1/token", headers=headers, json=payload)
        data = r.json()
        if "AccessToken" in data:
            self.access_token = data["AccessToken"]
        else:
            raise Exception("⚠️ فشل في الحصول على AccessToken")

    def _build_headers(self):
        return {
            "Host": "api.vulcanlabs.co",
            "Authorization": f"Bearer {self.access_token}",
            "X-Auth-Token": self.auth_token_static,
            "X-Vulcan-Application-Id": self.application_id,
            "Accept": "application/json",
            "User-Agent": "Chat Smith Android, Version 3.9.27(949)",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _clean_code(self, text: str) -> str:
        """
        يشيل الرموز الزايدة مثل ```python و ``` وأي فراغات زايدة
        """
        text = re.sub(r"```.*?```", lambda m: m.group(0).replace("```python", "").replace("```", ""), text, flags=re.S)
        return text.strip()

    # -----------------------------
    # الواجهة العامة
    # -----------------------------

    def set_training(self, msg: str):
        self.system_message = msg

    def ask(self, file_path: str, prompt: str) -> str:
        """يبعث برومبت لتعديل ملف أداة وينظف الكود الناتج"""
        if not self.access_token:
            self._get_access_token()

        # يقرأ الكود الحالي
        with open(file_path, "r", encoding="utf-8") as f:
            current_code = f.read()

        payload = {
            'usage_model': {'provider': 'openai', 'model': 'gpt-4o'},
            'user': self.device_id,
            'messages': [
                {'role': 'system', 'content': self.system_message},
                {'role': 'user', 'content': f"عدّل الكود التالي:\n{current_code}\n\nالتعليمات: {prompt}"}
            ],
            'nsfw_check': True,
        }

        r = requests.post(
            "https://api.vulcanlabs.co/smith-v2/api/v7/chat_android",
            headers=self._build_headers(),
            json=payload
        )
        data = r.json()

        if "choices" in data and len(data["choices"]) > 0:
            raw_code = data["choices"][0]["Message"]["content"]

            # تنظيف الكود من الرموز الزايدة
            clean_code = self._clean_code(raw_code)

            # يكتب الكود المعدل بالملف
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            return f"✅ تم تعديل الأداة {file_path}\n\nالكود المعدل:\n{clean_code}"
        else:
            raise Exception("⚠️ ما اجاني رد من السيرفر")