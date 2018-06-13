import json
import hashlib


class Block(object):
    def __init__(self, index, transactions, difficulty, prev_block_hash):
        self.index = index
        self.transactions = transactions
        self.difficulty = difficulty
        self.prev_block_hash = prev_block_hash
        self.mined_by = None
        self.block_data_hash = None
        self.nonce = None
        self.date_created = None
        self.block_hash = None
        self.calculate_block_data_hash()

    def calculate_block_data_hash(self):
        block_data = {
            'index': self.index,
            'transactions': self.get_transactions(),
            'difficulty': self.difficulty,
            'prevBlockHash': self.prev_block_hash,
            "minedBy": self.mined_by
        }
        block_data_json = json.JSONEncoder(separators=(',', ':')).encode(block_data)
        self.block_data_hash = hashlib.sha256(block_data_json.encode('utf8')).hexdigest()

    def calculate_block_hash(self):
        data = str(self.block_data_hash) + str(self.date_created) + str(self.nonce)
        self.block_hash = hashlib.sha256(data.encode('utf8')).hexdigest()

    def __repr__(self):
        block = {
            'index': self.index,
            'transactions': self.get_transactions(),
            'difficulty': self.difficulty,
            'prev_block_hash': self.prev_block_hash,
            'mined_by': self.mined_by,
            'block_data_hash': self.block_data_hash,
            'nonce': self.nonce,
            'date_created': self.date_created,
            'block_hash': self.block_hash
        }
        return block

    def get_transactions(self):
        transactions = []
        for transaction in self.transactions:
            transactions.append(transaction.__repr__())

        return transactions
