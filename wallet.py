import requests, datetime, hashlib, json, os, binascii
from pycoin.ecdsa import generator_secp256k1, sign, verify
from random import SystemRandom

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
        pass
    
    # returns detailed balance with confirmed and pending transactions
    def get_detailed_account_balance(self, address:str) -> object:
        pass
    
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
        
    def __get_random_string__(self, length) -> str:
        if self.__defined__(length) == False: return False
        if isinstance(length, int) == False: return False
        return binascii.hexlify(os.urandom(length))
    
    def __defined__(self, obj: object) -> bool:
        if obj == None or obj == "": return False
        return True
    
    def __get_next_private_key__(self) -> str:
        global seed, chain_number
        chain_number_string = str(chain_number).encode(enc)
        chain_number += 1
        seed_string = seed
        return hashlib.sha256(chain_number_string + seed_string.encode(enc)).hexdigest()
    
    def __get_compressed_public_key_from_private_key__(self, private_key:int) -> int:
        private_key_int = self.__convert_string_to_int__(private_key, 16)
        public_key_int = self.__convert_private_key_to_public_key_int__(private_key_int)
        compressed_public_key = self.__get_compressed_public_key_from_int__(public_key_int)
        # print("Your compressed public key:", compressed_public_key)
        return compressed_public_key
    
    def __convert_string_to_int__(self, string:str, length:int) -> int:
        if self.__defined__(string) == False: return False
        if isinstance(string, str) == False: return False
        if self.__defined__(length) == False: return False
        if isinstance(length, int) == False: return False
        return int(string, 16)
    
    def __convert_private_key_to_public_key_int__(self, private_key:int) -> int:
        if self.__defined__(private_key) == False: return False
        if isinstance(private_key, int) == False: return False
        if int(private_key) < 0: return False
        return (generator_secp256k1 * private_key).pair()
    
    def __get_compressed_public_key_from_int__(self, public_key:int) -> str:
        if self.__defined__(public_key) == False: return False
        if isinstance(public_key, tuple) == False: return False
        return (hex(public_key[0]))[2:] + str(public_key[1] % 2)
    
    def __get_address_from_compressed_public_key__(self, compressed_public_key:str) -> str:
        if self.__defined__(compressed_public_key) == False: return False
        if isinstance(compressed_public_key, str) == False: return False
        param = compressed_public_key.encode(enc)
        hashed_param = hashlib.new("ripemd160", param).hexdigest()
        # print("Your address:", hashed_param)
        return hashed_param
    
    def create_new_account(self) -> object:
        global accouts
        private_key = self.__get_next_private_key__()
        compressed_public_key = self.__get_compressed_public_key_from_private_key__(private_key)
        address = self.__get_address_from_compressed_public_key__(compressed_public_key)
        if compressed_public_key in accounts: return False#this should never happen
        accounts[compressed_public_key] = {
            "private_key": private_key,
            "compressed_public_key": compressed_public_key,
            "address": address
        }
        account_json = json.dumps(accounts[compressed_public_key], sort_keys = True).encode()
        return account_json
    
    def sign_transaction(self, recipient_address:str, value:int, fee:int, private_key:str, data:str) -> object:
        if self.__defined__(recipient_address) == False: return False
        if isinstance(recipient_address, str) == False: return False
        if self.__defined__(value) == False: return False
        if isinstance(value, int) == False: return False
        if self.__defined__(fee) == False: return False
        if isinstance(fee, int) == False: return False
        if self.__defined__(private_key) == False: return False
        if isinstance(private_key, str) == False: return False
        # dada can be empty, it is optional
        # if self.__defined__(data) == False: return False
        if isinstance(data, str) == False: return False
        private_key_int = self.__convert_string_to_int__(private_key, 16)
        compressed_public_key = self.__get_compressed_public_key_from_private_key__(private_key)
        address = self.__get_address_from_compressed_public_key__(compressed_public_key)
        transaction = {
            "from": address,
            "to": recipient_address,
            "value": value,
            "fee": fee,
            "dateCreated": datetime.datetime.now().isoformat(),
            "data": data,
            "senderPubKey": compressed_public_key
        }
        json_encoder = json.JSONEncoder(separators = (",", ":"))
        transaction_json = json_encoder.encode(transaction)
        transaction_json = transaction_json.encode(enc)
        hashed_transaction_json = hashlib.sha256(transaction_json).digest()
        hashed_transaction_int = int.from_bytes(hashed_transaction_json, byteorder = "big")
        #print(hex(hashed_transaction_int)[2:])
        transaction_signature = sign(
            generator_secp256k1, 
            private_key_int, 
            hashed_transaction_int
        )
        #print(transaction_signature)
        transaction["senderSignature"] = transaction_signature
        return json.dumps(transaction, sort_keys = True).encode()

#debug test output, must be removed once finalized
wlt = Wallet("softuni")
my_mnemonic_passphrase = wlt.get_passphrase()
print(my_mnemonic_passphrase)
loaded_json = json.loads(my_mnemonic_passphrase.decode())
generated_passphrase = loaded_json["mnemonic_phrase"]
act = wlt.create_new_account()
print("Fresh first key:", act)
#tran = wlt.sign_transaction("f893a004fe1b498b3b2970efbb4b0738baa28028", 1000000000, 5000, "2798dc0b52771b16a3ea76b12ea966590d2070106d1d8fda46a3d93bd7f7cfd5", "")
#print(tran)
print(wlt.restore_wallet(generated_passphrase, "softuni"))
act = wlt.create_new_account()
print("Restored first key:", act)