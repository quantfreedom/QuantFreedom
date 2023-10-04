# -*- coding: utf-8 -*-

"""
apexpro
------------------------

apexpro is a lightweight and high-performance API connector for the
RESTful and WebSocket APIs of the Apex pro exchange.

Documentation can be found at
https://api-docs.pro.apex.exchange/#introduction

:copyright: (c) 2020-2022 apexpro-exchange
:license: MIT License

"""

import time
import hmac
import json
import logging
import requests

from web3 import Web3
from apexpro.eth_signing import SignWithWeb3, SignOnboardingAction
from apexpro.eth_signing import SignWithKey
from apexpro.constants import REGISTER_ENVID_MAIN, APEX_HTTP_MAIN, URL_SUFFIX, NETWORKID_MAIN
from apexpro.starkex.helpers import private_key_to_public_key_pair_hex

from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor

from .eth import Eth
from .exceptions import FailedRequestError, InvalidRequestError
from .models import configDecoder

try:
    from simplejson.errors import JSONDecodeError
except ImportError:
    from json.decoder import JSONDecodeError

# Versioning.
VERSION = '1.0.0'


class HTTP:
    """
    Connector for Apexpro's HTTP API.

    The below class is maintained for compatibility reasons. You should
    prefer using the market-specific classes maintained in
    inverse_perpetual.py, usdc_perpetual.py, spot.py, etc

    :param endpoint: The endpoint URL of the HTTP API, e.g.
        'https://dev.pro.apex.exchange.com'.
    :type endpoint: str

    """

    # def __init__(self, endpoint=None, api_key=None, api_secret=None,
    #             logging_level=logging.INFO, log_requests=False,
    #             request_timeout=10, recv_window=5000, force_retry=False,
    #             retry_codes=None, ignore_codes=None, max_retries=3,
    #             retry_delay=3, referral_id=None, spot=False):
    #    """Initializes the HTTP class."""

    def __init__(
            self,
            endpoint,
            api_timeout=3000,  # TODO: Actually use this.
            default_ethereum_address=None,
            eth_private_key=None,
            eth_send_options=None,
            network_id=NETWORKID_MAIN,
            env_id=REGISTER_ENVID_MAIN,
            stark_private_key=None,
            stark_public_key=None,
            stark_public_key_y_coordinate=None,
            web3=None,
            web3_account=None,
            web3_provider=None,
            api_key_credentials=None,
            request_timeout=10, recv_window=5000, force_retry=False,
            retry_codes=None, max_retries=3,
            retry_delay=3, referral_id=None, proxies=None
    ):
        # Remove trailing '/' if present, from host.
        if endpoint.endswith('/'):
            self.endpoint = endpoint[:-1]
        # Set the endpoint.
        if endpoint is None:
            self.endpoint = APEX_HTTP_MAIN
        else:
            self.endpoint = endpoint

        # Setup logger.

        self.logger = logging.getLogger(__name__)

        if len(logging.root.handlers) == 0:
            # no handler on root logger set -> we add handler just for this logger to not mess with custom logic from outside
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                                                   datefmt='%Y-%m-%d %H:%M:%S'
                                                   )
                                 )
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)

        # self.logger.warning(
        #     'This HTTP class is maintained for compatibility purposes. You '
        #     'should prefer importing market-specific classes, like so: '
        #     'from apexpro import HTTP; '
        # )

        self.logger.debug('Initializing HTTP session.')
        self.log_requests = False

        self.proxies = proxies
        # Set web3 keys.
        self.eth_send_options = eth_send_options or {}
        self.stark_private_key = stark_private_key
        self.api_key_credentials = api_key_credentials
        self.stark_public_key_y_coordinate = stark_public_key_y_coordinate

        self.web3 = None
        self._eth = None
        self.eth_signer = None
        self.default_address = None
        self.network_id = None

        if web3 is not None or web3_provider is not None:
            if isinstance(web3_provider, str):
                web3_provider = Web3.HTTPProvider(web3_provider)
            self.web3 = web3 or Web3(web3_provider)
            self.eth_signer = SignWithWeb3(self.web3)
            self.default_address = self.web3.eth.defaultAccount or None
            self.network_id = self.web3.net.version

        if eth_private_key is not None or web3_account is not None:
            # May override web3 or web3_provider configuration.
            key = eth_private_key or web3_account.key
            self.eth_signer = SignWithKey(key)
            self.default_address = self.eth_signer.address

        self.default_address = default_ethereum_address or self.default_address
        self.network_id = int(
            network_id or self.network_id or REGISTER_ENVID_MAIN
        )
        self.env_id = int(
            env_id or self.env_id or REGISTER_ENVID_MAIN
        )

        # Derive the public keys.
        if stark_private_key is not None:
            self.stark_public_key, self.stark_public_key_y_coordinate = (
                private_key_to_public_key_pair_hex(stark_private_key)
            )
        if (
                stark_public_key is not None and
                stark_public_key != self.stark_public_key
        ):
            self.logger.warning('STARK public/private key mismatch')
        if (
                stark_public_key_y_coordinate is not None and
                stark_public_key_y_coordinate !=
                self.stark_public_key_y_coordinate
        ):
            self.logger.warning('STARK public/private key mismatch (y)')
        else:
            self.stark_public_key = stark_public_key
            self.stark_public_key_y_coordinate = stark_public_key_y_coordinate

        self.api_key_credentials = api_key_credentials

        self.signer = SignOnboardingAction(self.eth_signer, self.network_id)
        self.starkeySigner = SignOnboardingAction(self.eth_signer, self.env_id)

        # Set timeout.
        self.timeout = request_timeout
        self.recv_window = recv_window
        self.force_retry = force_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Set whitelist of non-fatal Apexpro status codes to retry on.
        if retry_codes is None:
            self.retry_codes = {10002, 10006, 30034, 30035, 130035, 130150}
        else:
            self.retry_codes = retry_codes

        # Initialize requests session.
        self.client = requests.Session()
        #self.client.trust_env = False
        self.client.headers.update(
            {
                'User-Agent': 'apexpro-python-sdk-' + VERSION,
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        self.client.proxies = self.proxies

        # Add referral ID to header.
        if referral_id:
            self.client.headers.update({'Referer': referral_id})

    def _exit(self):
        """Closes the request session."""
        self.client.close()
        self.logger.debug('HTTP session closed.')

    def _auth(self, method, params, recv_window):
        """
        Generates authentication signature per Apexpro API specifications.

        Notes
        -------------------
        Since the POST method requires a JSONified dict, we need to ensure
        the signature uses lowercase booleans instead of Python's
        capitalized booleans. This is done in the bug fix below.

        """

        api_key = self.api_key
        api_secret = self.api_secret

        if api_key is None or api_secret is None:
            raise PermissionError('Authenticated endpoints require keys.')

        # Append required parameters.
        params['api_key'] = api_key
        params['recv_window'] = recv_window
        params['timestamp'] = int(time.time() * 10 ** 3)

        # Sort dictionary alphabetically to create querystring.
        _val = '&'.join(
            [str(k) + '=' + str(v) for k, v in sorted(params.items()) if
             (k != 'sign') and (v is not None)]
        )

        # Bug fix. Replaces all capitalized booleans with lowercase.
        if method == 'POST':
            _val = _val.replace('True', 'true').replace('False', 'false')

        # Return signature.
        return str(hmac.new(
            bytes(api_secret, 'utf-8'),
            bytes(_val, 'utf-8'), digestmod='sha256'
        ).hexdigest())

    @property
    def eth(self):
        '''
        Get the eth module, used for interacting with Ethereum smart contracts.
        '''
        collateral_asset_id = ''
        token_contracts = ''
        web3_provider = ''
        starware_perpetuals_contract = self.config.get('global').get('starkExContractAddress')
        for k, v1 in enumerate(self.config.get('currency')):
            if v1.get('id') == 'USDC':
                collateral_asset_id = v1.get('starkExAssetId')
        for k, v2 in enumerate(self.config.get('multiChain').get('chains')):
            if v2.get('chainId') == self.network_id:
                web3_provider = v2.get('rpcUrl')
                for k, v3 in enumerate(v2.get('tokens')):
                    if v3.get('token') == 'USDC':
                        token_contracts = v3.get('tokenAddress')

        web3_provider = Web3.HTTPProvider(web3_provider)
        self.web3 =  Web3(web3_provider)

        if not self._eth:
            eth_private_key = getattr(self.eth_signer, '_private_key', None)
            if self.web3 and eth_private_key:
                self._eth = Eth(
                    web3=self.web3,
                    network_id=self.network_id,
                    eth_private_key=eth_private_key,
                    default_address=self.default_address,
                    stark_public_key=self.stark_public_key,
                    send_options=self.eth_send_options,
                    collateral_asset_id = collateral_asset_id,
                    starware_perpetuals_contract = starware_perpetuals_contract,
                    token_contracts = token_contracts,
                )
            else:
                raise Exception(
                    'Eth module is not supported since neither web3 ' +
                    'nor web3_provider was provided OR since neither ' +
                    'eth_private_key nor web3_account was provided',
                    )
        return self._eth

    def _verify_string(self, params, key):
        if key in params:
            if not isinstance(params[key], str):
                return False
            else:
                return True
        return True

    def configs(self, **kwargs):
        suffix = URL_SUFFIX + "/v1/symbols"
        configs = self._submit_request(
            method='GET',
            path=self.endpoint + suffix
        )
        self.env_id = configs['data']['global']['registerEnvId']
        self.config = configs['data']
        self.starkeySigner = SignOnboardingAction(self.eth_signer, self.env_id)
        return configs

    def _submit_request(self, method=None, path=None, query=None, headers=None):
        """
        Submits the request to the API.

        Notes
        -------------------
        We use the params argument for the GET method, and data argument for
        the POST method. Dicts passed to the data argument must be
        JSONified prior to submitting request.

        """

        if query is None:
            query = {}

        # Store original recv_window.
        recv_window = self.recv_window

        # Send request and return headers with body. Retry if failed.
        retries_attempted = self.max_retries
        req_params = None

        while True:

            retries_attempted -= 1
            if retries_attempted < 0:
                raise FailedRequestError(
                    request=f'{method} {path}: {req_params}',
                    message='Bad Request. Retries exceeded maximum.',
                    status_code=400,
                    time=dt.utcnow().strftime("%H:%M:%S")
                )

            retries_remaining = f'{retries_attempted} retries remain.'

            # Define parameters and log the request.
            if query is not None:
                req_params = {k: v for k, v in query.items() if
                              v is not None}

            else:
                req_params = {}

            # Log the request.
            if self.log_requests:
                self.logger.debug(f'Request -> {method} {path}: {req_params}')

            # Prepare request; use 'params' for GET and 'data' for POST.
            if method == 'GET':
                r = self.client.prepare_request(
                    requests.Request(method, path, params=req_params,
                                     headers=headers)
                )
            elif method == 'POST':
                r = self.client.prepare_request(
                    requests.Request(method, path,
                                     data=req_params,
                                     headers=headers)
                )

            # Attempt the request.
            try:
                s = self.client.send(r, timeout=self.timeout)

            # If requests fires an error, retry.
            except (
                    requests.exceptions.ReadTimeout,
                    requests.exceptions.SSLError,
                    requests.exceptions.ConnectionError
            ) as e:
                if self.force_retry:
                    self.logger.error(f'{e}. {retries_remaining}')
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise e

            # Convert response to dictionary, or raise if requests error.
            try:
                s_json = s.json()

            # If we have trouble converting, handle the error and retry.
            except JSONDecodeError as e:
                if self.force_retry:
                    self.logger.error(f'{e}. {retries_remaining}')
                    time.sleep(self.retry_delay)
                    continue
                else:
                    raise FailedRequestError(
                        request=f'{method} {path}: {req_params}',
                        message='Conflict. Could not decode JSON.',
                        status_code=409,
                        time=dt.utcnow().strftime("%H:%M:%S")
                    )
            else:
                return s_json
