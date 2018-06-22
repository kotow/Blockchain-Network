import requests, datetime, hashlib, json
from pycoin.ecdsa import generator_secp256k1, sign, verify
from random import SystemRandom
from crypto import get_random_string, get_compressed_public_key_from_private_key, convert_string_to_int, convert_private_key_to_public_key_int, get_compressed_public_key_from_int, get_address_from_compressed_public_key, sign_transaction

seed = None
mnemonic_phrase = None
password = None
salt = None
chain_number = None
enc = None
filename_words = "words.txt"
filename_salt = "salt.txt"
accounts = None

# Type-I deterministic wallet 
class Wallet(object):
    def __init__(self, pswd:str):
        global seed, chain_number, enc, mnemonic_phrase, password, salt, accounts
        if self.__defined__(pswd) == False: return False
        if isinstance(pswd, str) == False: return False
        accounts = {}
        enc = "utf8"
        # set seed, 12 word mnemonic phrase
        mnemonic_phrase = self.__get_twelve_words_as_list__()
        password = pswd
        salt = self.__get_salt__()
        seed = hashlib.sha256(mnemonic_phrase.encode(enc) + salt.encode(enc) + pswd.encode(enc)).hexdigest()
        # print("Your seed is", seed)
        chain_number = 0
        
    def get_passphrase(self):
        global mnemonic_phrase
        payload = {
            "mnemonic_phrase": mnemonic_phrase,
            "msg": "To restore the wallet you must provide the mnemonic_phrase and the password you used to generate the wallet. If you fail to provide both the coins will be lost!"
        }
        #print(transaction_signature)
        return json.dumps(payload, sort_keys = True).encode()
    
    def restore_wallet(self, mnemonic_passphrase:str, pswd:str) -> object:
        if self.__defined__(mnemonic_passphrase) == False: return False
        if isinstance(mnemonic_passphrase, str) == False: return False
        provided_mnemonic_passphrase = mnemonic_passphrase.split(" ")
        if len(provided_mnemonic_passphrase) != 12: return False
        if self.__defined__(pswd) == False: return False
        if isinstance(pswd, str) == False: return False
        payload = {}
        if self.__attempt_wallet_recovery__(mnemonic_passphrase, pswd): 
            payload = {
                "msg": "Your wallet has been restored. Please call create_new_account() as many times as you need to create the lost accounts.",
                "success": "True"
            }
        else:
            payload = {
                "msg": "Unable to restore wallet! Did you provide the 12 word mnemonic passphrase and the password you used to create the wallet?",
                "success": "Falses"
            }
        return json.dumps(payload, sort_keys = True).encode()
    
    # returns only confirmed balance
    def get_account_balance(self, address:str) -> object:
        # has to be run with pickle and verified
        if self.__defined__(address) == False: return False
        if isinstance(address, str) == False: return False
        blocks = self.__get_chain_from_node__()
        balances = {}
        for block in blocks:
            for transaction in block.transactions:
                if address == transaction.sender:
                    if not transaction.sender in balances.keys():
                        balances[transaction.sender] = 0
                    if not transaction.to in balances.keys():
                        balances[transaction.to] = 0
                    balances[transaction.to] += transaction.value
                    balances[transaction.sender] -= transaction.value
                    balances[transaction.sender] -= transaction.fee

        return json.dumps(accounts[balances], sort_keys = True).encode()
    
    def __attempt_wallet_recovery__(self, mnemonic_passphrase:str, pswd:str) -> bool:
        global seed, chain_number, enc, mnemonic_phrase, password, salt, accounts
        if self.__defined__(mnemonic_passphrase) == False: return False
        if isinstance(mnemonic_passphrase, str) == False: return False
        if self.__defined__(pswd) == False: return False
        if isinstance(pswd, str) == False: return False
        accounts = {}
        enc = "utf8"
        password = pswd
        salt = self.__get_salt__()
        seed = hashlib.sha256(mnemonic_passphrase.encode(enc) + salt.encode(enc) + pswd.encode(enc)).hexdigest()
        # print("Your seed is", seed)
        chain_number = 0
        return True
        
    def __get_twelve_words_as_list__(self) -> list:
        mnemonic_list = self.__get_mnemonic_wordlist_as_list__()
        cryptogen = SystemRandom()
        mnemonic_indexes = [cryptogen.randrange(2048) for i in range(12)]
        # print(type(mnemonic_list))
        return ' '.join([mnemonic_list[i] for i in mnemonic_indexes])
    
    def __get_salt__(self):
        with open(filename_salt) as file:
            slt = file.read()
        return slt
        
    def __get_mnemonic_wordlist_as_list__(self) -> list:
        with open(filename_words) as file:
            lines = file.read().splitlines()
        return lines
    
    def __defined__(self, obj: object) -> bool:
        if obj == None or obj == "": return False
        return True
    
    def __get_next_private_key__(self) -> str:
        global seed, chain_number
        chain_number_string = str(chain_number).encode(enc)
        chain_number += 1
        seed_string = seed
        return hashlib.sha256(chain_number_string + seed_string.encode(enc)).hexdigest()
    
    def create_new_account(self) -> object:
        global accouts
        private_key = self.__get_next_private_key__()
        compressed_public_key = get_compressed_public_key_from_private_key(private_key)
        address = get_address_from_compressed_public_key(compressed_public_key)
        if compressed_public_key in accounts: return False#this should never happen
        accounts[compressed_public_key] = {
            "private_key": private_key,
            "compressed_public_key": compressed_public_key,
            "address": address
        }
        account_json = json.dumps(accounts[compressed_public_key], sort_keys = True).encode()
        return account_json
    
    def __get_chain_from_node__(self):
        response = requests.get("http://192.168.214.192/chain")
        response_json = response.json()
        return response_json
    
    def sign_tx(self, recipient_address:str, value:int, fee:int, private_key:str, data:str) -> object:
        return sign_transaction(recipient_address, value, fee, private_key, data)

#debug test output, must be removed once finalized
#wlt = Wallet("softuni")
#my_mnemonic_passphrase = wlt.get_passphrase()
#print(my_mnemonic_passphrase)
#loaded_json = json.loads(my_mnemonic_passphrase.decode())
#generated_passphrase = loaded_json["mnemonic_phrase"]
#act = wlt.create_new_account()
#print("Fresh first key:", act)
#tran = wlt.sign_tx("f893a004fe1b498b3b2970efbb4b0738baa28028", 1000000000, 5000, "2798dc0b52771b16a3ea76b12ea966590d2070106d1d8fda46a3d93bd7f7cfd5", "")
#print(tran)
#print(wlt.restore_wallet(generated_passphrase, "softuni"))
#act = wlt.create_new_account()
#print("Restored first key:", act)