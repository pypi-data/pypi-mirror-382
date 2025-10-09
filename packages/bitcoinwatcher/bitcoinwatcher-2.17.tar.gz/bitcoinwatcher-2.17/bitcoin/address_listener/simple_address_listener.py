from bitcoin.address_listener.address_listener import AbstractAddressListener, AddressTxData
from bitcoin.models.address_tx_data import AddressTxType
from bitcoin.tx_listener.zmq_listener import ZMQTXListener


class SimpleAddressListener(AbstractAddressListener):
    def consume(self, subscribed_address, tx_hex, address_tx_data: [AddressTxData]):
        all_output = list(filter(lambda x: x.type == AddressTxType.OUTPUT and x.address == subscribed_address,
                                 address_tx_data))
        total_amount_in_output = sum(map(lambda x: x.amount_in_btc(), all_output))
        all_input = list(filter(lambda x: x.type == AddressTxType.INPUT and x.address == subscribed_address,
                                address_tx_data))
        total_amount_in_input = sum(map(lambda x: x.amount_in_btc(), all_input))
        # scale ito 4 decimal places
        print("Transaction status: ", address_tx_data[0].is_confirmed)
        total_amount_in_output = round(total_amount_in_output, self.DECIMAL_SCALE)
        print(f"Address {subscribed_address} received {total_amount_in_output} BTC in tx {address_tx_data[0].tx_id}")
        print(f"Address {subscribed_address} spent {total_amount_in_input} BTC in tx {address_tx_data[0].tx_id}")

    def __init__(self, addresses_to_listen: {str}):
        self.addresses = address
        super().__init__(addresses_to_listen=addresses_to_listen)


if __name__ == '__main__':
    address = ["bc1qp8j9sx6609h7llqufurxjgrwsqwt020tqzn0gs", "bc1qcq2uv5nk6hec6kvag3wyevp6574qmsm9scjxc2"]
    address_watcher = SimpleAddressListener(address)
    zmq_listener = ZMQTXListener(address_watcher)
    zmq_listener.start()
