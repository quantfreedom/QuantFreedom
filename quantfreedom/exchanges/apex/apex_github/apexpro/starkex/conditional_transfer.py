from collections import namedtuple
import math

from apexpro.constants import COLLATERAL_ASSET, ASSET_RESOLUTION
from apexpro.starkex.constants import CONDITIONAL_TRANSFER_FEE_ASSET_ID, ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
from apexpro.starkex.constants import CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS
from apexpro.starkex.constants import CONDITIONAL_TRANSFER_MAX_AMOUNT_FEE
from apexpro.starkex.constants import CONDITIONAL_TRANSFER_PADDING_BITS
from apexpro.starkex.constants import CONDITIONAL_TRANSFER_PREFIX
from apexpro.starkex.constants import ONE_HOUR_IN_SECONDS
from apexpro.starkex.helpers import fact_to_condition
from apexpro.starkex.helpers import nonce_from_client_id
from apexpro.starkex.helpers import to_quantums_exact
from apexpro.starkex.signable import Signable
from apexpro.starkex.starkex_resources.proxy import get_hash

StarkwareConditionalTransfer = namedtuple(
    'StarkwareConditionalTransfer',
    [
        'sender_position_id',
        'receiver_position_id',
        'receiver_public_key',
        'condition',
        'quantums_amount',
        'nonce',
        'expiration_epoch_hours',
    ],
)


class SignableConditionalTransfer(Signable):

    def __init__(
        self,
        network_id,
        sender_position_id,
        receiver_position_id,
        receiver_public_key,
        fact_registry_address,
        fact,
        human_amount,
        client_id,
        expiration_epoch_seconds,
        collateral_id
    ):
        self.collateral_asset_id = int(
            collateral_id,
            16,
        )
        receiver_public_key = (
            receiver_public_key
            if isinstance(receiver_public_key, int)
            else int(receiver_public_key, 16)
        )
        quantums_amount = to_quantums_exact(human_amount, ASSET_RESOLUTION[COLLATERAL_ASSET])
        expiration_epoch_hours = math.ceil(
            float(expiration_epoch_seconds) / ONE_HOUR_IN_SECONDS,
        ) + ORDER_SIGNATURE_EXPIRATION_BUFFER_HOURS
        message = StarkwareConditionalTransfer(
            sender_position_id=int(sender_position_id),
            receiver_position_id=int(receiver_position_id),
            receiver_public_key=receiver_public_key,
            condition=fact_to_condition(fact_registry_address, fact),
            quantums_amount=quantums_amount,
            nonce=nonce_from_client_id(client_id),
            expiration_epoch_hours=expiration_epoch_hours,
        )
        super(SignableConditionalTransfer, self).__init__(
            message,
        )

    def to_starkware(self):
        return self._message

    def _calculate_hash(self):
        """Calculate the hash of the Starkware order."""

        # TODO: Check values are in bounds

        # The transfer asset and fee asset are always the collateral asset.
        # Fees are not supported for conditional transfers.
        asset_ids = get_hash(
            self.collateral_asset_id,
            CONDITIONAL_TRANSFER_FEE_ASSET_ID,
        )

        part_1 = get_hash(
            get_hash(
                asset_ids,
                self._message.receiver_public_key,
            ),
            self._message.condition,
        )

        part_2 = self._message.sender_position_id
        part_2 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS['position_id']
        part_2 += self._message.receiver_position_id
        part_2 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS['position_id']
        part_2 += self._message.sender_position_id
        part_2 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS['nonce']
        part_2 += self._message.nonce

        part_3 = CONDITIONAL_TRANSFER_PREFIX
        part_3 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS['quantums_amount']
        part_3 += self._message.quantums_amount
        part_3 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS['quantums_amount']
        part_3 += CONDITIONAL_TRANSFER_MAX_AMOUNT_FEE
        part_3 <<= CONDITIONAL_TRANSFER_FIELD_BIT_LENGTHS[
            'expiration_epoch_hours'
        ]
        part_3 += self._message.expiration_epoch_hours
        part_3 <<= CONDITIONAL_TRANSFER_PADDING_BITS

        return get_hash(
            get_hash(
                part_1,
                part_2,
            ),
            part_3,
        )
