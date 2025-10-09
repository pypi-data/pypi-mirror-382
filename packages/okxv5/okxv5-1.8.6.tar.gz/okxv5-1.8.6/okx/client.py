import setup # 导入requests库，用于发送HTTP请求
import json # 导入json库，用于处理JSON数据
from . import consts as c, utils, exceptions # 从当前包导入consts模块（别名为c）、utils模块和exceptions模块

class Client(object):
    """
    API客户端类，用于与API进行交互
    """

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        构造函数，初始化客户端
        :param api_key: API密钥
        :param api_secret_key: API私钥
        :param passphrase: 交易密码
        :param use_server_time: 是否使用服务器时间，默认为False
        :param flag: 请求标记，默认为'1'
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

        # 获取时间戳
        timestamp = utils.get_timestamp()

        # 签名和请求头
        if self.use_server_time:
            # 如果使用服务器时间，则重新获取服务器时间戳
            timestamp = self._get_timestamp()

        # 根据请求方法决定请求体
        body = json.dumps(params) if method == c.POST else ""

        # 生成签名
        sign = utils.sign(utils.pre_hash(timestamp, method, request_path, str(body)), self.API_SECRET_KEY)
        # 获取请求头
        header = utils.get_header(self.API_KEY, sign, timestamp, self.PASSPHRASE, self.flag)

        # 发送请求
        response = None

        if method == c.GET:
            # 发送GET请求
            response = requests.get(url, headers=header)
        elif method == c.POST:
            # 发送POST请求
            response = requests.post(url, data=body, headers=header)

        # 异常处理
        # print(response.headers) # 调试用，打印响应头

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
        :return: 服务器时间戳字符串
        """
        url = c.API_URL + c.SERVER_TIMESTAMP_URL # 拼接获取服务器时间戳的URL
        response = requests.get(url) # 发送GET请求获取服务器时间
        if response.status_code == 200:
            # 如果请求成功，返回时间戳
            return response.json()['data'][0]['ts']
        else:
            # 如果请求失败，返回空字符串
            return ""
