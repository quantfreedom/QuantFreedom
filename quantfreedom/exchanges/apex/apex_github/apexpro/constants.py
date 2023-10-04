# ------------ API URLs ------------
APEX_HTTP_MAIN = 'https://pro.apex.exchange'
APEX_HTTP_TEST = 'https://testnet.pro.apex.exchange'
APEX_WS_MAIN = 'wss://quote.pro.apex.exchange'
APEX_WS_TEST = 'wss://quote-qa.pro.apex.exchange'

URL_SUFFIX = "/api"

# ------------ register_env_id ------------
REGISTER_ENVID_MAIN = 1
REGISTER_ENVID_TEST = 5

# ------------ network_id ------------
NETWORKID_MAIN = 1
NETWORKID_TEST = 5

# ------------ Signature Types ------------
SIGNATURE_TYPE_NO_PREPEND = 0
SIGNATURE_TYPE_DECIMAL = 1
SIGNATURE_TYPE_HEXADECIMAL = 2
SIGNATURE_TYPE_PERSONAL = 3


# ------------ Order Side ------------
ORDER_SIDE_BUY = 'BUY'
ORDER_SIDE_SELL = 'SELL'


# ------------ Assets ------------
ASSET_USDC = 'USDC'
ASSET_BTC = 'BTC'
ASSET_ETH = 'ETH'
ASSET_LINK = 'LINK'
ASSET_AAVE = 'AAVE'
ASSET_DOGE = 'DOGE'
ASSET_MATIC = 'MATIC'
COLLATERAL_ASSET = ASSET_USDC

ASSET_RESOLUTION = {
    ASSET_USDC: '1e6',
}

# ------------ Ethereum Transactions ------------
DEFAULT_GAS_AMOUNT = 250000
DEFAULT_GAS_MULTIPLIER = 1.5
DEFAULT_GAS_PRICE = 4000000000
DEFAULT_GAS_PRICE_ADDITION = 3
MAX_SOLIDITY_UINT = 115792089237316195423570985008687907853269984665640564039457584007913129639935  # noqa: E501


COLLATERAL_TOKEN_DECIMALS = 6

# ------------ Off-Chain Ethereum-Signed Actions ------------
OFF_CHAIN_ONBOARDING_ACTION = 'ApeX Onboarding' # action:ApeX Onboarding  onlySignOn:https://pro.apex.exchange nonce:1188491033265307648
OFF_CHAIN_KEY_DERIVATION_ACTION = 'L2 Key' #{"name": "ApeX","version": "1.0","envId": 1,"action": "L2 Key","onlySignOn": "https://pro.apex.exchange"}
