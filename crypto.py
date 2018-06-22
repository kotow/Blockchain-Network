import datetime, hashlib, json, os, binascii
from pycoin.ecdsa import generator_secp256k1, sign, verify
from random import SystemRandom
from helpers import defined

enc = "utf8"

def get_random_string(length:int) -> str:
    if defined(length) == False: return False
    if isinstance(length, int) == False: return False
    return binascii.hexlify(os.urandom(length))

def get_compressed_public_key_from_private_key(private_key:int) -> int:
    private_key_int = convert_string_to_int(private_key, 16)
    public_key_int = convert_private_key_to_public_key_int(private_key_int)
    compressed_public_key = get_compressed_public_key_from_int(public_key_int)
    # print("Your compressed public key:", compressed_public_key)
    return compressed_public_key

def convert_string_to_int(string:str, length:int) -> int:
    if defined(string) == False: return False
    if isinstance(string, str) == False: return False
    if defined(length) == False: return False
    if isinstance(length, int) == False: return False
    return int(string, 16)

def convert_private_key_to_public_key_int(private_key:int) -> int:
    if defined(private_key) == False: return False
    if isinstance(private_key, int) == False: return False
    if int(private_key) < 0: return False
    return (generator_secp256k1 * private_key).pair()

def get_compressed_public_key_from_int(public_key:int) -> str:
    if defined(public_key) == False: return False
    if isinstance(public_key, tuple) == False: return False
    return (hex(public_key[0]))[2:] + str(public_key[1] % 2)

def get_address_from_compressed_public_key(compressed_public_key:str) -> str:
    if defined(compressed_public_key) == False: return False
    if isinstance(compressed_public_key, str) == False: return False
    param = compressed_public_key.encode(enc)
    hashed_param = hashlib.new("ripemd160", param).hexdigest()
    # print("Your address:", hashed_param)
    return hashed_param

def sign_transaction(recipient_address:str, value:int, fee:int, private_key:str, data:str) -> object:
    if defined(recipient_address) == False: return False
    if isinstance(recipient_address, str) == False: return False
    if defined(value) == False: return False
    if isinstance(value, int) == False: return False
    if defined(fee) == False: return False
    if isinstance(fee, int) == False: return False
    if defined(private_key) == False: return False
    if isinstance(private_key, str) == False: return False
    # data can be empty, it is optional
    # if defined(data) == False: return False
    if isinstance(data, str) == False: return False
    private_key_int = convert_string_to_int(private_key, 16)
    compressed_public_key = get_compressed_public_key_from_private_key(private_key)
    address = get_address_from_compressed_public_key(compressed_public_key)
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