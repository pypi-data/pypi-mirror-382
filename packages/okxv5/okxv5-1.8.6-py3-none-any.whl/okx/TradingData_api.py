# 从.client模块导入Client类
from .client import Client
# 从.consts模块导入所有常量
from .consts import *


# 交易数据API类，继承自Client
class TradingDataAPI(Client):

    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类Client的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取支持的币种
    def get_support_coin(self):
        return self._request_without_params(GET, SUPPORT_COIN)

    # GET /api/v5/rubik/stat/contracts/open-interest-history    
    # 获取合约持仓量历史
    def get_open_interest_history(self, instId = '', period = '', end = '', begin = '', limit = ''):
        # 构建请求参数
        params = {'instId': instId, 'period': period, 'end': end, 'begin': begin, 'limit': limit}
        # 发送带参数的GET请求
        return self._request_with_params(GET, GET_OPEN_INTEREST_HISTORY, params)

    # 获取Taker成交量
    def get_taker_volume(self, ccy, instType, begin='', end='', period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'instType': instType, 'begin': begin, 'end': end, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, TAKER_VOLUME, params)

    # GET /api/v5/rubik/stat/taker-volume-contract
    # 获取合约Taker成交量
    def get_taker_volume_contract(self, instId, period = '', unit='', end='', begin='', limit = ''):
        # 构建请求参数
        params = {'instId': instId, 'period': period, 'unit': unit, 'end': end, 'begin': begin,'limit':limit}
        # 发送带参数的GET请求
        return self._request_with_params(GET, GET_TAKER_VOLUME_CONTRACT, params)

    # 获取杠杆借贷比率
    def get_margin_lending_ratio(self, ccy, begin='', end='', period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, MARGIN_LENDING_RATIO, params)

    # GET /api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader
    # 获取合约多空账户比率-顶尖交易员
    def get_long_short_account_ratio_contract_top_trader(self, instId = '', period = '', end = '', begin = '', limit = ''):
        # 构建请求参数
        params = {'instId': instId, 'period': period, 'end': end, 'begin': begin,'limit':limit}
        # 发送带参数的GET请求
        return self._request_with_params(GET, GET_LONG_SHORT_ACCOUNT_RADIO_CONTRACT_TOP_TRADER, params)

    # GET /api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader
    # 获取合约多空持仓比率-顶尖交易员
    def get_long_short_position_ratio_contract_top_trader(self, instId = '', period = '', end = '', begin = '', limit = ''):
        # 构建请求参数
        params = {'instId': instId, 'period': period, 'end': end, 'begin': begin,'limit':limit}
        # 发送带参数的GET请求
        return self._request_with_params(GET, GET_LONG_SHORT_POSTION_RADIO_CONTRACT_TOP_TRADER, params)

    # GET /api/v5/rubik/stat/contracts/long-short-account-ratio-contract
    # 获取合约多空账户比率
    def get_long_short_account_ratio_contract(self, instId = '', period = '', end = '', begin = '', limit = ''):
        # 构建请求参数
        params = {'instId': instId, 'period': period, 'end': end, 'begin': begin,'limit':limit}
        # 发送带参数的GET请求
        return self._request_with_params(GET, GET_LONG_SHORT_ACCOUNT_RADIO_CONTRACT, params)

    # 获取多空比率
    def get_long_short_ratio(self, ccy, begin='', end='', period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, LONG_SHORT_RATIO, params)

    # 获取合约持仓量和交易量
    def get_contracts_interest_volume(self, ccy, begin='', end='', period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'begin': begin, 'end': end, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, CONTRACTS_INTEREST_VOLUME, params)

    # 获取期权持仓量和交易量
    def get_options_interest_volume(self, ccy, period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, OPTIONS_INTEREST_VOLUME, params)

    # 获取看跌/看涨比率
    def get_put_call_ratio(self, ccy, period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, PUT_CALL_RATIO, params)

    # 获取按到期日划分的持仓量和交易量
    def get_interest_volume_expiry(self, ccy, period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, OPEN_INTEREST_VOLUME_EXPIRY, params)

    # 获取按行权价划分的持仓量和交易量
    def get_interest_volume_strike(self, ccy, expTime, period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'expTime': expTime, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, INTEREST_VOLUME_STRIKE, params)

    # 获取Taker资金流
    def get_taker_flow(self, ccy, period=''):
        # 构建请求参数
        params = {'ccy': ccy, 'period': period}
        # 发送带参数的GET请求
        return self._request_with_params(GET, TAKER_FLOW, params)