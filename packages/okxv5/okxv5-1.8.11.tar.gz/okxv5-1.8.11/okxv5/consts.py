# http header
API_URL = 'https://www.okx.com' # OKX API 的基础 URL

CONTENT_TYPE = 'Content-Type' # HTTP 请求头：内容类型
OK_ACCESS_KEY = 'OK-ACCESS-KEY' # HTTP 请求头：API 密钥
OK_ACCESS_SIGN = 'OK-ACCESS-SIGN' # HTTP 请求头：API 签名
OK_ACCESS_TIMESTAMP = 'OK-ACCESS-TIMESTAMP' # HTTP 请求头：时间戳
OK_ACCESS_PASSPHRASE = 'OK-ACCESS-PASSPHRASE' # HTTP 请求头：API 密码

ACEEPT = 'Accept' # HTTP 请求头：接受类型
COOKIE = 'Cookie' # HTTP 请求头：Cookie
LOCALE = 'Locale=' # HTTP 请求头：语言环境

APPLICATION_JSON = 'application/json' # 内容类型：JSON

GET = "GET" # HTTP 方法：GET
POST = "POST" # HTTP 方法：POST

SERVER_TIMESTAMP_URL = '/api/v5/public/time' # 获取服务器时间戳的 API 路径

# account (账户相关 API)
POSITION_RISK='/api/v5/account/account-position-risk' # 获取账户持仓风险的 API 路径
ACCOUNT_INFO = '/api/v5/account/balance' # 获取账户余额的 API 路径
POSITION_INFO = '/api/v5/account/positions' # 获取持仓信息的 API 路径
BILLS_DETAIL = '/api/v5/account/bills' # 获取账户账单详情的 API 路径
BILLS_ARCHIVE = '/api/v5/account/bills-archive' # 获取账户历史账单的 API 路径
ACCOUNT_CONFIG = '/api/v5/account/config' # 获取账户配置的 API 路径
POSITION_MODE = '/api/v5/account/set-position-mode' # 设置持仓模式的 API 路径
SET_LEVERAGE = '/api/v5/account/set-leverage' # 设置杠杆倍数的 API 路径
MAX_TRADE_SIZE = '/api/v5/account/max-size' # 获取最大可开仓数量的 API 路径
MAX_AVAIL_SIZE = '/api/v5/account/max-avail-size' # 获取最大可用数量的 API 路径
ADJUSTMENT_MARGIN = '/api/v5/account/position/margin-balance' # 调整保证金的 API 路径
GET_LEVERAGE = '/api/v5/account/leverage-info' # 获取杠杆信息的 API 路径
MAX_LOAN = '/api/v5/account/max-loan' # 获取最大可借金额的 API 路径
FEE_RATES = '/api/v5/account/trade-fee' # 获取交易手续费率的 API 路径
INTEREST_ACCRUED = '/api/v5/account/interest-accrued' # 获取已产生利息的 API 路径
INTEREST_RATE = '/api/v5/account/interest-rate' # 获取借贷利率的 API 路径
SET_GREEKS = '/api/v5/account/set-greeks' # 设置希腊字母参数显示模式的 API 路径
ISOLATED_MODE = '/api/v5/account/set-isolated-mode' # 设置逐仓模式的 API 路径
MAX_WITHDRAWAL = '/api/v5/account/max-withdrawal' # 获取最大提币数量的 API 路径
ACCOUNT_RISK = '/api/v5/account/risk-state' # 获取账户风险状态的 API 路径
BORROW_REPAY = '/api/v5/account/borrow-repay' # 借币/还币的 API 路径
BORROW_REPAY_HISTORY = '/api/v5/account/borrow-repay-history' # 获取借币/还币历史的 API 路径
INTEREST_LIMITS = '/api/v5/account/interest-limits' # 获取借贷限额的 API 路径
SIMULATED_MARGIN = '/api/v5/account/simulated_margin' # 获取模拟保证金的 API 路径
GREEKS = '/api/v5/account/greeks' # 获取希腊字母参数的 API 路径
POSITIONS_HISTORY = '/api/v5/account/positions-history' # 获取持仓历史的 API 路径
POSITION_TIRES = '/api/v5/account/position-tiers' # 获取持仓档位的 API 路径
ACTIVATE_OPTION = '/api/v5/account/activate-option' # 激活期权的 API 路径
QUICK_MARGIN_BRROW_REPAY = '/api/v5/account/quick-margin-borrow-repay' # 快捷杠杆借还的 API 路径
QUICK_MARGIN_BORROW_REPAY_HISTORY = '/api/v5/account/quick-margin-borrow-repay-history' # 获取快捷杠杆借还历史的 API 路径
VIP_INTEREST_ACCRUED = '/api/v5/account/vip-interest-accrued' # 获取 VIP 已产生利息的 API 路径
VIP_INTEREST_DEDUCTED = '/api/v5/account/vip-interest-deducted' # 获取 VIP 已扣除利息的 API 路径
VIP_LOAN_ORDER_LIST = '/api/v5/account/vip-loan-order-list' # 获取 VIP 借贷订单列表的 API 路径
VIP_LOAN_ORDER_DETAIL = '/api/v5/account/vip-loan-order-detail' # 获取 VIP 借贷订单详情的 API 路径
SET_LOAN_ALLOCATION = '/api/v5/account/subaccount/set-loan-allocation' # 设置子账户借贷分配的 API 路径
# INTEREST_LIMITS = '/api/v5/account/subaccount/interest-limits' # 获取子账户借贷限额的 API 路径 (重复定义)
SET_RISKOFFSET_TYPE = '/api/v5/account/set-riskOffset-type' # 设置风险抵消类型的 API 路径
SET_AUTO_LOAN = '/api/v5/account/set-auto-loan' # 设置自动借币的 API 路径
MMP_RESET = '/api/v5/account/mmp-reset' # 重置做市商保护的 API 路径
SET_RISKOFFSET_AMT = '/api/v5/account/set-riskOffset-amt' # 设置风险抵消金额的 API 路径
GET_FIXED_LOAN_BORROWING_LIMIT = '/api/v5/account/fixed-loan/borrowing-limit' # 获取固定借贷限额的 API 路径
GET_FIXED_LOAN_BORROWING_QUOTE = '/api/v5/account/fixed-loan/borrowing-quote' # 获取固定借贷报价的 API 路径
FIXED_LOAN_BORROWING_ORDER = '/api/v5/account/fixed-loan/borrowing-order' # 固定借贷下单的 API 路径
FIXED_LOAN_AMEND_BORROWING_ORDER = '/api/v5/account/fixed-loan/amend-borrowing-order' # 修改固定借贷订单的 API 路径
FIXED_LOAN_MANUAL_BORROWING = '/api/v5/account/fixed-loan/manual-reborrow' # 固定借贷手动续借的 API 路径
FIXED_LOAN_REPAY_BORROWING_ORDER = '/api/v5/account/fixed-loan/repay-borrowing-order' # 固定借贷还款订单的 API 路径
GET_FIXED_LOAN_BORROWING_ORDERS_LIST = '/api/v5/account/fixed-loan/borrowing-orders-list' # 获取固定借贷订单列表的 API 路径
GET_ACCOUNT_INSTRUMENTS = '/api/v5/account/instruments' # 获取账户交易产品的 API 路径
SPOT_MANUAL_BORROW_REPAY = '/api/v5/account/spot-manual-borrow-repay' # 现货手动借还的 API 路径
SET_AUTO_REPAY = '/api/v5/account/set-auto-repay' # 设置自动还款的 API 路径
GET_SPOT_BORROW_REPAY_HISTORY = '/api/v5/account/spot-borrow-repay-history' # 获取现货借还历史的 API 路径
CONVERT_TO_MARKET_LOAN = '/api/v5/account/fixed-loan/convert-to-market-loan' # 固定借贷转为市场借贷的 API 路径
REDYCE_LIABILITIES = '/api/v5/account/fixed-loan/reduce-liabilities' # 固定借贷减少负债的 API 路径
ACC_RATE_LIMIT = '/api/v5/trade/account-rate-limit' # 获取账户限速信息的 API 路径
BILLS_HISTORY_ARCHIVE = '/api/v5/account/bills-history-archive' # 获取历史账单归档的 API 路径 (重复定义)
GET_BILLS_HISTORY_ARCHIVE = '/api/v5/account/bills-history-archive' # 获取历史账单归档的 API 路径 (重复定义)
ACCOUNT_LEVEL_SWITCH_PRESET = '/api/v5/account/account-level-switch-preset' # 账户等级切换预设的 API 路径
SET_ACCOUNT_SWITCH_PRECHECK = '/api/v5/account/set-account-switch-precheck' # 设置账户切换预检查的 API 路径

# funding (资金相关 API)
DEPOSIT_ADDRESS = '/api/v5/asset/deposit-address' # 获取充值地址的 API 路径
GET_BALANCES = '/api/v5/asset/balances' # 获取所有币种余额的 API 路径
FUNDS_TRANSFER = '/api/v5/asset/transfer' # 资金划转的 API 路径
TRANSFER_STATE = '/api/v5/asset/transfer-state' # 获取资金划转状态的 API 路径
WITHDRAWAL_COIN = '/api/v5/asset/withdrawal' # 提币的 API 路径
DEPOSIT_HISTORIY = '/api/v5/asset/deposit-history' # 获取充值历史的 API 路径
CURRENCY_INFO = '/api/v5/asset/currencies' # 获取币种信息的 API 路径
PURCHASE_REDEMPT = '/api/v5/finance/savings/purchase-redempt' # 理财产品申购/赎回的 API 路径
BILLS_INFO = '/api/v5/asset/bills' # 获取资金账单信息的 API 路径
PIGGY_BALANCE = '/api/v5/finance/savings/balance' # 获取余币宝余额的 API 路径
DEPOSIT_LIGHTNING = '/api/v5/asset/deposit-lightning' # 闪电网络充值的 API 路径
WITHDRAWAL_LIGHTNING = '/api/v5/asset/withdrawal-lightning' # 闪电网络提币的 API 路径
CANCEL_WITHDRAWAL = '/api/v5/asset/cancel-withdrawal' # 撤销提币的 API 路径
WITHDRAWAL_HISTORIY = '/api/v5/asset/withdrawal-history' # 获取提币历史的 API 路径
CONVERT_DUST_ASSETS = '/api/v5/asset/convert-dust-assets' # 零钱转换的 API 路径
ASSET_VALUATION = '/api/v5/asset/asset-valuation' # 获取资产估值的 API 路径
SET_LENDING_RATE = '/api/v5/finance/savings/set-lending-rate' # 设置借贷利率的 API 路径
LENDING_HISTORY = '/api/v5/finance/savings/lending-history' # 获取借贷历史的 API 路径
LENDING_RATE_HISTORY = '/api/v5/asset/lending-rate-history' # 获取借贷利率历史的 API 路径
LENDING_RATE_SUMMARY = '/api/v5/asset/lending-rate-summary' # 获取借贷利率汇总的 API 路径
DEPOSIT_WITHDRAW_STATUS = '/api/v5/asset/deposit-withdraw-status' # 获取充提状态的 API 路径
EXCHANGE_LIST = '/api/v5/asset/exchange-list' # 获取兑换列表的 API 路径
MONTHLY_STATEMENT = '/api/v5/asset/monthly-statement' # 获取月度对账单的 API 路径
MONTHLY_STATEMENTS = '/api/v5/asset/monthly-statement' # 获取月度对账单的 API 路径 (重复定义)

# Market Data (市场数据相关 API)
TICKERS_INFO = '/api/v5/market/tickers' # 获取所有产品行情信息的 API 路径
TICKER_INFO = '/api/v5/market/ticker' # 获取单个产品行情信息的 API 路径
INDEX_TICKERS = '/api/v5/market/index-tickers' # 获取指数行情信息的 API 路径
ORDER_BOOKS = '/api/v5/market/books' # 获取深度数据的 API 路径
MARKET_CANDLES = '/api/v5/market/candles' # 获取 K 线数据的 API 路径
HISTORY_CANDLES = '/api/v5/market/history-candles' # 获取历史 K 线数据的 API 路径
INDEX_CANSLES = '/api/v5/market/index-candles' # 获取指数 K 线数据的 API 路径
MARKPRICE_CANDLES = '/api/v5/market/mark-price-candles' # 获取标记价格 K 线数据的 API 路径
MARKET_TRADES = '/api/v5/market/trades' # 获取最新成交数据的 API 路径
VOLUMNE = '/api/v5/market/platform-24-volume' # 获取平台 24 小时交易量数据的 API 路径
ORACLE = '/api/v5/market/oracle' # 获取预言机价格的 API 路径
Components = '/api/v5/market/index-components' # 获取指数成分数据的 API 路径
EXCHANGE_RATE = '/api/v5/market/exchange-rate' # 获取汇率的 API 路径
HISTORY_TRADES = '/api/v5/market/history-trades' # 获取历史成交数据的 API 路径
BLOCK_TICKERS = '/api/v5/market/block-tickers' # 获取区块行情信息的 API 路径
BLOCK_TICKER = '/api/v5/market/block-ticker' # 获取单个区块行情信息的 API 路径
BLOCK_TRADES = '/api/v5/market/trades' # 获取区块成交数据的 API 路径 (与 MARKET_TRADES 重复)
HISTORY_INDEX_CANDLES = '/api/v5/market/history-index-candles' # 获取历史指数 K 线数据的 API 路径
HISTORY_MARK_PRICE_CANDLES = '/api/v5/market/history-mark-price-candles' # 获取历史标记价格 K 线数据的 API 路径
INSTRUMENT_FAMILY_TRADES = '/api/v5/market/option/instrument-family-trades' # 获取期权交易产品系列成交数据的 API 路径
GET_BOOKS_LITE = '/api/v5/market/books-lite' # 获取轻量级深度数据的 API 路径
BOOKS_FULL = '/api/v5/market/books-full' # 获取完整深度数据的 API 路径
GET_CALL_AUCTION_DETAILS = '/api/v5/market/call-auction-details' # 获取集合竞价详情的 API 路径

# Public Data (公共数据相关 API)
INSTRUMENT_INFO = '/api/v5/public/instruments' # 获取交易产品信息的 API 路径
DELIVERY_EXERCISE = '/api/v5/public/delivery-exercise-history' # 获取交割/行权历史的 API 路径
OPEN_INTEREST = '/api/v5/public/open-interest' # 获取合约总持仓量的 API 路径
FUNDING_RATE = '/api/v5/public/funding-rate' # 获取资金费率的 API 路径
FUNDING_RATE_HISTORY = '/api/v5/public/funding-rate-history' # 获取资金费率历史的 API 路径
PRICE_LIMIT = '/api/v5/public/price-limit' # 获取价格限制的 API 路径
OPT_SUMMARY = '/api/v5/public/opt-summary' # 获取期权汇总的 API 路径
ESTIMATED_PRICE = '/api/v5/public/estimated-price' # 获取预估价格的 API 路径
DICCOUNT_INTETEST_INFO = '/api/v5/public/discount-rate-interest-free-quota' # 获取折扣利率和免息额度的 API 路径
SYSTEM_TIME = '/api/v5/public/time' # 获取系统时间的 API 路径
LIQUIDATION_ORDERS = '/api/v5/public/liquidation-orders' # 获取爆仓订单的 API 路径
MARK_PRICE = '/api/v5/public/mark-price' # 获取标记价格的 API 路径
TIER = '/api/v5/public/position-tiers' # 获取仓位档位的 API 路径
INTEREST_LOAN = '/api/v5/public/interest-rate-loan-quota' # 获取利率借款额度的 API 路径
UNDERLYING = '/api/v5/public/underlying' # 获取标的资产的 API 路径
VIP_INTEREST_RATE_LOAN_QUOTA = '/api/v5/public/vip-interest-rate-loan-quota' # 获取 VIP 利率借款额度的 API 路径
INSURANCE_FUND = '/api/v5/public/insurance-fund' # 获取风险准备金的 API 路径
CONVERT_CONTRACT_COIN = '/api/v5/public/convert-contract-coin' # 转换合约币种的 API 路径
INSTRUMENT_TICK_BANDS = '/api/v5/public/instrument-tick-bands' # 获取产品价格波动范围的 API 路径
OPTION_TRADES = '/api/v5/public/option-trades' # 获取期权成交数据的 API 路径

# TRADING DATA (交易数据相关 API)
SUPPORT_COIN = '/api/v5/rubik/stat/trading-data/support-coin' # 获取支持币种的 API 路径
TAKER_VOLUME = '/api/v5/rubik/stat/taker-volume' # 获取 taker 交易量的 API 路径
MARGIN_LENDING_RATIO = '/api/v5/rubik/stat/margin/loan-ratio' # 获取杠杆借贷比率的 API 路径
LONG_SHORT_RATIO = '/api/v5/rubik/stat/contracts/long-short-account-ratio' # 获取合约多空账户比的 API 路径
CONTRACTS_INTEREST_VOLUME = '/api/v5/rubik/stat/contracts/open-interest-volume' # 获取合约持仓量和交易量的 API 路径
OPTIONS_INTEREST_VOLUME = '/api/v5/rubik/stat/option/open-interest-volume' # 获取期权持仓量和交易量的 API 路径
PUT_CALL_RATIO = '/api/v5/rubik/stat/option/open-interest-volume-ratio' # 获取期权看涨看跌比的 API 路径
OPEN_INTEREST_VOLUME_EXPIRY = '/api/v5/rubik/stat/option/open-interest-volume-expiry' # 获取期权按到期日持仓量和交易量的 API 路径
INTEREST_VOLUME_STRIKE = '/api/v5/rubik/stat/option/open-interest-volume-strike' # 获取期权按行权价持仓量和交易量的 API 路径
TAKER_FLOW = '/api/v5/rubik/stat/option/taker-block-volume' # 获取期权大宗交易 taker 交易量的 API 路径
GET_OPEN_INTEREST_HISTORY = '/api/v5/rubik/stat/contracts/open-interest-history' # 获取合约持仓量历史的 API 路径
GET_TAKER_VOLUME_CONTRACT = '/api/v5/rubik/stat/taker-volume-contract' # 获取合约 taker 交易量的 API 路径
GET_LONG_SHORT_ACCOUNT_RADIO_CONTRACT_TOP_TRADER = '/api/v5/rubik/stat/contracts/long-short-account-ratio-contract-top-trader' # 获取合约精英交易员多空账户比的 API 路径
GET_LONG_SHORT_POSTION_RADIO_CONTRACT_TOP_TRADER = '/api/v5/rubik/stat/contracts/long-short-position-ratio-contract-top-trader' # 获取合约精英交易员多空持仓比的 API 路径
GET_LONG_SHORT_ACCOUNT_RADIO_CONTRACT = '/api/v5/rubik/stat/contracts/long-short-account-ratio-contract' # 获取合约多空账户比的 API 路径 (与 LONG_SHORT_RATIO 重复)

# TRADE (交易相关 API)
PLACR_ORDER = '/api/v5/trade/order' # 下单的 API 路径
BATCH_ORDERS = '/api/v5/trade/batch-orders' # 批量下单的 API 路径
CANAEL_ORDER = '/api/v5/trade/cancel-order' # 撤销订单的 API 路径
CANAEL_BATCH_ORDERS = '/api/v5/trade/cancel-batch-orders' # 批量撤销订单的 API 路径
AMEND_ORDER = '/api/v5/trade/amend-order' # 修改订单的 API 路径
AMEND_BATCH_ORDER = '/api/v5/trade/amend-batch-orders' # 批量修改订单的 API 路径
CLOSE_POSITION = '/api/v5/trade/close-position' # 平仓的 API 路径
ORDER_INFO = '/api/v5/trade/order' # 获取订单信息的 API 路径
ORDERS_PENDING = '/api/v5/trade/orders-pending' # 获取未成交订单的 API 路径
ORDERS_HISTORY = '/api/v5/trade/orders-history' # 获取订单历史的 API 路径
ORDERS_HISTORY_ARCHIVE = '/api/v5/trade/orders-history-archive' # 获取订单历史归档的 API 路径
ORDER_FILLS = '/api/v5/trade/fills' # 获取成交明细的 API 路径
ORDERS_FILLS_HISTORY = '/api/v5/trade/fills-history' # 获取成交历史的 API 路径
PLACE_ALGO_ORDER = '/api/v5/trade/order-algo' # 下高级委托单的 API 路径
CANCEL_ALGOS = '/api/v5/trade/cancel-algos' # 撤销高级委托单的 API 路径
AMEND_ALGOS = '/api/v5/trade/amend-algos' # 修改高级委托单的 API 路径
Cancel_Advance_Algos = '/api/v5/trade/cancel-advance-algos' # 撤销高级委托单的 API 路径 (与 CANCEL_ALGOS 重复)
ORDERS_ALGO_OENDING = '/api/v5/trade/orders-algo-pending' # 获取未生效高级委托单的 API 路径
ORDERS_ALGO_HISTORY = '/api/v5/trade/orders-algo-history' # 获取高级委托单历史的 API 路径
EASY_CONVERT_CURRENCY_LIST = '/api/v5/trade/easy-convert-currency-list' # 获取闪电互换币种列表的 API 路径
EASY_CONVERT = '/api/v5/trade/easy-convert' # 闪电互换的 API 路径
EASY_CONVERT_HISTORY = '/api/v5/trade/easy-convert-history' # 获取闪电互换历史的 API 路径
ONE_CLICK_REPAY_CURRENCY_LIST = '/api/v5/trade/one-click-repay-currency-list' # 获取一键还币币种列表的 API 路径
ONE_CLICK_REPAY = '/api/v5/trade/one-click-repay' # 一键还币的 API 路径
ONE_CLICK_REPAY_HISTORY = '/api/v5/trade/one-click-repay-history' # 获取一键还币历史的 API 路径
GET_ORDER_ALGO = '/api/v5/trade/order-algo' # 获取高级委托单详情的 API 路径 (与 PLACE_ALGO_ORDER 重复)
MASS_CANCEL = '/api/v5/trade/mass-cancel' # 批量撤单的 API 路径
CANCEL_ALL_AFTER = '/api/v5/trade/cancel-all-after' # 设置自动撤销所有订单的 API 路径
FILLS_ARCHIVE = '/api/v5/trade/fills-archive' # 获取成交明细归档的 API 路径
FILLS_ARCHIVES = '/api/v5/trade/fills-archive' # 获取成交明细归档的 API 路径 (重复定义)
ORDER_PRECHECK = '/api/v5/trade/order-precheck' # 订单预检查的 API 路径

# Sprd (价差交易相关 API)
SPRD_PLACE_ORDER = '/api/v5/sprd/order' # 价差下单的 API 路径
SPRD_CANCEL_ORDER = '/api/v5/sprd/cancel-order' # 价差撤单的 API 路径
SPRD_MASS_CANCELS = '/api/v5/sprd/mass-cancel' # 价差批量撤单的 API 路径
SPRD_AMEND_CANCELS = '/api/v5/sprd/amend-order' # 价差修改订单的 API 路径
SPRD_ORDER = '/api/v5/sprd/order' # 获取价差订单详情的 API 路径 (与 SPRD_PLACE_ORDER 重复)
SPRD_ORDERS_PENDING = '/api/v5/sprd/orders-pending' # 获取价差未成交订单的 API 路径
SPRD_ORDERS_HISTORY = '/api/v5/sprd/orders-history' # 获取价差订单历史的 API 路径
SPRD_ORDERS_HISTORY_ARCHIVE = '/api/v5/sprd/orders-history-archive' # 获取价差订单历史归档的 API 路径
SPRD_TRADES = '/api/v5/sprd/trades' # 获取价差成交数据的 API 路径
SPRD_SPREADS = '/api/v5/sprd/spreads' # 获取价差列表的 API 路径
SPRD_BOOKS = '/api/v5/sprd/books' # 获取价差深度数据的 API 路径
SPRD_TICKER = '/api/v5/market/sprd-ticker' # 获取价差行情信息的 API 路径
SPRD_PUBLIC_TRADES = '/api/v5/sprd/public-trades' # 获取价差公共成交数据的 API 路径
SPRD_CANCEL_ALL_AFTER = '/api/v5/sprd/cancel-all-after' # 设置价差自动撤销所有订单的 API 路径
GET_SPRD_CANDLES = '/api/v5/market/sprd-candles' # 获取价差 K 线数据的 API 路径
GET_SPRD_HISTORY_CANDLES = '/api/v5/market/sprd-history-candles' # 获取价差历史 K 线数据的 API 路径

# SubAccount (子账户相关 API)
BALANCE = '/api/v5/account/subaccount/balances' # 获取子账户余额的 API 路径
BILLs = '/api/v5/asset/subaccount/bills' # 获取子账户账单的 API 路径
DELETE = '/api/v5/users/subaccount/delete-apikey' # 移除此接口 (删除子账户 API Key)
RESET = '/api/v5/users/subaccount/modify-apikey' # 移除此接口 (修改子账户 API Key)
CREATE = '/api/v5/users/subaccount/apikey' # 移除此接口 (创建子账户 API Key)
WATCH = '/api/v5/users/subaccount/apikey' # 移除此接口 (查看子账户 API Key)
VIEW_LIST = '/api/v5/users/subaccount/list' # 获取子账户列表的 API 路径
SUBACCOUNT_TRANSFER = '/api/v5/asset/subaccount/transfer' # 子账户资金划转的 API 路径
ENTRUST_SUBACCOUNT_LIST = '/api/v5/users/entrust-subaccount-list' # 获取受托子账户列表的 API 路径
MODIFY_APIKEY = '/api/v5/users/subaccount/modify-apikey' # 修改子账户 API Key 的 API 路径
ASSET_BALANCES = '/api/v5/asset/subaccount/balances' # 获取子账户资产余额的 API 路径 (与 BALANCE 重复)
PARTNER_IF_REBATE = '/api/v5/users/partner/if-rebate' # 合作伙伴是否返佣的 API 路径
MAX_WITHDRAW = '/api/v5/account/subaccount/max-withdrawal' # 获取子账户最大提币数量的 API 路径
SUB_BILLS = '/api/v5/asset/subaccount/managed-subaccount-bills' # 获取代管子账户账单的 API 路径

# Broker (经纪商相关 API)
BROKER_INFO = '/api/v5/broker/nd/info' # 获取经纪商信息的 API 路径
CREATE_SUBACCOUNT = '/api/v5/broker/dma/create-subaccount' # 创建经纪商子账户的 API 路径
DELETE_SUBACCOUNT = '/api/v5/broker/dma/delete-subaccount' # 删除经纪商子账户的 API 路径
SUBACCOUNT_INFO = '/api/v5/broker/dma/subaccount-info' # 获取经纪商子账户信息的 API 路径
SUBACCOUNT_TRADE_FEE= '/api/v5/broker/dma/subaccount-trade-fee' # 获取经纪商子账户交易费用的 API 路径
SET_SUBACCOUNT_LEVEL = '/api/v5/broker/dma/set-subaccount-level' # 设置经纪商子账户等级的 API 路径
SET_SUBACCOUNT_FEE_REAT = '/api/v5/broker/nd/set-subaccount-fee-rate' # 设置经纪商子账户费率的 API 路径
SUBACCOUNT_DEPOSIT_ADDRESS = '/api/v5/asset/broker/dma/subaccount-deposit-address' # 获取经纪商子账户充值地址的 API 路径
SUBACCOUNT_DEPOSIT_HISTORY = '/api/v5/asset/broker/dma/subaccount-deposit-history' # 获取经纪商子账户充值历史的 API 路径
REBATE_DAILY = '/api/v5/broker/nd/rebate-daily' # 获取经纪商每日返佣的 API 路径
# BROKER_INFO = '/api/v5/broker/nd/info' # 获取经纪商信息的 API 路径 (重复定义) Broker 获取充值地址文档无法打开，预留位置
DMA_CREAET_APIKEY = '/api/v5/broker/dma/subaccount/apikey' # 创建 DMA 子账户 API Key 的 API 路径
DMA_SELECT_APIKEY = '/api/v5/broker/dma/subaccount/apikey' # 查询 DMA 子账户 API Key 的 API 路径
DMA_MODIFY_APIKEY = '/api/v5/broker/dma/subaccount/modify-apikey' # 修改 DMA 子账户 API Key 的 API 路径
DMA_DELETE_APIKEY = '/api/v5/broker/dma/subaccount/delete-apikey' # 删除 DMA 子账户 API Key 的 API 路径
GET_REBATE_PER_ORDERS = '/api/v5/broker/nd/rebate-per-orders' # 获取每笔订单返佣的 API 路径
REBATE_PER_ORDERS = '/api/v5/broker/nd/rebate-per-orders' # 获取每笔订单返佣的 API 路径 (重复定义)
MODIFY_SUBACCOUNT_DEPOSIT_ADDRESS = '/api/v5/asset/broker/dma/modify-subaccount-deposit-address' # 修改经纪商子账户充值地址的 API 路径
ND_SUBACCOUNT_WITHDRAWAL_HISTORY = '/api/v5/asset/broker/dma/subaccount-withdrawal-history' # 获取经纪商子账户提币历史的 API 路径
SET_SUBACCOUNT_ASSETS = '/api/v5/broker/dma/set-subaccount-assets' # 设置经纪商子账户资产的 API 路径
R_SACCOUNT_IP = '/api/v5/broker/dma/report-subaccount-ip' # 报告子账户 IP 的 API 路径
IF_REBATE = '/api/v5/broker/nd/if-rebate' # 是否返佣的 API 路径

# Convert (闪兑相关 API)
GET_CURRENCIES = '/api/v5/asset/convert/currencies' # 获取闪兑支持币种的 API 路径
GET_CURRENCY_PAIR = '/api/v5/asset/convert/currency-pair' # 获取闪兑币对的 API 路径
ESTIMATE_QUOTE = '/api/v5/asset/convert/estimate-quote' # 获取闪兑预估报价的 API 路径
CONVERT_TRADE = '/api/v5/asset/convert/trade' # 执行闪兑交易的 API 路径
CONVERT_HISTORY = '/api/v5/asset/convert/history' # 获取闪兑历史的 API 路径

# FDBroker (FD 经纪商相关 API)
FD_GET_REBATE_PER_ORDERS = '/api/v5/broker/fd/rebate-per-orders' # 获取 FD 经纪商每笔订单返佣的 API 路径
FD_REBATE_PER_ORDERS = '/api/v5/broker/fd/rebate-per-orders' # 获取 FD 经纪商每笔订单返佣的 API 路径 (重复定义)
FD_IF_REBATE = '/api/v5/broker/fd/if-rebate' # 获取 FD 经纪商是否返佣的 API 路径

# Rfq (询价相关 API)
COUNTERPARTIES = '/api/v5/rfq/counterparties' # 获取询价交易对手的 API 路径
CREATE_RFQ = '/api/v5/rfq/create-rfq' # 创建询价请求的 API 路径
CANCEL_RFQ = '/api/v5/rfq/cancel-rfq' # 撤销询价请求的 API 路径
CANCEL_BATCH_RFQS = '/api/v5/rfq/cancel-batch-rfqs' # 批量撤销询价请求的 API 路径
CANCEL_ALL_RSQS = '/api/v5/rfq/cancel-all-rfqs' # 撤销所有询价请求的 API 路径
EXECUTE_QUOTE = '/api/v5/rfq/execute-quote' # 执行报价的 API 路径
CREATE_QUOTE = '/api/v5/rfq/create-quote' # 创建报价的 API 路径
CANCEL_QUOTE = '/api/v5/rfq/cancel-quote' # 撤销报价的 API 路径
CANCEL_BATCH_QUOTES = '/api/v5/rfq/cancel-batch-quotes' # 批量撤销报价的 API 路径
CANCEL_ALL_QUOTES = '/api/v5/rfq/cancel-all-quotes' # 撤销所有报价的 API 路径
GET_RFQS = '/api/v5/rfq/rfqs' # 获取询价请求列表的 API 路径
GET_QUOTES = '/api/v5/rfq/quotes' # 获取报价列表的 API 路径
GET_RFQ_TRADES = '/api/v5/rfq/trades' # 获取询价成交数据的 API 路径
GET_PUBLIC_TRADES = '/api/v5/rfq/public-trades' # 获取询价公共成交数据的 API 路径
RFQ_CANCEL_ALL_AFTER = '/api/v5/rfq/cancel-all-after' # 设置询价自动撤销所有订单的 API 路径
MARKET_INSTRUMENT_SETTINGS = '/api/v5/rfq/maker-instrument-settings' # 获取做市商交易产品设置的 API 路径
MMP_RESET = '/api/v5/rfq/mmp-reset' # 询价做市商保护重置的 API 路径
MMP_CONFIG = '/api/v5/rfq/mmp-config' # 询价做市商保护配置的 API 路径
MMP_CONF = '/api/v5/rfq/mmp-config' # 询价做市商保护配置的 API 路径 (与 MMP_CONFIG 重复)
# MMP_CONFIG = '/api/v5/account/mmp-config' # 账户做市商保护配置的 API 路径 (重复定义)
MMP = '/api/v5/account/mmp-config' # 账户做市商保护配置的 API 路径 (与 MMP_CONFIG 重复)
SET_ACCOUNT_LEVEL = '/api/v5/account/set-account-level' # 设置账户等级的 API 路径
GET_MAKER_INSTRUMENT_SETTINGS = '/api/v5/rfq/maker-instrument-settings' # 获取做市商交易产品设置的 API 路径 (与 MARKET_INSTRUMENT_SETTINGS 重复)
POSITION_BUILDER = '/api/v5/account/position-builder' # 获取仓位构建器信息的 API 路径

# tradingBot (交易机器人相关 API)
GRID_ORDER_ALGO = '/api/v5/tradingBot/grid/order-algo' # 网格策略下单的 API 路径
GRID_AMEND_ORDER_ALGO = '/api/v5/tradingBot/grid/amend-order-algo' # 修改网格策略订单的 API 路径
GRID_STOP_ORDER_ALGO = '/api/v5/tradingBot/grid/stop-order-algo' # 停止网格策略订单的 API 路径
GRID_ORDERS_ALGO_PENDING = '/api/v5/tradingBot/grid/orders-algo-pending' # 获取网格策略未生效订单的 API 路径
GRID_ORDERS_ALGO_HISTORY = '/api/v5/tradingBot/grid/orders-algo-history' # 获取网格策略订单历史的 API 路径
GRID_ORDERS_ALGO_DETAILS = '/api/v5/tradingBot/grid/orders-algo-details' # 获取网格策略订单详情的 API 路径
GRID_SUB_ORDERS = '/api/v5/tradingBot/grid/sub-orders' # 获取网格策略子订单的 API 路径
GRID_POSITIONS = '/api/v5/tradingBot/grid/positions' # 获取网格策略持仓的 API 路径
GRID_WITHDRAW_INCOME = '/api/v5/tradingBot/grid/withdraw-income' # 网格策略提取收益的 API 路径
GRID_COMPUTE_MARGIN_BALANCE = '/api/v5/tradingBot/grid/compute-margin-balance' # 计算网格策略保证金余额的 API 路径
GRID_MARGIN_BALANCE = '/api/v5/tradingBot/grid/margin-balance' # 获取网格策略保证金余额的 API 路径
GRID_AI_PARAM = '/api/v5/tradingBot/grid/ai-param' # 获取网格策略 AI 参数的 API 路径
GRID_ADJUST_INVESTMETN = '/api/v5/tradingBot/grid/adjust-investment' # 调整网格策略投入的 API 路径
GRID_QUANTITY = '/api/v5/tradingBot/grid/grid-quantity' # 获取网格策略数量的 API 路径

# finance (金融相关 API)
STAKING_DEFI_OFFERS = '/api/v5/finance/staking-defi/offers' # 获取 Staking Defi 产品的 API 路径
STAKING_DEFI_PURCHASE = '/api/v5/finance/staking-defi/purchase' # 申购 Staking Defi 产品的 API 路径
STAKING_DEFI_REDEEM = '/api/v5/finance/staking-defi/redeem' # 赎回 Staking Defi 产品的 API 路径
STAKING_DEFI_CANCEL = '/api/v5/finance/staking-defi/cancel' # 取消 Staking Defi 订单的 API 路径
STAKING_DEFI_ORDERS_ACTIVE = '/api/v5/finance/staking-defi/orders-active' # 获取 Staking Defi 活跃订单的 API 路径
STAKING_DEFI_ORDERS_HISTORY = '/api/v5/finance/staking-defi/orders-history' # 获取 Staking Defi 订单历史的 API 路径
STAKING_DEFI_ETH_PURCASE = '/api/v5/finance/staking-defi/eth/purchase' # 申购 ETH Staking Defi 的 API 路径
STAKING_DEFI_ETH_REDEEM = '/api/v5/finance/staking-defi/eth/redeem' # 赎回 ETH Staking Defi 的 API 路径
STAKING_DEFI_ETH_BALANCE ='/api/v5/finance/staking-defi/eth/balance' # 获取 ETH Staking Defi 余额的 API 路径
STAKING_DEFI_ETH_P_R_HISTORY= '/api/v5/finance/staking-defi/eth/purchase-redeem-history' # 获取 ETH Staking Defi 申赎历史的 API 路径
STAKING_DEFI_ETH_APY_HISTORY = '/api/v5/finance/staking-defi/eth/apy-history' # 获取 ETH Staking Defi 年化收益率历史的 API 路径
SAVINGS_LENDING_RATE_SUM = '/api/v5/finance/savings/lending-rate-summary' # 借贷利率汇总的 API 路径
SAVINGS_LENDING_RATE_HIS = '/api/v5/finance/savings/lending-rate-history' # 借贷利率历史的 API 路径
FIXED_LOAN_LENDING_OFFERS = '/api/v5/finance/fixed-loan/lending-offers' # 获取固定借贷产品列表的 API 路径
FIXED_LOAN_LENDING_APY_HIS = '/api/v5/finance/fixed-loan/lending-apy-history' # 获取固定借贷年化收益率历史的 API 路径
FIXED_LOAN_PENDING_LENDING_VOL = '/api/v5/finance/fixed-loan/pending-lending-volume' # 获取固定借贷待匹配借贷量的 API 路径
FIXED_LOAN_LENDING_ORDER = '/api/v5/finance/fixed-loan/lending-order' # 固定借贷下单的 API 路径
FIXED_LOAN_AMEND_LENDING_ORDER = '/api/v5/finance/fixed-loan/amend-lending-order' # 修改固定借贷订单的 API 路径
FIXED_LOAN_LENDING_ORDERS_LIST = '/api/v5/finance/fixed-loan/lending-orders-list' # 获取固定借贷订单列表的 API 路径
FIXED_LOAN_LENDING_SUB_ORDERS = '/api/v5/finance/fixed-loan/lending-sub-orders' # 获取固定借贷子订单的 API 路径
STAKING_DEFI_ETH_PRODUCT_INFO = '/api/v5/finance/staking-defi/eth/product-info' # 获取 ETH Staking Defi 产品信息的 API 路径
STAKING_DEFI_SOL_PURCASE = '/api/v5/finance/staking-defi/sol/purchase' # 申购 SOL Staking Defi 的 API 路径
STAKING_DEFI_SOL_REDEEM = '/api/v5/finance/staking-defi/sol/redeem' # 赎回 SOL Staking Defi 的 API 路径
STAKING_DEFI_SOL_BALANCE = '/api/v5/finance/staking-defi/sol/balance' # 获取 SOL Staking Defi 余额的 API 路径
STAKING_DEFI_SOL_P_R_HISTORY = '/api/v5/finance/staking-defi/sol/purchase-redeem-history' # 获取 SOL Staking Defi 申赎历史的 API 路径
STAKING_DEFI_SOL_APY_HISTORY = '/api/v5/finance/staking-defi/sol/apy-history' # 获取 SOL Staking Defi 年化收益率历史的 API 路径
FLEXIBLE_LOAN_BORROW_CURRENCIES = '/api/v5/finance/flexible-loan/borrow-currencies' # 获取活期借贷可借币种的 API 路径
FLEXIBLE_LOAN_COLLATERAL_ASSETS = '/api/v5/finance/flexible-loan/collateral-assets' # 获取活期借贷可抵押资产的 API 路径
FLEXIBLE_LOAN_MAX_LOAN = '/api/v5/finance/flexible-loan/max-loan' # 获取活期借贷最大可借金额的 API 路径
FLEXIBLE_LOAN_MAX_C_R_A = '/api/v5/finance/flexible-loan/max-collateral-redeem-amount' # 获取活期借贷最大可赎回抵押物数量的 API 路径
FLEXIBLE_LOAN_ADJ_COLL = '/api/v5/finance/flexible-loan/adjust-collateral' # 调整活期借贷抵押物的 API 路径
FLEXIBLE_LOAN_LOAN_INFO = '/api/v5/finance/flexible-loan/loan-info' # 获取活期借贷信息的 API 路径
FLEXIBLE_LOAN_LOAN_HISTORY = '/api/v5/finance/flexible-loan/loan-history' # 获取活期借贷历史的 API 路径
FLEXIBLE_LOAN_INT_ACC = '/api/v5/finance/flexible-loan/interest-accrued' # 获取活期借贷已产生利息的 API 路径

# copytrading (跟单交易相关 API)
CURRENT_SUBPOSITIONS = '/api/v5/copytrading/current-subpositions' # 获取跟单当前子仓位的 API 路径
SUBPOSITIONS_HISTORY = '/api/v5/copytrading/subpositions-history' # 获取跟单子仓位历史的 API 路径
COPYTRADING_ALGO_ORDER = '/api/v5/copytrading/algo-order' # 跟单高级委托下单的 API 路径
COPYTRADING_CLOSE_POS = '/api/v5/copytrading/close-subposition' # 跟单平仓的 API 路径
COPYTRADING_INSTRUMENTS = '/api/v5/copytrading/instruments' # 获取跟单交易产品的 API 路径
COPYTRADING_SET_INSTRUMENTS = '/api/v5/copytrading/set-instruments' # 设置跟单交易产品的 API 路径
PROFIT_SHARING_DETAILS = '/api/v5/copytrading/profit-sharing-details' # 获取分润详情的 API 路径
TOTAL_PROFIT_SHARING = '/api/v5/copytrading/total-profit-sharing' # 获取总分润的 API 路径
UNREALIZED_PROFIT_SHARING_DETAILS = '/api/v5/copytrading/unrealized-profit-sharing-details' # 获取未实现分润详情的 API 路径
FIRST_COPY_SETTINGS = '/api/v5/copytrading/first-copy-settings' # 获取首次跟单设置的 API 路径
AMEND_COPY_SETTINGS = '/api/v5/copytrading/amend-copy-settings' # 修改跟单设置的 API 路径
STOP_COPY_SETTINGS = 'api/v5/copytrading/stop-copy-trading' # 停止跟单的 API 路径
COPY_SETTINGS = 'api/v5/copytrading/copy-trading' # 获取跟单设置的 API 路径
BATCH_LEVERAGE_INF = '/api/v5/copytrading/batch-leverage-info' # 批量获取杠杆信息的 API 路径
BATCH_SET_LEVERAGE = '/api/v5/copytrading/batch-set-leverage' # 批量设置杠杆的 API 路径
CURRENT_LEAD_TRADERS = '/api/v5/copytrading/current-lead-traders' # 获取当前带单交易员的 API 路径
LEAD_TRADERS_HISTORY = '/api/v5/copytrading/lead-traders-history' # 获取带单交易员历史的 API 路径
PUBLIC_LEAD_TRADERS = '/api/v5/copytrading/public-lead-traders' # 获取公开带单交易员的 API 路径
PUBLIC_WEEKLY_PNL = '/api/v5/copytrading/public-weekly-pnl' # 获取公开带单交易员周收益的 API 路径
PUBLIC_PNL = '/api/v5/copytrading/public-pnl' # 获取公开带单交易员收益的 API 路径
PUBLIC_STATS = '/api/v5/copytrading/public-stats' # 获取公开带单交易员统计数据的 API 路径
PUBLIC_PRE_CURR = '/api/v5/copytrading/public-preference-currency' # 获取公开带单交易员偏好币种的 API 路径
PUBLIC_CURR_SUBPOS = '/api/v5/copytrading/public-current-subpositions' # 获取公开带单交易员当前子仓位的 API 路径
PUBLIC_SUBPOS_HIS = '/api/v5/copytrading/public-subpositions-history' # 获取公开带单交易员子仓位历史的 API 路径
APP_LEA_TRAD = '/api/v5/copytrading/apply-lead-trading' # 申请带单交易的 API 路径
STOP_LEA_TRAD = '/api/v5/copytrading/stop-lead-trading' # 停止带单交易的 API 路径
AMEDN_PRO_SHAR_RATIO = '/api/v5/copytrading/amend-profit-sharing-ratio' # 修改分润比例的 API 路径
LEAD_TRADERS = '/api/v5/copytrading/lead-traders' # 获取带单交易员的 API 路径
WEEKLY_PNL = '/api/v5/copytrading/weekly-pnl' # 获取周收益的 API 路径
PNL = '/api/v5/copytrading/pnl' # 获取收益的 API 路径
STATS = '/api/v5/copytrading/stats' # 获取统计数据的 API 路径
PRE_CURR = '/api/v5/copytrading/preference-currency' # 获取偏好币种的 API 路径
PRE_CURR_SUNPOSITION = '/api/v5/copytrading/performance-current-subpositions' # 获取业绩当前子仓位的 API 路径
PRE_SUNPOSITION_HISTORY = '/api/v5/copytrading/performance-subpositions-history' # 获取业绩子仓位历史的 API 路径
COPY_TRADERS = '/api/v5/copytrading/copy-traders' # 获取跟单交易员的 API 路径
PUB_COPY_TRADERS = '/api/v5/copytrading/public-copy-traders' # 获取公开跟单交易员的 API 路径
CONFIG = '/api/v5/copytrading/config' # 获取跟单配置的 API 路径
TOTAL_UNREA_PRO_SHAR = '/api/v5/copytrading/total-unrealized-profit-sharing' # 获取总未实现分润的 API 路径

# Signal (信号交易相关 API)
CREAT_SIGNAL = '/api/v5/tradingBot/signal/create-signal' # 创建信号的 API 路径
SIGNALS = '/api/v5/tradingBot/signal/signals' # 获取信号列表的 API 路径
ORDER_ALGO_SIGNAL = '/api/v5/tradingBot/signal/order-algo' # 信号交易高级委托下单的 API 路径
SIGNAL_STOP_ORDER_ALGO = '/api/v5/tradingBot/signal/stop-order-algo' # 停止信号交易高级委托订单的 API 路径
SIGNAL_MARGIN_BALANCE = '/api/v5/tradingBot/signal/margin-balance' # 获取信号交易保证金余额的 API 路径
AMENDTPSL = '/api/v5/tradingBot/signal/amendTPSL' # 修改信号交易止盈止损的 API 路径
SIGNAL_SET_INSTRUMENTS = '/api/v5/tradingBot/signal/set-instruments' # 设置信号交易产品的 API 路径
ORDERS_ALGO_DETAILS = '/api/v5/tradingBot/signal/orders-algo-details' # 获取信号交易高级委托订单详情的 API 路径
ORDERS_ALGO_PENDING = '/api/v5/tradingBot/signal/orders-algo-pending' # 获取信号交易未生效高级委托订单的 API 路径
ORDERS_ALGO_HISTORY = '/api/v5/tradingBot/signal/orders-algo-history' # 获取信号交易高级委托订单历史的 API 路径
SIGNAL_POSITIONS = '/api/v5/tradingBot/signal/positions' # 获取信号交易持仓的 API 路径
SIGNAL_POSITIONS_HISTORY = '/api/v5/tradingBot/signal/positions-history' # 获取信号交易持仓历史的 API 路径
SIGNAL_CLOSE_POSITION = '/api/v5/tradingBot/signal/close-position' # 信号交易平仓的 API 路径
SUB_ORDER = '/api/v5/tradingBot/signal/sub-order' # 获取信号交易子订单的 API 路径
CANCEL_SUB_ORDER = '/api/v5/tradingBot/signal/cancel-sub-order' # 撤销信号交易子订单的 API 路径
SUB_ORDERS = '/api/v5/tradingBot/signal/sub-orders' # 获取信号交易子订单列表的 API 路径
EVENT_HISTORY = '/api/v5/tradingBot/signal/event-history' # 获取信号交易事件历史的 API 路径

# recurring (定投相关 API)
RECURRING_ORDER_ALGO = '/api/v5/tradingBot/recurring/order-algo' # 定投策略下单的 API 路径
RECURRING_AMEND_ORDER_ALGO = '/api/v5/tradingBot/recurring/amend-order-algo' # 修改定投策略订单的 API 路径
RECURRING_STOP_ORDER_ALGO = '/api/v5/tradingBot/recurring/stop-order-algo' # 停止定投策略订单的 API 路径
RECURRING_ORDER_ALGO_PENDING = '/api/v5/tradingBot/recurring/orders-algo-pending' # 获取定投策略未生效订单的 API 路径
RECURRING_ORDER_ALGO_HISTORY = '/api/v5/tradingBot/recurring/orders-algo-history' # 获取定投策略订单历史的 API 路径
RECURRING_ORDER_ALGO_DETAILS = '/api/v5/tradingBot/recurring/orders-algo-details' # 获取定投策略订单详情的 API 路径
RECURRING_SUB_ORDERS = '/api/v5/tradingBot/recurring/sub-orders' # 获取定投策略子订单的 API 路径

# status (系统状态相关 API)
STATUS = '/api/v5/system/status' # 获取系统状态的 API 路径
GET_ANNOUNCEMENTS = '/api/v5/support/announcements' # 获取公告列表的 API 路径
GET_ANNOUNCEMENTS_TYPES = '/api/v5/support/announcement-types' # 获取公告类型的 API 路径