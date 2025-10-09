from bitcoinlib.transactions import Transaction, Input
from ordipool.utils.utils import convert_to_hex


def count_inscriptions(vin: Input) -> int:
    ord_hex = convert_to_hex('ord')
    # count occurences of ord in the witness script
    return sum([witness.hex().count(ord_hex) for witness in vin.witnesses])


def count_reveal_inputs(tx: Transaction) -> int:
    return sum([count_inscriptions(vin) for vin in tx.inputs])


def is_reveal_tx(tx: Transaction) -> bool:
    count_of_inscriptions = count_reveal_inputs(tx)
    return count_of_inscriptions > 0
    # check if any of the witness contains ord, convert witness to hex


def has_satflow_op_return(tx: Transaction) -> bool:
    for output in tx.outputs:
        if output.script_type == 'nulldata' and output.lock_script:
            try:
                script_data = output.lock_script.hex()
                if b'SATFLOW'.hex() in script_data:
                    return True
            except:
                pass
    return False
