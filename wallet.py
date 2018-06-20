import requests, datetime, hashlib, json, os, binascii


seed = None
chain_number = None

# Type-I deterministic wallet 
class Wallet(object):
    def __init__(self):
        global seed, chain_number
        # set seed, 12 word mnemonic phrase
        mnemonic_phrase = "bee tower cell magestic sea road blister sparrow cookie yellow wood flame"
        seed = hashlib.sha1(mnemonic_phrase.encode("utf8")).hexdigest()
        print("Your seed is", seed)
        chain_number = 0
    
wlt = Wallet()