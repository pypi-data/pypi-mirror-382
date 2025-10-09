from abc import ABC, abstractmethod

from bitcoinlib.transactions import Transaction

from bitcoin.address_listener.address_listener import AddressTxData


class AbstractTxAddressDataExtractor(ABC):
    @abstractmethod
    def extract(self, tx: Transaction) -> [AddressTxData]:
        pass
