# 从.client模块导入Client类
from .client import Client
# 从.consts模块导入所有常量
from .consts import *


# 定义TradingBotAPI类，它继承自Client类
class TradingBotAPI(Client):
    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类Client的构造函数进行初始化
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 创建网格策略订单
    def grid_order_algo(self, instId='', algoOrdType='', maxPx='', minPx='', gridNum='', runType='', tpTriggerPx='',
                        slTriggerPx='', tag='', quoteSz='', algoClOrdId='',
                        baseSz='', sz='', direction='', lever='', basePos='', tpRatio='', slRatio='',
                        profitSharingRatio='', triggerParams=[]):
        # 构建请求参数字典
        params = {'instId': instId, 'algoOrdType': algoOrdType, 'maxPx': maxPx, 'minPx': minPx, 'gridNum': gridNum,
                  'runType': runType, 'tpTriggerPx': tpTriggerPx, 'slTriggerPx': slTriggerPx, 'tag': tag,
                  'quoteSz': quoteSz, 'baseSz': baseSz, 'sz': sz, 'direction': direction, 'lever': lever,
                  'basePos': basePos,
                  'tpRatio': tpRatio, 'slRatio': slRatio, 'algoClOrdId': algoClOrdId,
                  'profitSharingRatio': profitSharingRatio, 'triggerParams': triggerParams}
        # 发送POST请求，创建网格策略订单
        return self._request_with_params(POST, GRID_ORDER_ALGO, params)

    # 修改网格策略订单
    def grid_amend_order_algo(self, algoId='', instId='', slTriggerPx='', tpTriggerPx='', tpRatio='', slRatio=''):
        # 构建请求参数字典
        params = {'algoId': algoId, 'instId': instId, 'slTriggerPx': slTriggerPx, 'tpTriggerPx': tpTriggerPx,
                  'tpRatio': tpRatio, 'slRatio': slRatio, }
        # 发送POST请求，修改网格策略订单
        return self._request_with_params(POST, GRID_AMEND_ORDER_ALGO, params)

    # 停止网格策略订单
    def grid_stop_order_algo(self, algoId='', instId='', algoOrdType='', stopType=''):
        # 构建请求参数列表（注意这里是一个包含字典的列表）
        params = [{'algoId': algoId, 'instId': instId, 'algoOrdType': algoOrdType, 'stopType': stopType}]
        # 发送POST请求，停止网格策略订单
        return self._request_with_params(POST, GRID_STOP_ORDER_ALGO, params)

    # 获取网格策略待处理订单列表
    def grid_orders_algo_pending(self, algoOrdType='', algoId='', instId='', instType='', after='', before='',
                                 limit=''):
        # 构建请求参数字典
        params = {'algoOrdType': algoOrdType, 'algoId': algoId, 'instId': instId, 'instType': instType,
                  'after': after, 'before': before, 'limit': limit}
        # 发送GET请求，获取网格策略待处理订单
        return self._request_with_params(GET, GRID_ORDERS_ALGO_PENDING, params)

    # 获取网格策略历史订单列表
    def grid_orders_algo_history(self, algoOrdType='', algoId='', instId='', instType='', after='', before='',
                                 limit=''):
        # 构建请求参数字典
        params = {'algoOrdType': algoOrdType, 'algoId': algoId, 'instId': instId, 'instType': instType,
                  'after': after, 'before': before, 'limit': limit}
        # 发送GET请求，获取网格策略历史订单
        return self._request_with_params(GET, GRID_ORDERS_ALGO_HISTORY, params)

    # 获取网格策略订单详情
    def grid_orders_algo_details(self, algoOrdType='', algoId=''):
        # 构建请求参数字典
        params = {'algoOrdType': algoOrdType, 'algoId': algoId}
        # 发送GET请求，获取网格策略订单详情
        return self._request_with_params(GET, GRID_ORDERS_ALGO_DETAILS, params)

    # 获取网格子订单列表
    def grid_sub_orders(self, algoId='', algoOrdType='', type='', groupId='', after='', before='', limit=''):
        # 构建请求参数字典
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, 'type': type, 'groupId': groupId, 'after': after,
                  'before': before, 'limit': limit}
        # 发送GET请求，获取网格子订单
        return self._request_with_params(GET, GRID_SUB_ORDERS, params)

    # 获取网格策略持仓信息
    def grid_positions(self, algoOrdType='', algoId=''):
        # 构建请求参数字典
        params = {'algoOrdType': algoOrdType, 'algoId': algoId}
        # 发送GET请求，获取网格策略持仓
        return self._request_with_params(GET, GRID_POSITIONS, params)

    # 提取网格策略收益
    def grid_withdraw_income(self, algoId=''):
        # 构建请求参数字典
        params = {'algoId': algoId}
        # 发送POST请求，提取网格策略收益
        return self._request_with_params(POST, GRID_WITHDRAW_INCOME, params)

    # 计算网格策略的保证金余额
    def grid_compute_margin_balance(self, algoId='', type='', amt=''):
        # 构建请求参数字典
        params = {'algoId': algoId, 'type': type, 'amt': amt}
        # 发送POST请求，计算网格策略保证金余额
        return self._request_with_params(POST, GRID_COMPUTE_MARGIN_BALANCE, params)

    # 调整网格策略的保证金
    def grid_margin_balance(self, algoId='', type='', amt='', percent=''):
        # 构建请求参数字典
        params = {'algoId': algoId, 'type': type, 'amt': amt, 'percent': percent}
        # 发送POST请求，调整网格策略保证金
        return self._request_with_params(POST, GRID_MARGIN_BALANCE, params)

    # 获取网格策略AI参数
    def grid_ai_param(self, algoOrdType='', instId='', direction='', duration=''):
        # 构建请求参数字典
        params = {'algoOrdType': algoOrdType, 'instId': instId, 'direction': direction, 'duration': duration}
        # 发送GET请求，获取网格策略AI参数
        return self._request_with_params(GET, GRID_AI_PARAM, params)

    # POST /api/v5/tradingBot/grid/adjust-investment
    # 调整网格策略的投入资金
    def grid_adjust_investment(self, algoId='', amt=''):
        # 构建请求参数字典
        params = {'algoId': algoId, 'amt': amt}
        # 发送POST请求，调整网格策略投入资金
        return self._request_with_params(POST, GRID_ADJUST_INVESTMETN, params)

    # GET /api/v5/tradingBot/grid/grid-quantity
    # 获取网格策略的网格数量
    def grid_quantity(self, instId='', runType='', algoOrdType='', maxPx='', minPx='', lever=''):
        # 构建请求参数字典
        params = {'instId': instId, 'runType': runType, 'algoOrdType': algoOrdType, 'maxPx': maxPx, 'minPx': minPx,
                  'lever': lever}
        # 发送GET请求，获取网格策略网格数量
        return self._request_with_params(GET, GRID_QUANTITY, params)