from unittest import TestCase

from bitcoinlib.transactions import Transaction

from bitcoin.tests.data.transactions import batch_airdrop_tx_hex, tx_hex, non_reveal_tx_hex, tx_hex_2
from bitcoin.utils.bitcoin_utils import is_reveal_tx, count_reveal_inputs, has_satflow_op_return


class Test(TestCase):
    def test_is_reveal_tx(self):
        tx = Transaction.parse_hex(tx_hex, strict=False)
        self.assertTrue(is_reveal_tx(tx))

    def test_tx_hex_deserialization(self):
        tx=Transaction.parse_hex(tx_hex_2, strict=False)
        self.assertEqual(tx.txid, "8ca9bdedffbdf7c763dc41ec313f337b92c033530a546cb9cb2be5f486c9573a")

    def test_is_reveal_tx_in_second_input(self):
        tx = Transaction.parse_hex(batch_airdrop_tx_hex, strict=False)
        self.assertTrue(is_reveal_tx(tx))

    def test_is_not_reveal_tx(self):
        tx = Transaction.parse_hex(non_reveal_tx_hex, strict=False)
        self.assertFalse(is_reveal_tx(tx))

    def test_count_reveal_inputs(self):
        tx = Transaction.parse_hex(tx_hex, strict=False)
        self.assertEqual(count_reveal_inputs(tx), 1)

    def test_count_reveal_inputs_not_reveal(self):
        tx = Transaction.parse_hex(non_reveal_tx_hex, strict=False)
        self.assertEqual(count_reveal_inputs(tx), 0)

    def test_count_reveal_in_airdrop_tx(self):
        tx = Transaction.parse_hex(batch_airdrop_tx_hex, strict=False)
        self.assertEqual(count_reveal_inputs(tx), 1420)

    def test_has_satflow_op_return_true(self):
        satflow_tx_hex = "02000000000102121a4369bd06b9123b43f41a072c3832979927e1244dbf27b85b87e4348db6090100000000ffffffffdbe5c4bff3c32c18694c85eafa74c2626c99595156571bc333b58ec9e7e437030000000000ffffffff0398230000000000002200206925778b2282777c97222e5a6b7ce092c521c755f2fd912dd20449a53d741a983cb7590000000000160014dfafb9f5e2e1b8afde774a725aedbb5f127015bb0000000000000000096a07534154464c4f5701419cc0b1bcedab6113b7793c420b0eda8efb706be4a8202d4d9f129ae539880c7027e2abd67a8510771cfa90cffd5a9c76577b1f5388ca869714e629197acdf08d8101400a443de48021e733eb29237abfdd89016a1a171074c399b5a43e5c3349854e3ac1950fe9e27ef7280881f11f67dcc855bb34b2e44e48811d4c0dd4f6e89051ac00000000"
        tx = Transaction.parse_hex(satflow_tx_hex, strict=False)
        self.assertTrue(has_satflow_op_return(tx))

    def test_has_satflow_op_return_false(self):
        tx = Transaction.parse_hex(tx_hex, strict=False)
        self.assertFalse(has_satflow_op_return(tx))
