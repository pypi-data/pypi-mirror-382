def get_inscription_transaction_by_id(inscription_id: str) -> str:
    # Note: transaction id can be derived from inscription id by removing the last 2 characters
    return inscription_id[:-2]