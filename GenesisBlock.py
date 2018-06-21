from Transaction import Transaction
from Block import Block


faucet_address = 'ff9996f7924323baa4b54dfcfed49819254286d9'
null_address = "0000000000000000000000000000000000000000"
null_pub_key = "00000000000000000000000000000000000000000000000000000000000000000"
null_signature = [
    "0000000000000000000000000000000000000000000000000000000000000000",
    "0000000000000000000000000000000000000000000000000000000000000000"
]

genesis_date = "2018-01-01T00:00:00.000Z"
genesis_faucet_transaction = Transaction(
    null_address,
    faucet_address,
    1000000000000,
    0,
    genesis_date,
    "genesis tx",
    null_pub_key,
    None,
    null_signature,
    0,
    True
)

genesis_block = Block(
    0,
    [genesis_faucet_transaction],
    0,
    None,
    null_address
)
