from flask import Flask, jsonify, request
from p2p_python.utils import setup_p2p_params
from p2p_python.client import PeerClient
from Blockchain import Blockchain
import json, pickle, binascii, os, requests
from GenesisBlock import *


class Node(object):
    def __init__(self, server_host, server_port, blockchain: Blockchain):
        self.node_id = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        self.host = server_host
        self.port = server_port
        self.self_url = "http://{}:{}".format(self.host, self.port)
        self.peers = {}
        self.chain = blockchain
        self.chain_id = self.chain.blocks[0].block_data_hash

        setup_p2p_params(
            network_ver=1000,
            p2p_port=4001,
            p2p_accept=True,
            sub_dir='user2',
            f_debug=True)
        self.pc = PeerClient(f_local=True)
        self.pc.start(f_stabilize=True)

    def notify_peers_about_new_block(self):
        notification = {
            'blocksCount': self.chain.blocks.length,
            'cumulativeDifficulty': self.chain.calc_cumulative_difficulty(),
            'nodeUrl': node.self_url
        }
        for node_id, node_url in self.peers:
            requests.post("http://" + node_url + "/blocks", jsonify(notification))

    def notify_peers_about_new_transcation(self, transaction):
        for node_id, node_url in self.peers:
            requests.post("http://" + node_url + "/transactions/send", jsonify(transaction))

    def sync_chain(self, peer_chain):
        print(peer_chain)
        #  TODO:  validate all blocks and transactions
        this_chain_difficulty = self.chain.calc_cumulative_difficulty()
        print(peer_chain)
        peer_chain_difficulty = peer_chain['cumulativeDifficulty']
        if peer_chain_difficulty > this_chain_difficulty:
            blocks = requests.get("http://" + peer_chain['peerUrl'] + "/blocks").json()
            self.chain.blocks = []
            for block in blocks:
                if block.block_hash != block['block_hash']:
                    sync_block_transactions = []
                    for transaction in block['transactions']:
                        synced_tnx = Transaction(
                            transaction['from'],
                            transaction['to'],
                            transaction['value'],
                            transaction['fee'],
                            transaction['dateCreated'],
                            transaction['data'],
                            transaction['transactionDataHash'],
                            transaction['senderPubKey'],
                            transaction['senderSignature']
                        )
                        sync_block_transactions.append(synced_tnx)
                    synced_clock = Block(
                        block['index'],
                        sync_block_transactions,
                        block['difficulty'],
                        block['prev_block_hash'],
                        block['mined_by']
                    )
                    synced_clock.block_data_hash = block['block_data_hash']
                    synced_clock.nonce = block['nonce']
                    synced_clock.date_created = block['date_created']
                    synced_clock.block_hash = block['block_hash']
                    self.chain.blocks.append(synced_clock)
            # self.chain.pending_transactions = [] TODO: synchronize pending transactions
            # self.chain.mining_jobs = [] TODO: sync mining jobs?


app = Flask(__name__)
# chain = Blockchain(genesis_block, 3)
# if pickle.load( open( "save.p", "rb" ) ):
chain = pickle.load(open("save.p", "rb"))
node = Node('192.168.214.192', '5000', chain)


@app.route('/info', methods=['GET'])
def info():
    response = {
        'about': 'KYRChain/0.1',
        'nodeId': node.node_id,
        'chainId': node.chain_id,
        'nodeUrl': node.self_url,
        'peers': len(node.peers),
        'currentDifficulty': node.chain.current_difficulty,
        'blocksCount': len(node.chain.blocks),
        'cumulativeDifficulty': node.chain.calc_cumulative_difficulty(),
        'confirmedTransactions': len(node.chain.get_confirmed_transactions()),
        'pendingTransactions': len(node.chain.get_pending_transactions())
    }
    return json.dumps(response)


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
        node.notify_peers_about_new_transcation(values)
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
    node.notify_peers_about_new_block()

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


@app.route('/peers', methods=['GET'])
def get_peers():
    return json.dumps(node.peers)


@app.route('/peers/connect', methods=['POST'])
def connect_peer():
    values = request.json
    peer_url = values['peerUrl']
    # node.pc.p2p.create_connection(host=peer_url, port=5000)
    node_info = requests.get("http://" + peer_url + "/info").json()
    node.sync_chain(node_info)
    node.peers.update({values['nodeId']: values['peerUrl']})

    return 'kurec', 200


@app.route('/peers/notify-new-block', methods=['POST'])
def sync_new_block():
    node.sync_chain(request.json)
    return "Thank you for the notification.", 200

if __name__ == '__main__':
    app.run(host='192.168.214.192', port=5000)
