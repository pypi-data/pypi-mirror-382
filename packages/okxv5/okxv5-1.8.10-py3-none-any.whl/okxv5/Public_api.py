# 从 .client 模块导入 Client 类
from .client import Client
# 从 .consts 模块导入所有常量
from .consts import *


# PublicAPI 类继承自 Client 类
class PublicAPI(Client):

    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类 Client 的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取交易产品列表
    def get_instruments(self, instType = 'FUTURES', uly = 'BTC-USDT', instFamily = '', instId = ''):
        # 构造请求参数
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, INSTRUMENT_INFO, params)

    # 获取交割/行权历史
    def get_deliver_history(self, instType, uly, after='', before='', limit=''):
        # 构造请求参数
        params = {'instType': instType, 'uly': uly, 'after': after, 'before': before, 'limit': limit}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, DELIVERY_EXERCISE, params)

    # 获取持仓量
    def get_open_interest(self, instType, uly='', instId='',instFamily=''):
        # 构造请求参数
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, OPEN_INTEREST, params)

    # 获取资金费率
    def get_funding_rate(self, instId):
        # 构造请求参数
        params = {'instId': instId}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, FUNDING_RATE, params)

    # 获取资金费率历史
    def funding_rate_history(self, instId, after='', before='', limit=''):
        # 构造请求参数
        params = {'instId': instId, 'after': after, 'before': before, 'limit': limit}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, FUNDING_RATE_HISTORY, params)

    # 获取限价
    def get_price_limit(self, instId):
        # 构造请求参数
        params = {'instId': instId}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, PRICE_LIMIT, params)

    # 获取期权市场数据
    def get_opt_summary(self, uly, expTime=''):
        # 构造请求参数
        params = {'uly': uly, 'expTime': expTime}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, OPT_SUMMARY, params)

    # 获取预估交割/行权价格
    def get_estimated_price(self, instId):
        # 构造请求参数
        params = {'instId': instId}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, ESTIMATED_PRICE, params)

    # 获取折扣率和免息额度
    def discount_interest_free_quota(self, ccy=''):
        # 构造请求参数
        params = {'ccy': ccy}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, DICCOUNT_INTETEST_INFO, params)

    # 获取系统时间
    def get_system_time(self):
        # 发送不带参数的 GET 请求
        return self._request_without_params(GET, SYSTEM_TIME)

    # 获取爆仓订单
    def get_liquidation_orders(self, instType, mgnMode='', instId='', ccy='', uly='', alias='', state='', before='',
                               after='', limit='',instFamily = ''):
        # 构造请求参数
        params = {'instType': instType, 'mgnMode': mgnMode, 'instId': instId, 'ccy': ccy, 'uly': uly,
                  'alias': alias, 'state': state, 'before': before, 'after': after, 'limit': limit,'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, LIQUIDATION_ORDERS, params)

    # 获取标记价格
    def get_mark_price(self, instType, uly='', instId='',instFamily=''):
        # 构造请求参数
        params = {'instType': instType, 'uly': uly, 'instId': instId,'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, MARK_PRICE, params)

    # 获取等级费率
    def get_tier(self, instType, tdMode, uly='', instId='', ccy='', tier='',instFamily=''):
        # 构造请求参数
        params = {'instType': instType, 'tdMode': tdMode, 'uly': uly, 'instId': instId, 'ccy': ccy, 'tier': tier,'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, TIER, params)

    # 获取利率和借贷额度
    def get_interest_loan(self):
        # 发送不带参数的 GET 请求
        return self._request_without_params(GET, INTEREST_LOAN)

    # 获取标的指数
    def get_underlying(self, instType):
        # 构造请求参数
        params = {'instType': instType}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, UNDERLYING, params)

    # 获取 VIP 利率借贷额度
    def get_vip_interest_rate_loan_quota(self):
        # 构造空参数
        params = {}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, VIP_INTEREST_RATE_LOAN_QUOTA, params)

    # 获取保险基金数据
    def get_insurance_fund(self,instType = '', type = '', uly = '', ccy = '', before = '', after = '', limit = '',instFamily=''):
        # 构造请求参数
        params = {'instType':instType, 'type':type, 'uly':uly, 'ccy':ccy, 'before':before, 'after':after, 'limit':limit,'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, INSURANCE_FUND, params)

    # 转换合约币种
    def convert_contract_coin(self, type = '', instId = '', sz = '', px = '', unit = '', opType=''):
        # 构造请求参数
        params = {'type':type, 'instId':instId, 'sz':sz, 'px':px, 'unit':unit, 'opType':opType}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, CONVERT_CONTRACT_COIN, params)

    # 获取交易产品最小变动档位
    def instrument_tick_bands(self, instType = '', instFamily = ''):
        # 构造请求参数
        params = {'instType':instType, 'instFamily':instFamily}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, INSTRUMENT_TICK_BANDS, params)

    # 获取期权最新成交
    def option_trades(self, instId = '', instFamily = '', optType = ''):
        # 构造请求参数
        params = {'instId':instId, 'instFamily':instFamily, 'optType':optType}
        # 发送带参数的 GET 请求
        return self._request_with_params(GET, OPTION_TRADES, params)