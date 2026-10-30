import itertools
import json
import os
import time
from hash_utils import modulo_hash, sha256_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HANDOFF_FILE = os.path.join(BASE_DIR, "handoff.json")

MAX_ATTEMPTS = 2_000_000
PROGRESS_EVERY = 200
COMMON_SPECIALS = ["@", "!", "#", "$", "_", "-", ""]


WIDTH = 72
def print_banner(title: str) -> None:
    print("=" * WIDTH)
    print(title.center(WIDTH))
    print("=" * WIDTH)


def print_step(step_no: int, title: str) -> None:
    print(f"\n[{step_no}] {title}")
    print("-" * WIDTH)

# permutation engine
def leet_variants(word: str) -> set:
    subs = {"a": "4", "e": "3", "o": "0", "s": "5", "i": "1", "g": "9", "b": "8"}
    base_variants = {word, word.lower(), word.upper(), word.capitalize()}

    result = set(base_variants)

    for base in base_variants:
        positions = [i for i, ch in enumerate(base) if ch.lower() in subs]
        positions = positions[:10]
        for r in range(len(positions) + 1):
            for combo in itertools.combinations(positions, r):
                chars = list(base)
                for idx in combo:
                    chars[idx] = subs[chars[idx].lower()]
                result.add("".join(chars))
    return result


def password_building(profile: dict) -> list:
    name_tokens = set()
    for key in ("fname", "surname", "lname", "nickname", "petname", "favourite_food", "favourite_color"):
        value = profile.get(key, "")
        if value:
            name_tokens |= leet_variants(value)
    number_token = [
        profile.get("byear", ""),
        profile.get("bday", ""),
        profile.get("bmonth", ""),
        profile.get("phone_number", "")
    ]
    number_token = [t for t in number_token if t]  # loại bỏ rỗng

    specials = list(dict.fromkeys(COMMON_SPECIALS))

    parts = [list(name_tokens), number_token, specials]
    candidates = set()

    for order in itertools.permutations(range(3)):
        groups = [parts[i] if parts[i] else [""] for i in order]
        for combo in itertools.product(*groups):
            candidates.add("".join(combo))
    return list(candidates)


# password cracking

def password_cracking(target_hashes: dict, wordlist: list, label: str) -> dict:
    print(f"\n>> Cracking: {label}")
    print(f"   Wordlist size: {len(wordlist):,} candidates")

    start = time.perf_counter()
    target_modulo = target_hashes["modulo_hash"]
    target_sha = target_hashes["sha256_hash"]

    modulo_hits = 0
    checked = 0
    found = None

    for candidate in wordlist:
        checked += 1
        if checked > MAX_ATTEMPTS:
            print(f"   ... reached the {MAX_ATTEMPTS:,} attempt limit, stopping.")
            break
        if checked % PROGRESS_EVERY == 0:
            elapsed = time.perf_counter() - start
            print(f"   ... tried {checked:,} candidates ({elapsed * 1000:.2f} ms) | current: '{candidate}'")

        if modulo_hash(candidate) == target_modulo:
            modulo_hits += 1

            if sha256_hash(candidate) == target_sha:
                found = candidate
                break
    elapsed = time.perf_counter() - start

    if found:
        print(f"   RESULT   : CRACKED -> '{found}'")
        print(f"   Time     : {elapsed * 1000:.2f} ms")
        print(f"   Attempts : {checked:,}")
        print(f"   Modulo false-positives before match: {modulo_hits - 1}")
    else:
        print(f"   RESULT   : NOT CRACKED (ran out of candidates)")
        print(f"   Time     : {elapsed * 1000:.2f} ms")
        print(f"   Attempts : {checked:,}")
        print(f"   Modulo false-positives encountered : {modulo_hits}")

    return {
        "label": label,
        "password": found,
        "success": found is not None,
        "elapsed_ms": elapsed * 1000,
        "checked": checked,
        "modulo_hits": modulo_hits,
    }


def main():
    print_banner("ATTACKER PROGRAM — Team B (Dictionary Attack Simulation)")

    # -------------------------------------------------------------
    print_step(1, "Loading handoff.json from Team A")
    try:
        with open(HANDOFF_FILE, "r", encoding="utf-8") as f:
            handoff = json.load(f)
    except FileNotFoundError:
        print(f"  ERROR: '{HANDOFF_FILE}' not found.")
        print("  -> Please run defender.py first to generate it.")
        return

    profile = handoff["target_profile"]
    print(f"  Source file  : {HANDOFF_FILE}")
    print(f"  Profile keys : {len(profile)}")
    for key, value in profile.items():
        print(f"    - {key:<18}: {value}")

    # -------------------------------------------------------------
    print_step(2, "Building candidate wordlist (permutation engine)")
    wordlist = password_building(profile)
    print(f"  Total candidates generated: {len(wordlist):,}")

    # -------------------------------------------------------------
    print_step(3, "Cracking Password 1 (profile-based)")
    results = [password_cracking(
        handoff["password_1_hash"], wordlist,
        "Password 1 — profile-based (built by team A)"
    )]

    print_step(4, "Cracking Password 2 (secure random)")
    print("  Type 1 to crack the random password too, or 0 to skip:")
    try:
        option = int(input("  > "))
    except ValueError:
        option = 0

    if option:
        results.append(password_cracking(
            handoff["password_2_hash"], wordlist,
            "Password 2 — secure random (python secrets library)"
        ))
    else:
        print("  Skipped by user.")

    # -------------------------------------------------------------
    print_step(5, "Summary")
    name_col = max(len("Password"), max(len(r["label"]) for r in results)) + 2
    header = f"  {'Password':<{name_col}}{'Result':<10}{'Time (ms)':>12}  {'Attempts':>10}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in results:
        status = "CRACKED" if r["success"] else "SAFE"
        print(f"  {r['label']:<{name_col}}{status:<10}{r['elapsed_ms']:>12.2f}  {r['checked']:>10,}")

    print()
    print_banner("DONE")


if __name__ == "__main__":
    main()