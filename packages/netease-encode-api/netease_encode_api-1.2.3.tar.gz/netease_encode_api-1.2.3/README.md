from http.client import responses

# netease_encode_api

网易云weapi解码和封装。

## 安装

1. 请下载带有 pip 包安装器的 Python, 并将 Python 添加到 PATH。
2. 打开命令行输入 `pip install netease_encode_api`
3. 在 Python 代码内引用: `from netease_encode_api import EncodeSession`

## 使用

在 1.2.0+ 版本, `EncodeSession` 类已经成为了 `requests.Session` 的子类。
在不需要解码时, 请按照 `request.Session` 的使用方式正常使用。
在需要解码时, 请使用 `EncodeSession.encoded_post(url, data)`。

预留了 `EncodeSession.cmd_login()`, 受不可抗力控制 (网易云好像最近抓第三方蛮狠的), 暂未实现, 请耐心等待。在此之前, 请先用 Cookies 填写的方式, 写入 `MUSIC_U` 字段登录。具体方式如下:

1. 在网页版登录网易云音乐;
2. 打开浏览器开发者工具, 切换到 `Application (应用程序)` 标签页;
3. 找到 `Cookies` 一栏, 找到 `MUSIC_U` 字段, 复制其值;
4. 在 Python 代码内, 调用 `EncodeSession.set_cookie("MUSIC_U", "复制的值")` 方法, 即可登录。

## 示例

```python
from netease_encode_api import EncodeSession
es = EncodeSession()
# 加密获取歌曲下载链接
url = "https://music.163.com/weapi/song/enhance/player/url/v1"
data = {"ids":"[1462389992]",
        "level":"exhigh",
        "encodeType":"mp3"}
responses = es.encoded_post(url, data)
download_url = responses["data"][0]["url"]
download_responses = es.get(download_url)
with open(test.mp3, "wb") as f: f.write(download_responses.content)

```