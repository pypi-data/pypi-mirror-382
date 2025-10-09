import requests # 导入requests库，用于发送HTTP请求
import json # 导入json库，用于处理JSON数据
import datetime # 导入datetime库，用于时间戳处理
import time # 导入time库，用于获取本地时间戳
from . import consts as c, utils, exceptions # 从当前包导入consts模块（别名为c）、utils模块和exceptions模块

class Client(object):
    """
    API客户端类，用于与API进行交互
    """

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='0'):     # 1为实盘，0为模拟盘
        """
        构造函数，初始化客户端
        :param api_key: API密钥
        :param api_secret_key: API私钥
        :param passphrase: 交易密码
        :param use_server_time: 是否使用服务器时间，默认为False
        :param flag: 请求标记，默认为'0'
        """
        self.API_KEY = api_key # 设置API密钥
        self.API_SECRET_KEY = api_secret_key # 设置API私钥
        self.PASSPHRASE = passphrase # 设置交易密码
        self.use_server_time = use_server_time # 设置是否使用服务器时间
        self.flag = flag # 设置请求标记

    def _request(self, method, request_path, params):
        """
        私有方法，用于发送HTTP请求
        :param method: HTTP请求方法（GET或POST）
        :param request_path: 请求路径
        :param params: 请求参数
        :return: API响应的JSON数据
        :raise exceptions.OkxAPIException: 如果API返回非2xx状态码
        """
        if method == c.GET:
            # 如果是GET请求，将参数解析为字符串并附加到请求路径
            request_path = request_path + utils.parse_params_to_str(params)
        # 拼接完整的URL
        url = c.API_URL + request_path

        # 确定最终用于请求头和签名的 ISO 8601 格式时间戳
        final_iso8601_timestamp = ""

        if self.use_server_time:
            # 获取服务器时间（返回 Unix 毫秒字符串）
            server_ts_ms_str = self._get_timestamp()
            if server_ts_ms_str:
                try:
                    ms = int(server_ts_ms_str)
                    dt_object = datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc)
                    final_iso8601_timestamp = dt_object.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
                except ValueError:
                    print(f"Error: Could not convert server timestamp '{server_ts_ms_str}' to ISO 8601. Using raw for signing/header.")
                    final_iso8601_timestamp = server_ts_ms_str # 转换失败时，回退使用原始值
            else:
                # 如果获取服务器时间失败，则回退到本地 UTC 时间
                print("Warning: Failed to get server time. Falling back to local UTC time for timestamp.")
                final_iso8601_timestamp = utils.get_timestamp() # utils.get_timestamp() 已经返回 ISO 8601 格式
        else:
            # 使用本地时间（utils.get_timestamp() 已经返回 ISO 8601 格式）
            final_iso8601_timestamp = utils.get_timestamp()

        # 根据请求方法决定请求体
        body = json.dumps(params) if method == c.POST else ""

        # 生成签名，使用ISO 8601格式的时间戳
        sign = utils.sign(utils.pre_hash(final_iso8601_timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        # 获取请求头，使用ISO 8601格式的时间戳
        header = utils.get_header(self.API_KEY, sign, final_iso8601_timestamp, self.PASSPHRASE, self.flag)

        # 发送请求
        response = None

        if method == c.GET:
            # 发送GET请求
            response = requests.get(url, headers=header)
        elif method == c.POST:
            # 发送POST请求
            response = requests.post(url, data=body, headers=header)

        if not str(response.status_code).startswith('2'):
            # 如果响应状态码不是2xx，则抛出API异常
            raise exceptions.OkxAPIException(response)

        # 返回JSON格式的响应数据
        return response.json()

    def _request_without_params(self, method, request_path):
        """
        私有方法，发送不带参数的HTTP请求
        :param method: HTTP请求方法
        :param request_path: 请求路径
        :return: API响应的JSON数据
        """
        return self._request(method, request_path, {})

    def _request_with_params(self, method, request_path, params):
        """
        私有方法，发送带参数的HTTP请求
        :param method: HTTP请求方法
        :param request_path: 请求路径
        :param params: 请求参数
        :return: API响应的JSON数据
        """
        return self._request(method, request_path, params)

    def _get_timestamp(self):
        """
        私有方法，获取服务器时间戳
        :return: 服务器时间戳字符串 (Unix毫秒)
        """
        url = c.API_URL + c.SERVER_TIMESTAMP_URL # 拼接获取服务器时间戳的URL
        response = requests.get(url) # 发送GET请求获取服务器时间
        if response.status_code == 200:
            # 如果请求成功，返回时间戳
            return response.json()['data'][0]['ts']
        else:
            # 如果请求失败，返回空字符串
            return ""