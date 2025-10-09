from .client import Client
from .consts import *


class ConvertAPI(Client):
    # 初始化
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取所有币种
    def get_currencies(self):
        params = {}
        return self._request_with_params(GET, GET_CURRENCIES, params)

    # 获取指定币对信息
    def get_currency_pair(self, fromCcy='', toCcy=''):
        params = {"fromCcy": fromCcy, 'toCcy': toCcy}
        return self._request_with_params(GET, GET_CURRENCY_PAIR, params)

    # 估算兑换报价
    def estimate_quote(self, baseCcy = '', quoteCcy = '', side = '', rfqSz = '', rfqSzCcy = '', clQReqId = '',tag=''):
        params = {'baseCcy': baseCcy, 'quoteCcy': quoteCcy, 'side':side, 'rfqSz':rfqSz, 'rfqSzCcy':rfqSzCcy, 'clQReqId':clQReqId,'tag':tag}
        return self._request_with_params(POST, ESTIMATE_QUOTE, params)

    # 执行兑换交易
    def convert_trade(self, quoteId = '', baseCcy = '', quoteCcy = '', side = '', sz = '', szCcy = '', clTReqId = '',tag=''):
        params = {'quoteId': quoteId, 'baseCcy': baseCcy, 'quoteCcy':quoteCcy, 'side':side, 'sz':sz, 'szCcy':szCcy, 'clTReqId':clTReqId,'tag':tag}
        return self._request_with_params(POST, CONVERT_TRADE, params)

    # 获取兑换历史记录
    def get_convert_history(self, after = '', before = '', limit = '',tag=''):
        params = {'after': after, 'before': before, 'limit':limit,'tag':tag}
        return self._request_with_params(GET, CONVERT_HISTORY, params)