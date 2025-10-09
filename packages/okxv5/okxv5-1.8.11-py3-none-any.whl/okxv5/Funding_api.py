from .client import Client
from .consts import *


class FundingAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # 获取充币地址
    def get_deposit_address(self, ccy):
        params = {'ccy': ccy}
        return self._request_with_params(GET, DEPOSIT_ADDRESS, params)

    # 获取账户余额
    def get_balances(self, ccy=''):
        params = {'ccy': ccy}
        return self._request_with_params(GET, GET_BALANCES, params)

    # 资金划转
    def funds_transfer(self, ccy, amt, froms, to, type='0', subAcct='', clientId='',loanTrans='',omitPosRisk=''):
        params = {'ccy': ccy, 'amt': amt, 'from': froms, 'to': to, 'type': type, 'subAcct': subAcct,'clientId': clientId,'loanTrans':loanTrans,'omitPosRisk':omitPosRisk}
        return self._request_with_params(POST, FUNDS_TRANSFER, params)

    # 获取资金划转状态
    def transfer_state(self, transId,type=''):
        params = {'transId': transId, 'type': type}
        return self._request_with_params(POST, TRANSFER_STATE, params)

    # 提币
    def coin_withdraw(self, ccy, amt, dest, toAddr, fee,chain='',areaCode='',clientId=''):
        params = {'ccy': ccy, 'amt': amt, 'dest': dest, 'toAddr': toAddr, 'fee': fee,'chain': chain,'areaCode':areaCode,'clientId':clientId}
        return self._request_with_params(POST, WITHDRAWAL_COIN, params)

    # 获取充币记录
    def get_deposit_history(self, ccy='', state='', after='', before='', limit='',txId='',depId='',fromWdId=''):
        params = {'ccy': ccy, 'state': state, 'after': after, 'before': before, 'limit': limit,'txId':txId,'depId':depId,'fromWdId':fromWdId}
        return self._request_with_params(GET, DEPOSIT_HISTORIY, params)

    # 获取提币记录
    def get_withdrawal_history(self, ccy='', state='', after='', before='', limit='',txId='',depId='',wdId=''):
        params = {'ccy': ccy, 'state': state, 'after': after, 'before': before, 'limit': limit,'txId':txId,'depId':depId,'wdId':wdId}
        return self._request_with_params(GET, WITHDRAWAL_HISTORIY, params)

    # 小额资产兑换
    def convert_dust_assets(self, ccy):
        params = {'ccy': ccy}
        return self._request_with_params(POST, CONVERT_DUST_ASSETS, params)

    # 获取币种列表
    def get_currency(self,ccy=''):
        params = {'ccy':ccy}
        return self._request_with_params(GET, CURRENCY_INFO,params)

    # 余币宝申购/赎回
    def purchase_redempt(self, ccy, amt, side,rate):
        params = {'ccy': ccy, 'amt': amt, 'side': side,'rate': rate}
        return self._request_with_params(POST, PURCHASE_REDEMPT, params)

    # 获取账单流水
    def get_bills(self, ccy='', type='', after='', before='', limit=''):
        params = {'ccy': ccy, 'type': type, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLS_INFO, params)


    # 获取余币宝余额
    def get_piggy_balance(self, ccy=''):
        params = {}
        if ccy:
            params = {'ccy':ccy}
        return self._request_with_params(GET, PIGGY_BALANCE, params)


    # 获取闪电充币
    def get_deposit_lightning(self, ccy,amt,to=""):
        params = {'ccy':ccy,'amt':amt}
        if to:
            params = {'to':to}
        return self._request_with_params(GET, DEPOSIT_LIGHTNING, params)

    # 闪电提币
    def withdrawal_lightning(self, ccy,invoice,memo):
        params = {'ccy':ccy, 'invoice':invoice,'memo':memo}
        return self._request_with_params(POST, WITHDRAWAL_LIGHTNING, params)

    # 撤销提币
    def cancel_withdrawal(self, wdId):
        params = {'wdId':wdId,}
        return self._request_with_params(POST , CANCEL_WITHDRAWAL, params)

    # 获取账户资产估值
    def get_asset_valuation(self, ccy):
        params = {'ccy':ccy}
        return self._request_with_params(GET, ASSET_VALUATION, params)

    # 设置借币利率
    def set_lending_rate(self, ccy,rate):
        params = {'ccy':ccy,'rate':rate}
        return self._request_with_params(POST, SET_LENDING_RATE, params)


    # 获取借币历史
    def get_lending_rate(self, ccy='',before='',after='',limit='',):
        params = {'ccy': ccy, 'after': after, 'before': before, 'limit': limit,}
        return self._request_with_params(GET, LENDING_HISTORY, params)


    # 获取借币利率历史
    def get_lending_rate_history(self, ccy='',):
        params = {'ccy': ccy,}
        return self._request_with_params(GET, LENDING_RATE_HISTORY, params)

    # 获取借币利率汇总
    def get_lending_rate_summary(self, ccy='',before='',after='',limit='',):
        params = {'ccy': ccy, 'after': after, 'before': before, 'limit': limit,}
        return self._request_with_params(GET,LENDING_RATE_SUMMARY, params)

    # 获取充值/提现状态
    def deposit_withdraw_status(self, wdId = '', txId = '', ccy = '', to = '', chain = ''):
        params = {'wdId': wdId, 'txId': txId, 'ccy': ccy, 'to': to, 'chain':chain}
        return self._request_with_params(GET,DEPOSIT_WITHDRAW_STATUS, params)

    # 获取子账户免息额度及利息
    def exchange_list(self):
        return self._request_without_params(GET,EXCHANGE_LIST)

    # 获取月度账单（内部转账）
    def monthly_statement(self,month=''):
        params = {'month':month}
        return self._request_with_params(POST, MONTHLY_STATEMENT,params)

    # 获取月度账单
    def monthly_statement(self,month=''):
        params = {'month':month}
        return self._request_with_params(GET, MONTHLY_STATEMENTS,params)