from abc import ABC, abstractmethod

from bitcoinlib.transactions import Transaction


class AbstractTxListener(ABC):
    @abstractmethod
    def on_tx(self, tx: Transaction):
        pass
