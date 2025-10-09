import math
import os
from multiprocessing.pool import ThreadPool

from bitcoinlib.transactions import Transaction

from bitcoin.address_listener.address_listener import AddressTxData
from bitcoin.models.address_tx_data import AddressTxType, BitmapDetails
from bitcoin.utils.bitcoin_rpc import BitcoinRPC
from bitcoin.tx_extractors.abstract_extractor import AbstractTxAddressDataExtractor
from bitcoin.utils.context_aware_logging import logger, ctx_tx_status


class BitcoinRPCAddressDataExtractor(AbstractTxAddressDataExtractor):
    bitcoinrpc: BitcoinRPC
    thread_pool = ThreadPool(processes=os.environ.get("THREAD_POOL_SIZE", 5))

    def __init__(self):
        self.bitcoinrpc = BitcoinRPC()

    def fetch_all_inputs(self, inputs):
        unique_txids = list(set([input.prev_txid.hex() for input in inputs]))
        rpc_calls = [["getrawtransaction", tx_id, True] for tx_id in unique_txids]
        data = self.bitcoinrpc.get_new_connection().batch_(rpc_calls)
        tx_id_to_data = {tx_id: current_tx for tx_id, current_tx in zip(unique_txids, data)}
        list_of_vouts = []
        for input in inputs:
            tx_id = input.prev_txid.hex()
            current_tx = tx_id_to_data[tx_id]
            vout = current_tx["vout"][input.output_n_int]
            list_of_vouts.append(vout)
        return list_of_vouts

    def get_address_tx_from_inputdata(self, tx_id, tx_status, input_data):
        address = input_data["scriptPubKey"]["address"]
        amount = int(input_data.get("value", 0).real * 100000000)
        return AddressTxData(tx_id=tx_id, is_confirmed=tx_status, address=address, _amount=amount,
                             type=AddressTxType.INPUT)

    @staticmethod
    def check_bitmap_patterns(tx: Transaction) -> str:
        """Check if transaction contains bitmap inscription patterns"""
        patterns = [
            "036f7264",         # ord
            "746578742f706c61696e",  # text/plain
            "2e6269746d6170"    # .bitmap
        ]

        raw_hex = tx.raw_hex()
        if all(p in raw_hex for p in patterns):
            bitmap_pattern = "e6269746d6170"
            index = raw_hex.find(bitmap_pattern)
            if index != -1 and index >= 13:
                before_hex = raw_hex[index-13:index]
                try:
                    decoded_text = bytes.fromhex(before_hex + bitmap_pattern).decode("utf-8", errors="ignore")
                    return decoded_text
                except:
                    return "[could not decode bitmap]"
        return None

    @staticmethod
    def calculate_transaction_fee(tx: Transaction, inputs_data: list) -> int:
        """Calculate transaction fee manually using fetched input data and outputs"""
        # Calculate total input value from fetched RPC data
        total_input_value = 0
        for input_data in inputs_data:
            value = input_data.get("value", 0)
            total_input_value += int(value * 100000000)  # Convert to satoshis

        # Calculate total output value from transaction outputs
        total_output_value = sum(output.value for output in tx.outputs)

        # Fee = inputs - outputs
        calculated_fee = total_input_value - total_output_value

        logger.info("Fee calculation - Input: %d sats, Output: %d sats, Fee: %d sats",
                   total_input_value, total_output_value, calculated_fee)

        return calculated_fee

    def extract(self, tx: Transaction) -> [AddressTxData]:
        logger.info("Extracting rpc tx data")
        outputs = tx.outputs
        tx_id = tx.txid
        address_tx_data = []
        inputs = tx.inputs
        # bulk get all the inputs from BitcoinRPC using thread pool
        inputs_data = self.fetch_all_inputs(inputs)
        is_confirmed = self.bitcoinrpc.is_confirmed(tx_id)
        ctx_tx_status.set(is_confirmed)
        logger.info("Transaction is_confirmed: %s", is_confirmed)

        # Calculate fee manually using fetched input data
        calculated_fee = self.calculate_transaction_fee(tx, inputs_data)
        virtual_size = tx.vsize
        fee_per_vbyte = math.ceil(calculated_fee / virtual_size * 100) / 100 if virtual_size > 0 else 0
        logger.info("Transaction vsize: %d, Fee per vbyte: %.2f sats/vbyte", virtual_size, fee_per_vbyte)
        # Check for bitmap inscription
        bitmap_inscription = self.check_bitmap_patterns(tx)
        if bitmap_inscription:
            logger.info("Bitmap inscription found: %s", bitmap_inscription)
        for input in inputs:
            address = input.address
            amount = 0
            if len(inputs_data) > 0:
                input_data = inputs_data.pop(0)
                input_tx_data = self.get_address_tx_from_inputdata(tx_id, is_confirmed, input_data)
                address_tx_data.append(input_tx_data)
            else:
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
        if bitmap_inscription is not None:
            bitmap_details = BitmapDetails()
            bitmap_details.fee = calculated_fee
            bitmap_details.fee_per_vbyte = fee_per_vbyte
            bitmap_details.bitmap_number = int(bitmap_inscription.split(".bitmap")[0])
            address_tx_data[0].bitmap_details = bitmap_details
        return address_tx_data
