import os

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from bitcoin.utils.constants import default_host
from bitcoin.utils.context_aware_logging import ctx_tx, ctx_tx_status, logger, get_logger


class BitcoinRPC:
    rpc_user = os.environ.get("RPC_USER")
    rpc_password = os.environ.get("RPC_PASSWORD")
    rpc_host = os.environ.get("RPC_HOST", default_host)
    rpc_port = os.environ.get("RPC_PORT", 8332)

    def __init__(self):
        self.rpc_string = f"http://{self.rpc_user}:{self.rpc_password}@{self.rpc_host}:{self.rpc_port}"

    def get_new_connection(self):
        return AuthServiceProxy(self.rpc_string)

    def get_transaction(self, txid: str) -> dict:
        return self.get_new_connection().getrawtransaction(txid, True)

    def is_confirmed(self, txid: str) -> bool:
        try:
            self.get_new_connection().getmempoolentry(txid)
            return False
        except JSONRPCException as e:
            return True


if __name__ == '__main__':
    logger = get_logger(__name__)
    rpc = BitcoinRPC()
    txid = '775c85bb56a3fc86bf6b100a1e9ff54b6d4dcc3670fb76f98365d99a32c18e53'
    try:
        ctx_tx.set('686d025f16d9f20353665a9d865e575e3e4d14214f6f7045149a17dd6bf0fac6')
        ctx_tx_status.set('confirmed')
        tx_data = rpc.get_transaction(txid)
        logger.info("Transaction is confirmed")
    except JSONRPCException as e:
        print(f"An error occurred: {e}")
