import math
from collections import namedtuple

from apexpro.constants import COLLATERAL_ASSET, ASSET_RESOLUTION
from apexpro.starkex.constants import ONE_HOUR_IN_SECONDS, WITHDRAWAL_TO_ADDRESS_PREFIX, \
    ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
from apexpro.starkex.constants import WITHDRAWAL_FIELD_BIT_LENGTHS
from apexpro.starkex.constants import WITHDRAWAL_PADDING_BITS
from apexpro.starkex.helpers import nonce_from_client_id
from apexpro.starkex.helpers import to_quantums_exact
from apexpro.starkex.signable import Signable
from apexpro.starkex.starkex_resources.proxy import get_hash

StarkwareWithdrawal = namedtuple(
    'StarkwareWithdrawal',
    [
        'quantums_amount',
        'position_id',
        'nonce',
        'expiration_epoch_hours',
        'eth_address',
    ],
)


class SignableWithdrawal(Signable):

    def __init__(
        self,
        network_id,
        position_id,
        human_amount,
        client_id,
        expiration_epoch_seconds,
        eth_address,
        collateral_id,
    ):
        self.collateral_asset_id = int(
            collateral_id,
            16,
        )
        quantums_amount = to_quantums_exact(human_amount, ASSET_RESOLUTION[COLLATERAL_ASSET])
        expiration_epoch_hours = math.ceil(
            float(expiration_epoch_seconds) / ONE_HOUR_IN_SECONDS,
        ) + ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
        message = StarkwareWithdrawal(
            quantums_amount=quantums_amount,
            position_id=int(position_id),
            nonce=nonce_from_client_id(client_id),
            expiration_epoch_hours=expiration_epoch_hours,
            eth_address=eth_address,
        )
        super(SignableWithdrawal, self).__init__(message)

    def to_starkware(self):
        return self._message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware order."""

        # TODO: Check values are in bounds

        packed = WITHDRAWAL_TO_ADDRESS_PREFIX
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['position_id']
        packed += self._message.position_id
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['nonce']
        packed += self._message.nonce
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['quantums_amount']
        packed += self._message.quantums_amount
        packed <<= WITHDRAWAL_FIELD_BIT_LENGTHS['expiration_epoch_hours']
        packed += self._message.expiration_epoch_hours
        packed <<= WITHDRAWAL_PADDING_BITS


        return get_hash(
            get_hash(
            self.collateral_asset_id,
            int(self._message.eth_address, 16)
            ),
            packed,
        )
