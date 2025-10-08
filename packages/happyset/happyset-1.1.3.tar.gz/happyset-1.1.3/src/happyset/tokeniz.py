import os
import sudachipy
from sudachipy import tokenizer
from sudachipy import dictionary
import MeCab
import unidic

def Get_tokenizMecab_IPAdic(sentence):
    t = MeCab.Tagger("-r /usr/local/etc/mecabrc -d /usr/local/lib/mecab/dic/ipadic/")
    return t.parse(sentence)

def Get_tokenizMecab_unidic(sentence):
    t = MeCab.Tagger("-d "+os.path.join(unidic.__path__[0],"dicdir"))
    return t.parse(sentence)

def Get_tokenizSudachi(sentence):
    config_path = os.path.join(sudachipy.__path__[0],"resources/sudachi.json")
    tokenizer_obj = dictionary.Dictionary(config_path=config_path, dict_type='full').create()
    tokens = tokenizer_obj.tokenize(sentence,tokenizer.Tokenizer.SplitMode.C)
    output = []
    for t in tokens :
        tmp = list(t.part_of_speech())
        tmp.insert(0,t.surface())
        output.append(tmp)
    return output
