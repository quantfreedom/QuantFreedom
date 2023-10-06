import base64
import hashlib

import websocket
import threading
import time
import json
import hmac
import logging
import re
import copy
from . import HTTP, APEX_HTTP_MAIN
from .constants import APEX_WS_MAIN
from .helpers.request_helpers import generate_now


logger = logging.getLogger(__name__)

PRIVATE_REQUEST_PATH = '/ws/accounts'
PRIVATE_WSS = "/realtime_private?v=2"
PUBLIC_WSS = "/realtime_public?v=2"

class _WebSocketManager:
    def __init__(self, callback_function, endpoint="", api_key_credentials=None,
                 ping_interval=15, ping_timeout=None,
                 restart_on_error=True, trace_logging=False):

        if endpoint.endswith('/'):
            self.endpoint = endpoint[:-1]
        # Set the endpoint.
        if endpoint is None:
            self.endpoint = APEX_WS_MAIN
        else:
            self.endpoint = endpoint

        self.api_key_credentials = api_key_credentials

        self.callback = callback_function

        # Setup the callback directory following the format:
        #   {
        #       "topic_name": function
        #   }
        self.callback_directory = {}

        # Set ping settings.
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

        # Other optional data handling settings.
        self.handle_error = restart_on_error
        self.timer = None
        self.r_timer = None

        # Enable websocket-client's trace logging for extra debug information
        # on the websocket connection, including the raw sent & recv messages
        websocket.enableTrace(trace_logging)

        # Set initial state, initialize dictionary and connect.
        self._reset()

    def sign(
            self,
            request_path,
            method,
            iso_timestamp,
    ):

        message_string = (
                iso_timestamp +
                method +
                request_path
        )
        hashed = hmac.new(
            base64.standard_b64encode(
                (self.api_key_credentials['secret']).encode(encoding='utf-8'),
            ),
            msg=message_string.encode(encoding='utf-8'),
            digestmod=hashlib.sha256,
        )
        return base64.standard_b64encode(hashed.digest()).decode()

    def runTimer(self):
        time_stamp = generate_now()
        ping = json.dumps({
            "op": "ping",
            "args": [str(time_stamp)]
        })
        self.ws.send(ping)
        #print("send ping:" + ping)

    def _on_open(self):
        """
        Log WS open.
        """

        logger.debug(f"WebSocket  opened.")

    def _on_message(self, message):
        """
        Parse incoming messages.
        """
        self.callback(json.loads(message))

    def _connect(self, url):
        """
        Open websocket in a thread.
        """
        self.private_websocket = True if url.__contains__("private") else False

        time_stamp = generate_now()
        self.ws = websocket.WebSocketApp(
            url=url + '&timestamp=' + str(time_stamp),
            on_message=lambda ws, msg: self._on_message(msg),
            on_close=self._on_close(),
            on_open=self._on_open(),
            on_error=lambda ws, err: self._on_error(err)
        )

        # Setup the thread running WebSocketApp.
        self.wst = threading.Thread(target=lambda: self.ws.run_forever(
            ping_interval=self.ping_interval,
            ping_timeout=self.ping_timeout
        ))

        # Configure as daemon; start.
        self.wst.daemon = True
        self.wst.start()

        # Attempt to connect for X seconds.
        retries = 10
        while retries > 0 and (not self.ws.sock or not self.ws.sock.connected):
            retries -= 1
            time.sleep(1)

        # If connection was not successful, raise error.
        if retries <= 0:
            self.exit()
            raise websocket.WebSocketTimeoutException("Connection failed.")

        # If given an api_key, authenticate.
        if self.api_key_credentials:
            self._auth(time_stamp)

    def _auth(self, time_stamp):
        """
        Authorize websocket connection.
        """

        signature = self.sign(
            request_path=PRIVATE_REQUEST_PATH,
            method='GET',
            iso_timestamp=str(time_stamp),
        )

        req = {
            'type': 'login',
            'topics': ['ws_notify_v1', 'ws_accounts_v1'],
            'httpMethod': 'GET',
            'requestPath': PRIVATE_REQUEST_PATH,
            'apiKey': self.api_key_credentials['key'],
            'passphrase': self.api_key_credentials['passphrase'],
            'timestamp': time_stamp,
            'signature': signature,
        }
        sendStr = \
            {
                "op": "login",
                "args": [json.dumps(req)]
            }

        # Authenticate with API.
        self.ws.send(
            json.dumps(sendStr)
        )

    def _on_error(self, error):
        """
        Exit on errors and raise exception, or attempt reconnect.
        """

        if not self.exited:
            logger.error(f"WebSocket  encountered error: {error}.")
            self.exit()

        # Reconnect.
        if self.handle_error:
            self._reset()
            if self.private_websocket:
                self._connect(self.endpoint + PRIVATE_WSS)
            else:
                self._connect(self.endpoint + PUBLIC_WSS)

    def _on_close(self):
        """
        Log WS close.
        """
        logger.debug(f"WebSocket closed.")

    def _reset(self):
        """
        Set state booleans and initialize dictionary.
        """
        self.exited = False
        self.auth = False
        self.data = {}

    def exit(self):
        """
        Closes the websocket connection.
        """

        self.ws.close()
        while self.ws.sock:
            continue
        self.exited = True


class _ApexWebSocketManager(_WebSocketManager):
    def __init__(self, **kwargs):
        super().__init__(self._handle_incoming_message, **kwargs)

    def subscribe(self, sendStr, topic, callback):
        """
        Formats and sends the subscription message, given a topic. Saves the
        provided callback function, to be called by incoming messages.
        """

        if self.private_websocket:
            # Spot private topics don't need a subscription message
            self._set_callback(topic, callback)
            return

        self.ws.send(sendStr)
        self._set_callback(topic, callback)

    def _handle_incoming_message(self, message):
        #print(message)
        def is_ping_message():
            if type(message) == dict and message.get("op") == "ping":
                return True
            else:
                return False

        def is_auth_message():
            if type(message) == dict and \
                    message.get("request") is not None and message.get("request").get("op") is not None and message.get("request").get("op") == "login":
                return True
            else:
                return False

        def is_subscription_message():
            if type(message) == dict and \
                    message.get("request") is not None and message.get("request").get("op") is not None and message.get("request").get("op") == "subscribe":
                return True
            else:
                return False

        if is_ping_message():
            time_stamp = generate_now()
            pong = json.dumps({
                "op": "pong",
                "args": [str(time_stamp)]
            })
            self.ws.send(pong)
            #print("send pong:" + pong)
            return

        # Check auth
        if is_auth_message():
            # If we get successful spot auth, notify user
            if message.get("success") is not None and message.get("success") == "true":
                logger.debug(f"Authorization successful.")
                self.auth = True

        # Check subscription
        elif is_subscription_message():
            # If we get successful spot subscription, notify user
            if message.get("success") is not None and message.get("success") == "true":
                logger.debug(f"Subscription successful.")


        else:  # Standard topic push
                if message.get('topic') is not None and self.callback_directory.get(message.get('topic')) is not None:
                    callback_function = self.callback_directory[message['topic'] ]
                    callback_function(message)

    def _set_callback(self, topic, callback_function):
        self.callback_directory[topic] = callback_function

    def _get_callback(self, topic):
        return self.callback_directory[topic]

    def _pop_callback(self, topic):
        self.callback_directory.pop(topic)

    def _check_callback_directory(self, topics):
        for topic in topics:
            if topic in self.callback_directory:
                raise Exception(f"You have already subscribed to this topic: "
                                f"{topic}")


def _identify_ws_method(input_wss_url, wss_dictionary):
    """
    This method matches the input_wss_url with a particular WSS method. This
    helps ensure that, when subscribing to a custom topic, the topic
    subscription message is sent down the correct WSS connection.
    """
    path = re.compile("(wss://)?([^/\s]+)(.*)")
    input_wss_url_path = path.match(input_wss_url).group(3)
    for wss_url, function_call in wss_dictionary.items():
        wss_url_path = path.match(wss_url).group(3)
        if input_wss_url_path == wss_url_path:
            return function_call


def _find_index(source, target, key):
    """
    Find the index in source list of the targeted ID.
    """
    return next(i for i, j in enumerate(source) if j[key] == target[key])


def _make_public_kwargs(private_kwargs):
    public_kwargs = copy.deepcopy(private_kwargs)
    public_kwargs.pop("api_key_credentials", "")
    return public_kwargs
