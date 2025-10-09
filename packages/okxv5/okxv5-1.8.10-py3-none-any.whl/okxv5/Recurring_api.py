from .client import Client
from .consts import *


class RecurringAPI(Client):
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类 Client 的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # POST /api/v5/tradingBot/recurring/order-algo
    def recurring_order_algo(self, stgyName = '', recurringList = [], period = '', recurringDay = '', recurringTime = '', timeZone = '', amt = '', investmentCcy = '', tdMode = '', algoClOrdId = '', tag = ''):
        """
        创建定投策略订单
        参数:
            stgyName: 策略名称
            recurringList: 定投列表，包含定投币种和比例等信息
            period: 定投周期类型
            recurringDay: 定投日 (period 为 weekly 或 monthly 时必填)
            recurringTime: 定投时间 (HH:MM)
            timeZone: 时区
            amt: 每期定投金额
            investmentCcy: 投资币种
            tdMode: 交易模式
            algoClOrdId: 用户自定义的策略订单 ID
            tag: 自定义标签
        """
        params = {'stgyName': stgyName, 'recurringList': recurringList, 'period': period, 'recurringDay':recurringDay, 'recurringTime': recurringTime,
        'timeZone': timeZone,'amt': amt,'investmentCcy': investmentCcy,'tdMode': tdMode,'algoClOrdId': algoClOrdId,'tag': tag}
        return self._request_with_params(POST, RECURRING_ORDER_ALGO, params)

    # POST /api/v5/tradingBot/recurring/amend-order-algo
    def recurring_amend_order_algo(self, algoId = '', stgyName = ''):
        """
        修改定投策略订单
        参数:
            algoId: 策略 ID
            stgyName: 策略名称 (修改后的名称)
        """
        params = {'algoId': algoId, 'stgyName': stgyName}
        return self._request_with_params(POST, RECURRING_AMEND_ORDER_ALGO, params)

    # POST /api/v5/tradingBot/recurring/stop-order-algo
    def recurring_stop_order_algo(self, orders_data):
        """
        停止定投策略订单
        参数:
            orders_data: 包含要停止的策略 ID 的数据列表
        """
        return self._request_with_params(POST, RECURRING_STOP_ORDER_ALGO, orders_data)

    # GET /api/v5/tradingBot/recurring/orders-algo-pending
    def recurring_orders_algo_pending(self, algoId = '', after = '', before = '', limit = ''):
        """
        获取定投策略待处理订单列表
        参数:
            algoId: 策略 ID
            after: 查询此 ID 之后的数据
            before: 查询此 ID 之前的数据
            limit: 返回结果的数量，默认 100，最大 100
        """
        params = {'algoId': algoId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, RECURRING_ORDER_ALGO_PENDING, params)

    # GET /api/v5/tradingBot/recurring/orders-algo-history
    def recurring_orders_algo_history(self, algoId = '', after = '', before = '', limit = ''):
        """
        获取定投策略历史订单列表
        参数:
            algoId: 策略 ID
            after: 查询此 ID 之后的数据
            before: 查询此 ID 之前的数据
            limit: 返回结果的数量，默认 100，最大 100
        """
        params = {'algoId': algoId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, RECURRING_ORDER_ALGO_HISTORY, params)

    # GET /api/v5/tradingBot/recurring/orders-algo-details
    def recurring_orders_algo_details(self, algoId = ''):
        """
        获取定投策略订单详情
        参数:
            algoId: 策略 ID (必填)
        """
        params = {'algoId': algoId}
        return self._request_with_params(GET, RECURRING_ORDER_ALGO_DETAILS, params)

    # GET /api/v5/tradingBot/recurring/sub-orders
    def recurring_sub_orders(self, algoId = '', ordId = '', after = '', before = '', limit = ''):
        """
        获取定投子订单列表
        参数:
            algoId: 策略 ID
            ordId: 子订单 ID
            after: 查询此 ID 之后的数据
            before: 查询此 ID 之前的数据
            limit: 返回结果的数量，默认 100，最大 100
        """
        params = {'algoId': algoId, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, RECURRING_SUB_ORDERS, params)
