import json
import secrets
import string 
from hash_utils import hash_val

PROFILE_FILE = "C:\\CodeStuff\\python\\project\\user_profile.txt"


#scan user profile
def load_profile(path: str = PROFILE_FILE) -> dict:
    profile = {}
    with open(path,"r",encoding='utf=8') as f:
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            key,_,value = line.partition("=")
            profile[key.strip()] = value.strip()
    return profile

#word leet
def leetspeak(word: str)->str:
    subs = {"a": "4", "e": "3", "o": "0", "s": "5", "i": "1", "g": "9", "b": "6"}
    for plain,repl in subs.items():
        word = word.replace(plain,repl)
    return word

#user profile password
def generate_user_profile_password(profile: dict) -> str:
    SPECIAL_CHAR = "@"
    base = profile.get("fname","") or profile.get("nickname","")
    leet = leetspeak(base)
    year = profile.get("byear","")
    phonenumber = profile.get("phone_number", "")
    return f"{leet}{SPECIAL_CHAR}{year}"

    
def generate_random_password_using_secrets(length: int = 16)->str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-=+"
    return "".join(secrets.choice(alphabet) for _ in range(length)) 

def main():
    profile = load_profile()
    password_1 = generate_user_profile_password(profile)
    password_2 = generate_random_password_using_secrets()
    password1_hash = hash_val(password_1)
    password2_hash = hash_val(password_2)

    #password 1 info
    print(f"Password 1: {password_1}")
    print(f"Modulo value of password 1: {password1_hash["modulo_hash"]}")
    print(f"Sha256 value of password 1: {password1_hash["sha256_hash"]}")
    
    #password 2 info
    print(f"Password 2: {password_2}")
    print(f"Modulo value of password 2: {password2_hash["modulo_hash"]}")
    print(f"Sha256 value of password 2: {password2_hash["sha256_hash"]}")

    public_info = {
        "target_profile": profile,
        "password_1_hash": password1_hash, 
        "password_2_hash": password2_hash 
    }

    with open("C:\\CodeStuff\\python\\project\\handoff.json", "w", encoding="utf-8") as f:
        json.dump(public_info,f,ensure_ascii=False,indent=2)

if __name__ == "__main__":
    main()