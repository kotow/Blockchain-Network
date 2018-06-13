import requests, datetime, hashlib, json


class Miner(object):
    def __init__(self, host, port, address):
        self.node_url = "http://{}:{}".format(host, port)
        self.get_mining_job_url = '{}/mining/get-mining-job/{}'.format(self.node_url, address)
        self.submit_mined_block_url = "{}/mining/submit-mined-block".format(self.node_url)
        self.current_mining_job = None

    def get_mining_job(self):
        response = requests.get(self.get_mining_job_url)
        self.current_mining_job = response.json()
        # print(self.current_mining_job["blockDataHash"])

    def mine(self):
        date_created = int(datetime.datetime.now().timestamp())
        nonce = 0
        data = str(self.current_mining_job["blockDataHash"] + str(date_created) + str(nonce))
        data_hash = hashlib.sha256(data.encode("utf8")).hexdigest()
        # print(data_hash[0:self.current_mining_job['difficulty']])
        while data_hash[0:self.current_mining_job['difficulty']] != '0'*self.current_mining_job['difficulty']:
            nonce += 1
            data = str(self.current_mining_job["blockDataHash"]) + str(date_created) + str(nonce)
            data_hash = hashlib.sha256(data.encode("utf8")).hexdigest()
            # print(data_hash[0:self.current_mining_job['difficulty']])

        print('=',data)
        response = {
            'nonce': nonce,
            'date': date_created,
            'hash': data_hash,
            'job_index': self.current_mining_job['jobIndex']
        }
        # print(self.current_mining_job["blockDataHash"])
        requests.post(self.submit_mined_block_url, None, json.dumps(response))


miner = Miner('localhost', '5000', "647c740e4777d6324e56ee6aa83d5a5fb62d566e")
miner.get_mining_job()
miner.mine()