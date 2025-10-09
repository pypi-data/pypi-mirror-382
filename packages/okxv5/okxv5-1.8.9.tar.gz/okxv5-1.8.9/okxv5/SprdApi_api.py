from .client import Client
from .consts import *


class SprdAPI(Client):
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类Client的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 下单 POST /api/v5/sprd/order
    # Place Order
    def place(self,sprdId,side,ordType,sz,px='',clOrdId='',tag='',):
        """
        下单
        :param sprdId: Spread ID，交易对，如 BTC-USD
        :param side: 订单方向，买或卖（buy, sell）
        :param ordType: 订单类型，如 limit（限价单），market（市价单）
        :param sz: 订单数量
        :param px: 价格，仅限限价单
        :param clOrdId: 客户自定义订单ID
        :param tag: 订单标签
        :return: 请求结果
        """
        params = {'sprdId':sprdId,'clOrdId':clOrdId,'tag':tag,'side':side,'ordType':ordType,
                  'sz':sz,'px':px,}
        return self._request_with_params(POST, SPRD_PLACE_ORDER, params)

    # 撤单 POST /api/v5/sprd/cancel-order
    # Cancel Order
    def cancel_order(self,ordId='',clOrdId=''):
        """
        撤销订单
        :param ordId: 订单ID
        :param clOrdId: 客户自定义订单ID
        :return: 请求结果
        """
        params = {'ordId':ordId,'clOrdId':clOrdId}
        return self._request_with_params(POST, SPRD_CANCEL_ORDER, params)

    # 全部撤单 POST /api/v5/sprd/mass-cancel
    # Mass Cancel Orders
    def mass_cancel(self,sprdId):
        """
        批量撤销订单
        :param sprdId: Spread ID，交易对
        :return: 请求结果
        """
        params = {'sprdId':sprdId}
        return self._request_with_params(POST, SPRD_MASS_CANCELS, params)

    # 修改订单 POST /api/v5/sprd/amend-order
    # Amend Order
    def amend_cancel(self,reqId='',ordId='', clOrdId='', newSz='', newPx=''):
        """
        修改订单
        :param reqId: 请求ID
        :param ordId: 订单ID
        :param clOrdId: 客户自定义订单ID
        :param newSz: 新的订单数量
        :param newPx: 新的订单价格
        :return: 请求结果
        """
        params = {'reqId':reqId, 'ordId':ordId, 'clOrdId':clOrdId, 'newSz':newSz, 'newPx':newPx, }
        return self._request_with_params(POST, SPRD_AMEND_CANCELS, params)

    # 获取订单信息 GET /api/v5/sprd/order
    # Get Order Details
    def order(self, ordId='', clOrdId=''):
        """
        获取订单信息
        :param ordId: 订单ID
        :param clOrdId: 客户自定义订单ID
        :return: 请求结果
        """
        params = {'ordId': ordId, 'clOrdId': clOrdId}
        return self._request_with_params(GET, SPRD_ORDER, params)

    # 获取未成交订单列表 GET /api/v5/sprd/orders-pending
    # Get Pending Orders List
    def orders_pending(self,sprdId='', ordType='', state='', beginId='', endId='', limit=''):
        """
        获取未成交订单列表
        :param sprdId: Spread ID，交易对
        :param ordType: 订单类型
        :param state: 订单状态
        :param beginId: 起始订单ID
        :param endId: 结束订单ID
        :param limit: 返回结果数量限制
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'ordType': ordType,
                  'state': state,
                  'endId': endId,
                  'beginId': beginId,'limit': limit,
                  }
        return self._request_with_params(GET, SPRD_ORDERS_PENDING, params)

    # 获取历史订单记录（近21天) GET /api/v5/sprd/orders-history
    # Get Order History (last 21 days)
    def orders_history(self,sprdId='',ordType='',state='',beginId='',endId='',limit='',
                       begin='',end='',):
        """
        获取历史订单记录（近21天）
        :param sprdId: Spread ID，交易对
        :param ordType: 订单类型
        :param state: 订单状态
        :param beginId: 起始订单ID
        :param endId: 结束订单ID
        :param limit: 返回结果数量限制
        :param begin: 查询起始时间戳
        :param end: 查询结束时间戳
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'ordType': ordType,
                  'state': state,'begin': begin, # 注意: 原始代码此处'begin': state可能是个错误，应为'begin': begin
                  'endId': endId,'end': end,     # 注意: 原始代码此处'end': endId可能是个错误，应为'end': end
                  'beginId': beginId, 'limit': limit,
                  }
        return self._request_with_params(GET, SPRD_ORDERS_HISTORY, params)


    # 获取历史订单记录（近3个月) GET /api/v5/sprd/orders-history-archive
    # Get Order History Archive (last 3 months)
    def orders_history_archive(self, sprdId='', ordType='', state='', beginId='', endId='', limit='',
                       begin='', end='', ):
        """
        获取历史订单记录（近3个月）
        :param sprdId: Spread ID，交易对
        :param ordType: 订单类型
        :param state: 订单状态
        :param beginId: 起始订单ID
        :param endId: 结束订单ID
        :param limit: 返回结果数量限制
        :param begin: 查询起始时间戳
        :param end: 查询结束时间戳
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'ordType': ordType,
                  'state': state, 'begin': begin, # 注意: 原始代码此处'begin': state可能是个错误，应为'begin': begin
                  'endId': endId, 'end': end,     # 注意: 原始代码此处'end': endId可能是个错误，应为'end': end
                  'beginId': beginId, 'limit': limit,
                  }
        return self._request_with_params(GET, SPRD_ORDERS_HISTORY_ARCHIVE, params)

    # 获取历史成交数据（近七天）GET /api/v5/sprd/trades
    # Get Trade History (last 7 days)
    def trades(self,sprdId='',tradeId='',ordId='',beginId='',endId='',limit='',begin='',end='',):
        """
        获取历史成交数据（近七天）
        :param sprdId: Spread ID，交易对
        :param tradeId: 成交ID
        :param ordId: 订单ID
        :param beginId: 起始成交ID
        :param endId: 结束成交ID
        :param limit: 返回结果数量限制
        :param begin: 查询起始时间戳
        :param end: 查询结束时间戳
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'ordId': ordId,'tradeId': tradeId,'begin': begin, # 注意: 原始代码此处'begin': state可能是个错误，应为'begin': begin
                  'endId': endId,'end': end, # 注意: 原始代码此处'end': endId可能是个错误，应为'end': end
                  'beginId': beginId, 'limit': limit,}
        return self._request_with_params(GET, SPRD_TRADES, params)

    # 获取Spreads（公共）GET /api/v5/sprd/spreads
    # Get Spreads (Public)
    def spreads(self,baseCcy='',instId='',sprdId='',state='',):
        """
        获取所有或指定Spread产品信息（公共）
        :param baseCcy: 标的币种
        :param instId: 乐器ID
        :param sprdId: Spread ID，交易对
        :param state: Spread产品状态
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'baseCcy': baseCcy, 'instId': instId,'state': state,}
        return self._request_with_params(GET, SPRD_SPREADS, params)

    # 获取Spread产品深度（公共）GET /api/v5/sprd/books
    # Get Spread Product Depth (Public)
    def books(self,sprdId='',sz='',):
        """
        获取Spread产品深度信息（公共）
        :param sprdId: Spread ID，交易对
        :param sz: 深度档位数量
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'sz': sz,}
        return self._request_with_params(GET, SPRD_BOOKS, params)

    # 获取单个Spread产品行情信息（公共） GET /api/v5/sprd/ticker
    # Get Single Spread Product Ticker (Public)
    def ticker(self,sprdId=''):
        """
        获取单个Spread产品行情信息（公共）
        :param sprdId: Spread ID，交易对
        :return: 请求结果
        """
        params = {'sprdId': sprdId}
        return self._request_with_params(GET, SPRD_TICKER, params)

    # 获取公共成交数据（公共）GET /api/v5/sprd/public-trades
    # Get Public Trade Data (Public)
    def public_trades(self,sprdId=''):
        """
        获取公共成交数据（公共）
        :param sprdId: Spread ID，交易对
        :return: 请求结果
        """
        params = {'sprdId': sprdId}
        return self._request_with_params(GET, SPRD_PUBLIC_TRADES, params)

    # POST /api/v5/sprd/cancel-all-after
    # Cancel All Orders After Timeout
    def sprd_cancel_all_after(self,timeOut=''):
        """
        设置自动撤销所有订单的倒计时
        :param timeOut: 倒计时（毫秒）
        :return: 请求结果
        """
        params = {'timeOut':timeOut }
        return self._request_with_params(POST, SPRD_CANCEL_ALL_AFTER, params)


    # GET /api/v5/market/sprd-candles
    # Get Spread Candlestick Data
    def get_sprd_candles(self,sprdId='', bar='', after='', before='', limit=''):
        """
        获取Spread产品K线数据
        :param sprdId: Spread ID，交易对
        :param bar: K线周期
        :param after: 查询起始时间戳
        :param before: 查询结束时间戳
        :param limit: 返回结果数量限制
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'bar': bar, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_SPRD_CANDLES, params)

    # GET /api/v5/market/sprd-history-candles
    # Get Spread Historical Candlestick Data
    def get_sprd_history_candles(self,sprdId='', bar='', after='', before='', limit=''):
        """
        获取Spread产品历史K线数据
        :param sprdId: Spread ID，交易对
        :param bar: K线周期
        :param after: 查询起始时间戳
        :param before: 查询结束时间戳
        :param limit: 返回结果数量限制
        :return: 请求结果
        """
        params = {'sprdId': sprdId, 'bar': bar, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, GET_SPRD_HISTORY_CANDLES, params)