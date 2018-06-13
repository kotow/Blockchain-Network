from Transaction import Transaction
from Block import Block
import datetime


class Blockchain(object):
    def __init__(self, genesis_block, start_difficulty):
        self.blocks = [genesis_block]
        self.pending_transactions = []
        self.current_difficulty = start_difficulty
        self.mining_jobs = {}
        self.mining_job_index = 0

    @property
    def last_block(self):
        return self.blocks[-1]

    def extend_chain(self, new_block):
        if new_block.index != len(self.blocks):
            return "The submitted block was already mined by someone else"

        prev_block = self.blocks[len(self.blocks) - 1]
        if prev_block.block_hash != new_block.prev_block_hash:
            return "Incorrect prevBlockHash"

        self.blocks.append(new_block)
        self.pending_transactions = []
        # self.removePendingTransactions(new_block.transactions)
        return new_block

    def add_new_transaction(self, tran_data):
        tran = Transaction(
            tran_data['from'],
            tran_data['to'],
            tran_data['value'],
            tran_data['fee'],
            tran_data['dateCreated'],
            tran_data['data'],
            tran_data['senderPubKey'],
            None,
            (tran_data['senderSignature'][0], tran_data['senderSignature'][1]),
            None,
            None
        )

        if not tran.verify_signature():
            return "Invalid signature: " + str(tran_data['senderSignature'][0] + tran_data['senderSignature'][1])

        self.pending_transactions.append(tran)

        return tran

    def get_blocks(self):
        blocks = []
        for block in self.blocks:
            blocks.append(block.__repr__())

        return blocks

    def get_mining_job(self, miner_address)-> Block:
        next_block_index = len(self.blocks)

        miner_reward_transaction = Transaction(
            0,
            miner_address,
            12,
            0,
            datetime.datetime.now().isoformat(),
            "data",
            0,
            None,
            0,
            next_block_index,
            True
        )

        miner_reward_transaction.calculate_data_hash()
        self.pending_transactions.append(miner_reward_transaction)

        prev_block_hash = self.blocks[len(self.blocks)-1].block_hash
        next_block = Block(
            next_block_index,
            self.pending_transactions,
            self.current_difficulty,
            prev_block_hash,
            miner_address
        )
        self.mining_job_index += 1
        self.mining_jobs[self.mining_job_index] = next_block

        return next_block

    def new_block(self, block_data_hash, nonce, date, job_index):
        block = self.mining_jobs[job_index]
        block.nonce = nonce
        block.date_created = date
        print(block.date_created)
        block.calculate_block_hash()
        print(block.block_hash, block_data_hash)
        if block.block_data_hash == block.nonce:
            self.extend_chain(block)
