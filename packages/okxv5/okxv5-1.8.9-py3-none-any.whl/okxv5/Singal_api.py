# 从 .client 模块导入 Client 类
from .client import Client
# 从 .consts 模块导入所有常量
from .consts import *


# SignalApi 类继承自 Client 类
class SignalApi(Client):
    # 构造函数
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        # 调用父类 Client 的构造函数
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 创建信号通道
    def create_signal(self, signalChanName='', signalChanDesc=''):
        # 构建请求参数
        params = {'signalChanName': signalChanName, 'signalChanDesc': signalChanDesc}
        # 发送 POST 请求创建信号
        return self._request_with_params(POST, CREAT_SIGNAL, params)

    # 获取信号列表
    def signals(self, signalSourceType='', signalChanId='', after='', before='',
                limit='', ):
        # 构建请求参数
        params = {'signalSourceType': signalSourceType, 'signalChanId': signalChanId, 'after': after,
                  'before': before, 'limit': limit, }
        # 发送 GET 请求获取信号列表
        return self._request_with_params(GET, SIGNALS, params)

    # 策略下单
    def order_algo(self, includeAll='', signalChanId='', instIds='', lever='',
                   investAmt='', subOrdType='', ratio='', entrySettingParam='', exitSettingParam='', ):
        # 构建请求参数
        params = {'includeAll': includeAll, 'signalChanId': signalChanId, 'instIds': instIds,
                  'lever': lever, 'investAmt': investAmt, 'subOrdType': subOrdType, 'ratio': ratio,
                  'entrySettingParam': entrySettingParam,
                  'exitSettingParam': exitSettingParam}
        # 发送 POST 请求进行策略下单
        return self._request_with_params(POST, ORDER_ALGO_SIGNAL, params)

    # 停止策略订单
    def signal_stop_order_algo(self, algoId='', ):
        # 构建请求参数
        params = {'algoId': algoId, }
        # 发送 POST 请求停止策略订单
        return self._request_with_params(POST, SIGNAL_STOP_ORDER_ALGO, params)

    # 策略保证金余额操作
    def signal_margin_balance(self, algoId='', type='', amt='', allowReinvest='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'type': type, 'amt': amt, 'allowReinvest': allowReinvest, }
        # 发送 POST 请求进行保证金余额操作
        return self._request_with_params(POST, SIGNAL_MARGIN_BALANCE, params)

    # 修改止盈止损参数
    def amendTPSL(self, algoId='', exitSettingParam='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'exitSettingParam': exitSettingParam, }
        # 发送 POST 请求修改止盈止损参数
        return self._request_with_params(POST, AMENDTPSL, params)

    # 设置策略交易对
    def signal_set_instruments(self, algoId='', instIds='', includeAll=''):
        # 构建请求参数
        params = {'algoId': algoId, 'instIds': instIds, 'includeAll': includeAll}
        # 发送 POST 请求设置策略交易对
        return self._request_with_params(POST, SIGNAL_SET_INSTRUMENTS, params)

    # 获取策略订单详情
    def orders_algo_details(self, algoId='', algoOrdType='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, }
        # 发送 GET 请求获取策略订单详情
        return self._request_with_params(GET, ORDERS_ALGO_DETAILS, params)

    # 获取策略待处理订单
    def orders_algo_pending(self, algoId='', algoOrdType='', after='', before='', limit='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, 'after': after,
                  'before': before, 'limit': limit, }
        # 发送 GET 请求获取策略待处理订单
        return self._request_with_params(GET, ORDERS_ALGO_PENDING, params)

    # 获取策略历史订单
    def orders_algo_history(self, algoId='', algoOrdType='', after='', before='', limit='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, 'after': after,
                  'before': before, 'limit': limit, }
        # 发送 GET 请求获取策略历史订单
        return self._request_with_params(GET, ORDERS_ALGO_HISTORY, params)

    # 获取策略持仓
    def signal_positions(self, algoId='', algoOrdType='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, }
        # 发送 GET 请求获取策略持仓
        return self._request_with_params(GET, SIGNAL_POSITIONS, params)

    # 获取策略历史持仓
    def signal_positions_history(self, algoId='', instId='', after='', before='', limit='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'instId': instId, 'after': after,
                  'before': before, 'limit': limit, }
        # 发送 GET 请求获取策略历史持仓
        return self._request_with_params(GET, SIGNAL_POSITIONS_HISTORY, params)

    # 策略平仓
    def signal_close_position(self, algoId='', instId='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'instId': instId, }
        # 发送 POST 请求进行策略平仓
        return self._request_with_params(POST, SIGNAL_CLOSE_POSITION, params)

    # 下子订单
    def sub_order(self, algoId='', instId='', side='', ordType='', sz='', px='', reduceOnly=''):
        # 构建请求参数
        params = {'algoId': algoId, 'instId': instId, 'side': side, 'ordType': ordType, 'sz': sz, 'px': px,
                  'reduceOnly': reduceOnly, }
        # 发送 POST 请求下子订单
        return self._request_with_params(POST, SUB_ORDER, params)

    # 取消子订单
    def cancel_sub_order(self, algoId='', instId='', signalOrdId='', ):
        # 构建请求参数
        params = {'algoId': algoId, 'instId': instId, 'signalOrdId': signalOrdId, }
        # 发送 POST 请求取消子订单
        return self._request_with_params(POST, CANCEL_SUB_ORDER, params)

    # 获取子订单列表
    def sub_orders(self, algoId='', algoOrdType='', signalOrdId='', state='', after='', before='', limit='',
                   begin='', end='', type='', clOrdId=''):
        # 构建请求参数
        params = {'algoId': algoId, 'algoOrdType': algoOrdType, 'state': state, 'after': after, 'before': before,
                  'limit': limit,
                  'begin': begin, 'end': end, 'type': type, 'clOrdId': clOrdId, 'signalOrdId': signalOrdId, }
        # 发送 GET 请求获取子订单列表
        return self._request_with_params(GET, SUB_ORDERS, params)

    # 获取事件历史
    def event_history(self, algoId='', after='', before='', limit='',
                      ):
        # 构建请求参数
        params = {'algoId': algoId, 'after': after, 'before': before, 'limit': limit,
                  }
        # 发送 GET 请求获取事件历史
        return self._request_with_params(GET, EVENT_HISTORY, params)
