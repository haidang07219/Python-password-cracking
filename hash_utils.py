import hashlib

def modulo_hash(password: str) ->int:
    return sum(ord(i) for i in password) % 1000

def sha256_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_val(password: str)->dict:
    return{
        "modulo_hash":modulo_hash(password),
        "sha256_hash":sha256_hash(password)
    }
