from flask import Flask, jsonify, request
from Blockchain import Blockchain
from Block import Block
from Transaction import Transaction
import json, pickle, binascii, os, p2p_python
from GenesisBlock import *


class Node(object):
    def __init__(self, server_host, server_port, blockchain):
        self.nodeId = binascii.b2a_hex(os.urandom(15))
        self.host = server_host
        self.port = server_port
        self.self_url = "http://{}:{}".format(self.host, self.port)
        self.peers = {}
        self.chain = blockchain
        self.chainId = self.chain.blocks[0].blockHash


app = Flask(__name__)
# chain = Blockchain(genesis_block, 3)
# if pickle.load( open( "save.p", "rb" ) ):
chain = pickle.load(open("save.p", "rb"))


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': chain.get_blocks(),
        'length': len(chain.get_blocks())
    }

    return json.dumps(response)


@app.route('/blocks', methods=['GET'])
def get_transactions():
    return json.dumps(chain.get_blocks())


@app.route('/blocks/<block_id>', methods=['GET'])
def get_block(block_id):
    current_block = None
    for next_block in chain.blocks:
        if int(next_block.index) == int(block_id):
            current_block = next_block
            break

    return json.dumps(current_block.__repr__())


@app.route('/transactions/pending', methods=['GET'])
def get_pending_transactions():
    return json.dumps(chain.get_pending_transactions())


@app.route('/transactions/confirmed', methods=['GET'])
def get_confirmed_transactions():
    return json.dumps(chain.get_confirmed_transactions())


@app.route('/transactions/<transaction_hash>', methods=['GET'])
def get_confirmed_transaction_by_hash(transaction_hash):
    return json.dumps(chain.get_transaction_by_hash(transaction_hash))


@app.route('/transactions/send', methods=['POST'])
def new_transaction():
    pickle.dump(chain, open("save.p", "wb"))
    values = request.json
    available_balance = chain.get_balance_for_address(values['from'])['safeBalance']
    if int(available_balance) < (int(values['value']) + int(values['fee'])):
        return 'kurec', 400
    tran = chain.add_new_transaction(values)
    if isinstance(tran, Transaction):
        return hex(tran.transaction_data_hash)[2:], 201
    else:
        return "kurec2", 400


@app.route('/mining/get-mining-job/<address>', methods=['GET'])
def get_mining_job(address):
    new_block = chain.get_mining_job(address)
    pickle.dump(chain, open("save.p", "wb"))
    response_object = {
        "index": new_block.index,
        "transactionsIncluded": len(new_block.get_transactions()),
        "difficulty": new_block.difficulty,
        "expectedReward": 12,
        "rewardAddress": address,
        "blockDataHash": new_block.block_data_hash,
        "jobIndex": chain.mining_job_index
    }

    return json.dumps(response_object)


@app.route('/mining/submit-mined-block', methods=['POST'])
def mine():
    values = json.loads(request.json)
    pickle.dump(chain, open("save.p", "wb"))
    print('data', values)
    new_block_data_hash = chain.new_block(values['hash'], values['nonce'], values['date'], values['job_index'])

    return jsonify(new_block_data_hash)


@app.route('/balances', methods=['GET'])
def balances():
    result = chain.get_balances()

    return json.dumps(result)


@app.route('/address/<address>/balance', methods=['GET'])
def balance_for_address(address):
    result = chain.get_balance_for_address(address)

    return json.dumps(result)


@app.route('/address/<address>/transactions', methods=['GET'])
def transactions_for_address(address):
    result = chain.get_transactions_for_address(address)

    return json.dumps(result)


@app.route('/peers/connect', methods=['POST'])
def connect_peer():
    return ''


if __name__ == '__main__':
    app.run(host='192.168.214.192', port=5000)
