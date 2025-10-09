# 从 .client 模块导入 Client 类
from .client import Client
# 从 .consts 模块导入所有常量
from .consts import *


# FDBrokerAPI 类，继承自 Client 类
class FDBrokerAPI(Client):
    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类 Client 的构造函数进行初始化
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取每个订单的返利信息
    def fd_rebate_per_orders(self, begin='', end='', brokerType=''):
        # 构建请求参数字典
        params = {'begin': begin, 'end': end, 'brokerType': brokerType}
        # 发送 POST 请求并返回结果
        return self._request_with_params(POST, FD_REBATE_PER_ORDERS, params)

    # 获取每个订单的返利详情
    def fd_get_rebate_per_orders(self, type='', begin='', end='', brokerType=''):
        # 构建请求参数字典
        params = {'type': type, 'begin': begin, 'end': end, 'brokerType': brokerType}
        # 发送 GET 请求并返回结果
        return self._request_with_params(GET, FD_GET_REBATE_PER_ORDERS, params)

    # 查询是否返利
    def fd_if_rebate(self, apiKey='', brokerType=''):
        # 构建请求参数字典
        params = {'apiKey': apiKey, 'brokerType': brokerType}
        # 发送 GET 请求并返回结果
        return self._request_with_params(GET, FD_IF_REBATE, params)