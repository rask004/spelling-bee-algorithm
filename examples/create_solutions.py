import json
from pathlib import Path

import spelling_bee

config_file = Path("./config.json")
with open(config_file) as fp:
    config:dict = json.load(fp)

path_freq_table = Path(config[spelling_bee.KEY_FREQ_TABLE_PATH])
path_wordlist = Path(config[spelling_bee.KEY_WORDLIST_PATH])
threshold = config[spelling_bee.KEY_MAINLETTER_THRESHOLD]
letters_count = config[spelling_bee.KEY_TOTAL_LETTERS_PER_SOLUTION]
min_words = config[spelling_bee.KEY_MIN_WORDS_PER_SOLUTION]
vowels = config[spelling_bee.KEY_VALID_VOWELS]
vowel_limits = tuple(config[spelling_bee.KEY_VOWEL_LIMITS])
exclude = config[spelling_bee.KEY_EXCLUDED_EXTRA_LETTERS]
path_output = Path(config[spelling_bee.KEY_OUTPUT_PATH])


with open(path_freq_table) as fp:
    base_freq_table = json.load(fp)["frequency"]

alpha, freq = spelling_bee.get_alphabet_frequency(base_freq_table, threshold)
wordlist = spelling_bee.load_wordlist(path_wordlist, alpha, min_length=4)
main_letters = tuple([a for a,_ in freq])
letter_combos = spelling_bee.create_letter_group_solutions(alpha, wordlist, key_letters=main_letters, letters_count=letters_count, min_words=min_words, vowels=vowels, vowel_limits=vowel_limits, exclude=exclude)

with open(path_output, "w") as fp:
    json.dump(letter_combos, fp)
