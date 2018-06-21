from Transaction import Transaction
from Block import Block
from GenesisBlock import null_address, null_signature, null_pub_key
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

        for transaction in prev_block.transactions:
            transaction.mined_in_block_index = prev_block.index
        self.blocks.append(new_block)
        self.pending_transactions = []

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
        #  TODO:  check already in chain
        if not tran.verify_signature():
            return "Invalid signature: " + str(tran_data['senderSignature'][0] + tran_data['senderSignature'][1])

        self.pending_transactions.append(tran)

        return tran

    def get_blocks(self):
        blocks = []
        for block in self.blocks:
            blocks.append(block.__repr__())

        return blocks

    def get_mining_job(self, miner_address) -> Block:
        next_block_index = len(self.blocks)

        miner_reward_transaction = Transaction(
            null_address,
            miner_address,
            12,
            0,
            datetime.datetime.now().isoformat(),
            "miner reward tnx",
            null_pub_key,
            None,
            null_signature,
            next_block_index,
            True
        )

        miner_reward_transaction.calculate_data_hash()
        self.pending_transactions.append(miner_reward_transaction)

        prev_block_hash = self.blocks[len(self.blocks) - 1].block_hash
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
        block.calculate_block_hash()
        print(block.block_hash == block_data_hash)
        if block.block_hash == block_data_hash:
            self.extend_chain(block)

    def get_balances(self):
        balances = {}
        for block in self.blocks:
            for transaction in block.transactions:
                if not transaction.sender in balances.keys():
                    balances[transaction.sender] = 0
                if not transaction.to in balances.keys():
                    balances[transaction.to] = 0
                balances[transaction.to] += transaction.value
                balances[transaction.sender] -= transaction.value
                balances[transaction.sender] -= transaction.fee

        return balances

    def get_balance_for_address(self, address):
        address_balance = {
            'safeBalance': 0,
            'confirmedBalance': 0,
            'pendingBalance': 0
        }
        for block in self.blocks:
            for transaction in block.transactions:
                if transaction.sender == address:
                    address_balance['safeBalance'] -= transaction.value
                    address_balance['safeBalance'] -= transaction.fee
                if transaction.to == address:
                    if transaction.mined_in_block_index > (len(self.blocks) - 6):
                        address_balance['safeBalance'] += transaction.value
                    else:
                        address_balance['confirmedBalance'] += transaction.value

        for transaction in self.pending_transactions:
            if transaction.sender == address:
                address_balance['safeBalance'] -= transaction.value
                address_balance['safeBalance'] -= transaction.fee
            if transaction.to == address:
                address_balance['pendingBalance'] += transaction.value

        return address_balance

    def get_pending_transactions(self):
        response = []
        for transaction in self.pending_transactions:
            response.append(transaction.__repr__())
        return response

    def get_confirmed_transactions(self):
        response = []
        for block in self.blocks:
            for transaction in block.transactions:
                response.append(transaction.__repr__())
        return response

    def get_transaction_by_hash(self, tran_hash):
        confirmed_transactions = self.get_confirmed_transactions()
        pending_transactions = self.get_pending_transactions()
        all_transactions = confirmed_transactions + pending_transactions
        print(all_transactions[0]['transactionDataHash'])
        print(tran_hash)
        print(type(all_transactions[0]['transactionDataHash']))
        print(type(tran_hash))
        tran = next((x for x in all_transactions if x['transactionDataHash'] == int(tran_hash)), None)
        if tran:
            return tran
        return None

    def get_transactions_for_address(self, address):
        address_transactions = []
        for block in self.blocks:
            for transaction in block.transactions:
                if transaction.sender == address:
                    address_transactions.append(transaction.__repr__())
                if transaction.to == address:
                    address_transactions.append(transaction.__repr__())
        for transaction in self.pending_transactions:
            if transaction.sender == address:
                address_transactions.append(transaction.__repr__())
            if transaction.to == address:
                address_transactions.append(transaction.__repr__())

        return address_transactions

    def calc_cumulative_difficulty(self):
        difficulty = 0
        for block in self.blocks:
            difficulty += 16 ** block.difficulty
        return difficulty

