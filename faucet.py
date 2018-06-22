from flask import Flask, jsonify, request, json
import requests
#from wallet import Wallet
from datetime import datetime, timedelta
from crypto import sign_transaction, verify_transaction
from helpers import defined
app = Flask(__name__)

address = "8c3c1f0c6c09dc3030d87fdfc2f70e43e6a10afc"
compressed_public_key = "e504d06f02b085438689dc63d68d40b5b8261268abe76cfa665d06eb5f9e016c0"
private_key = "f74b3e7d8e550b0a3697a585963a3bd0076aa009adefdad753c74bc7e329e205"
history = {}
hours_delta = 1

@app.route('/request/<address>', methods = ['GET'])
def request_coins(address):
    global history
    current_time = datetime.now()
    payload = {
        "msg": "",
        "success": ""
    }
    seed_address = True
    if address in history:
        if history[address] + timedelta(hours = hours_delta) < current_time:
            payload["msg"] = "One coin was sent to the following address: " + address
            payload["success"] = True
        else:
            seed_address = False
            payload["msg"] = "You have already received one coin within the last hour. Please wait."
            payload["success"] = False
            
    else:
        payload["msg"] = "One coin was sent to the following address: " + address
        payload["success"] = True
        history[address] = datetime.now()
    if seed_address:
        transaction = sign_tx(address)
        # print(transaction)
        payload["POST to node"] = post_transaction(transaction)
    
    return json.dumps(payload, sort_keys = True).encode()

def sign_tx(address:str):
    if defined(address) == False: return False
    if isinstance(address, str) == False: return False
    return sign_transaction(address, 1000000000, 5000, private_key, "seeded by faucet")

def post_transaction(transaction:object) -> int:
#    print(transaction)
#    print(transaction.decode())
    response = requests.post("http://192.168.214.192/transactions/send", data = json.dumps(transaction.decode()))
    return response.status_code
    
if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 7777)
        