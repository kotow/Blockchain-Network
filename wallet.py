import requests, datetime, hashlib, json, os, binascii


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

    def get_bytes_random_string(self, length:int) -> bytes:
        if self.defined(length) == False: return False
        if isinstance(length, int) == False: return False
        return os.urandom(length)
    
    def convert_bytes_string_to_int(self, hex_str:bytes, length:int) -> int:
        if self.defined(hex_str) == False: return False
        if isinstance(hex_str, bytes) == False: return False
        if self.defined(length) == False: return False
        if isinstance(length, int) == False: return False
        return int(binascii.hexlify(hex_str), 16)
    
    def get_next_private_key(self):
        global seed, chain_number
        private_key = hashlib.sha256(chain_number + seed)
        
    
wlt = Wallet()