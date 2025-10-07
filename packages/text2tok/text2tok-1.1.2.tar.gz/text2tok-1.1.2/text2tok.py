import os
import sys
import logging
import unicodedata

import regex as re

try:
    import icu
except ModuleNotFoundError:
    logging.info(
        "PyICU is not installed.\n"
        "If ICU-based tokenizers are needed, install PyICU:\n"
        "$ apt install pkg-config libicu-dev\n"
        "$ pip install --no-binary=:pyicu: pyicu"
    )

original_level = os.environ.get("TRANSFORMERS_VERBOSITY")
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
from transformers import AutoTokenizer
if original_level is None:
    del os.environ["TRANSFORMERS_VERBOSITY"]
else:
    os.environ["TRANSFORMERS_VERBOSITY"] = original_level

"""
utilities
"""


class ICUFoldFilter:
    removal_mark_set = {"Mn", "Me", "Mc"}

    @classmethod
    def filter(cls, text):
        if not text:
            return text
        text = text.casefold()
        text = unicodedata.normalize("NFKC", text)
        text = unicodedata.normalize("NFKD", text)
        text = "".join(c for c in text if unicodedata.category(c) not in cls.removal_mark_set)
        text = unicodedata.normalize("NFC", text)
        return text


class BigramTokenizer:
    @classmethod
    def tokenize(cls, text):
        if not text:
            return []

        if len(text) == 1:
            return [text]

        return [
            text[i:i + 2]
            for i in range(len(text) - 1)
        ]


class EnStopWord:
    # import nltk
    # from nltk.corpus import stopwords
    # nltk.download("stopwords")
    # stop_word_set = set(stopwords.words("english"))

    # from spacy.lang.en import stop_words
    # stop_word_set = stop_words.STOP_WORDS
    # stop_word_dict = {word: True for word in stop_word_set}
    # apos = "‘’'ʼʻ"
    # for apos_character in apos:
    #     stop_word_dict[f"{apos_character}t"] = True  # spaCy stop words contain "n't", we add "'t" as well
    # with open("stop_word.json", "w", encoding="utf8") as f:
    #     json.dump(stop_word_dict, f, ensure_ascii=False)

    stop_word_dict = {word: True for word in [
        "if", "thereupon", "very", "’ve", "below", "amount", "until", "thence", "becomes", "are", "forty", "me", "whom",
        "out", "between", "side", "up", "wherever", "with", "somewhere", "when", "sixty", "whenever", "further", "have",
        "anyone", "whence", "itself", "something", "bottom", "you", "your", "where", "among", "seeming", "fifteen",
        "somehow", "beside", "also", "had", "that", "just", "there", "call", "yourself", "mine", "toward", "'d",
        "eleven", "herein", "he", "moreover", "please", "another", "eight", "herself", "at", "down", "mostly", "nor",
        "via", "n‘t", "’d", "enough", "unless", "by", "‘s", "an", "although", "would", "became", "thereafter",
        "elsewhere", "on", "any", "thru", "same", "anyway", "afterwards", "hereby", "n't", "more", "ever", "nowhere",
        "though", "re", "three", "within", "some", "take", "whoever", "name", "part", "a", "be", "her", "many", "back",
        "latterly", "‘d", "’m", "whose", "twelve", "whatever", "'s", "‘ve", "who", "from", "yet", "through", "show",
        "were", "anything", "else", "has", "due", "‘re", "should", "namely", "less", "hence", "quite", "really",
        "whereafter", "full", "can", "they", "every", "'m", "fifty", "during", "'ve", "together", "never", "after",
        "under", "everywhere", "into", "hers", "say", "but", "what", "will", "since", "do", "such", "off", "move", "’s",
        "'re", "meanwhile", "seems", "one", "none", "even", "seem", "along", "again", "whither", "‘m", "everything",
        "too", "serious", "everyone", "five", "hundred", "whereas", "therefore", "doing", "’re", "the", "above", "am",
        "indeed", "whole", "still", "than", "against", "then", "ca", "two", "either", "here", "hereupon", "top",
        "these", "former", "them", "done", "it", "was", "seemed", "all", "whereby", "nobody", "whether", "us",
        "several", "which", "does", "almost", "regarding", "however", "cannot", "their", "my", "becoming", "per",
        "nine", "‘ll", "next", "upon", "towards", "we", "already", "always", "become", "only", "hereafter", "why",
        "'ll", "six", "yours", "most", "him", "around", "alone", "onto", "our", "sometime", "made", "now", "using",
        "anyhow", "i", "latter", "beyond", "so", "besides", "this", "least", "anywhere", "someone", "across", "about",
        "or", "put", "whereupon", "nevertheless", "is", "much", "yourselves", "beforehand", "no", "once", "third", "go",
        "nothing", "rather", "each", "myself", "while", "for", "as", "empty", "perhaps", "others", "see", "because",
        "except", "get", "’ll", "make", "been", "therein", "otherwise", "throughout", "n’t", "wherein", "give",
        "formerly", "neither", "how", "thus", "themselves", "last", "over", "and", "his", "few", "sometimes", "himself",
        "being", "could", "noone", "amongst", "might", "not", "four", "ours", "various", "keep", "may", "of", "own",
        "front", "ourselves", "behind", "first", "its", "to", "she", "well", "before", "both", "other", "twenty",
        "used", "ten", "without", "thereby", "often", "did", "must", "those", "in", "‘t", "’t", "'t", "ʼt", "ʻt",
    ]}


class CJKBigramEnStopTokenizer:
    # from nltk.stem import PorterStemmer
    # stemmer = PorterStemmer()

    @classmethod
    def tokenize(cls, text):
        if not text:
            return []

        # first character
        c = text[0]
        buffer_is_cjk = unicodedata.name(c, "").startswith("CJK")
        buffer = [c]

        # loop through all characters
        token_list = []
        for c in text[1:]:
            c_is_cjk = unicodedata.name(c, "").startswith("CJK")

            if buffer_is_cjk:
                if c_is_cjk:
                    buffer.append(c)
                else:
                    buffer_bigram_list = BigramTokenizer.tokenize("".join(buffer))
                    for token in buffer_bigram_list:
                        token_list.append(token)
                    buffer = [c]
                    buffer_is_cjk = False
            else:
                if c_is_cjk:
                    token = "".join(buffer)
                    if token not in EnStopWord.stop_word_dict:
                        token_list.append(token)
                    buffer = [c]
                    buffer_is_cjk = True
                else:
                    buffer.append(c)

        # remaining buffer
        if buffer_is_cjk:
            buffer_bigram_list = BigramTokenizer.tokenize("".join(buffer))
            for token in buffer_bigram_list:
                token_list.append(token)
        else:
            token = "".join(buffer)
            if token not in EnStopWord.stop_word_dict:
                token_list.append(token)

        return token_list


"""
regex-based methodology
"""


class RegexFoldCJKBigramEnStopTokenizer:
    apos = "‘’'ʼʻ"
    number = r"\d+(?:[.,]\d+)*"
    hostname = r"\w+(?:\.\w+)+"
    word = rf"\w+(?:[{apos}]\w+)*"
    subword = rf"[{apos}]?\w+"

    word_pattern = re.compile(rf"\b(?:{number}|{hostname}|{word})\b", re.WORD)
    subword_pattern = re.compile(rf"(?:{number})|(?:{hostname})|(?:{subword})")

    @classmethod
    def tokenize(cls, text):
        token_list = [
            en_stopped_subword_or_cjk_bigram
            for word in cls.word_pattern.findall(text)
            for subword in cls.subword_pattern.findall(word)
            for en_stopped_subword_or_cjk_bigram in CJKBigramEnStopTokenizer.tokenize(ICUFoldFilter.filter(subword))
        ]
        return token_list


reg_tokenize = RegexFoldCJKBigramEnStopTokenizer.tokenize


"""
ICU-based methodology
"""


class ICUTokenizer:
    # for emoji removal
    #   BreakIterator is erroneous with emojis
    # rule = "[:Emoji:] Remove"
    # transliterator = icu.Transliterator.createInstance(rule)
    if "icu" in sys.modules:
        emoji_removal_set = icu.UnicodeSet("[:Emoji:]")
        emoji_removal_set.removeAll(icu.UnicodeSet("[:Nd:]"))  # keep digits
        emoji_removal_set.freeze()

    @classmethod
    def tokenize(cls, text):
        # text = cls.transliterator.transliterate(text)
        text = "".join(c for c in text if c not in cls.emoji_removal_set)

        it = icu.BreakIterator.createWordInstance(icu.Locale("und"))
        it.setText(text)
        i = it.first()
        token_list = []

        for j in it:
            status = it.getRuleStatus()
            if status > 0:  # status 0: spaces, punctuation, symbols
                token = text[i:j]
                token_list.append(token)
            i = j
        return token_list


class ICURegexFoldEnStopTokenizer:
    # y'all've --> y 'all 've
    apos = "‘’'ʼʻ"
    subword_pattern = re.compile(rf"[{apos}]?\w+")  # y'all've --> y 'all 've

    @classmethod
    def tokenize(cls, text):
        subword_list = [
            subword
            for word in ICUTokenizer.tokenize(text)
            for subword in cls.subword_pattern.findall(word)
        ]

        token_list = []
        for token in subword_list:
            token = ICUFoldFilter.filter(token)
            if token not in EnStopWord.stop_word_dict:
                token_list.append(token)
        return token_list


icu_tokenize = ICURegexFoldEnStopTokenizer.tokenize


"""
LLM-based methodology
"""


class BPETokenizer:
    def __init__(self, model_name, cache_dir=None):
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        return

    def __call__(self, text):
        enc = self.tokenizer(text, add_special_tokens=False, return_offsets_mapping=True)

        # merge tokens that split a multibyte character
        #   -> BPE could split a multibyte character
        #   -> offset_mapping is a list of token spans defined by character offset in the original text
        #       If two spans overlap: they split a multibyte character
        offset_list = enc["offset_mapping"]
        if not offset_list:
            return []
        merged_offset_list = offset_list[:1]
        for i2, j2 in offset_list[1:]:
            i1, j1 = merged_offset_list[-1]
            if i2 < j1:
                merged_offset_list[-1] = (min(i1, i2), max(j1, j2))
            else:
                merged_offset_list.append((i2, j2))
        tokenized_text = [text[i:j] for i, j in merged_offset_list]

        # merge tokens that are sub-words
        #   whenever the preceding token ends in, and succeeding token starts with, an alphabetic letter
        def is_alphabetic(c):
            return c.isalpha() and "IDEOGRAPH" not in unicodedata.name(c, "")

        merged_tokenized_text = tokenized_text[:1]
        for token in tokenized_text[1:]:
            preceding_token = merged_tokenized_text[-1]
            if is_alphabetic(preceding_token[-1]) and is_alphabetic(token[0]):
                merged_tokenized_text[-1] = preceding_token + token
            else:
                merged_tokenized_text.append(token)

        # strip and remove empty tokens
        stripped_tokenized_text = []
        for token in merged_tokenized_text:
            token = token.strip()
            if token:
                stripped_tokenized_text.append(token)

        return stripped_tokenized_text


class BERTTokenizer:
    def __init__(self, model_name, cache_dir=None):
        if cache_dir:
            os.environ["HF_HOME"] = cache_dir
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        return

    def __call__(self, text):
        tokenized_text = self.tokenizer.tokenize(text, add_special_tokens=False)

        if not tokenized_text:
            return tokenized_text

        # glue tokens
        merged_tokenized_text = tokenized_text[:1]
        for token in tokenized_text[1:]:
            if token.startswith("##"):
                merged_tokenized_text[-1] = merged_tokenized_text[-1] + token[2:]
            else:
                merged_tokenized_text.append(token)

        # strip and remove empty tokens
        stripped_tokenized_text = []
        for token in merged_tokenized_text:
            token = token.strip()
            if token:
                stripped_tokenized_text.append(token)

        return stripped_tokenized_text


"""
usage
"""


def _main():
    text_list = [
        "",
        "去過中國science院，覺得it's pretty good。",
        "I'm having a state-of-the-art \"whopper\" at Mendy's and James'.",
        "中國科學院，今天天氣真好，嗎",
        "I can’t ‘admire’ such a 'beautiful' dog.",
        "y'all've done “GOOD”.",
        "最多容納59,000個人,或5.9萬人,坪數對人數為1:3.",
        f"I have a {chr(0x1F525)} dream such that the sun is cold.",
    ]

    if "icu" in sys.modules:
        tokenize_list = [
            ("REG", reg_tokenize),
            ("ICU", icu_tokenize),
            ("BPE", BPETokenizer("Qwen/Qwen3-8B", cache_dir=None)),
            ("BRT", BERTTokenizer("google-bert/bert-base-multilingual-cased", cache_dir=None)),
        ]
    else:
        tokenize_list = [
            ("REG", reg_tokenize),
            ("BPE", BPETokenizer("Qwen/Qwen3-8B", cache_dir=None)),
            ("BRT", BERTTokenizer("google-bert/bert-base-multilingual-cased", cache_dir=None)),
        ]

    for text in text_list:
        print(f"{text}")
        for name, tokenize in tokenize_list:
            token_list = tokenize(text)
            print(f"[{name}] {token_list}")
        print("\n")
    return


if __name__ == "__main__":
    _main()
    sys.exit()
