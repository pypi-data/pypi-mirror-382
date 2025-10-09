# coding=utf-8


class OkxAPIException(Exception):
    """
    OKX API异常类，用于处理从OKX API返回的错误响应。
    """
    def __init__(self, response):
        """
        构造函数，初始化API异常。
        :param response: HTTP响应对象，通常包含错误信息。
        """
        # 打印响应文本和状态码
        print(response.text + ', ' + str(response.status_code))
        self.code = 0  # 错误码初始化
        try:
            json_res = response.json()  # 尝试将响应解析为JSON
        except ValueError:
            # 如果解析失败，则消息为无效JSON格式
            self.message = 'Invalid JSON error message from Okx: {}'.format(response.text)
        else:
            # 如果JSON解析成功，检查是否包含'code'和'msg'字段
            if "code" in json_res.keys() and "msg" in json_res.keys():
                self.code = json_res['code']  # 提取错误码
                self.message = json_res['msg']  # 提取错误消息
            else:
                self.code = 'None'  # 如果没有'code'和'msg'，则为系统错误
                self.message = 'System error'

        self.status_code = response.status_code  # HTTP状态码
        self.response = response  # 原始HTTP响应
        self.request = getattr(response, 'request', None)  # 原始HTTP请求

    def __str__(self):  # pragma: no cover
        """
        返回此异常的字符串表示。
        :return: 包含错误码和消息的字符串。
        """
        return 'API Request Error(code=%s): %s' % (self.code, self.message)


class OkxRequestException(Exception):
    """
    OKX 请求异常类，用于处理在发送请求时发生的错误（例如网络问题）。
    """
    def __init__(self, message):
        """
        构造函数，初始化请求异常。
        :param message: 异常消息。
        """
        self.message = message

    def __str__(self):
        """
        返回此异常的字符串表示。
        :return: 包含请求异常消息的字符串。
        """
        return 'OkxRequestException: %s' % self.message


class OkxParamsException(Exception):
    """
    OKX 参数异常类，用于处理由于参数错误导致的问题。
    """
    def __init__(self, message):
        """
        构造函数，初始化参数异常。
        :param message: 异常消息。
        """
        self.message = message

    def __str__(self):
        """
        返回此异常的字符串表示。
        :return: 包含参数异常消息的字符串。
        """
        return 'OkxParamsException: %s' % self.message
