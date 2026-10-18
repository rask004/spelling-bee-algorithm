"""functions for creating candidate solutions for ny-times spelling bee like puzzles"""

all = ["get_alphabet_frequency", "load_wordlist", "create_letter_group_solutions", "create_config_file"]
import json
from itertools import combinations
from pathlib import Path

KEY_FREQ_TABLE_PATH = "freq_table_path"
KEY_OUTPUT_PATH = "output_path"
KEY_WORDLIST_PATH = "wordlist"
KEY_VALID_VOWELS = "vowels"
KEY_MAINLETTER_THRESHOLD = "threshold"
KEY_TOTAL_LETTERS_PER_SOLUTION = "letters_per_solution"
KEY_MIN_WORDS_PER_SOLUTION = "min_words"
KEY_VOWEL_LIMITS = "vowels_min_max"
KEY_EXCLUDED_EXTRA_LETTERS = "excluded_letters"


def get_alphabet_frequency(letter_frequency:dict[str, int|float], threshold:float=0.0, ignore_chars:str|tuple[str, ...]=""):
    """Creates an sequence of Alphabet letters and a normalized letter frequency sequence from a given
    letter frequency kv-pair. A cut off threshold can be given to restrict the output letter frequencies.

    letter_frequency    dict, with keys as letter characters and values as frequency numbers
    threshold           number, letter frequencies less than this are removed from the output frequency sequence
    ignore_chars        str, characters that should not appear in alphabet or frequency table.

    Returns :
        alphabet                tuple, contains all unique letters from the letter frequency input
        freq                    tuple[letters], filtered frequency tuples. Frequencies range from 0.0 to 1.0"""

    if not (isinstance(threshold, float) and threshold >= 0):
        raise ValueError("threshold should be a number >= 0")
    for k, v in letter_frequency.items():
        if not (isinstance(k, str) and len(k) > 0):
            raise ValueError("letter_frequency keys should be non-empty strings")
        if not (isinstance(v, int|float) and v > 0):
            raise ValueError("letter_frequency values should be int > 0")
    if not (isinstance(ignore_chars, str) or isinstance(ignore_chars, tuple)):
        raise ValueError("ignore_chars should be either a str or a tuple of str items")

    alphabet = tuple(sorted([x for x in letter_frequency.keys() if x not in ignore_chars and x != ""]))
    m = max([letter_frequency[a] for a in alphabet])
    if threshold <= 0:
        freq = [(a, letter_frequency[a] / m) for a in alphabet]
    else:
        freq = [(a, letter_frequency[a] / m) for a in alphabet if letter_frequency[a] >= threshold]
    return alphabet, freq


def load_wordlist(fname:Path, alphabet:tuple[str, ...], *, min_length:int=4):
    """load and filter a word list.

    fname       Path object pointing to a valid text file.
    alphabet    sequence of strings representing valid letters.
    min_length: minimum size of each word.

    Returns :   a sequence of words that contain only the letters present in alphabet"""
    if not fname.exists():
        raise ValueError("fname should be a valid Path object to an existing text file")
    if not isinstance(alphabet, tuple):
        raise ValueError("alphabet should be tuple containing valid letters as strings to check the list of words with")
    if not (isinstance(min_length, int) and min_length > 0):
            raise ValueError("")

    with open(fname) as fp:
        words = [n.strip().upper() for n in fp.readlines() if len(n.strip()) >= min_length]
    for i in range(len(words)-1, -1, -1):
        w = words[i]
        for a in alphabet:
            w = w.replace(a, "")
        if len(w) > 0:
            del words[i]
    return tuple(words)


def create_letter_group_solutions(alphabet:tuple[str, ...], wordlist:tuple[str,...], *, key_letters:tuple[str, ...], letters_count:int, min_words:int, vowels:tuple[str,...]=('A','E','I','O','U'), vowel_limits:tuple[int,int]=(1,3), exclude=""):
    """create a dict containing letter groups and the words each letter group can spell.

    alphabet                sequence of accepted letters
    wordlist                sequence of possible words for solution
    key_letters             sequence of key letters
    letter_subgroup_size    how many extra letters per solution
    vowels                  which letters are considered vowels. Default is English language vowels.
    vowel_limits            how many vowels allowed per solution,   (minimum, maximum)
    exclude                 letters to always exclude from extra letter groups
    min_words               minimum words required per solution

    Returns:
        letter_groupings:dict[str, dict[str, list]]    base key is single char str, sub-dict keys are strs representing the letter group, and the list has all words that the key letter / letter group combo can spell.
    """
    letter_subgroup_size = letters_count - 1
    alphabet_ = frozenset([a.upper() for a in alphabet])
    vowels_ = frozenset([v.upper() for v in vowels if v in alphabet_])
    exclusions_ = frozenset([a.upper() for a in exclude])
    letter_groups = dict()
    for k in key_letters:
        k = k.upper()
        if k not in alphabet_:
            continue
        vd, vu = vowel_limits
        if k in vowels_:
            vu -= 1
            vd -= 1
        subgroups:dict[str, list[str]] = {}
        letter_groups[k] = subgroups
        candidate_letters = sorted(a for a in alphabet_ if a != k and a not in exclusions_)
        for c in combinations(candidate_letters, letter_subgroup_size):
            vowel_count = len(vowels_.intersection(set(c)))
            if not vd <= vowel_count <= vu:
                continue
            subgroup = "".join(sorted(a for a in c))
            words = [w for w in gen_words_to_letter_group(k, subgroup, wordlist, alphabet_)]
            # print(k, subgroup, len(words), words[:min_words])
            if len(words) >= min_words:
                subgroups[subgroup] = words
    return letter_groups


def gen_words_to_letter_group(key_letter:str, letter_subgroup:str, word_list:tuple[str, ...], alpha:frozenset[str]):
    """generator for finding words for each letter group.

    key_letter          key letter for this grouping
    letter_subgroup     subgroup key for this grouping
    word_list           list to find words from
    alpha               alphabet of all letters

    Yields:             valid words."""

    out_letters = frozenset([a for a in alpha if a not in letter_subgroup and a != key_letter])
    for word in word_list:
        w_letters = frozenset(c for c in word)
        if out_letters.intersection(w_letters):
            continue
        yield word


def create_config_file(config_fpath:str, /, lang_freq_table_fpath:str, solutions_json_fpath:str, *, word_list_fpath:str, lang_vowels:list[str]|tuple[str, ...], freq_threshold:float, puzzle_letter_count:int, min_words_per_solution:int, min_vowel_count:int, max_vowel_count:int, exclude_letters:str):
    """Generate a config file using given arguments."""
    config = {
        KEY_FREQ_TABLE_PATH: lang_freq_table_fpath,
        KEY_OUTPUT_PATH: solutions_json_fpath,
        KEY_WORDLIST_PATH: word_list_fpath,
        KEY_VALID_VOWELS: lang_vowels,
        KEY_MAINLETTER_THRESHOLD: freq_threshold,
        KEY_TOTAL_LETTERS_PER_SOLUTION: puzzle_letter_count,
        KEY_MIN_WORDS_PER_SOLUTION: min_words_per_solution,
        KEY_VOWEL_LIMITS: [min_vowel_count, max_vowel_count],
        KEY_EXCLUDED_EXTRA_LETTERS: exclude_letters
    }
    with open(config_fpath, "w") as fp:
        json.dump(config, fp)
