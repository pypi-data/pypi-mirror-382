from .client import Client
from .consts import *


class BrokerAPI(Client):
    """
    BrokerAPI 类继承自 Client，用于处理经纪商相关的 API 请求。
    """
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        构造函数，初始化 BrokerAPI 实例。
        :param api_key: API 密钥
        :param api_secret_key: API 私钥
        :param passphrase: 密码
        :param use_server_time: 是否使用服务器时间，默认为 False
        :param flag: 区域标志，默认为 '1'
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    def broker_info(self):
        """
        获取经纪商信息。
        :return: API 请求结果
        """
        params = {}
        return self._request_with_params(GET, BROKER_INFO, params)

    def create_subaccount(self, subAcct='', label='', clientIP='',mainAcct=''):
        """
        创建子账户。
        :param subAcct: 子账户名称
        :param label: 子账户标签
        :param clientIP: 客户端 IP
        :param mainAcct: 主账户名称
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'label': label, 'clientIP':clientIP,'mainAcct':mainAcct}
        return self._request_with_params(POST, CREATE_SUBACCOUNT, params)

    def delete_subaccount(self, subAcct=''):
        """
        删除子账户。
        :param subAcct: 子账户名称
        :return: API 请求结果
        """
        params = {'subAcct': subAcct}
        return self._request_with_params(POST, DELETE_SUBACCOUNT, params)

    def subaccount_info(self, subAcct='', page='', limit='', uid=''):
        """
        获取子账户信息。
        :param subAcct: 子账户名称
        :param page: 页码
        :param limit: 每页限制数量
        :param uid: 用户 ID
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'page': page, 'limit': limit, 'uid':uid}
        return self._request_with_params(GET, SUBACCOUNT_INFO, params)

    def subaccount_trade_fee(self, subAcct='', page='', limit='', uid=''):
        """
        获取子账户交易费率。
        :param subAcct: 子账户名称
        :param page: 页码
        :param limit: 每页限制数量
        :param uid: 用户 ID
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'page': page, 'limit': limit, 'uid':uid}
        return self._request_with_params(GET, SUBACCOUNT_TRADE_FEE, params)

    def set_subaccount_level(self, subAcct='', acctLv=''):
        """
        设置子账户等级。
        :param subAcct: 子账户名称
        :param acctLv: 账户等级
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'acctLv': acctLv}
        return self._request_with_params(POST, SET_SUBACCOUNT_LEVEL, params)

    def set_subaccount_fee_rate(self, subAcct='', instType='', chgType='', chgTaker='',
                                chgMaker='', effDate='', mgnType='',quoteCcyType = ''):
        """
        设置子账户费率。
        :param subAcct: 子账户名称
        :param instType: 交易产品类型
        :param chgType: 费用类型
        :param chgTaker: Taker 费率
        :param chgMaker: Maker 费率
        :param effDate: 生效日期
        :param mgnType: 保证金模式
        :param quoteCcyType: 报价币种类型
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'instType': instType, 'chgType': chgType, 'chgTaker': chgTaker,
                  'chgMaker':chgMaker, 'effDate':effDate, 'mgnType':mgnType, 'quoteCcyType':quoteCcyType}
        return self._request_with_params(POST, SET_SUBACCOUNT_FEE_REAT, params)

    def subaccount_deposit_address(self, subAcct='', ccy='', chain='', addrType='', to=''):
        """
        获取子账户充值地址。
        :param subAcct: 子账户名称
        :param ccy: 币种
        :param chain: 链名称
        :param addrType: 地址类型
        :param to: 目标
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'ccy': ccy, 'chain': chain, 'addrType': addrType, 'to': to}
        return self._request_with_params(POST, SUBACCOUNT_DEPOSIT_ADDRESS, params)

    def subaccount_deposit_history(self, subAcct = '', ccy = '', txId = '', state = '', after = '', before = '', limit = ''):
        """
        获取子账户充值历史。
        :param subAcct: 子账户名称
        :param ccy: 币种
        :param txId: 交易 ID
        :param state: 状态
        :param after: 查询在指定时间戳之后的数据
        :param before: 查询在指定时间戳之前的数据
        :param limit: 限制数量
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'ccy': ccy, 'txId': txId, 'state': state, 'after': after, 'before': before, 'limit':limit}
        return self._request_with_params(GET, SUBACCOUNT_DEPOSIT_HISTORY, params)

    def rebate_daily(self, subAcct = '', begin = '', end = '', page = '', limit = '',
                     beginTime = '', endTime = ''):
        """
        获取每日返佣数据。
        :param subAcct: 子账户名称
        :param begin: 开始日期
        :param end: 结束日期
        :param page: 页码
        :param limit: 每页限制数量
        :param beginTime: 开始时间
        :param endTime: 结束时间
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'begin': begin, 'end': end, 'page': page, 'limit': limit,
                  'beginTime':beginTime, 'endTime': endTime}
        return self._request_with_params(GET, REBATE_DAILY, params)

    def dma_create_apikey(self, subAcct = '', label = '', passphrase = '', ip = '', perm = ''):
        """
        创建 DMA API Key。
        :param subAcct: 子账户名称
        :param label: 标签
        :param passphrase: 密码
        :param ip: IP 地址
        :param perm: 权限
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'label': label, 'passphrase': passphrase, 'ip': ip, 'perm': perm}
        return self._request_with_params(POST, DMA_CREAET_APIKEY, params)

    def dma_select_apikey(self, subAcct = '', apiKey = ''):
        """
        查询 DMA API Key。
        :param subAcct: 子账户名称
        :param apiKey: API 密钥
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'apiKey': apiKey}
        return self._request_with_params(GET, DMA_SELECT_APIKEY, params)

    def dma_modify_apikey(self, subAcct = '', apiKey = '', label = '', perm = '', ip = ''):
        """
        修改 DMA API Key。
        :param subAcct: 子账户名称
        :param apiKey: API 密钥
        :param label: 标签
        :param perm: 权限
        :param ip: IP 地址
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'apiKey': apiKey, 'label': label, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, DMA_MODIFY_APIKEY, params)

    def dma_delete_apikey(self, subAcct = '', apiKey = ''):
        """
        删除 DMA API Key。
        :param subAcct: 子账户名称
        :param apiKey: API 密钥
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'apiKey': apiKey}
        return self._request_with_params(POST, DMA_DELETE_APIKEY, params)

    def rebate_per_orders(self, begin = '', end = ''):
        """
        获取每笔订单返佣数据 (POST 请求)。
        :param begin: 开始日期
        :param end: 结束日期
        :return: API 请求结果
        """
        params = {'begin': begin, 'end': end}
        return self._request_with_params(POST, REBATE_PER_ORDERS, params)

    def get_rebate_per_orders(self, type = '', begin = '', end = ''):
        """
        获取每笔订单返佣数据 (GET 请求)。
        :param type: 类型
        :param begin: 开始日期
        :param end: 结束日期
        :return: API 请求结果
        """
        params = {'type': type, 'begin': begin, 'end': end}
        return self._request_with_params(GET, GET_REBATE_PER_ORDERS, params)

    def modify_subaccount_deposit_address(self, subAcct = '', ccy = '', chain = '', addr = '', to = ''):
        """
        修改子账户充值地址。
        :param subAcct: 子账户名称
        :param ccy: 币种
        :param chain: 链名称
        :param addr: 地址
        :param to: 目标
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'ccy': ccy, 'chain': chain, 'addr': addr, 'to': to}
        return self._request_with_params(POST, MODIFY_SUBACCOUNT_DEPOSIT_ADDRESS, params)

    def nd_subaccount_withdrawal_history(self, subAcct = '', ccy = '', wdId = '', clientId = '', txId = '', type = '', state = '', after = '', before = '', limit = ''):
        """
        获取 ND 子账户提现历史。
        :param subAcct: 子账户名称
        :param ccy: 币种
        :param wdId: 提现 ID
        :param clientId: 客户端 ID
        :param txId: 交易 ID
        :param type: 类型
        :param state: 状态
        :param after: 查询在指定时间戳之后的数据
        :param before: 查询在指定时间戳之前的数据
        :param limit: 限制数量
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'ccy': ccy, 'wdId': wdId, 'clientId': clientId, 'txId': txId, 'type': type, 'state': state, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ND_SUBACCOUNT_WITHDRAWAL_HISTORY, params)

    # POST /api/v5/broker/nd/set-subaccount-assets
    def set_subaccount_assets(self, subAcct = '', ccy = ''):
        """
        设置子账户资产。
        :param subAcct: 子账户名称
        :param ccy: 币种
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'ccy': ccy,}
        return self._request_with_params(POST, SET_SUBACCOUNT_ASSETS, params)

    # POST /api/v5/broker/nd/set-subaccount-assets
    def report_subaccount_ip(self, subAcct, clientIP):
        """
        报告子账户 IP。
        :param subAcct: 子账户名称
        :param clientIP: 客户端 IP
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'clientIP': clientIP,}
        return self._request_with_params(POST, R_SACCOUNT_IP, params)


    def if_rebate(self, apiKey='',uid='',subAcct='',):
        """
        查询是否有返佣。
        :param apiKey: API 密钥
        :param uid: 用户 ID
        :param subAcct: 子账户名称
        :return: API 请求结果
        """
        params = {'subAcct': subAcct, 'apiKey': apiKey,'uid': uid,}
        return self._request_with_params(GET, IF_REBATE, params)