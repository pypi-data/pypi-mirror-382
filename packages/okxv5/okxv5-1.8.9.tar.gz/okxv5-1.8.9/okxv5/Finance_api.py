# 从 .client 模块导入 Client 类
from .client import Client
# 从 .consts 模块导入所有常量
from .consts import *


# FinanceAPI 类继承自 Client 类
class FinanceAPI(Client):

    # 构造函数，初始化 Client
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 查看项目
    def staking_defi_offers(self, productId = '', protocolType = '', ccy = ''):
        params = {'productId': productId, 'protocolType': protocolType, 'ccy': ccy}
        return self._request_with_params(GET, STAKING_DEFI_OFFERS, params)

    # 订阅项目
    def staking_defi_purchase(self, productId = '', investData = [], term= '',tag=''):
        params = {'productId': productId, 'investData': investData, 'term': term,'tag':tag}
        return self._request_with_params(POST, STAKING_DEFI_PURCHASE, params)

    # 赎回项目
    def staking_defi_redeem(self, ordId = '', protocolType = '', allowEarlyRedeem= ''):
        params = {'ordId': ordId, 'protocolType': protocolType, 'allowEarlyRedeem': allowEarlyRedeem}
        return self._request_with_params(POST, STAKING_DEFI_REDEEM, params)

    # 取消项目订阅/赎回
    def staking_defi_cancel(self, ordId = '', protocolType = ''):
        params = {'ordId': ordId, 'protocolType': protocolType}
        return self._request_with_params(POST, STAKING_DEFI_CANCEL, params)

    # 查看活动订单
    def staking_defi_orders_active(self, productId = '', protocolType = '', ccy = '', state = ''):
        params = {'productId': productId, 'protocolType': protocolType, 'ccy': ccy, 'state':state}
        return self._request_with_params(GET, STAKING_DEFI_ORDERS_ACTIVE, params)

    # 查看历史订单
    def staking_defi_orders_history(self, productId = '', protocolType = '', ccy = '', after = '', before = '', limit = ''):
        params = {'productId': productId, 'protocolType': protocolType, 'ccy': ccy, 'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, STAKING_DEFI_ORDERS_HISTORY, params)

    # 质押借贷 ETH 申购
    def staking_defi_eth_purcase(self, amt = ''):
        params = {}
        return self._request_with_params(POST, STAKING_DEFI_ETH_PURCASE, params)

    # 质押借贷 ETH 赎回
    def staking_defi_eth_redeem(self, amt = ''):
        params = {}
        return self._request_with_params(POST, STAKING_DEFI_ETH_REDEEM, params)

    # 质押借贷 ETH 余额
    def staking_defi_eth_balance(self, ):
        params = {}
        return self._request_with_params(GET, STAKING_DEFI_ETH_BALANCE, params)

    # 质押借贷 ETH 申购/赎回历史
    def staking_defi_eth_p_r_history(self,type='',status='',after='',before='',limit='', ):
        params = {'type': type,'status': status,'after': after,'before': before,'limit': limit,}
        return self._request_with_params(GET, STAKING_DEFI_ETH_P_R_HISTORY, params)

    # 质押借贷 ETH APY 历史
    def staking_defi_eth_apy_history(self,days='',):
        params = {'days': days,}
        return self._request_with_params(GET, STAKING_DEFI_ETH_APY_HISTORY, params)

    # 质押借贷 ETH 产品信息
    def staking_defi_eth_product_info(self):
        params = {}
        return self._request_with_params(GET, STAKING_DEFI_ETH_PRODUCT_INFO, params)

    # POST /api/v5/finance/staking-defi/sol/purchase (质押借贷 SOL 申购)
    def staking_defi_sol_purcase(self, amt = ''):
        params = {}
        return self._request_with_params(POST, STAKING_DEFI_SOL_PURCASE, params)

    # POST /api/v5/finance/staking-defi/sol/redeem (质押借贷 SOL 赎回)
    def staking_defi_sol_redeem(self, amt = ''):
        params = {}
        return self._request_with_params(POST, STAKING_DEFI_SOL_REDEEM, params)

    # GET /api/v5/finance/staking-defi/sol/balance (质押借贷 SOL 余额)
    def staking_defi_sol_balance(self, ):
        params = {}
        return self._request_with_params(GET, STAKING_DEFI_SOL_BALANCE, params)

    # GET /api/v5/finance/staking-defi/sol/purchase-redeem-history (质押借贷 SOL 申购/赎回历史)
    def staking_defi_sol_p_r_history(self,type='',status='',after='',before='',limit='', ):
        params = {'type': type,'status': status,'after': after,'before': before,'limit': limit,}
        return self._request_with_params(GET, STAKING_DEFI_SOL_P_R_HISTORY, params)

    # GET /api/v5/finance/staking-defi/sol/apy-history (质押借贷 SOL APY 历史)
    def staking_defi_sol_apy_history(self,days='',):
        params = {'days': days,}
        return self._request_with_params(GET, STAKING_DEFI_SOL_APY_HISTORY, params)

    # 储蓄借贷利率汇总
    def savings_lending_rate_summary(self,ccy='',):
        params = {'ccy': ccy,}
        return self._request_with_params(GET, SAVINGS_LENDING_RATE_SUM, params)

    # 储蓄借贷利率历史
    def savings_lending_rate_his(self,ccy='',after='',before='',limit='',):
        params = {'ccy': ccy,'after': after,'before': before,'limit': limit,}
        return self._request_with_params(GET, SAVINGS_LENDING_RATE_HIS, params)

    # 定期借贷报价
    def fixed_loan_lending_offers(self, ccy='', term='',  ):
        params = {'ccy': ccy, 'term': term, }
        return self._request_with_params(GET, FIXED_LOAN_LENDING_OFFERS, params)

    # 定期借贷 APY 历史
    def fixed_loan_lending_apy_history(self, ccy='', term='',  ):
        params = {'ccy': ccy, 'term': term, }
        return self._request_with_params(GET, FIXED_LOAN_LENDING_APY_HIS, params)

    # 定期借贷待处理借贷量
    def fixed_loan_pending_lending_vol(self, ccy='', term='',  ):
        params = {'ccy': ccy, 'term': term, }
        return self._request_with_params(GET, FIXED_LOAN_PENDING_LENDING_VOL, params)

    # POST /api/v5/finance/fixed-loan/lending-order (定期借贷下单)
    def fixed_loan_lending_order(self, ccy = '', amt = '', rate = '', term = '', autoRenewal = ''):
        params = {'ccy':ccy,'amt':amt,'rate':rate,'term':term,'autoRenewal':autoRenewal}
        return self._request_with_params(POST, FIXED_LOAN_LENDING_ORDER, params)

    # POST /api/v5/finance/fixed-loan/amend-lending-order (定期借贷修改订单)
    def fixed_loan_amend_lending_order(self, ordId = '', changeAmt = '', rate = '', autoRenewal = ''):
        params = {'ordId':ordId,'changeAmt':changeAmt,'rate':rate,'autoRenewal':autoRenewal}
        return self._request_with_params(POST, FIXED_LOAN_AMEND_LENDING_ORDER, params)

    # GET /api/v5/finance/fixed-loan/lending-orders-list (定期借贷订单列表)
    def fixed_loan_lending_orders_list(self, ordId='', ccy='', state='', after='', before='', limit=''):
        params = {'ordId': ordId, 'ccy': ccy, 'state':state, 'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, FIXED_LOAN_LENDING_ORDERS_LIST, params)

    # GET /api/v5/finance/fixed-loan/lending-sub-orders (定期借贷子订单列表)
    def fixed_loan_lending_sub_orders(self, ordId='', state='', after='', before='', limit=''):
        params = {'ordId': ordId, 'state':state, 'after':after, 'before':before, 'limit':limit}
        return self._request_with_params(GET, FIXED_LOAN_LENDING_SUB_ORDERS, params)

    # GET /api/v5/finance/flexible-loan/borrow-currencies (灵活借贷可借币种)
    def flexible_loan_borrow_currencies(self):
        params = {}
        return self._request_with_params(GET, FLEXIBLE_LOAN_BORROW_CURRENCIES, params)

    # GET /api/v5/finance/flexible-loan/collateral-assets (灵活借贷抵押资产)
    def flexible_loan_collateral_assets(self, ccy = ''):
        params = {'ccy':ccy}
        return self._request_with_params(GET, FLEXIBLE_LOAN_COLLATERAL_ASSETS, params)

    # POST /api/v5/finance/flexible-loan/max-loan (灵活借贷最大可借金额)
    def flexible_loan_max_loan(self, borrowCcy = '', supCollateral = []):
        params = {'borrowCcy':borrowCcy,'supCollateral':supCollateral}
        return self._request_with_params(POST, FLEXIBLE_LOAN_MAX_LOAN, params)

    # GET /api/v5/finance/flexible-loan/max-collateral-redeem-amount (灵活借贷最大可赎回抵押品数量)
    def flexible_loan_max_c_r_a(self, borrowCcy = ''):
        params = {'borrowCcy':borrowCcy}
        return self._request_with_params(GET, FLEXIBLE_LOAN_MAX_C_R_A, params)

    # POST /api/v5/finance/flexible-loan/adjust-collateral (灵活借贷调整抵押品)
    def flexible_loan_adj_coll(self, type = '', collateralCcy = '', collateralAmt = ''):
        params = {'type':type,'collateralCcy':collateralCcy,'collateralAmt':collateralAmt}
        return self._request_with_params(POST, FLEXIBLE_LOAN_ADJ_COLL, params)

    # GET /api/v5/finance/flexible-loan/loan-info (灵活借贷借贷信息)
    def flexible_loan_loan_info(self):
        params = {}
        return self._request_with_params(GET, FLEXIBLE_LOAN_LOAN_INFO, params)

    # GET /api/v5/finance/flexible-loan/loan-history (灵活借贷借贷历史)
    def flexible_loan_loan_history(self, type = '', after = '', before = '', limit = ''):
        params = {'type':type, 'after':after,'before':before,'limit':limit}
        return self._request_with_params(GET, FLEXIBLE_LOAN_LOAN_HISTORY, params)

    # GET /api/v5/finance/flexible-loan/interest-accrued (灵活借贷计息记录)
    def flexible_loan_interest_accrued(self, ccy = '', after = '', before = '', limit = ''):
        params = {'ccy':ccy, 'after':after,'before':before,'limit':limit}
        return self._request_with_params(GET, FLEXIBLE_LOAN_INT_ACC, params)