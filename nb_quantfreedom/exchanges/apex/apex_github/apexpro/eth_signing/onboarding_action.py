from web3 import Web3

from apexpro.constants import REGISTER_ENVID_MAIN
from apexpro.eth_signing import util
from apexpro.eth_signing.sign_off_chain_action import SignOffChainAction

# On mainnet, include an extra onlySignOn parameter.
EIP712_ONBOARDING_ACTION_STRUCT = [
    {'type': 'string', 'name': 'action'},
    {'type': 'string', 'name': 'onlySignOn'},
    {'type': 'string', 'name': 'nonce'},
]
EIP712_ONBOARDING_ACTION_STRUCT_STRING = (
    'ApeX(' +
    'string action,' +
    'string onlySignOn,' +
    'string nonce' +
    ')'
)
EIP712_ONBOARDING_ACTION_STRUCT_TESTNET = [
    {'type': 'string', 'name': 'action'},
]
EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET = (
    'apex(' +
    'string action' +
    ')'
)
EIP712_STRUCT_NAME = 'ApeX'

ONLY_SIGN_ON_DOMAIN_MAINNET = 'https://pro.apex.exchange'


class SignOnboardingAction(SignOffChainAction):

    def get_eip712_struct(self):
        # On mainnet, include an extra onlySignOn parameter.
        #if self.network_id == REGISTER_ENVID_MAIN:
        return EIP712_ONBOARDING_ACTION_STRUCT
        #else:
        #    return EIP712_ONBOARDING_ACTION_STRUCT_TESTNET

    def get_eip712_struct_name(self):
        return EIP712_STRUCT_NAME

    def get_eip712_message(
        self,
        **message,
    ):
        eip712_message = super(SignOnboardingAction, self).get_eip712_message(
            **message,
        )

        # On mainnet, include an extra onlySignOn parameter.
        #if self.network_id == REGISTER_ENVID_MAIN:
        eip712_message['message']['onlySignOn'] = (
                'https://pro.apex.exchange'
        )

        return eip712_message

    def get_hash(
        self,
        action,
        nonce
    ):
        # On mainnet, include an extra onlySignOn parameter.
        #if self.network_id == REGISTER_ENVID_MAIN:
        eip712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING
        #else:
        #    eip712_struct_str = EIP712_ONBOARDING_ACTION_STRUCT_STRING_TESTNET

        data = [
            [
                'bytes32',
                'bytes32',
            ],
            [
                util.hash_string(eip712_struct_str),
                util.hash_string(action)
            ],
        ]

        # On mainnet, include an extra onlySignOn parameter.
        #if self.network_id == REGISTER_ENVID_MAIN:
        data[0].append('bytes32')
        data[1].append(util.hash_string(ONLY_SIGN_ON_DOMAIN_MAINNET))

        data[0].append('bytes32')
        data[1].append(util.hash_string(nonce))

        struct_hash = Web3.solidityKeccak(*data)
        return self.get_eip712_hash(struct_hash)
