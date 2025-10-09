# 从当前包导入Client类
from .client import Client
# 从当前包导入所有常量
from .consts import *


# StatusAPI类继承自Client类
class StatusAPI(Client):
    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类Client的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取系统状态
    def status(self, state=''):
        # 构建请求参数字典，'state' 为状态参数
        params = {'state': state}
        # 调用父类的_request_with_params方法发送GET请求，获取状态信息
        return self._request_with_params(GET, STATUS, params)

    # GET /api/v5/support/announcements
    # 获取公告列表
    def get_announcements(self, annType = '', page = ''):
        # 构建请求参数字典，'annType' 为公告类型，'page' 为页码
        params = {'annType': annType, 'page': page}
        # 调用父类的_request_with_params方法发送GET请求，获取公告信息
        return self._request_with_params(GET, GET_ANNOUNCEMENTS, params)

    # GET /api/v5/support/announcement-types
    # 获取公告类型
    def get_announcements_types(self):
        # 构建空的请求参数字典
        params = {}
        # 调用父类的_request_with_params方法发送GET请求，获取公告类型信息
        return self._request_with_params(GET, GET_ANNOUNCEMENTS_TYPES, params)