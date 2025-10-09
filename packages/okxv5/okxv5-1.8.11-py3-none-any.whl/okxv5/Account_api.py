from .client import Client
from .consts import *


class AccountAPI(Client):
    """
    账户API类，继承自Client，用于与账户相关的操作
    """
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        初始化AccountAPI客户端
        :param api_key: API Key
        :param api_secret_key: API Secret Key
        :param passphrase: 密码
        :param use_server_time: 是否使用服务器时间，默认为False
        :param flag: 区域标识，默认为'1'
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取持仓风险
    def get_position_risk(self, instType=''):
        """
        获取持仓风险
        :param instType: 产品类型
        :return: 响应数据
        """
        params = {}
        if instType:
            params['instType'] = instType
        return self._request_with_params(GET, POSITION_RISK, params)

    # 获取余额
    def get_account(self, ccy=''):
        """
        获取账户余额信息
        :param ccy: 币种
        :return: 响应数据
        """
        params = {}
        if ccy:
            params['ccy'] = ccy
        return self._request_with_params(GET, ACCOUNT_INFO, params)

    # 获取持仓信息
    def get_positions(self, instType='', instId=''):
        """
        获取持仓信息
        :param instType: 产品类型
        :param instId: 产品ID
        :return: 响应数据
        """
        params = {'instType': instType, 'instId': instId}
        return self._request_with_params(GET, POSITION_INFO, params)

    # 获取账单明细 (近7天)
    def get_bills_detail(self, instType='', instId='', ccy='', mgnMode='', ctType='', type='', subType='', after='', before='',begin='',end='',
                         limit=''):
        """
        获取账单明细 (近7天)
        :param instType: 产品类型
        :param instId: 产品ID
        :param ccy: 币种
        :param mgnMode: 保证金模式
        :param ctType: 合约类型
        :param type: 账单类型
        :param subType: 账单子类型
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param begin: 起始时间戳
        :param end: 结束时间戳
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'instType': instType, 'ccy': ccy, 'mgnMode': mgnMode, 'ctType': ctType, 'type': type,
                  'subType': subType, 'after': after, 'before': before, 'limit': limit, 'instId':instId, 'begin':begin, 'end':end}
        return self._request_with_params(GET, BILLS_DETAIL, params)

    # 获取账单明细 (近3个月)
    def get_bills_details(self, instType='', instId = '', ccy='', mgnMode='', ctType='', type='', subType='', after='', before='',begin='',end='',
                          limit=''):
        """
        获取账单明细 (近3个月)
        :param instType: 产品类型
        :param instId: 产品ID
        :param ccy: 币种
        :param mgnMode: 保证金模式
        :param ctType: 合约类型
        :param type: 账单类型
        :param subType: 账单子类型
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param begin: 起始时间戳
        :param end: 结束时间戳
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'instType': instType, 'ccy': ccy, 'mgnMode': mgnMode, 'ctType': ctType, 'type': type,
                  'subType': subType, 'after': after, 'before': before, 'limit': limit, 'instId':instId, 'begin':begin, 'end':end}
        return self._request_with_params(GET, BILLS_ARCHIVE, params)

    # 获取账户配置
    def get_account_config(self):
        """
        获取账户配置
        :return: 响应数据
        """
        return self._request_without_params(GET, ACCOUNT_CONFIG)

    # 获取持仓模式
    def get_position_mode(self, posMode):
        """
        获取持仓模式
        :param posMode: 持仓模式
        :return: 响应数据
        """
        params = {'posMode': posMode}
        return self._request_with_params(POST, POSITION_MODE, params)

    # 设置杠杆
    def set_leverage(self, lever, mgnMode, instId='', ccy='', posSide=''):
        """
        设置杠杆
        :param lever: 杠杆倍数
        :param mgnMode: 保证金模式
        :param instId: 产品ID
        :param ccy: 币种
        :param posSide: 持仓方向
        :return: 响应数据
        """
        params = {'lever': lever, 'mgnMode': mgnMode, 'instId': instId, 'ccy': ccy, 'posSide': posSide}
        return self._request_with_params(POST, SET_LEVERAGE, params)

    # 获取单个产品最大可交易量
    def get_maximum_trade_size(self, instId, tdMode, ccy='', px='', leverage='',unSpotOffset=''):
        """
        获取单个产品最大可交易量
        :param instId: 产品ID
        :param tdMode: 交易模式
        :param ccy: 币种
        :param px: 价格
        :param leverage: 杠杆倍数
        :param unSpotOffset: 现货对冲模式下，对手方交易账户中的对手币种余额
        :return: 响应数据
        """
        params = {'instId': instId, 'tdMode': tdMode, 'ccy': ccy, 'px': px, 'leverage':leverage,'unSpotOffset':unSpotOffset}
        return self._request_with_params(GET, MAX_TRADE_SIZE, params)

    # 获取最大可用交易量
    def get_max_avail_size(self, instId, tdMode, ccy='', reduceOnly='', unSpotOffset='',quickMgnType='',px=''):
        """
        获取最大可用交易量
        :param instId: 产品ID
        :param tdMode: 交易模式
        :param ccy: 币种
        :param reduceOnly: 是否只减仓
        :param unSpotOffset: 现货对冲模式下，对手方交易账户中的对手币种余额
        :param quickMgnType: 快捷杠杆类型
        :param px: 价格
        :return: 响应数据
        """
        params = {'instId': instId, 'tdMode': tdMode, 'ccy': ccy, 'reduceOnly': reduceOnly,
                  'unSpotOffset':unSpotOffset,'quickMgnType':quickMgnType,'px': px}
        return self._request_with_params(GET, MAX_AVAIL_SIZE, params)

    # 调整保证金
    def Adjustment_margin(self, instId, posSide, type, amt,loanTrans=''):
        """
        调整保证金
        :param instId: 产品ID
        :param posSide: 持仓方向
        :param type: 调整类型
        :param amt: 调整金额
        :param loanTrans: 借币还币场景
        :return: 响应数据
        """
        params = {'instId': instId, 'posSide': posSide, 'type': type, 'amt': amt,'loanTrans':loanTrans}
        return self._request_with_params(POST, ADJUSTMENT_MARGIN, params)

    # 获取杠杆
    def get_leverage(self, instId, mgnMode, ccy):
        """
        获取杠杆倍数
        :param instId: 产品ID
        :param mgnMode: 保证金模式
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'instId': instId, 'mgnMode': mgnMode, 'ccy':ccy}
        return self._request_with_params(GET, GET_LEVERAGE, params)

    # 获取逐仓最大可借币量
    def get_max_load(self, instId, mgnMode, mgnCcy):
        """
        获取逐仓最大可借币量
        :param instId: 产品ID
        :param mgnMode: 保证金模式
        :param mgnCcy: 保证金币种
        :return: 响应数据
        """
        params = {'instId': instId, 'mgnMode': mgnMode, 'mgnCcy': mgnCcy}
        return self._request_with_params(GET, MAX_LOAN, params)

    # 获取手续费率
    def get_fee_rates(self, instType = '', instId='', uly='', category='', instFamily='',ruleType = ''):
        """
        获取手续费率
        :param instType: 产品类型
        :param instId: 产品ID
        :param uly: 标的指数
        :param category: 市场分类
        :param instFamily: 产品族
        :param ruleType: 规则类型
        :return: 响应数据
        """
        params = {'instType': instType, 'instId': instId, 'uly': uly, 'category': category,'instFamily':instFamily,'ruleType':ruleType}
        return self._request_with_params(GET, FEE_RATES, params)

    # 获取计息记录
    def get_interest_accrued(self, instId='', ccy='', mgnMode='', after='', before='', limit='', type=''):
        """
        获取计息记录
        :param instId: 产品ID
        :param ccy: 币种
        :param mgnMode: 保证金模式
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :param type: 利率类型
        :return: 响应数据
        """
        params = {'instId': instId, 'ccy': ccy, 'mgnMode': mgnMode, 'after': after, 'before': before, 'limit': limit, 'type':type}
        return self._request_with_params(GET, INTEREST_ACCRUED, params)

    # 获取借币利率
    def get_interest_rate(self, ccy=''):
        """
        获取借币利率
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'ccy': ccy}
        return self._request_with_params(GET, INTEREST_RATE, params)

    # 设置Greeks (PA/BS)
    def set_greeks(self, greeksType):
        """
        设置Greeks (PA/BS)
        :param greeksType: Greeks类型
        :return: 响应数据
        """
        params = {'greeksType': greeksType}
        return self._request_with_params(POST, SET_GREEKS, params)

    # 设置逐仓模式
    def set_isolated_mode(self, isoMode,type):
        """
        设置逐仓模式
        :param isoMode: 逐仓模式
        :param type: 类型
        :return: 响应数据
        """
        params = {'isoMode': isoMode, 'type':type}
        return self._request_with_params(POST, ISOLATED_MODE, params)

    # 获取最大提币量
    def get_max_withdrawal(self, ccy=''):
        """
        获取最大提币量
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'ccy': ccy}
        return self._request_with_params(GET, MAX_WITHDRAWAL, params)

    # 获取账户风险状态
    def get_account_risk(self):
        """
        获取账户风险状态
        :return: 响应数据
        """
        return self._request_without_params(GET, ACCOUNT_RISK)

    # 借币/还币
    def borrow_repay(self, ccy='', side='', amt='', ordId = ''):
        """
        借币/还币
        :param ccy: 币种
        :param side: 方向 (borrow:借入, repay:归还)
        :param amt: 数量
        :param ordId: 订单ID
        :return: 响应数据
        """
        params = {'ccy': ccy, 'side': side, 'amt': amt, 'ordId':ordId}
        return self._request_with_params(POST, BORROW_REPAY, params)

    # 获取借币/还币历史
    def get_borrow_repay_history(self, ccy='', after='', before='', limit=''):
        """
        获取借币/还币历史
        :param ccy: 币种
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ccy': ccy, 'after': after, 'before': before, 'limit':limit}
        return self._request_with_params(GET, BORROW_REPAY_HISTORY, params)

    # 获取借币利率及限额
    def get_interest_limits(self, type='',ccy=''):
        """
        获取借币利率及限额
        :param type: 类型
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'type': type, 'ccy': ccy}
        return self._request_with_params(GET, INTEREST_LIMITS, params)

    # 获取模拟保证金
    def get_simulated_margin(self, instType	='',inclRealPos='',spotOffsetType='',simPos=[]):
        """
        获取模拟保证金
        :param instType: 产品类型
        :param inclRealPos: 是否包含真实仓位
        :param spotOffsetType: 现货对冲模式类型
        :param simPos: 模拟持仓
        :return: 响应数据
        """
        params = {'instType': instType, 'inclRealPos': inclRealPos,'spotOffsetType':spotOffsetType,'simPos': simPos}
        return self._request_with_params(POST, SIMULATED_MARGIN, params)

    # 获取Greeks
    def get_greeks(self, ccy=''):
        """
        获取Greeks
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'ccy': ccy,}
        return self._request_with_params(GET, GREEKS, params)

    def get_positions_history(self, instType='', instId = '', mgnMode = '', type = '', after = '', before = '', limit = '', posId = ''):
        """
        获取历史持仓信息
        :param instType: 产品类型
        :param instId: 产品ID
        :param mgnMode: 保证金模式
        :param type: 类型
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :param posId: 持仓ID
        :return: 响应数据
        """
        params = {'instType': instType, 'instId':instId, 'mgnMode':mgnMode, 'type':type, 'after':after, 'before':before, 'limit':limit, 'posId':posId}
        return self._request_with_params(GET, POSITIONS_HISTORY, params)

    def position_tiers(self, instType='',uly=''):
        """
        获取持仓档位
        :param instType: 产品类型
        :param uly: 标的指数
        :return: 响应数据
        """
        params = {'instType': instType, 'uly': uly}
        return self._request_with_params(GET, POSITION_TIRES, params)

    def activate_option(self):
        """
        激活期权
        :return: 响应数据
        """
        params = {}
        return self._request_with_params(POST, ACTIVATE_OPTION, params)

    def set_auto_loan(self,autoLoan = ''):
        """
        设置自动借币
        :param autoLoan: 是否自动借币
        :return: 响应数据
        """
        params = {'autoLoan':autoLoan}
        return self._request_with_params(POST, SET_AUTO_LOAN, params)

    def quick_margin_borrow_repay(self, instId='', ccy='', side='', amt=''):
        """
        快捷杠杆借币/还币
        :param instId: 产品ID
        :param ccy: 币种
        :param side: 方向 (borrow:借入, repay:归还)
        :param amt: 数量
        :return: 响应数据
        """
        params = {'instId':instId, 'ccy':ccy, 'side':side, 'amt':amt}
        return self._request_with_params(POST, QUICK_MARGIN_BRROW_REPAY, params)

    def quick_margin_borrow_repay_history(self, instId='', ccy='', side='', after='', before='', begin='', end='', limit=''):
        """
        获取快捷杠杆借币/还币历史
        :param instId: 产品ID
        :param ccy: 币种
        :param side: 方向 (borrow:借入, repay:归还)
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param begin: 起始时间戳
        :param end: 结束时间戳
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'instId': instId, 'ccy': ccy, 'side': side, 'after': after, 'before': before, 'begin': begin, 'end': end, 'limit': limit}
        return self._request_with_params(GET, QUICK_MARGIN_BORROW_REPAY_HISTORY, params)

    # GET /api/v5/account/vip-interest-accrued
    def vip_interest_accrued(self, ccy = '', ordId = '', after = '', before = '', limit = ''):
        """
        获取VIP计息记录
        :param ccy: 币种
        :param ordId: 订单ID
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, VIP_INTEREST_ACCRUED, params)

    # GET /api/v5/account/vip-interest-deducted
    def vip_interest_deducted(self, ccy = '', ordId = '', after = '', before = '', limit = ''):
        """
        获取VIP扣息记录
        :param ccy: 币种
        :param ordId: 订单ID
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, VIP_INTEREST_DEDUCTED, params)

    # GET /api/v5/account/vip-loan-order-list
    def vip_loan_order_list(self, ordId = '', state = '', ccy = '', after = '', before = '', limit = ''):
        """
        获取VIP借贷订单列表
        :param ordId: 订单ID
        :param state: 订单状态
        :param ccy: 币种
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ordId': ordId, 'state': state, 'ccy': ccy, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, VIP_LOAN_ORDER_LIST, params)

    # GET /api/v5/account/vip-loan-order-detail
    def vip_loan_order_detail(self, ccy = '', ordId = '', after = '', before = '', limit = ''):
        """
        获取VIP借贷订单详情
        :param ccy: 币种
        :param ordId: 订单ID
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ccy': ccy, 'ordId': ordId, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, VIP_LOAN_ORDER_DETAIL, params)

    # POST /api/v5/account/subaccount/set-loan-allocation
    def set_loan_allocation(self, enable, alloc:[]):
        """
        设置借贷分配
        :param enable: 是否启用
        :param alloc: 分配列表
        :return: 响应数据
        """
        params = {'enable': enable, 'alloc': alloc}
        return self._request_with_params(POST, SET_LOAN_ALLOCATION, params)

    # GET /api/v5/account/subaccount/interest-limits
    def interest_limits(self, subAcct = '', ccy = ''):
        """
        获取子账户借币限额
        :param subAcct: 子账户名称
        :param ccy: 币种
        :return: 响应数据
        """
        params = {'subAcct': subAcct, 'ccy': ccy}
        return self._request_with_params(GET, INTEREST_LIMITS, params)

    # POST /api/v5/account/set-riskOffset-type
    def set_riskOffset_type(self, type = ''):
        """
        设置风险对冲类型
        :param type: 风险对冲类型
        :return: 响应数据
        """
        params = {'type':type}
        return self._request_with_params(POST, SET_RISKOFFSET_TYPE, params)

    # POST /api/v5/account/mmp-reset
    def mmp_reset(self,instType,instFamily):
        """
        MMP重置
        :param instType: 产品类型
        :param instFamily: 产品族
        :return: 响应数据
        """
        params = {'instType': instType,'instFamily':instFamily}
        return self._request_with_params(POST, MMP_RESET, params)

    # POST /api/v5/account/mmp-config
    def mmp_config(self,instFamily,timeInterval,frozenInterval,qtyLimit):
        """
        MMP配置
        :param instFamily: 产品族
        :param timeInterval: 时间间隔
        :param frozenInterval: 冻结间隔
        :param qtyLimit: 数量限制
        :return: 响应数据
        """
        params = {'instFamily': instFamily,'timeInterval': timeInterval,'frozenInterval': frozenInterval,'qtyLimit': qtyLimit,}
        return self._request_with_params(POST, MMP_CONFIG, params)

    # GET /api/v5/account/mmp-config
    def mmp(self,instFamily):
        """
        获取MMP配置
        :param instFamily: 产品族
        :return: 响应数据
        """
        params = {'instFamily': instFamily}
        return self._request_with_params(GET, MMP, params)

    # POST /api/v5/account/set-account-level
    def set_account_level(self,acctLv):
        """
        设置账户等级
        :param acctLv: 账户等级
        :return: 响应数据
        """
        params = {'acctLv': acctLv}
        return self._request_with_params(POST, SET_ACCOUNT_LEVEL, params)


    def position_builder(self,inclRealPosAndEq='',spotOffsetType='',simPos='',simAsset='',
                         greeksType='',):
        """
        持仓构建器
        :param inclRealPosAndEq: 是否包含真实持仓和权益
        :param spotOffsetType: 现货对冲模式类型
        :param simPos: 模拟持仓
        :param simAsset: 模拟资产
        :param greeksType: Greeks类型
        :return: 响应数据
        """
        params = {'acctLv': acctLv, 'spotOffsetType': spotOffsetType, 'simPos': simPos, 'simAsset': simAsset,
                  'greeksType': greeksType, }
        return self._request_with_params(POST, POSITION_BUILDER, params)


    # POST /api/v5/account/set-riskOffset-amt
    def set_riskOffset_amt(self,ccy = '', clSpotInUseAmt = ''):
        """
        设置风险对冲金额
        :param ccy: 币种
        :param clSpotInUseAmt: 现货对冲使用金额
        :return: 响应数据
        """
        params = {'ccy': ccy, 'clSpotInUseAmt': clSpotInUseAmt}
        return self._request_with_params(POST, SET_RISKOFFSET_AMT, params)

    # GET /api/v5/account/fixed-loan/borrowing-limit
    def get_fixed_loan_borrowing_limit(self):
        """
        获取固收借贷限额
        :return: 响应数据
        """
        params = {}
        return self._request_with_params(GET, GET_FIXED_LOAN_BORROWING_LIMIT, params)

    # GET /api/v5/account/fixed-loan/borrowing-quote
    def get_fixed_loan_borrowing_quote(self,type = '', ccy = '', amt = '', maxRate = '', term = '', ordId = ''):
        """
        获取固收借贷报价
        :param type: 类型
        :param ccy: 币种
        :param amt: 数量
        :param maxRate: 最大利率
        :param term: 期限
        :param ordId: 订单ID
        :return: 响应数据
        """
        params = {'type':type, 'ccy':ccy, 'amt':amt, 'maxRate':maxRate, 'maxRate':maxRate, 'term':term, 'ordId':ordId}
        return self._request_with_params(GET, GET_FIXED_LOAN_BORROWING_QUOTE, params)


    # POST /api/v5/account/fixed-loan/borrowing-order
    def fixed_loan_borrowing_order(self,ccy = '', amt = '', maxRate = '', term = '', reborrow = '', reborrowRate = ''):
        """
        固收借贷下单
        :param ccy: 币种
        :param amt: 数量
        :param maxRate: 最大利率
        :param term: 期限
        :param reborrow: 是否续借
        :param reborrowRate: 续借利率
        :return: 响应数据
        """
        params = {'ccy':ccy, 'amt':amt, 'maxRate':maxRate, 'term':term, 'reborrow':reborrow, 'reborrowRate':reborrowRate}
        return self._request_with_params(POST, FIXED_LOAN_BORROWING_ORDER, params)


    # POST /api/v5/account/fixed-loan/amend-borrowing-order
    def fixed_loan_amend_borrowing_order(self,ordId = '', reborrow = '', renewMaxRate = ''):
        """
        修改固收借贷订单
        :param ordId: 订单ID
        :param reborrow: 是否续借
        :param renewMaxRate: 续借最大利率
        :return: 响应数据
        """
        params = {'ordId':ordId, 'reborrow':reborrow, 'renewMaxRate':renewMaxRate}
        return self._request_with_params(POST, FIXED_LOAN_AMEND_BORROWING_ORDER, params)


    # POST /api/v5/account/fixed-loan/manual-reborrow
    def fixed_loan_manual_reborrow(self,ordId = '', maxRate = ''):
        """
        手动续借固收借贷订单
        :param ordId: 订单ID
        :param maxRate: 最大利率
        :return: 响应数据
        """
        params = {'ordId':ordId, 'maxRate':maxRate}
        return self._request_with_params(POST, FIXED_LOAN_MANUAL_BORROWING, params)

    # POST /api/v5/account/fixed-loan/repay-borrowing-order
    def fixed_loan_repay_borrowing_order(self,ordId = ''):
        """
        归还固收借贷订单
        :param ordId: 订单ID
        :return: 响应数据
        """
        params = {'ordId':ordId}
        return self._request_with_params(POST, FIXED_LOAN_REPAY_BORROWING_ORDER, params)


    # GET /api/v5/account/fixed-loan/borrowing-orders-list
    def get_fixed_loan_borrowing_orders_list(self,ordId = '', ccy = '', state = '', after = '', before = '',limit = '',term = ''):
        """
        获取固收借贷订单列表
        :param ordId: 订单ID
        :param ccy: 币种
        :param state: 状态
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :param term: 期限
        :return: 响应数据
        """
        params = {'ordId':ordId, 'ccy':ccy, 'state':state, 'after':after, 'before':before, 'limit':limit, 'term':term}
        return self._request_with_params(GET, GET_FIXED_LOAN_BORROWING_ORDERS_LIST, params)

    # GET /api/v5/account/instruments
    def get_account_instruments(self,instType = '', uly = '', instFamily = '', instId = ''):
        """
        获取账户产品信息
        :param instType: 产品类型
        :param uly: 标的指数
        :param instFamily: 产品族
        :param instId: 产品ID
        :return: 响应数据
        """
        params = {'instType':instType, 'uly':uly, 'instFamily':instFamily, 'instId':instId}
        return self._request_with_params(GET, GET_ACCOUNT_INSTRUMENTS, params)


    # POST /api/v5/account/spot-manual-borrow-repay
    def spot_manual_borrow_repay(self,ccy = '', side = '', amt = ''):
        """
        现货手动借币/还币
        :param ccy: 币种
        :param side: 方向 (borrow:借入, repay:归还)
        :param amt: 数量
        :return: 响应数据
        """
        params = {'ccy':ccy, 'side':side, 'amt':amt}
        return self._request_with_params(POST, SPOT_MANUAL_BORROW_REPAY, params)


    # POST /api/v5/account/set-auto-repay
    def set_auto_repay(self,autoRepay = ''):
        """
        设置自动还币
        :param autoRepay: 是否自动还币
        :return: 响应数据
        """
        params = {'autoRepay':autoRepay}
        return self._request_with_params(POST, SET_AUTO_REPAY, params)


    # GET /api/v5/account/spot-borrow-repay-history
    def get_spot_borrow_repay_history(self,ccy = '', type = '', after = '', before = '', limit = ''):
        """
        获取现货借币/还币历史
        :param ccy: 币种
        :param type: 类型
        :param after: 查询ID的起始点
        :param before: 查询ID的结束点
        :param limit: 返回结果的数量
        :return: 响应数据
        """
        params = {'ccy':ccy, 'type':type, 'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, GET_SPOT_BORROW_REPAY_HISTORY, params)

    # POST /api/v5/account/fixed-loan/convert-to-market-loan
    def convert_to_market_loan(self,ordId = ''):
        """
        转换为市场借贷
        :param ordId: 订单ID
        :return: 响应数据
        """
        params = {'ordId':ordId}
        return self._request_with_params(POST, CONVERT_TO_MARKET_LOAN, params)

    # POST /api/v5/account/fixed-loan/reduce-liabilities
    def reduce_liabilities(self,ordId = '',pendingRepay = ''):
        """
        减少负债
        :param ordId: 订单ID
        :param pendingRepay: 待还金额
        :return: 响应数据
        """
        params = {'ordId':ordId,'pendingRepay':pendingRepay}
        return self._request_with_params(POST, REDYCE_LIABILITIES, params)

    # GET /api/v5/trade/account-rate-limit
    def account_rate_limit(self,):
        """
        获取账户限速
        :return: 响应数据
        """
        params = {}
        return self._request_with_params(GET, ACC_RATE_LIMIT, params)

    # POST /api/v5/account/bills-history-archive
    def bills_history_archive(self,year = '', quarter = ''):
        """
        账单历史归档
        :param year: 年份
        :param quarter: 季度
        :return: 响应数据
        """
        params = {'year':year, 'quarter':quarter}
        return self._request_with_params(POST, BILLS_HISTORY_ARCHIVE, params)

    # GET /api/v5/account/bills-history-archive
    def get_bills_history_archive(self, year = '', quarter = ''):
        """
        获取账单历史归档
        :param year: 年份
        :param quarter: 季度
        :return: 响应数据
        """
        params = {'year':year, 'quarter':quarter}
        return self._request_with_params(GET, GET_BILLS_HISTORY_ARCHIVE, params)

    # POST /api/v5/account/account-level-switch-preset
    def account_level_switch_preset(self,acctLv = '', lever = '', riskOffsetType = ''):
        """
        账户等级切换预设
        :param acctLv: 账户等级
        :param lever: 杠杆倍数
        :param riskOffsetType: 风险对冲类型
        :return: 响应数据
        """
        params = {'acctLv':acctLv, 'lever':lever, 'riskOffsetType':riskOffsetType}
        return self._request_with_params(POST, ACCOUNT_LEVEL_SWITCH_PRESET, params)

    # GET /api/v5/account/set-account-switch-precheck
    def set_account_switch_precheck(self, acctLv = ''):
        """
        设置账户切换预检
        :param acctLv: 账户等级
        :return: 响应数据
        """
        params = {'acctLv':acctLv}
        return self._request_with_params(GET, SET_ACCOUNT_SWITCH_PRECHECK, params)
