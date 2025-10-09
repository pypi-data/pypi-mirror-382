import hmac
import base64
import time
import datetime
from . import consts as c


def sign(message, secretKey):
    """
    使用 HMAC-SHA256 算法对消息进行签名。
    :param message: 要签名的消息。
    :param secretKey: 密钥。
    :return: 经过 base64 编码的签名。
    """
    # 使用 secretKey 作为密钥，对 message 进行 HMAC-SHA256 加密
    mac = hmac.new(bytes(secretKey, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()  # 获取摘要
    return base64.b64encode(d)  # 对摘要进行 base64 编码


def pre_hash(timestamp, method, request_path, body):
    """
    生成预哈希字符串，用于构建签名消息。
    :param timestamp: 时间戳。
    :param method: HTTP 请求方法 (GET, POST 等)。
    :param request_path: 请求路径。
    :param body: 请求体。
    :return: 拼接后的字符串。
    """
    # 拼接时间戳、大写的请求方法、请求路径和请求体
    return str(timestamp) + str.upper(method) + request_path + body


def get_header(api_key, sign, timestamp, passphrase, flag):
    """
    生成 HTTP 请求头。
    :param api_key: API 密钥。
    :param sign: 签名。
    :param timestamp: 时间戳。
    :param passphrase: 密码。
    :param flag: 模拟交易标志。
    :return: 包含所有必要信息的字典形式的请求头。
    """
    header = dict()
    header[c.CONTENT_TYPE] = c.APPLICATION_JSON  # 设置内容类型为 JSON
    header[c.OK_ACCESS_KEY] = api_key  # 设置 API 密钥
    header[c.OK_ACCESS_SIGN] = sign  # 设置签名
    header[c.OK_ACCESS_TIMESTAMP] = str(timestamp)  # 设置时间戳
    header[c.OK_ACCESS_PASSPHRASE] = passphrase  # 设置密码

    # OKX API: 'x-simulated-trading': '1' for simulated, '0' for real
    # Our 'flag' parameter: '1' for real, '0' for simulated
    # 所以，如果我们的 flag 是 '0' (模拟盘)，x-simulated-trading 设置为 '1'。
    # 如果我们的 flag 是 '1' (实盘)，x-simulated-trading 设置为 '0'。
    header['x-simulated-trading'] = '1' if flag == '0' else '0'

    return header


def parse_params_to_str(params):
    """
    将字典形式的参数解析为 URL 查询字符串。
    :param params: 字典形式的参数。
    :return: URL 查询字符串。
    """
    url = '?'
    # 遍历参数字典，将键值对拼接成 URL 查询字符串
    for key, value in params.items():
        url = url + str(key) + '=' + str(value) + '&'
    return url[0:-1]  # 去掉最后一个 '&'


def get_timestamp():
    """
    获取 UTC 时间戳，格式为 ISO 8601，带毫秒和 'Z'。
    :return: UTC 时间戳字符串。
    """
    now = datetime.datetime.utcnow()  # 获取当前 UTC 时间
    t = now.isoformat("T", "milliseconds")  # 格式化为 ISO 8601 字符串，包含毫秒
    return t + "Z"  # 添加 'Z' 表示 UTC


def signature(timestamp, method, request_path, body, secret_key):
    """
    生成完整的签名。
    :param timestamp: 时间戳。
    :param method: HTTP 请求方法 (GET, POST 等)。
    :param request_path: 请求路径。
    :param body: 请求体。
    :param secret_key: 密钥。
    :return: 经过 base64 编码的签名。
    """
    # 如果请求体为空字典或 None，则将其设置为空字符串
    if str(body) == '{}' or str(body) == 'None':
        body = ''
    # 拼接时间戳、大写的请求方法、请求路径和请求体，形成待签名的消息
    message = str(timestamp) + str.upper(method) + request_path + str(body)

    # 使用 secret_key 作为密钥，对 message 进行 HMAC-SHA256 加密
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()  # 获取摘要

    return base64.b64encode(d)  # 对摘要进行 base64 编码