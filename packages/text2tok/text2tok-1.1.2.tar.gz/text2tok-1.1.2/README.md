# text2tok

[![PyPI version](https://img.shields.io/pypi/v/text2tok.svg?maxAge=3600)](https://pypi.org/project/text2tok)
[![PyPI license](https://img.shields.io/pypi/l/text2tok.svg?maxAge=3600)](https://github.com/jacobvsdanniel/text2tok/blob/master/LICENSE)

Text tokenizers optimized for sparse retrieval.

## Installation

```
python -m pip install text2tok

# (optional) enabling ICU-based tokenizers
apt install pkg-config libicu-dev
python -m pip install --no-binary=:pyicu: pyicu
```

## Usage

```py
from text2tok import reg_tokenize, icu_tokenize, BPETokenizer, BERTTokenizer

text_list = [
    "去過中國science院，覺得it's pretty good。",
    "I'm having a state-of-the-art \"whopper\" at Mendy's and James'.",
    "I can’t ‘admire’ such a 'beautiful' dog.",
    "最多容納59,000個人,或5.9萬人,坪數對人數為1:3.",
]

cache_dir = "/root/hf_cache"
bpe_model = "Qwen/Qwen3-8B"
bert_model = "google-bert/bert-base-multilingual-cased"

tokenizer_list = [
    ("REG", reg_tokenize),
    ("ICU", icu_tokenize),
    ("BPE", BPETokenizer(bpe_model, cache_dir=cache_dir)),
    ("BRT", BERTTokenizer(bert_model, cache_dir=cache_dir)),
]

for text in text_list:
    print(f"{text}")
    for name, tokenize in tokenizer_list:
        token_list = tokenize(text)
        print(f"[{name}] {token_list}")
    print()
```

Result:
```
去過中國science院，覺得it's pretty good。
[REG] ['去過', '過中', '中國', 'science', '院', '覺得', 'pretty', 'good']
[ICU] ['去', '過', '中國', 'science', '院', '覺得', 'pretty', 'good']
[BPE] ['去', '過', '中國', 'science', '院', '，', '覺得', 'it', "'s", 'pretty', 'good', '。']
[BRT] ['去', '過', '中', '國', 'science', '院', '，', '覺', '得', 'it', "'", 's', 'pretty', 'good', '。']

I'm having a state-of-the-art "whopper" at Mendy's and James'.
[REG] ['having', 'state', 'art', 'whopper', 'mendy', 'james']
[ICU] ['having', 'state', 'art', 'whopper', 'mendy', 'james']
[BPE] ['I', "'m", 'having', 'a', 'state', '-of', '-the', '-art', '"', 'whopper', '"', 'at', 'Mendy', "'s", 'and', 'James', "'."]
[BRT] ['I', "'", 'm', 'having', 'a', 'state', '-', 'of', '-', 'the', '-', 'art', '"', 'whopper', '"', 'at', 'Mendy', "'", 's', 'and', 'James', "'", '.']

I can’t ‘admire’ such a 'beautiful' dog.
[REG] ['admire', 'beautiful', 'dog']
[ICU] ['admire', 'beautiful', 'dog']
[BPE] ['I', 'can', '’t', '‘', 'admire', '’', 'such', 'a', "'", 'beautiful', "'", 'dog', '.']
[BRT] ['I', 'can', '[UNK]', 't', '[UNK]', 'admire', '[UNK]', 'such', 'a', "'", 'beautiful', "'", 'dog', '.']

最多容納59,000個人,或5.9萬人,坪數對人數為1:3.
[REG] ['最多', '多容', '容納', '59,000', '個人', '或', '5.9', '萬人', '坪數', '數對', '對人', '人數', '數為', '1', '3']
[ICU] ['最多', '容納', '59', '000', '個人', '或', '5', '9', '萬人', '坪', '數', '對', '人數', '為', '1', '3']
[BPE] ['最多', '容', '納', '5', '9', ',', '0', '0', '0', '個人', ',', '或', '5', '.', '9', '萬', '人', ',', '坪', '數', '對', '人', '數', '為', '1', ':', '3', '.']
[BRT] ['最', '多', '容', '納', '59', ',', '000', '個', '人', ',', '或', '5', '.', '9', '萬', '人', ',', '坪', '數', '對', '人', '數', '為', '1', ':', '3', '.']
```
