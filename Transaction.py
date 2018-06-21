import hashlib
import json
from pycoin.ecdsa import generator_secp256k1, sign, verify, secp256k1
from pycoin.ecdsa import *


class Transaction(object):
    def __init__(self, sender, to, value, fee, date_created, data, sender_pub_key, transaction_data_hash=None,
                 sender_signature=None, mined_in_block_index=None, transfer_successful=False):
        self.sender = sender
        self.to = to
        self.value = value
        self.fee = fee
        self.date_created = date_created
        self.data = data
        self.sender_pub_key = sender_pub_key
        self.transaction_data_hash = transaction_data_hash
        if self.transaction_data_hash is None:
            self.calculate_data_hash()
        self.sender_signature = sender_signature
        self.mined_in_block_index = mined_in_block_index
        self.transfer_successful = transfer_successful

    def calculate_data_hash(self):
        tran_data = {
            'from': self.sender,
            'to': self.to,
            'value': self.value,
            'fee': self.fee,
            'dateCreated': self.date_created,
            'data': self.data,
            'senderPubKey': self.sender_pub_key
        }

        tran_data_json = json.JSONEncoder(separators=(',', ':')).encode(tran_data)
        self.transaction_data_hash = hashlib.sha256(tran_data_json.encode('utf8')).digest()
        self.transaction_data_hash = int.from_bytes(self.transaction_data_hash, byteorder="big")

    def verify_signature(self):
        is_odd = (int(self.sender_pub_key[-1:]) % 2 == 0)
        pub_pair = public_pair_for_x(generator_secp256k1, int(self.sender_pub_key[:-1], 16), is_odd)
        signature_pair = (int(self.sender_signature[0], 16), int(self.sender_signature[1], 16))

        return verify(generator_secp256k1, pub_pair, self.transaction_data_hash, signature_pair)

    def __repr__(self):
        tran_data = {
            'from': self.sender,
            'to': self.to,
            'value': self.value,
            'fee': self.fee,
            'dateCreated': self.date_created,
            'data': self.data,
            'transactionDataHash': self.transaction_data_hash,
            'senderPubKey': self.sender_pub_key,
            'senderSignature': self.sender_signature
        }
        return tran_data
