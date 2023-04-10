import re

MODE = "first"
SAVED_PHRASES = {
    "missing trie node": MODE,
    "No state available for block": MODE,
    "Reverted": MODE,
    "Bad Gateway": MODE,
    "Service Unavailable": MODE,
    "Bad Request": MODE,
    "Not Found": MODE,
    "Not Allowed": MODE,
    "Gateway Time-out": MODE,
    "Internal Server Error": MODE,
    "Service Temporarily Unavailable": MODE,
    "the block height passed is invalid": MODE,
    "error": MODE,
    "Block could not be found": "cut_middle",
    "tx.origin is not authorized to deploy a contract": "cut_middle",
    "getdeletestateobject error": "cut_middle",
    '{"response"': "second",
}


def filter_msg_for_mode(msg: str, mode: str, phrase: str = None):
    split_msg = msg.split(":")
    if phrase is not None:
        split_msg[0] = phrase
    if mode == "first":
        return split_msg[0]
    elif mode == "first_last":
        return f"{split_msg[0]}:{split_msg[-1]}"
    return None


def is_saved_phrase_in_msg(saved_phrase: str, msg: str, mode: str):
    if mode == "cut_middle":
        split_msg = msg.split(" ")
        split_msg = [split_msg[0]] + split_msg[2:]
        return saved_phrase in " ".join(split_msg)
    return saved_phrase in msg


def filter_error_msg(msg: str, mode: str = "first"):
    numbers_re = r"[0-9]"
    msg = re.sub(numbers_re, "", msg).lower()
    for saved_phrase in SAVED_PHRASES:
        phrase_mode = SAVED_PHRASES[saved_phrase]
        saved_phrase = saved_phrase.lower()
        if is_saved_phrase_in_msg(saved_phrase, msg.split(":")[0], phrase_mode):
            return filter_msg_for_mode(msg, phrase_mode, saved_phrase)
    return filter_msg_for_mode(msg, mode)


def create_msg_groups(errors_dict):
    chain_msg_groups = {}
    # Create msg groups and number of errors for this group
    for group in errors_dict:
        errors_count, chain, msg = group
        error_msg = filter_error_msg(msg, MODE)
        if chain not in chain_msg_groups:
            chain_msg_groups[chain] = {}
        if error_msg is not None:
            if error_msg in chain_msg_groups[chain]:
                chain_msg_groups[chain][error_msg] += errors_count
            else:
                chain_msg_groups[chain][error_msg] = errors_count
    return chain_msg_groups
