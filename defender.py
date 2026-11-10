import json
import os
import secrets
import string
from hash_utils import hash_val

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_FILE = os.path.join(BASE_DIR, "user_profile.txt")
HANDOFF_FILE = os.path.join(BASE_DIR, "handoff.json")

# scan user profile
def load_profile(path: str = PROFILE_FILE) -> dict:
    profile = {}
    with open(path, "r", encoding="utf-8") as f:   
        for lineno, raw_line in enumerate(f, start=1):
            line = raw_line.strip()
            key, _, value = line.partition("=")
            profile[key.strip()] = value.strip()
    return profile

# word leet
def leetspeak(word: str) -> str:
    subs = {"a": "4", "e": "3", "o": "0", "s": "5", "i": "1", "g": "9", "b": "6"}
    for plain, repl in subs.items():
        word = word.replace(plain, repl)
    return word

# user profile password
def generate_user_profile_password(profile: dict) -> str:
    SPECIAL_CHAR = "@"
    base = profile.get("fname", "") or profile.get("nickname", "")
    leet = leetspeak(base)
    year = profile.get("byear", "")

    #return "NhuH4iDag@21092007)"   
    return f"{leet}{SPECIAL_CHAR}{year}"


def generate_random_password_using_secrets(length) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_-=+"
    return "".join(secrets.choice(alphabet) for _ in range(length))

WIDTH = 72
def print_banner(title: str) -> None:
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def print_step(step_no: int, title: str) -> None:
    print(f"\n[{step_no}] {title}")
    print("-" * WIDTH)


def main():
    print_banner("DEFENDER PROGRAM — Team A (Password Generation & Hashing)")

    
    print_step(1, "Loading user profile")
    profile = load_profile()
    print(f"  Source file : {PROFILE_FILE}")
    print(f"  Fields read : {len(profile)}")
    for key, value in profile.items():
        print(f"    - {key:<18}: {value}")

    print_step(2, "Generating passwords")
    password_1 = generate_user_profile_password(profile)
    password_2 = generate_random_password_using_secrets(16)
    print(f"  Password 1 (profile-based) : {password_1}")
    print(f"  Password 2 (random/secrets): {password_2}")

  
    print_step(3, "Hashing passwords (Modulo + SHA-256)")
    password1_hash = hash_val(password_1)
    password2_hash = hash_val(password_2)

    print(f"  {'Password':<12}{'Modulo':>8}   SHA-256")
    print(f"  {'-' * 12}{'-' * 8}   {'-' * 64}")
    print(f"  {'Password 1':<12}{password1_hash['modulo_hash']:>8}   {password1_hash['sha256_hash']}")
    print(f"  {'Password 2':<12}{password2_hash['modulo_hash']:>8}   {password2_hash['sha256_hash']}")

    print_step(4, "Writing handoff.json for Team B")
    fullname = " ".join(
        part for part in [profile.get("lname", ""), profile.get("surname", ""), profile.get("fname", "")]
        if part
    )
    public_info = {
        "target_profile": {**profile, "fullname": fullname},  
        "password_1_hash": password1_hash,
        "password_2_hash": password2_hash
    }

    with open(HANDOFF_FILE, "w", encoding="utf-8") as f:
        json.dump(public_info, f, ensure_ascii=False, indent=2)

    print(f"  Saved to : {HANDOFF_FILE}")
    print(f"  Contains : target_profile, password_1_hash, password_2_hash")
    print(f"  NOTE     : plaintext passwords are NOT included — hashes only.")

    print()
    print_banner("DONE — handoff.json ready for attacker.py")


if __name__ == "__main__":
    main()