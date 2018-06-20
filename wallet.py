import requests, datetime, hashlib, json, os, binascii
from pycoin.ecdsa import generator_secp256k1

seed = None
chain_number = None

# Type-I deterministic wallet 
class Wallet(object):
    def __init__(self):
        global seed, chain_number
        # set seed, 12 word mnemonic phrase
        mnemonic_phrase = "bee tower cell magestic sea road blister sparrow cookie yellow wood flame"
        seed = hashlib.sha256(mnemonic_phrase.encode("utf8")).hexdigest()
        # print("Your seed is", seed)
        chain_number = 0
    
    def __defined__(self, obj: object) -> bool:
        if obj == None or obj == "": return False
        return True
    
    def __get_next_private_key__(self) -> str:
        global seed, chain_number
        chain_number_string = str(chain_number).encode("utf8")
        chain_number += 1
        seed_string = seed
        return hashlib.sha256(chain_number_string + seed_string.encode("utf8")).hexdigest()
    
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
        param = compressed_public_key.encode("utf8")
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
    
wlt = Wallet()
act = wlt.create_new_account()
print(act)