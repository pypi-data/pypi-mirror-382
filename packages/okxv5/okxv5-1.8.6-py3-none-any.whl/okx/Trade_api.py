from .client import Client
from .consts import *


class TradeAPI(Client):
    """
    交易API类，继承自Client，用于执行各种交易操作。
    """

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        初始化TradeAPI客户端。

        Args:
            api_key (str): API密钥。
            api_secret_key (str): API秘密密钥。
            passphrase (str): 密码。
            use_server_time (bool, optional): 是否使用服务器时间。默认为False。
            flag (str, optional): 区域标识。默认为'1'。
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Place Order 下单
    def place_order(self, instId, tdMode, side, ordType, sz, ccy='', clOrdId='', tag='', posSide='', px='',
                    reduceOnly='', tgtCcy='', banAmend='',quickMgnType='',tpTriggerPx = '', tpOrdPx = '',
                    slTriggerPx = '', slOrdPx = '', tpTriggerPxType = '', slTriggerPxType = '',stpId='',
                    stpMode='',attachAlgoClOrdId=''):
        """
        下单。

        Args:
            instId (str): 产品ID。
            tdMode (str): 交易模式。
            side (str): 交易方向。
            ordType (str): 订单类型。
            sz (str): 订单数量。
            ccy (str, optional): 保证金币种。默认为空。
            clOrdId (str, optional): 客户自定义订单ID。默认为空。
            tag (str, optional): 订单标签。默认为空。
            posSide (str, optional): 持仓方向。默认为空。
            px (str, optional): 委托价格。默认为空。
            reduceOnly (str, optional): 是否只减仓。默认为空。
            tgtCcy (str, optional): 交易币种。默认为空。
            banAmend (str, optional): 是否禁止修改。默认为空。
            quickMgnType (str, optional): 快速追加保证金类型。默认为空。
            tpTriggerPx (str, optional): 止盈触发价。默认为空。
            tpOrdPx (str, optional): 止盈委托价。默认为空。
            slTriggerPx (str, optional): 止损触发价。默认为空。
            slOrdPx (str, optional): 止损委托价。默认为空。
            tpTriggerPxType (str, optional): 止盈触发价类型。默认为空。
            slTriggerPxType (str, optional): 止损触发价类型。默认为空。
            stpId (str, optional): 自成交保护ID。默认为空。
            stpMode (str, optional): 自成交保护模式。默认为空。
            attachAlgoClOrdId (str, optional): 关联的策略订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
                  'clOrdId': clOrdId, 'tag': tag, 'posSide': posSide, 'px': px, 'reduceOnly': reduceOnly,
                  'tgtCcy': tgtCcy, 'banAmend': banAmend,'quickMgnType':quickMgnType,'tpTriggerPx':tpTriggerPx,'tpOrdPx':tpOrdPx,'slTriggerPx':slTriggerPx
                  ,'slOrdPx':slOrdPx,'tpTriggerPxType':tpTriggerPxType,'slTriggerPxType':slTriggerPxType,
                  'stpId':stpId,'stpMode':stpMode,'attachAlgoClOrdId':attachAlgoClOrdId}
        return self._request_with_params(POST, PLACR_ORDER, params)

    # Place Multiple Orders 批量下单
    def place_multiple_orders(self, orders_data):
        """
        批量下单。

        Args:
            orders_data (list): 订单数据列表。
        Returns:
            dict: API请求结果。
        """
        return self._request_with_params(POST, BATCH_ORDERS, orders_data)

    # Cancel Order 撤销订单
    def cancel_order(self, instId, ordId='', clOrdId=''):
        """
        撤销订单。

        Args:
            instId (str): 产品ID。
            ordId (str, optional): 订单ID。默认为空。
            clOrdId (str, optional): 客户自定义订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'ordId': ordId, 'clOrdId': clOrdId}
        return self._request_with_params(POST, CANAEL_ORDER, params)

    # Cancel Multiple Orders 批量撤销订单
    def cancel_multiple_orders(self, orders_data):
        """
        批量撤销订单。

        Args:
            orders_data (list): 订单数据列表。
        Returns:
            dict: API请求结果。
        """
        return self._request_with_params(POST, CANAEL_BATCH_ORDERS, orders_data)

    # Amend Order 修改订单
    def amend_order(self, instId, cxlOnFail='', ordId='', clOrdId='', reqId='', newSz='',
                    newPx = '', newTpTriggerPx='', newTpOrdPx='',newSlTriggerPx='', newSlOrdPx='',
                    newTpTriggerPxType='', newSlTriggerPxType=''):
        """
        修改订单。

        Args:
            instId (str): 产品ID。
            cxlOnFail (str, optional): 订单修改失败后是否自动撤销。默认为空。
            ordId (str, optional): 订单ID。默认为空。
            clOrdId (str, optional): 客户自定义订单ID。默认为空。
            reqId (str, optional): 请求ID。默认为空。
            newSz (str, optional): 新的订单数量。默认为空。
            newPx (str, optional): 新的委托价格。默认为空。
            newTpTriggerPx (str, optional): 新的止盈触发价。默认为空。
            newTpOrdPx (str, optional): 新的止盈委托价。默认为空。
            newSlTriggerPx (str, optional): 新的止损触发价。默认为空。
            newSlOrdPx (str, optional): 新的止损委托价。默认为空。
            newTpTriggerPxType (str, optional): 新的止盈触发价类型。默认为空。
            newSlTriggerPxType (str, optional): 新的止损触发价类型。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'cxlOnFailc': cxlOnFail, 'ordId': ordId, 'clOrdId': clOrdId, 'reqId': reqId,
                  'newSz': newSz,'newPx': newPx,'newTpTriggerPx': newTpTriggerPx,'newTpOrdPx': newTpOrdPx,
                  'newSlTriggerPx': newSlTriggerPx,'newSlOrdPx': newSlOrdPx,'newTpTriggerPxType': newTpTriggerPxType,
                  'newSlTriggerPxType': newSlTriggerPxType}
        return self._request_with_params(POST, AMEND_ORDER, params)

    # Amend Multiple Orders 批量修改订单
    def amend_multiple_orders(self, orders_data):
        """
        批量修改订单。

        Args:
            orders_data (list): 订单数据列表。
        Returns:
            dict: API请求结果。
        """
        return self._request_with_params(POST, AMEND_BATCH_ORDER, orders_data)

    # Close Positions 平仓
    def close_positions(self, instId, mgnMode, posSide='', ccy='',autoCxl='',clOrdId='',tag=''):
        """
        平仓。

        Args:
            instId (str): 产品ID。
            mgnMode (str): 保证金模式。
            posSide (str, optional): 持仓方向。默认为空。
            ccy (str, optional): 保证金币种。默认为空。
            autoCxl (str, optional): 是否自动撤销。默认为空。
            clOrdId (str, optional): 客户自定义订单ID。默认为空。
            tag (str, optional): 订单标签。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'mgnMode': mgnMode, 'posSide': posSide, 'ccy': ccy,'autoCxl':autoCxl,'clOrdId':clOrdId,'tag':tag}
        return self._request_with_params(POST, CLOSE_POSITION, params)

    # Get Order Details 获取订单详情
    def get_orders(self, instId, ordId='', clOrdId=''):
        """
        获取订单详情。

        Args:
            instId (str): 产品ID。
            ordId (str, optional): 订单ID。默认为空。
            clOrdId (str, optional): 客户自定义订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'ordId': ordId, 'clOrdId': clOrdId}
        return self._request_with_params(GET, ORDER_INFO, params)

    # Get Order List 获取订单列表
    def get_order_list(self, instType='', uly='', instId='', ordType='', state='', after='', before='', limit='', instFamily = ''):
        """
        获取订单列表。

        Args:
            instType (str, optional): 产品类型。默认为空。
            uly (str, optional): 标的。默认为空。
            instId (str, optional): 产品ID。默认为空。
            ordType (str, optional): 订单类型。默认为空。
            state (str, optional): 订单状态。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            instFamily (str, optional): 产品族。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'ordType': ordType, 'state': state,
                  'after': after, 'before': before, 'limit': limit, 'instFamily':instFamily}
        return self._request_with_params(GET, ORDERS_PENDING, params)

    # Get Order History (last 7 days）获取订单历史（最近7天）
    def get_orders_history(self, instType='', uly='', instId='', ordType='', state='', after='', before='', limit='', instFamily ='', category = '', begin = '', end = ''):
        """
        获取订单历史（最近7天）。

        Args:
            instType (str, optional): 产品类型。默认为空。
            uly (str, optional): 标的。默认为空。
            instId (str, optional): 产品ID。默认为空。
            ordType (str, optional): 订单类型。默认为空。
            state (str, optional): 订单状态。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            instFamily (str, optional): 产品族。默认为空。
            category (str, optional): 订单种类。默认为空。
            begin (str, optional): 查询的起始时间。默认为空。
            end (str, optional): 查询的结束时间。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'ordType': ordType, 'state': state,
                  'after': after, 'before': before, 'limit': limit, 'instFamily': instFamily, 'category': category, 'begin': begin, 'end': end}
        return self._request_with_params(GET, ORDERS_HISTORY, params)

    # Get Order History (last 3 months) 获取订单历史（最近3个月）
    def orders_history_archive(self, instType, uly='', instId='', ordType='', state='', after='', before='', limit='', instFamily ='', category = '', begin = '', end = ''):
        """
        获取订单历史（最近3个月）。

        Args:
            instType (str): 产品类型。
            uly (str, optional): 标的。默认为空。
            instId (str, optional): 产品ID。默认为空。
            ordType (str, optional): 订单类型。默认为空。
            state (str, optional): 订单状态。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            instFamily (str, optional): 产品族。默认为空。
            category (str, optional): 订单种类。默认为空。
            begin (str, optional): 查询的起始时间。默认为空。
            end (str, optional): 查询的结束时间。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'ordType': ordType, 'state': state,
                  'after': after, 'before': before, 'limit': limit, 'instFamily': instFamily, 'category': category, 'begin': begin, 'end': end}
        return self._request_with_params(GET, ORDERS_HISTORY_ARCHIVE, params)

    # Get Transaction Details 获取成交明细
    def get_fills(self, instType='', uly='', instId='', ordId='', after='', before='',
                  limit='', instFamily = '', begin = '', end = '',subType=''):
        """
        获取成交明细。

        Args:
            instType (str, optional): 产品类型。默认为空。
            uly (str, optional): 标的。默认为空。
            instId (str, optional): 产品ID。默认为空。
            ordId (str, optional): 订单ID。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            instFamily (str, optional): 产品族。默认为空。
            begin (str, optional): 查询的起始时间。默认为空。
            end (str, optional): 查询的结束时间。默认为空。
            subType (str, optional): 交易类型。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'ordId': ordId, 'after': after, 'before': before,
                  'limit': limit, 'instFamily': instFamily, 'begin': begin, 'end': end,'subType':subType}
        return self._request_with_params(GET, ORDER_FILLS, params)

    # Place Algo Order 下策略订单
    def place_algo_order(self, instId='', tdMode='', side='', ordType='', sz='', ccy='',
                         posSide='', reduceOnly='', tpTriggerPx='',
                         tpOrdPx='', slTriggerPx='', slOrdPx='',
                         triggerPx='', orderPx='', tgtCcy='', pxVar='',
                         pxSpread='', cxlOnClosePos='',
                         szLimit='', pxLimit='', timeInterval='', tpTriggerPxType='', slTriggerPxType='',
                         callbackRatio='',callbackSpread='',activePx='',tag='',triggerPxType='',
                         algoClOrdId='',quickMgnType='',closeFraction='', attachAlgoClOrdId=''):
        """
        下策略订单。

        Args:
            instId (str, optional): 产品ID。默认为空。
            tdMode (str, optional): 交易模式。默认为空。
            side (str, optional): 交易方向。默认为空。
            ordType (str, optional): 订单类型。默认为空。
            sz (str, optional): 订单数量。默认为空。
            ccy (str, optional): 保证金币种。默认为空。
            posSide (str, optional): 持仓方向。默认为空。
            reduceOnly (str, optional): 是否只减仓。默认为空。
            tpTriggerPx (str, optional): 止盈触发价。默认为空。
            tpOrdPx (str, optional): 止盈委托价。默认为空。
            slTriggerPx (str, optional): 止损触发价。默认为空。
            slOrdPx (str, optional): 止损委托价。默认为空。
            triggerPx (str, optional): 触发价格。默认为空。
            orderPx (str, optional): 委托价格。默认为空。
            tgtCcy (str, optional): 交易币种。默认为空。
            pxVar (str, optional): 价格波动幅度。默认为空。
            pxSpread (str, optional): 价格点差。默认为空。
            cxlOnClosePos (str, optional): 平仓时是否自动撤销策略订单。默认为空。
            szLimit (str, optional): 数量限制。默认为空。
            pxLimit (str, optional): 价格限制。默认为空。
            timeInterval (str, optional): 时间间隔。默认为空。
            tpTriggerPxType (str, optional): 止盈触发价类型。默认为空。
            slTriggerPxType (str, optional): 止损触发价类型。默认为空。
            callbackRatio (str, optional): 回调比例。默认为空。
            callbackSpread (str, optional): 回调点差。默认为空。
            activePx (str, optional): 激活价格。默认为空。
            tag (str, optional): 订单标签。默认为空。
            triggerPxType (str, optional): 触发价格类型。默认为空。
            algoClOrdId (str, optional): 策略订单ID。默认为空。
            quickMgnType (str, optional): 快速追加保证金类型。默认为空。
            closeFraction (str, optional): 平仓比例。默认为空。
            attachAlgoClOrdId (str, optional): 关联的策略订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId': instId, 'tdMode': tdMode, 'side': side, 'ordType': ordType, 'sz': sz, 'ccy': ccy,
                  'posSide': posSide, 'reduceOnly': reduceOnly, 'tpTriggerPx': tpTriggerPx, 'tpOrdPx': tpOrdPx,
                  'slTriggerPx': slTriggerPx, 'slOrdPx': slOrdPx, 'triggerPx': triggerPx, 'orderPx': orderPx,
                  'tgtCcy': tgtCcy, 'pxVar': pxVar, 'szLimit': szLimit, 'pxLimit': pxLimit,
                  'timeInterval': timeInterval, 'cxlOnClosePos': cxlOnClosePos,
                  'pxSpread': pxSpread, 'tpTriggerPxType': tpTriggerPxType, 'slTriggerPxType': slTriggerPxType,
                  'callbackRatio' : callbackRatio, 'callbackSpread':callbackSpread,'activePx':activePx,
                  'tag':tag,'triggerPxType':triggerPxType,'algoClOrdId':algoClOrdId,'quickMgnType':quickMgnType,
                  'closeFraction':closeFraction, 'attachAlgoClOrdId':attachAlgoClOrdId}
        return self._request_with_params(POST, PLACE_ALGO_ORDER, params)

    # Cancel Algo Order 撤销策略订单
    def cancel_algo_order(self, params):
        """
        撤销策略订单。

        Args:
            params (dict): 撤销策略订单的参数。
        Returns:
            dict: API请求结果。
        """
        return self._request_with_params(POST, CANCEL_ALGOS, params)

    # POST /api/v5/trade/amend-algos 修改策略订单
    def amend_algos(self, instId='', algoId='', algoClOrdId='', cxlOnFail = '',reqId = '',newSz = '',
                    newTpTriggerPx = '',newTpOrdPx = '',newSlTriggerPx = '',
                    newSlOrdPx = '',newTpTriggerPxType = '',newSlTriggerPxType='',
                    newTriggerPx='',newOrdPx='',newTriggerPxType='',attachAlgoOrds=[]):
        """
        修改策略订单。

        Args:
            instId (str, optional): 产品ID。默认为空。
            algoId (str, optional): 策略订单ID。默认为空。
            algoClOrdId (str, optional): 客户自定义策略订单ID。默认为空。
            cxlOnFail (str, optional): 订单修改失败后是否自动撤销。默认为空。
            reqId (str, optional): 请求ID。默认为空。
            newSz (str, optional): 新的订单数量。默认为空。
            newTpTriggerPx (str, optional): 新的止盈触发价。默认为空。
            newTpOrdPx (str, optional): 新的止盈委托价。默认为空。
            newSlTriggerPx (str, optional): 新的止损触发价。默认为空。
            newSlOrdPx (str, optional): 新的止损委托价。默认为空。
            newTpTriggerPxType (str, optional): 新的止盈触发价类型。默认为空。
            newSlTriggerPxType (str, optional): 新的止损触发价类型。默认为空。
            newTriggerPx (str, optional): 新的触发价格。默认为空。
            newOrdPx (str, optional): 新的委托价格。默认为空。
            newTriggerPxType (str, optional): 新的触发价格类型。默认为空。
            attachAlgoOrds (list, optional): 关联的策略订单列表。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instId':instId,'algoId':algoId,'algoClOrdId':algoClOrdId,'cxlOnFail':cxlOnFail,
                  'reqId':reqId,'newSz':newSz,'newTpTriggerPx':newTpTriggerPx,'newTpOrdPx':newTpOrdPx,
                  'newSlTriggerPx':newSlTriggerPx,'newSlOrdPx':newSlOrdPx,'newTpTriggerPxType':newTpTriggerPxType,
                  'newSlTriggerPxType':newSlTriggerPxType,'newTriggerPx':newTriggerPx, 'newOrdPx':newOrdPx, 'newTriggerPxType':newTriggerPxType,
                  'attachAlgoOrds':attachAlgoOrds}
        return self._request_with_params(POST, AMEND_ALGOS, params)

    # Cancel Advance Algos 撤销高级策略订单
    def cancel_advance_algos(self, params):
        """
        撤销高级策略订单。

        Args:
            params (dict): 撤销高级策略订单的参数。
        Returns:
            dict: API请求结果。
        """
        return self._request_with_params(POST, Cancel_Advance_Algos, params)

    # Get Algo Order List 获取策略订单列表
    def order_algos_list(self, ordType, algoId='', instType='', instId='', after='', before='', limit='',algoClOrdId=''):
        """
        获取策略订单列表。

        Args:
            ordType (str): 订单类型。
            algoId (str, optional): 策略订单ID。默认为空。
            instType (str, optional): 产品类型。默认为空。
            instId (str, optional): 产品ID。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            algoClOrdId (str, optional): 客户自定义策略订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'ordType': ordType, 'algoId': algoId, 'instType': instType, 'instId': instId, 'after': after,
                  'before': before, 'limit': limit,'algoClOrdId':algoClOrdId}
        return self._request_with_params(GET, ORDERS_ALGO_OENDING, params)

    # Get Algo Order History 获取策略订单历史
    def order_algos_history(self, ordType, state='', algoId='', instType='', instId='', after='', before='', limit=''):
        """
        获取策略订单历史。

        Args:
            ordType (str): 订单类型。
            state (str, optional): 订单状态。默认为空。
            algoId (str, optional): 策略订单ID。默认为空。
            instType (str, optional): 产品类型。默认为空。
            instId (str, optional): 产品ID。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'ordType': ordType, 'state': state, 'algoId': algoId, 'instType': instType, 'instId': instId,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_ALGO_HISTORY, params)

    # Get Transaction Details History 获取成交明细历史
    def get_fills_history(self, instType, uly='', instId='', ordId='', after='', before='', limit='',subType=''):
        """
        获取成交明细历史。

        Args:
            instType (str): 产品类型。
            uly (str, optional): 标的。默认为空。
            instId (str, optional): 产品ID。默认为空。
            ordId (str, optional): 订单ID。默认为空。
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
            subType (str, optional): 交易类型。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType': instType, 'uly': uly, 'instId': instId, 'ordId': ordId, 'after': after, 'before': before,
                  'limit': limit,'subType':subType}
        return self._request_with_params(GET, ORDERS_FILLS_HISTORY, params)

    def easy_convert_currency_list(self, source = ''):
        """
        获取闪兑币种列表。

        Args:
            source (str, optional): 来源。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'source':source}
        return self._request_with_params(GET, EASY_CONVERT_CURRENCY_LIST, params)

    def easy_convert(self, fromCcy = '', toCcy = '', source = ''):
        """
        执行闪兑。

        Args:
            fromCcy (str, optional): 源币种。默认为空。
            toCcy (str, optional): 目标币种。默认为空。
            source (str, optional): 来源。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'fromCcy':fromCcy, 'toCcy':toCcy, 'source':source}
        return self._request_with_params(POST, EASY_CONVERT, params)

    def easy_convert_history(self, after = '', before = '', limit = ''):
        """
        获取闪兑历史记录。

        Args:
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, EASY_CONVERT_HISTORY, params)

    def one_click_repay_currency_list(self, debtType = ''):
        """
        获取一键还币币种列表。

        Args:
            debtType (str, optional): 负债类型。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'debtType':debtType}
        return self._request_with_params(GET, ONE_CLICK_REPAY_CURRENCY_LIST, params)

    def one_click_repay(self, debtCcy = '', repayCcy = ''):
        """
        执行一键还币。

        Args:
            debtCcy (str, optional): 负债币种。默认为空。
            repayCcy (str, optional): 还币币种。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'debtCcy':debtCcy, 'repayCcy':repayCcy}
        return self._request_with_params(POST, ONE_CLICK_REPAY, params)

    def one_click_repay_history(self, after = '', before = '', limit = ''):
        """
        获取一键还币历史记录。

        Args:
            after (str, optional): 查询ID的起始点。默认为空。
            before (str, optional): 查询ID的结束点。默认为空。
            limit (str, optional): 返回结果数量。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, ONE_CLICK_REPAY_HISTORY, params)

    # GET /api/v5/trade/order-algo 获取策略订单信息
    def get_order_algo(self, algoId = '', algoClOrdId = ''):
        """
        获取策略订单信息。

        Args:
            algoId (str, optional): 策略订单ID。默认为空。
            algoClOrdId (str, optional): 客户自定义策略订单ID。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'algoId':algoId, 'algoClOrdId':algoClOrdId}
        return self._request_with_params(GET, GET_ORDER_ALGO, params)

    # POST /api/v5/trade/mass-cancel 批量撤销订单
    def mass_cancel(self,instType= '',instFamily = '',lockInterval = ''):
        """
        批量撤销订单。

        Args:
            instType (str, optional): 产品类型。默认为空。
            instFamily (str, optional): 产品族。默认为空。
            lockInterval (str, optional): 锁定时间间隔。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instType':instType, 'instFamily':instFamily, 'lockInterval':lockInterval}
        return self._request_with_params(POST, MASS_CANCEL, params)

    def cancel_all_after(self,timeOut= '', tag = ''):
        """
        取消所有订单在指定时间后。

        Args:
            timeOut (str, optional): 超时时间（秒）。默认为空。
            tag (str, optional): 订单标签。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'timeOut': timeOut, 'tag': tag}
        return self._request_with_params(POST, CANCEL_ALL_AFTER, params)

    # POST / api / v5 / trade / fills - archive 成交明细归档
    def fills_archive(self,year, quarter):
        """
        获取成交明细归档。

        Args:
            year (int): 年份。
            quarter (int): 季度。
        Returns:
            dict: API请求结果。
        """
        params = {'year': year, 'quarter':quarter}
        return self._request_with_params(POST, FILLS_ARCHIVE, params)

    # GET / api / v5 / trade / fills - archive 获取成交明细归档
    def fills_archives(self,year, quarter):
        """
        获取成交明细归档。

        Args:
            year (int): 年份。
            quarter (int): 季度。
        Returns:
            dict: API请求结果。
        """
        params = {'year': year, 'quarter':quarter}
        return self._request_with_params(GET, FILLS_ARCHIVES, params)

    # POST /api/v5/trade/order-precheck 订单预检查
    def order_precheck(self,instid = '', tdMode = '', side = '', posSide = '', ordType = '', sz = '', px = '',
        reduceOnly = '', tgtCcy = '', attachAlgoOrds = []):
        """
        订单预检查。

        Args:
            instid (str, optional): 产品ID。默认为空。
            tdMode (str, optional): 交易模式。默认为空。
            side (str, optional): 交易方向。默认为空。
            posSide (str, optional): 持仓方向。默认为空。
            ordType (str, optional): 订单类型。默认为空。
            sz (str, optional): 订单数量。默认为空。
            px (str, optional): 委托价格。默认为空。
            reduceOnly (str, optional): 是否只减仓。默认为空。
            tgtCcy (str, optional): 交易币种。默认为空。
            attachAlgoOrds (list, optional): 关联的策略订单列表。默认为空。
        Returns:
            dict: API请求结果。
        """
        params = {'instid': instid, 'tdMode':tdMode, 'side':side, 'posSide':posSide, 'ordType':ordType,
        'sz':sz, 'px':px, 'reduceOnly':reduceOnly, 'tgtCcy':tgtCcy, 'attachAlgoOrds':attachAlgoOrds}
        return self._request_with_params(POST, ORDER_PRECHECK, params)