from .client import Client
from .consts import *


class MarketAPI(Client):
    """
    市场行情API接口类，继承自Client
    """

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        构造函数
        :param api_key: API Key
        :param api_secret_key: API Secret Key
        :param passphrase: 密码
        :param use_server_time: 是否使用服务器时间 (默认为False)
        :param flag: 请求类型 (默认为'1')
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Get Tickers 获取所有产品行情信息
    def get_tickers(self, instType, uly='',instFamily=''):
        """
        获取所有产品行情信息
        :param instType: 产品类型
        :param uly: 标的指数 (可选)
        :param instFamily: 交易品种 (可选)
        :return: 产品行情信息
        """
        if uly:
            params = {'instType': instType, 'uly': uly}
        else:
            params = {'instType': instType}
        return self._request_with_params(GET, TICKERS_INFO, params)

    # Get Ticker 获取单个产品行情信息
    def get_ticker(self, instId):
        """
        获取单个产品行情信息
        :param instId: 产品ID
        :return: 单个产品行情信息
        """
        params = {'instId': instId}
        return self._request_with_params(GET, TICKER_INFO, params)

    # Get Index Tickers 获取指数行情信息
    def get_index_ticker(self, quoteCcy='', instId=''):
        """
        获取指数行情信息
        :param quoteCcy: 计价币种 (可选)
        :param instId: 产品ID (可选)
        :return: 指数行情信息
        """
        params = {'quoteCcy': quoteCcy, 'instId': instId}
        return self._request_with_params(GET, INDEX_TICKERS, params)

    # Get Order Book 获取产品深度信息
    def get_orderbook(self, instId, sz=''):
        """
        获取产品深度信息
        :param instId: 产品ID
        :param sz: 深度档位 (可选)
        :return: 产品深度信息
        """
        params = {'instId': instId, 'sz': sz}
        return self._request_with_params(GET, ORDER_BOOKS, params)

    # Get Candlesticks 获取K线数据
    def get_candlesticks(self, instId, after='', before='', bar='', limit=''):
        """
        获取K线数据
        :param instId: 产品ID
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: K线数据
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, MARKET_CANDLES, params)

    # GGet Candlesticks History（top currencies only）获取K线数据历史 (仅适用于主流币种)
    def get_history_candlesticks(self, instId, after='', before='', bar='', limit=''):
        """
        获取K线数据历史 (仅适用于主流币种)
        :param instId: 产品ID
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: K线数据历史
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, HISTORY_CANDLES, params)

    # Get Index Candlesticks 获取指数K线数据
    def get_index_candlesticks(self, instId, after='', before='', bar='', limit=''):
        """
        获取指数K线数据
        :param instId: 产品ID
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 指数K线数据
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, INDEX_CANSLES, params)

    # Get Mark Price Candlesticks 获取标记价格K线数据
    def get_markprice_candlesticks(self, instId, after='', before='', bar='', limit=''):
        """
        获取标记价格K线数据
        :param instId: 产品ID
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 标记价格K线数据
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, MARKPRICE_CANDLES, params)

    # Get Index Candlesticks 获取成交明细
    def get_trades(self, instId, limit=''):
        """
        获取成交明细
        :param instId: 产品ID
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 成交明细
        """
        params = {'instId': instId, 'limit': limit}
        return self._request_with_params(GET, MARKET_TRADES, params)

    # Get Volume 获取公共基础信息 (交易量)
    def get_volume(self):
        """
        获取公共基础信息 (交易量)
        :return: 交易量信息
        """
        return self._request_without_params(GET, VOLUMNE)

    # Get Oracle 获取链上最新成交价
    def get_oracle(self):
        """
        获取链上最新成交价
        :return: 链上最新成交价
        """
        return self._request_without_params(GET, ORACLE)

    # Get Index Components 获取指数成分
    def get_index_components(self, index):
        """
        获取指数成分
        :param index: 指数ID
        :return: 指数成分信息
        """
        params = {'index': index}
        return self._request_with_params(GET, Components, params)

    # Get Tier 获取杠杆利率和借币限额
    def get_tier(self, instType='', tdMode='', uly='', instId='', ccy='', tier=''):
        """
        获取杠杆利率和借币限额
        :param instType: 产品类型 (可选)
        :param tdMode: 交易模式 (可选)
        :param uly: 标的指数 (可选)
        :param instId: 产品ID (可选)
        :param ccy: 币种 (可选)
        :param tier: 档位 (可选)
        :return: 杠杆利率和借币限额
        """
        params = {'instType': instType, 'tdMode': tdMode, 'uly': uly, 'instId': instId, 'ccy': ccy, 'tier': tier}
        return self._request_with_params(GET, TIER, params)

    # Get exchange rate 获取法币汇率
    def get_exchange_rate(self):
        """
        获取法币汇率
        :return: 法币汇率
        """
        params = {}
        return self._request_with_params(GET, BORROW_REPAY, params)

    # Get history trades 获取历史成交明细
    def get_history_trades(self, instId = '', after = '', before = '', limit = ''):
        """
        获取历史成交明细
        :param instId: 产品ID (可选)
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 历史成交明细
        """
        params = {'instId':instId, 'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, HISTORY_TRADES, params)

    # Get block history tickers 获取大宗交易产品行情列表
    def get_block_tickers(self, instType = '', uly = '',instFamily =''):
        """
        获取大宗交易产品行情列表
        :param instType: 产品类型 (可选)
        :param uly: 标的指数 (可选)
        :param instFamily: 交易品种 (可选)
        :return: 大宗交易产品行情列表
        """
        params = {'instType':instType, 'uly':uly,'instFamily':instFamily}
        return self._request_with_params(GET, BLOCK_TICKERS, params)

    # Get block history ticker 获取大宗交易产品行情
    def get_block_ticker(self, instId = ''):
        """
        获取大宗交易产品行情
        :param instId: 产品ID (可选)
        :return: 大宗交易产品行情
        """
        params = {'instId':instId}
        return self._request_with_params(GET, BLOCK_TICKER, params)

    # Get block trades 获取大宗交易公共成交数据
    def get_block_trades(self, instId = ''):
        """
        获取大宗交易公共成交数据
        :param instId: 产品ID (可选)
        :return: 大宗交易公共成交数据
        """
        params = {'instId':instId}
        return self._request_with_params(GET, BLOCK_TRADES, params)

    # Get history index candlesticks 获取历史指数K线数据
    def get_history_index_candlesticks(self, instId ='', after='', before='', bar='', limit=''):
        """
        获取历史指数K线数据
        :param instId: 产品ID (可选)
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 历史指数K线数据
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, HISTORY_INDEX_CANDLES, params)

    # Get history mark price candlesticks 获取历史标记价格K线数据
    def get_history_markprice_candlesticks(self, instId ='', after='', before='', bar='', limit=''):
        """
        获取历史标记价格K线数据
        :param instId: 产品ID (可选)
        :param after: 请求此时间戳之前（更旧）的数据 (可选)
        :param before: 请求此时间戳之后（更新）的数据 (可选)
        :param bar: 时间粒度 (可选)
        :param limit: 返回结果的数量，默认100，最大300 (可选)
        :return: 历史标记价格K线数据
        """
        params = {'instId': instId, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, HISTORY_MARK_PRICE_CANDLES, params)

    # GET /api/v5/market/option/instrument-family-trades 获取期权交易品种最新成交
    def instrument_family_trades(self, instFamily = ''):
        """
        获取期权交易品种最新成交
        :param instFamily: 交易品种 (可选)
        :return: 期权交易品种最新成交数据
        """
        params = {'instFamily':instFamily}
        return self._request_with_params(GET, INSTRUMENT_FAMILY_TRADES, params)

    # GET /api/v5/market/books-lite 获取轻量级深度数据
    def get_books_lite(self, instId=''):
        """
        获取轻量级深度数据
        :param instId: 产品ID (可选)
        :return: 轻量级深度数据
        """
        params = {'instId': instId}
        return self._request_with_params(GET, GET_BOOKS_LITE, params)

    # books_full 获取全量深度数据
    def books_full(self, instId='',sz=''):
        """
        获取全量深度数据
        :param instId: 产品ID (可选)
        :param sz: 深度档位 (可选)
        :return: 全量深度数据
        """
        params = {'instId': instId,'sz':sz}
        return self._request_with_params(GET, BOOKS_FULL, params)

    # GET /api/v5/market/call-auction-details 获取集合竞价信息
    def get_call_auction_details(self, instId=''):
        """
        获取集合竞价信息
        :param instId: 产品ID (可选)
        :return: 集合竞价信息
        """
        params = {'instId': instId}
        return self._request_with_params(GET, GET_CALL_AUCTION_DETAILS, params)