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
        print("Your seed is", seed)
        chain_number = 0
    
    def defined(self, obj: object) -> bool:
        if obj == None or obj == "": return False
        return True
    
    def get_next_private_key(self):
        global seed, chain_number
        chain_number_string = str(chain_number).encode("utf8")
        chain_number += 1
        seed_string = seed
        return hashlib.sha256(chain_number_string + seed_string.encode("utf8")).hexdigest()
    
    def get_compressed_public_key_from_private_key(self, private_key:int) -> int:
        private_key_int = self.convert_string_to_int(private_key, 16)
        public_key_int = self.convert_private_key_to_public_key_int(private_key_int)
        compressed_public_key = self.get_compressed_public_key_from_int(public_key_int)
        print("Your compressed public key:", compressed_public_key)
        return compressed_public_key
    
    def convert_string_to_int(self, string:str, length:int) -> int:
        if self.defined(string) == False: return False
        if isinstance(string, str) == False: return False
        if self.defined(length) == False: return False
        if isinstance(length, int) == False: return False
        return int(string, 16)
    
    def convert_private_key_to_public_key_int(self, private_key:int) -> int:
        if self.defined(private_key) == False: return False
        if isinstance(private_key, int) == False: return False
        if int(private_key) < 0: return False
        return (generator_secp256k1 * private_key).pair()
    
    def get_compressed_public_key_from_int(self, public_key:int) -> str:
        if self.defined(public_key) == False: return False
        if isinstance(public_key, tuple) == False: return False
        return (hex(public_key[0]))[2:] + str(public_key[1] % 2)
    
    def get_address_from_compressed_public_key(self, compressed_public_key:str)-> str:
        if self.defined(compressed_public_key) == False: return False
        if isinstance(compressed_public_key, str) == False: return False
        param = public_key.encode("utf8")
        hashed_param = hashlib.new("ripemd160", param).hexdigest()
        print("Your address:", hashed_param)
        return hashed_param
        
    
wlt = Wallet()
private_key = wlt.get_next_private_key()
print("Your private key is", private_key)
public_key = wlt.get_compressed_public_key_from_private_key(private_key)
address = wlt.get_address_from_compressed_public_key(public_key)