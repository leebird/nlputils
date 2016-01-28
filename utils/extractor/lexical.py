from __future__ import unicode_literals, print_function
from ..helper import RangeHelper


def extract_mid_word(helper, entity1, entity2):
    if RangeHelper.char_range_overlap(entity1, entity2):
        return []
    
    if entity1.token_start > entity2.token_end:
        start, end = entity2.token_end + 1, entity1.token_start - 1
    else:
        start, end = entity1.token_end + 1, entity2.token_start - 1

    words = []
    for token in helper.doc.token[start:end+1]:
        words.append(token.word)
    
    return words


def extract_left_word(helper, sentence, entity, word_num):
    start = entity.token_start - word_num
    if start < sentence.token_start:
        start = sentence.token_start

    words = []
    for token in helper.doc.token[start: entity.token_start]:
        words.append(token.word)
    return words


def extract_right_word(helper, sentence, entity, word_num):
    end = entity.token_end + word_num
    if end > sentence.token_end:
        end = sentence.token_end

    words = []
    for token in helper.doc.token[entity.token_end+1: end+1]:
        words.append(token.word)
    return words

    

