# benchmark between mempool and bitcoinrcp get transaction info
import os
import time
import requests
from ordipool.ordipool.mempoolio import Mempool

from bitcoin.utils.bitcoin_rpc import BitcoinRPC
from bitcoin.utils.constants import default_host

host = os.environ.get("RPC_HOST", default_host)
base_url = f"http://{host}:3006/api"

mempool = Mempool(base_url)
bitcoinrpc = BitcoinRPC()

if __name__ == '__main__':

    txid = 'a6293e898b056fbea0329d071b1b237e4449ff464cdbc7a9ed8a770b97aafd4c'
    times = 1000
    # start = time.time()
    # for i in range(times):
    #     print(i)
    #     mempool.get_transaction(txid)
    # end = time.time()
    # print(f"mempool took: {end - start}")

    start = time.time()
    for i in range(times):
        tx = bitcoinrpc.get_transaction(txid)
    end = time.time()

