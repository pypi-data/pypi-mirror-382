import re


def to_pascal_case(s: str) -> str:
    parts = re.split(r'[\s_\-]+', s.strip())
    result = []
    for word in parts:
        if word:
            result.append(word[0].upper() + word[1:])
    return ''.join(result)


def normalize_name(s: str) -> str:
    after = to_pascal_case(s)
    #print(f"{s} -> {after}")
    return after


def compare_names(name1: str, name2: str) -> bool:
    return normalize_name(name1).lower() == normalize_name(name2).lower()

