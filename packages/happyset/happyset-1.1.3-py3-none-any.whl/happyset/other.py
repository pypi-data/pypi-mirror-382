import itertools
import re
import time

def Conv_2dListTo1dList(l_2d):
    return list(itertools.chain.from_iterable(l_2d))

def Replace_match(sentence, targetWord, replaceWord):
    match = re.search(targetWord,sentence)
    if match:
        return sentence.replace(match.group(),replaceWord)
    else:
        return sentence

def Wait(sec):
    time.sleep(sec)

