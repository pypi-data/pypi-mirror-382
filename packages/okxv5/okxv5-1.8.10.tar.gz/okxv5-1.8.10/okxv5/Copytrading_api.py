from .client import Client
from .consts import *


class CopytradingAPI(Client):
    """
    跟单交易API客户端
    继承自Client类，提供了跟单交易相关的API接口
    """

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        初始化CopytradingAPI客户端
        :param api_key: API Key
        :param api_secret_key: Secret Key
        :param passphrase: 交易密码
        :param use_server_time: 是否使用服务器时间，默认为False
        :param flag: 请求类型，默认为'1'
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # GET /api/v5/copytrading/current-subpositions
    def current_subpositions(self, instId='',after='', before='', limit='',uniqueCode='',subPosType=''):
        """
        获取当前跟单子仓位列表 (交易员/带单员)
        :param instId: 标的ID
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :param uniqueCode: 交易员唯一编码
        :param subPosType: 子仓类型
        :return: 当前跟单子仓位列表
        """
        params = {'instId': instId, 'after': after, 'before': before, 'limit': limit,'uniqueCode': uniqueCode,'subPosType': subPosType, }
        return self._request_with_params(GET, CURRENT_SUBPOSITIONS, params)

    # GET /api/v5/copytrading/subpositions-history
    def subpositions_history(self, instId='', after='', before='', limit='',subPosType=''):
        """
        获取跟单历史子仓位列表 (交易员/带单员)
        :param instId: 标的ID
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :param subPosType: 子仓类型
        :return: 跟单历史子仓位列表
        """
        params = {'instId': instId, 'after': after, 'before': before, 'limit': limit,'subPosType':subPosType}
        return self._request_with_params(GET, SUBPOSITIONS_HISTORY, params)

    # POST /api/v5/copytrading/algo-order
    def copytrading_algo_order(self, subPosId='', tpTriggerPx='', slTriggerPx='', tpTriggerPxType='',
                               slTriggerPxType='', tag='',subPosType='',tpOrdPx='',slOrdPx=''):
        """
        设置跟单止盈止损订单 (交易员/带单员)
        :param subPosId: 子仓ID
        :param tpTriggerPx: 止盈触发价
        :param slTriggerPx: 止损触发价
        :param tpTriggerPxType: 止盈触发价类型
        :param slTriggerPxType: 止损触发价类型
        :param tag: 自定义标签
        :param subPosType: 子仓类型
        :param tpOrdPx: 止盈委托价格
        :param slOrdPx: 止损委托价格
        :return: 止盈止损订单结果
        """
        params = {'subPosId': subPosId, 'tpTriggerPx': tpTriggerPx,'tpOrdPx': tpOrdPx,'slOrdPx': slOrdPx,
                  'slTriggerPx': slTriggerPx, 'tpTriggerPxType': tpTriggerPxType,
                  'slTriggerPxType': slTriggerPxType,'tag':tag,'subPosType':subPosType}
        return self._request_with_params(POST, COPYTRADING_ALGO_ORDER, params)

    # POST /api/v5/copytrading/close-subposition
    def copytrading_close_subposition(self, subPosId='',tag='',subPosType='',ordType='',px=''):
        """
        平仓跟单子仓位 (交易员/带单员)
        :param subPosId: 子仓ID
        :param tag: 自定义标签
        :param subPosType: 子仓类型
        :param ordType: 订单类型
        :param px: 委托价格
        :return: 平仓结果
        """
        params = {'subPosId': subPosId,'tag':tag,"subPosType":subPosType,"ordType":ordType,'px':px}
        return self._request_with_params(POST, COPYTRADING_CLOSE_POS, params)

    # GET /api/v5/copytrading/instruments
    def copytrading_instruments(self):
        """
        获取跟单交易员交易对 (带单员)
        :return: 跟单交易员交易对列表
        """
        params = {}
        return self._request_with_params(GET, COPYTRADING_INSTRUMENTS, params)

    # POST /api/v5/copytrading/set-instruments
    def copytrading_set_instruments(self, instId=''):
        """
        设置跟单交易员交易对 (带单员)
        :param instId: 交易对ID
        :return: 设置结果
        """
        params = {'instId': instId}
        return self._request_with_params(POST, COPYTRADING_SET_INSTRUMENTS, params)

    # GET /api/v5/copytrading/profit-sharing-details
    def profit_sharing_details(self, after='', before='', limit=''):
        """
        获取跟单员分润明细 (交易员)
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :return: 跟单员分润明细列表
        """
        params = {'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, PROFIT_SHARING_DETAILS, params)

    # GET /api/v5/copytrading/total-profit-sharing
    def total_profit_sharing(self):
        """
        获取总分润收益 (交易员)
        :return: 总分润收益
        """
        params = {}
        return self._request_with_params(GET, TOTAL_PROFIT_SHARING, params)

    # GET /api/v5/copytrading/unrealized-profit-sharing-details
    def unrealized_profit_sharing_details(self):
        """
        获取未结算分润明细 (交易员)
        :return: 未结算分润明细
        """
        params = {}
        return self._request_with_params(GET, UNREALIZED_PROFIT_SHARING_DETAILS, params)

    # POST / api / v5 / copytrading / first - copy - settings
    def first_copy_settings(self,instType='',uniqueCode='',copyMgnMode='',copyInstIdType='',instId='',copyMode='',
                                             copyTotalAmt='',copyAmt='',copyRatio='',tpRatio='',slRatio='',slTotalAmt='',
                                             subPosCloseType=''):
        """
        首次设置跟单参数 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param copyMgnMode: 跟单保证金模式
        :param copyInstIdType: 跟单交易对类型
        :param instId: 标的ID
        :param copyMode: 跟单模式
        :param copyTotalAmt: 跟单总金额
        :param copyAmt: 单笔跟单金额
        :param copyRatio: 跟单比例
        :param tpRatio: 止盈比例
        :param slRatio: 止损比例
        :param slTotalAmt: 总止损金额
        :param subPosCloseType: 子仓平仓类型
        :return: 设置结果
        """
        params = {'instType':instType,'uniqueCode':uniqueCode,'copyMgnMode':copyMgnMode,'copyInstIdType':copyInstIdType,'instId':instId,'copyMode':copyMode,
                  'copyTotalAmt':copyTotalAmt,'copyAmt':copyAmt,'copyRatio':copyRatio,'tpRatio':tpRatio,'slRatio':slRatio,
                  'slTotalAmt':slTotalAmt,'subPosCloseType':subPosCloseType,}
        return self._request_with_params(POST, FIRST_COPY_SETTINGS, params)

    # POST /api/v5/copytrading/amend-copy-settings
    def amend_copy_settings(self,instType='',uniqueCode='',copyMgnMode='',copyInstIdType='',instId='',copyMode='',
                                             copyTotalAmt='',copyAmt='',copyRatio='',tpRatio='',slRatio='',slTotalAmt='',
                                             subPosCloseType=''):
        """
        修改跟单参数 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param copyMgnMode: 跟单保证金模式
        :param copyInstIdType: 跟单交易对类型
        :param instId: 标的ID
        :param copyMode: 跟单模式
        :param copyTotalAmt: 跟单总金额
        :param copyAmt: 单笔跟单金额
        :param copyRatio: 跟单比例
        :param tpRatio: 止盈比例
        :param slRatio: 止损比例
        :param slTotalAmt: 总止损金额
        :param subPosCloseType: 子仓平仓类型
        :return: 修改结果
        """
        params = {'instType':instType,'uniqueCode':uniqueCode,'copyMgnMode':copyMgnMode,'copyInstIdType':copyInstIdType,'instId':instId,'copyMode':copyMode,
                  'copyTotalAmt':copyTotalAmt,'copyAmt':copyAmt,'copyRatio':copyRatio,'tpRatio':tpRatio,'slRatio':slRatio,
                  'slTotalAmt':slTotalAmt,'subPosCloseType':subPosCloseType,}
        return self._request_with_params(POST, AMEND_COPY_SETTINGS, params)

    # POST /api/v5/copytrading/stop-copy-trading
    def stop_copy_trading(self,instType='',uniqueCode='',subPosCloseType=''):
        """
        停止跟单 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param subPosCloseType: 子仓平仓类型
        :return: 停止结果
        """
        params = {'instType':instType,'uniqueCode':uniqueCode,'subPosCloseType':subPosCloseType,}
        return self._request_with_params(POST, STOP_COPY_SETTINGS, params)

    # GET /api/v5/copytrading/copy-trading
    def copy_settings(self,instType='',uniqueCode=''):
        """
        获取跟单参数 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 跟单参数
        """
        params = {'instType':instType,'uniqueCode':uniqueCode,}
        return self._request_with_params(GET, COPY_SETTINGS, params)

    # GET /api/v5/copytrading/batch-leverage-info
    def batch_leverage_inf(self,mgnMode='',uniqueCode='',instId=''):
        """
        批量获取交易员杠杆信息 (交易员)
        :param mgnMode: 保证金模式
        :param uniqueCode: 交易员唯一编码
        :param instId: 标的ID
        :return: 杠杆信息列表
        """
        params = {'mgnMode':mgnMode,'uniqueCode':uniqueCode,'instId':instId,}
        return self._request_with_params(GET, BATCH_LEVERAGE_INF, params)

    # POST /api/v5/copytrading/batch-set-leverage
    def batch_set_leverage(self,mgnMode='',lever='',instId=''):
        """
        批量设置交易员杠杆 (交易员)
        :param mgnMode: 保证金模式
        :param lever: 杠杆倍数
        :param instId: 标的ID
        :return: 设置结果
        """
        params = {'mgnMode':mgnMode,'lever':lever,'instId':instId,}
        return self._request_with_params(POST, BATCH_SET_LEVERAGE, params)

    # GET  /api/v5/copytrading/current-lead-traders
    def current_lead_traders(self,instType='',):
        """
        获取当前带单员列表 (带单员)
        :param instType: 产品类型
        :return: 当前带单员列表
        """
        params = {'instType':instType,}
        return self._request_with_params(GET, CURRENT_LEAD_TRADERS, params)

    # GET  /api/v5/copytrading/lead-traders-history
    def lead_traders_history(self, instType='',after='',before='',limit='', ):
        """
        获取历史带单员列表 (带单员)
        :param instType: 产品类型
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :return: 历史带单员列表
        """
        params = {'instType': instType,'after': after,'before': before,'limit': limit, }
        return self._request_with_params(GET, LEAD_TRADERS_HISTORY, params)

    # GET /api/v5/copytrading/public-lead-traders
    def public_lead_traders(instType='',sortType='',state='',minLeadDays='',minAssets='',maxAssets='',
                                             minAum='',maxAum='',dataVer='',page='',limit=''):
        """
        获取公共带单员列表
        :param instType: 产品类型
        :param sortType: 排序类型
        :param state: 状态
        :param minLeadDays: 最少带单天数
        :param minAssets: 最少资产
        :param maxAssets: 最多资产
        :param minAum: 最少管理资产
        :param maxAum: 最多管理资产
        :param dataVer: 数据版本
        :param page: 页码
        :param limit: 返回结果集数量，默认100
        :return: 公共带单员列表
        """
        params = {'instType': sortType, 'sortType': sortType, 'state': state, 'minLeadDays': minLeadDays,
                  'minAssets': minAssets, 'maxAssets': maxAssets, 'minAum': minAum, 'maxAum': maxAum,
                  'dataVer': dataVer, 'page': page, 'limit': limit,
                  }
        return self._request_with_params(GET, PUBLIC_LEAD_TRADERS, params)

    # GET /api/v5/copytrading/public-weekly-pnl
    def public_weekly_pnl(self, instType='', uniqueCode=''):
        """
        获取公共带单员周Pnl数据
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 周Pnl数据
        """
        params = {'instType': instType, 'uniqueCode': uniqueCode, }
        return self._request_with_params(GET, PUBLIC_WEEKLY_PNL, params)

    # GET /api/v5/copytrading/public-pnl
    def public_pnl(self, instType='', uniqueCode='',lastDays=''):
        """
        获取公共带单员Pnl数据
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param lastDays: 最近天数
        :return: Pnl数据
        """
        params = {'instType': instType, 'uniqueCode': uniqueCode, 'lastDays': lastDays}
        return self._request_with_params(GET, PUBLIC_PNL, params)

    # GET /api/v5/copytrading/public-stats
    def public_stats(self, instType='', uniqueCode='', lastDays=''):
        """
        获取公共带单员统计数据
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param lastDays: 最近天数
        :return: 统计数据
        """
        params = {'instType': instType, 'uniqueCode': uniqueCode, 'lastDays': lastDays}
        return self._request_with_params(GET, PUBLIC_STATS, params)

    # GET /api/v5/copytrading/public-preference-currency
    def public_preference_currency(self, instType='', uniqueCode=''):
        """
        获取公共带单员偏好币种
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 偏好币种
        """
        params = {'instType': instType, 'uniqueCode': uniqueCode, }
        return self._request_with_params(GET, PUBLIC_PRE_CURR, params)


    # GET /api/v5/copytrading/public-current-subpositions
    def public_current_subpositions(self, after='', before='', limit='', instType='', uniqueCode=''):
        """
        获取公共带单员当前跟单子仓位列表
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 公共带单员当前跟单子仓位列表
        """
        params = {'instType': instType,'after': after,'before': before,'limit': limit, 'uniqueCode':uniqueCode}
        return self._request_with_params(GET, PUBLIC_CURR_SUBPOS, params)

    # GET /api/v5/copytrading/public-subpositions-history
    def public_subpositions_history(self, after='', before='', limit='', instType='', uniqueCode=''):
        """
        获取公共带单员历史跟单子仓位列表
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 公共带单员历史跟单子仓位列表
        """
        params = {'instType': instType, 'after': after, 'before': before, 'limit': limit, 'uniqueCode': uniqueCode}
        return self._request_with_params(GET, PUBLIC_SUBPOS_HIS, params)

    def apply_lead_trading(self, instType='',instId='', ):
        """
        申请带单
        :param instType: 产品类型
        :param instId: 标的ID
        :return: 申请结果
        """
        params = {'instType': instType, 'instId': instId,}
        return self._request_with_params(POST, APP_LEA_TRAD, params)

    def stop_lead_trading(self, instType='',):
        """
        停止带单
        :param instType: 产品类型
        :return: 停止结果
        """
        params = {'instType': instType,}
        return self._request_with_params(POST, STOP_LEA_TRAD, params)


    def amend_profit_sharing_ratio(self, instType='',profitSharingRatio=''):
        """
        修改分润比例 (带单员)
        :param instType: 产品类型
        :param profitSharingRatio: 分润比例
        :return: 修改结果
        """
        params = {'instType': instType,'profitSharingRatio': profitSharingRatio}
        return self._request_with_params(POST, AMEDN_PRO_SHAR_RATIO, params)


    def lead_traders(self, instType='',sortType='',state='',minLeadDays='',minAssets='',maxAssets='',
                     minAum='',maxAum='',dataVer='',page='',limit='',):
        """
        获取带单员列表 (交易员)
        :param instType: 产品类型
        :param sortType: 排序类型
        :param state: 状态
        :param minLeadDays: 最少带单天数
        :param minAssets: 最少资产
        :param maxAssets: 最多资产
        :param minAum: 最少管理资产
        :param maxAum: 最多管理资产
        :param dataVer: 数据版本
        :param page: 页码
        :param limit: 返回结果集数量，默认100
        :return: 带单员列表
        """
        params = {'instType': instType,'sortType': sortType,'state': state,'minLeadDays': minLeadDays,
                  'minAssets': minAssets,'maxAssets': maxAssets,'minAum': minAum,'maxAum': maxAum,
                  'dataVer': dataVer,'page': page,'limit': limit,}
        return self._request_with_params(GET, LEAD_TRADERS, params)


    def weekly_pnl(self, instType='',uniqueCode=''):
        """
        获取交易员周Pnl数据 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 周Pnl数据
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,}
        return self._request_with_params(GET, WEEKLY_PNL, params)


    def pnl(self, instType='',uniqueCode='',lastDays = ''):
        """
        获取交易员Pnl数据 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param lastDays: 最近天数
        :return: Pnl数据
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'lastDays': lastDays,}
        return self._request_with_params(GET, PNL, params)


    def stats(self, instType='',uniqueCode='',lastDays = ''):
        """
        获取交易员统计数据 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param lastDays: 最近天数
        :return: 统计数据
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'lastDays': lastDays,}
        return self._request_with_params(GET, STATS, params)


    def preference_currency(self, instType='',uniqueCode=''):
        """
        获取交易员偏好币种 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :return: 偏好币种
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,}
        return self._request_with_params(GET, PRE_CURR, params)


    def performance_current_subpositions(self, instType='',uniqueCode='', after='', before='', limit='', ):
        """
        获取交易员当前跟单子仓位列表 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :return: 交易员当前跟单子仓位列表
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'after': after,'before': before,'limit': limit, }
        return self._request_with_params(GET, PRE_CURR_SUNPOSITION, params)


    def performance_subpositions_history(self, instType='',uniqueCode='', after='', before='', limit='', ):
        """
        获取交易员历史跟单子仓位列表 (交易员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param after: 查询ID，分页用
        :param before: 查询ID，分页用
        :param limit: 返回结果集数量，默认100
        :return: 交易员历史跟单子仓位列表
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'after': after,'before': before,'limit': limit, }
        return self._request_with_params(GET, PRE_SUNPOSITION_HISTORY, params)


    def copy_traders(self, instType='',uniqueCode='', limit='', ):
        """
        获取跟单员列表 (带单员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param limit: 返回结果集数量，默认100
        :return: 跟单员列表
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'limit': limit, }
        return self._request_with_params(GET, COPY_TRADERS, params)


    def public_copy_traders(self, instType='',uniqueCode='', limit='', ):
        """
        获取公共跟单员列表 (带单员)
        :param instType: 产品类型
        :param uniqueCode: 交易员唯一编码
        :param limit: 返回结果集数量，默认100
        :return: 公共跟单员列表
        """
        params = {'instType': instType,'uniqueCode': uniqueCode,'limit': limit, }
        return self._request_with_params(GET, PUB_COPY_TRADERS, params)


    def config(self, ):
        """
        获取跟单配置 (交易员/带单员)
        :return: 跟单配置
        """
        params = {}
        return self._request_with_params(GET, CONFIG, params)


    def total_unrealized_profit_sharing(self, instType = ''):
        """
        获取未结算总分润收益 (交易员)
        :param instType: 产品类型
        :return: 未结算总分润收益
        """
        params = {'instType':instType}
        return self._request_with_params(GET, TOTAL_UNREA_PRO_SHAR, params)
