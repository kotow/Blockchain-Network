import requests, datetime, hashlib, json, os, binascii
from pycoin.ecdsa import generator_secp256k1, sign, verify
from random import SystemRandom

seed = None
mnemonic_phrase = None
password = None
chain_number = None
enc = None
filename = "words.txt"

# Type-I deterministic wallet 
class Wallet(object):
    def __init__(self, password:str):
        global seed, chain_number, enc, mnemonic_phrase
        if self.__defined__(password) == False: return False
        if isinstance(password, str) == False: return False
        enc = "utf8"
        # set seed, 12 word mnemonic phrase
        mnemonic_phrase = self.__get_twelve_words_as_list__()
        seed = hashlib.sha256(mnemonic_phrase.encode(enc)).hexdigest()
        # print("Your seed is", seed)
        chain_number = 0
        
    def get_passphrase(self):
        payload = {
            "mnemonic_phrase": "",
            "msg": "To restore the wallet you must provide the mnemonic_phrase"
        }
        #print(transaction_signature)
        return json.dumps(payload, sort_keys = True).encode()
        
    def __get_twelve_words_as_list__(self) -> list:
        mnemonic_list = self.__get_mnemonic_wordlist_as_list__()
        cryptogen = SystemRandom()
        mnemonic_indexes = [cryptogen.randrange(2048) for i in range(12)]
        print(type(mnemonic_list))
        return ' '.join([mnemonic_list[i] for i in mnemonic_indexes])
        
    def __get_mnemonic_wordlist_as_list__(self) -> list:
        with open(filename) as file:
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
        private_key = self.__get_next_private_key__()
        compressed_public_key = self.__get_compressed_public_key_from_private_key__(private_key)
        address = self.__get_address_from_compressed_public_key__(compressed_public_key)
        account_json = json.dumps({
            "private_key": private_key,
            "compressed_public_key": compressed_public_key,
            "address": address
        }, sort_keys = True).encode()
        return account_json
    
    def sign_transaction(self, recipient_address:str, value:int, fee:int, private_key:str, data:str) -> object:
        print(1)
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
    
wlt = Wallet()
wlt.__get_twelve_words_as_list__()
#act = wlt.create_new_account()
#print(act)
#tran = wlt.sign_transaction("f893a004fe1b498b3b2970efbb4b0738baa28028", 1000000000, 5000, "2798dc0b52771b16a3ea76b12ea966590d2070106d1d8fda46a3d93bd7f7cfd5", "")
#print(tran)

