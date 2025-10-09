from bitcoinlib.transactions import Transaction

from bitcoin.address_listener.address_listener import AddressTxData
from bitcoin.models.address_tx_data import AddressTxType
from bitcoin.tx_extractors.abstract_extractor import AbstractTxAddressDataExtractor
from bitcoin.utils.context_aware_logging import ctx_tx_status


class DefaultTxAddressDataExtractor(AbstractTxAddressDataExtractor):
    def extract(self, tx: Transaction) -> [AddressTxData]:
        outputs = tx.outputs
        address_tx_data = []
        inputs = tx.inputs
        is_confirmed = tx.status == "confirmed"
        ctx_tx_status.set(is_confirmed)
        for input in inputs:
            address = input.address
            amount = 0
            address_tx_data.append(AddressTxData(is_confirmed=is_confirmed,
                                                 address=address,
                                                 type=AddressTxType.INPUT,
                                                 _amount=amount,
                                                 tx_id=tx.txid))
        for output in outputs:
            amount = output.value
            address_tx_data.append(AddressTxData(is_confirmed=is_confirmed,
                                                 address=output.address,
                                                 _amount=amount,
                                                 type=AddressTxType.OUTPUT,
                                                 tx_id=tx.txid))
        return address_tx_data
