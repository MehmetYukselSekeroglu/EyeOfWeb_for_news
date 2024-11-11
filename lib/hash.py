import hashlib
from .env import DEFAULT_CHARSET as __DEFAULT_CHARSET__


def string_to_hash(hash_strings="NULL", hash_algorithm="sha512") -> dict:
    if hash_strings == "NULL" or hash_strings == "":
        return {"success" : "false","message" : "HASH STRING IS NULL!"}
    
    if hash_algorithm == "sha1":
        hasher = hashlib.sha1()
    elif hash_algorithm == "sha256":
        hasher = hashlib.sha256()
    elif hash_algorithm == "sha512":
        hasher = hashlib.sha512()
    elif hash_algorithm == "md5":
        hasher = hashlib.md5()
    elif hash_algorithm == "sha224":
        hasher = hashlib.sha224()
    else:
        return {"success" : "false","message" : "NOT SUPPORTED HASH ALGORITHM!"}
    
    hasher.update(hash_strings.encode("utf-8"))
    hashed_data = str(hasher.hexdigest())
    return {"success" : "true","data" : hashed_data}


def sha1_imageHash(data) -> str:
    return hashlib.sha1(data).hexdigest()


def sha512hasher(text:str) -> str:
    hasher = hashlib.sha512()
    hasher.update(text.encode(__DEFAULT_CHARSET__))
    return str(hasher.hexdigest())


def loginCreditHhasher(text:str) -> str:
    text = sha512hasher(text=text)
    text = sha512hasher(text=text)
    return text


def file_hash_sha1(file_path:str) -> str:
    sha_1_hasher = hashlib.sha1()
    with open(file_path,"rb") as targetFile:
        sha_1_hasher.update(targetFile.read())
    return sha_1_hasher.hexdigest()


def all_hash(file_path:str) -> dict:     
    with open(file_path, "rb") as targetFile:
        raw_data = targetFile.read()
        
    return {
        "sha1": hashlib.sha1(raw_data).hexdigest(),
        "sha256":hashlib.sha256(raw_data).hexdigest(),
        "md5":hashlib.md5(raw_data).hexdigest()
    }
        
        
        
            
    
    
    
    
    
