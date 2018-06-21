from flask import Flask, jsonify, request, json
#from wallet import Wallet
from datetime import datetime, timedelta
app = Flask(__name__)

address = "ff9996f7924323baa4b54dfcfed49819254286d9"
compressed_public_key = "8836410c68dc0fb116b35799111974ec0c793cb397a5a51af49f7d95c61127ce0"
private_key = "ee544e7cde8316db3d667d721f2ab43c77092066d7243aca14ee9c239c516ad5"
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
    if address in history:
        if history[address] + timedelta(hours = hours_delta) < current_time:
#            print(history[address])
#            print(history[address] + timedelta(hours = hours_delta))
#            print(history[address] + timedelta(hours = hours_delta) > current_time)
            payload["msg"] = "ok, sending you one additional coin"
            payload["success"] = True
        else:
            payload["msg"] = "no, please wait"
            payload["success"] = False
            
    else:
        payload["msg"] = "ok, sending you one initial coin"
        payload["success"] = True
        history[address] = datetime.now()
    return json.dumps(payload, sort_keys = True).encode()
    
if __name__ == '__main__':
    app.run(host = '127.0.0.1', port = 7777)
        