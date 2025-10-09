from .client import Client
from .consts import *


class SubAccountAPI(Client):
    """
    子账户API类，继承自Client，用于与子账户相关的操作。
    """
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        """
        初始化SubAccountAPI实例。

        参数:
            api_key (str): API密钥。
            api_secret_key (str): API私钥。
            passphrase (str): 密码。
            use_server_time (bool, optional): 是否使用服务器时间，默认为False。
            flag (str, optional): 区域标识，'1'为真实环境，'0'为模拟盘。
        """
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    def balances(self, subAcct):
        """
        获取子账户资产余额。

        参数:
            subAcct (str): 子账户名称。

        返回:
            dict: 包含子账户余额信息的响应。
        """
        params = {"subAcct": subAcct}
        return self._request_with_params(GET, BALANCE, params)

    def bills(self, ccy='', type='', subAcct='', after='', before='', limit=''):
        """
        获取子账户账单记录。

        参数:
            ccy (str, optional): 币种，如“BTC”，默认为空。
            type (str, optional): 账单类型，默认为空。
            subAcct (str, optional): 子账户名称，默认为空。
            after (str, optional): 查询起始ID，默认为空。
            before (str, optional): 查询结束ID，默认为空。
            limit (str, optional): 返回结果的数量，默认为空。

        返回:
            dict: 包含子账户账单记录的响应。
        """
        params = {"ccy": ccy, 'type': type, 'subAcct': subAcct, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLs, params)
    # 移除此接口
    def delete(self, pwd, subAcct, apiKey):
        """
        删除子账户（此接口已移除）。

        参数:
            pwd (str): 密码。
            subAcct (str): 子账户名称。
            apiKey (str): API密钥。

        返回:
            dict: 删除子账户的响应。
        """
        params = {'pwd': pwd, 'subAcct': subAcct, 'apiKey': apiKey}
        return self._request_with_params(POST, DELETE, params)
    # 移除此接口
    def reset(self, pwd, subAcct, label, apiKey, perm, ip=''):
        """
        重置子账户API密钥（此接口已移除）。

        参数:
            pwd (str): 密码。
            subAcct (str): 子账户名称。
            label (str): API密钥标签。
            apiKey (str): API密钥。
            perm (str): 权限。
            ip (str, optional): IP地址，默认为空。

        返回:
            dict: 重置API密钥的响应。
        """
        params = {'pwd': pwd, 'subAcct': subAcct, 'label': label, 'apiKey': apiKey, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, RESET, params)
    # 移除此接口
    def create(self, pwd, subAcct, label, Passphrase, perm='', ip=''):
        """
        创建子账户（此接口已移除）。

        参数:
            pwd (str): 密码。
            subAcct (str): 子账户名称。
            label (str): API密钥标签。
            Passphrase (str): 密码。
            perm (str, optional): 权限，默认为空。
            ip (str, optional): IP地址，默认为空。

        返回:
            dict: 创建子账户的响应。
        """
        params = {'pwd': pwd, 'subAcct': subAcct, 'label': label, 'Passphrase': Passphrase, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, CREATE, params)
    # 移除此接口
    def watch(self, subAcct,apiKey=''):
        """
        监控子账户（此接口已移除）。

        参数:
            subAcct (str): 子账户名称。
            apiKey (str, optional): API密钥，默认为空。

        返回:
            dict: 监控子账户的响应。
        """
        params = {'subAcct': subAcct,'apiKey':apiKey}
        return self._request_with_params(GET, WATCH, params)

    def view_list(self, enable='', subAcct='', after='', before='', limit='',uid=''):
        """
        查看子账户列表。

        参数:
            enable (str, optional): 是否启用，默认为空。
            subAcct (str, optional): 子账户名称，默认为空。
            after (str, optional): 查询起始ID，默认为空。
            before (str, optional): 查询结束ID，默认为空。
            limit (str, optional): 返回结果的数量，默认为空。
            uid (str, optional): 用户ID，默认为空。

        返回:
            dict: 包含子账户列表的响应。
        """
        params = {'enable': enable, 'subAcct': subAcct, 'after': after,
                  'before': before, 'limit': limit,'uid':uid}
        return self._request_with_params(GET, VIEW_LIST, params)

    def subAccount_transfer(self, ccy, amt, froms, to, fromSubAccount,toSubAccount,loanTrans='',omitPosRisk=''):
        """
        子账户资金划转。

        参数:
            ccy (str): 币种。
            amt (str): 划转数量。
            froms (str): 转出方。
            to (str): 转入方。
            fromSubAccount (str): 转出子账户名称。
            toSubAccount (str): 转入子账户名称。
            loanTrans (str, optional): 借贷划转类型，默认为空。
            omitPosRisk (str, optional): 是否忽略持仓风险，默认为空。

        返回:
            dict: 子账户资金划转的响应。
        """
        params = {'ccy': ccy, 'amt': amt, 'from': froms, 'to': to, 'fromSubAccount': fromSubAccount, 'toSubAccount': toSubAccount,'loanTrans':loanTrans,'omitPosRisk':omitPosRisk}
        return self._request_with_params(POST, SUBACCOUNT_TRANSFER, params)

    def entrust_subaccount_list(self, subAcct):
        """
        查询托管子账户列表。

        参数:
            subAcct (str): 子账户名称。

        返回:
            dict: 包含托管子账户列表的响应。
        """
        params = {'subAcct': subAcct}
        return self._request_with_params(GET, ENTRUST_SUBACCOUNT_LIST, params)

    def modify_apikey(self, subAcct, apiKey, label, perm, ip):
        """
        修改子账户API密钥。

        参数:
            subAcct (str): 子账户名称。
            apiKey (str): API密钥。
            label (str): API密钥标签。
            perm (str): 权限。
            ip (str): IP地址。

        返回:
            dict: 修改API密钥的响应。
        """
        params = {'subAcct': subAcct, 'apiKey': apiKey, 'label': label, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, MODIFY_APIKEY, params)

    def partner_if_rebate(self, apiKey = ''):
        """
        查询合伙人返佣信息。

        参数:
            apiKey (str, optional): API密钥，默认为空。

        返回:
            dict: 包含合伙人返佣信息的响应。
        """
        params = {'apiKey': apiKey}
        return self._request_with_params(GET, PARTNER_IF_REBATE, params)

    # 获取子账户最大可转余额 max-withdrawal
    def max_withdrawal(self, subAcct, ccy = ''):
        """
        获取子账户最大可划转余额。

        参数:
            subAcct (str): 子账户名称。
            ccy (str, optional): 币种，默认为空。

        返回:
            dict: 包含最大可划转余额的响应。
        """
        params = {'subAcct': subAcct,'ccy': ccy,}
        return self._request_with_params(GET, MAX_WITHDRAW, params)

    # 查询托管子账户转账记录 managed-subaccount-bills
    def managed_subaccount_bills(self,ccy='',type='',subAcct='',subUid='',after='',before='',limit=''):
        """
        查询托管子账户转账记录。

        参数:
            ccy (str, optional): 币种，默认为空。
            type (str, optional): 账单类型，默认为空。
            subAcct (str, optional): 子账户名称，默认为空。
            subUid (str, optional): 子账户UID，默认为空。
            after (str, optional): 查询起始ID，默认为空。
            before (str, optional): 查询结束ID，默认为空。
            limit (str, optional): 返回结果的数量，默认为空。

        返回:
            dict: 包含托管子账户转账记录的响应。
        """
        params = {'ccy': ccy,'type': type,'subAcct': subAcct,'subUid': subUid,'after': after,'before': before,
                  'limit': limit,}
        return self._request_with_params(GET,SUB_BILLS,params)