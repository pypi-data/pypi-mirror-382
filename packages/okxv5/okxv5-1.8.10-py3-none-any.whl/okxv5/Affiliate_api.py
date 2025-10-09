from .client import Client  # 从当前包导入 Client 类
from .consts import *       # 从当前包导入 consts 模块的所有内容（常量）


class AffiliateAPI(Client):  # 定义 AffiliateAPI 类，它继承自 Client 类

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 构造函数，用于初始化 AffiliateAPI 实例
        # 参数:
        # api_key: API 密钥
        # api_secret_key: API 秘密密钥
        # passphrase: 交易密码
        # use_server_time: 是否使用服务器时间，默认为 False
        # flag: 标志位，默认为 '1'
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)
        # 调用父类 Client 的构造函数来初始化父类部分