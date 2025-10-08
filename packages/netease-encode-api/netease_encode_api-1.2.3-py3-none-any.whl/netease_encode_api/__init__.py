"""
netease_encode_api/__init__.py
Version: 1.2.0
Author: CooooldWind_, DeepSeek-R1, DeepSeek-V3, 豆包
E-Mail: 3091868003@qq.com
Copyright @CooooldWind_ / Following GNU_AGPLV3+ License
"""

import json
import time
from urllib import response

import requests
from base64 import b64encode
from Crypto.Cipher import AES
from netease_encode_api.global_args import GlobalArgs

import pyqrcode


class EncodeSession(requests.Session):
    # 继承自 requests.Session
    """
    WeAPI解码类（继承自requests.Session）
    """

    def __init__(self):
        super().__init__()
        # 显式调用父类初始化
        self.__global = GlobalArgs()
        self.__encode_arg_g = "0CoJUm6Qyw8W8jud"
        self.__encode_arg_i = "vlgPRPyGhwA6F4Sq"
        self.__encode_sec_key = self.__global.ENCODE_SEC_KEY
        # 固定为常见电脑Chrome浏览器的headers
        self.__headers = {
            'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.last_response: dict = None

    def __to_hex(self, encode_data):
        """
        16进制解码
        """
        temp = 16 - len(encode_data) % 16
        return encode_data + chr(temp) * temp

    def __encode_params(self, encode_data: str = "", encode_key: str = ""):
        """
        解码的关键函数(1)
        """
        func_iv = "0102030405060708"
        encode_data = self.__to_hex(encode_data)
        base64_sec_key = AES.new(
            key=encode_key.encode("utf-8"),
            iv=func_iv.encode("utf-8"),
            mode=AES.MODE_CBC,
        ).encrypt(encode_data.encode("utf-8"))
        return str(b64encode(base64_sec_key), "utf-8")

    def __get_params(self, encode_data: str = ""):
        """
        解码的关键函数(2)
        """
        return self.__encode_params(
            self.__encode_params(encode_data, self.__encode_arg_g), self.__encode_arg_i
        )

    def encoded_post(self, url: str, data: dict) -> requests.Response:
        """
        发送加密的POST请求并获取响应。
        需要给出 `url` 和 `data` 作为参数。
        """
        processed_data = {
            "params": self.__get_params(json.dumps(data)).encode("UTF-8"),
            "encSecKey": self.__encode_sec_key,
        }
        # 使用继承自父类的 post 方法
        return self.post(url=url, data=processed_data)

    def cmd_login(self):
        # 没开发完。现在问题是，弹“803”登录成功前，会弹“8821”行为验证的状态码。找不出原因。
        unikey = self.encoded_post("https://music.163.com/weapi/login/qrcode/unikey", {"type": "1"}).json()["unikey"]
        login_qrcode_link = f"https://music.163.com/login?codekey={unikey}&refer=scan"
        print(pyqrcode.create(login_qrcode_link, error="L").terminal(quiet_zone=1))
        status_code = 801
        while 803 > status_code > 800:
            time.sleep(0.5)
            status_code = int(self.encoded_post("https://music.163.com/weapi/login/qrcode/client/login",
                                                {"key": unikey, "type": "1"}).json()["code"])
        if status_code == 803:
            print("Succeed.")
        else:
            print("Failed.")
        return None

