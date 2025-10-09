import os
from abc import ABC, abstractmethod

from bitcoinlib.transactions import Transaction
from ordipool.ordipool.mempoolio import Mempool

from bitcoin.models.address_tx_data import AddressTxData
from bitcoin.tx_extractors.bitcoin_rpc import BitcoinRPCAddressDataExtractor
from bitcoin.tx_extractors.default import DefaultTxAddressDataExtractor
from bitcoin.tx_listener.abstract_tx_listener import AbstractTxListener
from bitcoin.utils.constants import default_host
from bitcoin.utils.context_aware_logging import logger
from bitcoin.utils.bitcoin_utils import has_satflow_op_return


class AbstractAddressListener(AbstractTxListener, ABC):
    DECIMAL_SCALE = 5
    host = os.environ.get("RPC_HOST", default_host)
    base_url = f"http://{host}:3006/api"
    mempool = Mempool(base_url=base_url)
    default_tx_extractor = DefaultTxAddressDataExtractor()
    rpc_tx_extractor = BitcoinRPCAddressDataExtractor()

    def __init__(self, addresses_to_listen: {str}):
        self.addresses_to_listen = addresses_to_listen

    @abstractmethod
    def consume(self, tx_hex, subscribed_address, address_tx_data: [AddressTxData]):
        pass

    def filter_address_tx_data(self, address_tx_data: [AddressTxData]) -> [str]:
        filtered_address_tx_data = list(filter(lambda x: x.address in self.addresses_to_listen and x.address != "",
                                               address_tx_data))
        # get all address
        return list(set((map(lambda x: x.address, filtered_address_tx_data))))

    def on_tx(self, tx: Transaction):
        # get all address in the inputs and outputs along with the amount
        if tx.coinbase:
            return
        logger.debug(f"Extracting default tx data")
        address_tx_data = self.default_tx_extractor.extract(tx)
        # get the address tx data from mempool for full details if any address matches
        try:
            logger.info(f"Extracting rpc tx data")
            address_tx_data = self.rpc_tx_extractor.extract(tx)
        except Exception as e:
            logger.error(f"Error in getting rpc tx data, taking defaults", exc_info=True)
            address_tx_data = address_tx_data
        # filter the address we are interested in
        addresses_for_events = self.filter_address_tx_data(address_tx_data)

        if len(addresses_for_events) == 0:
            if has_satflow_op_return(tx):
                logger.info(f"Transaction {tx.txid} has satflow op_return but no addresses to listen to.")
                self.consume(tx_hex=tx.raw_hex(), subscribed_address="SATFLOW", address_tx_data=address_tx_data)
            else:
                logger.debug(f"No addresses to listen to for transaction {tx.txid}.")
        bitmap_tx = next((addr_data for addr_data in address_tx_data if addr_data.bitmap_details is not None), None)
        if bitmap_tx:
            logger.info(f"Transaction {tx.txid} contains bitmap inscription: {bitmap_tx.bitmap_details}")
            self.consume(tx_hex=tx.raw_hex(), subscribed_address="BITMAP",address_tx_data=address_tx_data)
        for address in addresses_for_events:
            self.consume(tx_hex=tx.raw_hex(), subscribed_address=address, address_tx_data=address_tx_data)
