import itertools
import json
import time
from hash_utils import modulo_hash,sha256_hash

MAX_ATTEMPTS = 2000000
PROGRESS_EVERY = 200

COMMON_SPECIALS = ["@", "!", "#", "$", "_", "-", ""]

#permutation engine
def leet_variants(word: str)-> set:
    subs = {"a": "4", "e": "3", "o": "0", "s": "5", "i": "1", "g": "9", "b": "8"}
    base_variants = {word, word.lower(),word.upper(),word.capitalize()}

    result = set(base_variants)

    for base in base_variants:
        positions = [i for i,ch in enumerate(base) if ch.lower() in subs]
        positions = positions[:10]
        for r in range(len(positions) + 1):
            for combo in itertools.combinations(positions, r):
                chars = list(base)
                for idx in combo:
                    chars[idx] = subs[chars[idx].lower()]
                result.add("".join(chars))
    return result

def password_building(profile: dict) ->list:
    name_tokens = set()
    for key in ("fname", "surname", "lname", "nickname", "petname", "favourite_food", "favourite_color"):
        value = profile.get(key,"")
        if value:
            name_tokens |= leet_variants(value)
    number_token = [
        profile.get("byear",""),
        profile.get("bday",""),
        profile.get("bmonth",""),
        profile.get("phone_number","")
    ]
    number_token = [t for t in number_token if t] #loại bỏ rỗng

    specials = list(dict.fromkeys(COMMON_SPECIALS))

    parts = [list(name_tokens), number_token, specials]
    candidates = set()

    for order in itertools.permutations(range(3)):
        groups = [parts[i] if parts[i] else[""] for i in order]
        for combo in itertools.product(*groups):
            candidates.add("".join(combo))
    return list(candidates)

#password cracking

def password_cracking(target_hashes: dict, wordlist: list, label: str)->bool:
    print(f"Trying {label}")
    
    start = time.perf_counter()
    target_modulo = target_hashes["modulo_hash"]
    target_sha = target_hashes["sha256_hash"]

    modulo_hits = 0
    checked = 0
    found = None

    for candidate in wordlist:
        checked += 1
        if checked > MAX_ATTEMPTS:
            print("Out of attempts range, stop")
            break
        if checked % PROGRESS_EVERY == 0:
            elapsed = time.perf_counter() - start
            print(candidate) ##################################################
            print(f"Tried {checked} candidates ({elapsed * 1000:.2f} ms)")

        if modulo_hash(candidate) == target_modulo:
            modulo_hits += 1

            if sha256_hash(candidate) == target_sha:
                found = candidate
                break
    elapsed = time.perf_counter() - start

    if(found):
        print(f"Successful, Password is '{found}'")
        print(f"Cracked in {elapsed * 1000:.2f} ms with {checked} candidates suspended ")
        print(f"Modulo value hit {modulo_hits - 1} times before finding the target candidates")
        print("=" * 64)
    else:
        print(f"Failed with {checked} candidates suspended in {elapsed * 1000:.2f} ms")
        print(f"Modulo value hit {modulo_hits} times")            

    return found is not None

def main():
    try:
        with open("C:\\CodeStuff\\python\\project\\handoff.json","r", encoding="utf-8") as f:
            handoff = json.load(f)
    except FileNotFoundError:
        print("File Not Found, please run the defender.py programme at first")
        return

    profile = handoff["target_profile"]


    wordlist = password_building(profile)


    p1 = password_cracking(handoff["password_1_hash"], wordlist,"Password 1 based on user profile given by team A (defender)")
    print("Type 1 to continue cracking secure random password / 0 to quit")
    option = int(input())
    if option: p2 = password_cracking(handoff["password_2_hash"], wordlist, "Password 2 based on secure random using python secrets library given by team A (defender)")
    
    
if __name__ == "__main__":
    main()