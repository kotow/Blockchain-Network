from flask import Flask, jsonify, request
from Blockchain import Blockchain
from Block import Block
from Transaction import Transaction
import json


app = Flask(__name__)
block = Block(0, [], 1, 0, None, 0, 1, 1, 0)
chain = Blockchain(block, 3)


@app.route('/chain', methods=['GET'])
def get_chain():
    response = {
        'chain': chain.get_blocks(),
        'length': len(chain.get_blocks())
    }
    print(response)
    return json.dumps(response)


@app.route('/transactions/send', methods=['POST'])
def new_transaction():
    values = request.json
    print(values)
    tran = chain.add_new_transaction(values)
    if isinstance(tran, Transaction):
        return hex(tran.transaction_data_hash)[2:], 201
    else:
        return "kurec", 400


@app.route('/transactions/sign', methods=['POST'])
def sign_transaction():
    values = request.json
    print(values)
    tran = Transaction(
        values['from'],
        values['to'],
        values['value'],
        values['fee'],
        values['dateCreated'],
        values['data'],
        values['senderPubKey'],
        None,
        (values['senderSignature'][0], values['senderSignature'][1]),
        None,
        None
    )
    if isinstance(tran, Transaction):
        tran.sign("7e4670ae70c98d24f3662c172dc510a085578b9ccc717e6c2f4e547edd960a34")
        return tran.__repr__()
        return "tran.sender_signature", 201
    else:
        return "kurec", 400


@app.route('/mining/get-mining-job/<address>', methods=['GET'])
def get_mining_job(address):
    new_block = chain.get_mining_job(address)

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
    print('data', values)
    new_block_data_hash = chain.new_block(values['hash'], values['nonce'], values['date'], values['job_index'])

    return jsonify(new_block_data_hash)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)