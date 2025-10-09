from unittest import TestCase

from bitcoin.address_listener.address_listener import AbstractAddressListener, AddressTxData
from bitcoin.models.address_tx_data import AddressTxType


class DummyAddressListener(AbstractAddressListener):

    def consume(self, subscribed_address, tx_hex:str, address_tx_data: [AddressTxData]):
        pass

    def __init__(self, address_to_listen: [str]):
        super().__init__(address_to_listen)


class TestAbstractAddressListener(TestCase):
    def test_filter_address_tx_data_one_address(self):
        address_listener = DummyAddressListener("3P4WqXDbSL")
        input_tx_data = [AddressTxData(tx_id="tx id", address="3P4WqXDbSL", type=AddressTxType.OUTPUT, _amount=1000)]
        address_tx_data = address_listener.filter_address_tx_data(input_tx_data)
        self.assertEqual(len(address_tx_data), len(input_tx_data))

    def test_filter_address_tx_data_multiple_addresses(self):
        address_listener = DummyAddressListener(["3P4WqXDbSL", "3P4WqXDbSL2"])
        input_tx_data = [AddressTxData(tx_id="tx id", address="3P4WqXDbSL", type=AddressTxType.OUTPUT, _amount=1000),
                         AddressTxData(tx_id="tx id", address="3P4WqXDbSL2", type=AddressTxType.OUTPUT, _amount=1000),
                         AddressTxData(tx_id="tx id", address="3P4WqXDbSL3", type=AddressTxType.OUTPUT, _amount=1000)]
        address_tx_data = address_listener.filter_address_tx_data(input_tx_data)
        self.assertEqual(len(address_tx_data), 2)
        self.assertListEqual(sorted(address_tx_data), ["3P4WqXDbSL", "3P4WqXDbSL2"])
        self.assertNotEqual(len(address_tx_data), len(input_tx_data))

    def test_filter_address_tx_data_empty_address_in_input(self):
        address_listener = DummyAddressListener("3P4WqXDbSL")
        input_tx_data = [AddressTxData(tx_id="tx id", address="", type=AddressTxType.OUTPUT, _amount=1000)]
        address_tx_data = address_listener.filter_address_tx_data(input_tx_data)
        self.assertEqual(len(address_tx_data), 0)

    def test_filter_duplicate_output_tx_data(self):
        address_listener = DummyAddressListener("3P4WqXDbSL")
        output_tx_data = [AddressTxData(tx_id="tx id", address="3P4WqXDbSL", type=AddressTxType.OUTPUT, _amount=1000),
                          AddressTxData(tx_id="tx id", address="3P4WqXDbSL", type=AddressTxType.OUTPUT, _amount=1000)]
        address_tx_data = address_listener.filter_address_tx_data(output_tx_data)
        self.assertEqual(len(address_tx_data), 1)
        self.assertEqual(address_tx_data[0], "3P4WqXDbSL")
        self.assertNotEqual(len(address_tx_data), len(output_tx_data))

    def test_filter_where_its_in_input(self):
        address_listener = DummyAddressListener("3P4WqXDbSL")
        input_tx_data = [AddressTxData(tx_id="tx id", address="3P4WqXDbSL", type=AddressTxType.INPUT, _amount=1000)]
        output_tx_data = [AddressTxData(tx_id="tx id", address="3P4WqXDbSLD", type=AddressTxType.OUTPUT, _amount=1000)]
        address_tx_data = address_listener.filter_address_tx_data(input_tx_data + output_tx_data)
        self.assertEqual(len(address_tx_data), 1)
