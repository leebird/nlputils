from __future__ import unicode_literals, print_function
from ..helper import RangeHelper


def extract_mid_token(helper, entity1, entity2):
    if RangeHelper.char_range_overlap(entity1, entity2):
        return []
    
    if entity1.token_start > entity2.token_end:
        start, end = entity2.token_end + 1, entity1.token_start - 1
    else:
        start, end = entity1.token_end + 1, entity2.token_start - 1

    tokens = []
    for token in helper.doc.token[start:end+1]:
        tokens.append(token)
    
    return tokens


def extract_left_token(helper, sentence, entity, word_num):
    start = entity.token_start - word_num
    if start < sentence.token_start:
        start = sentence.token_start

    tokens = []
    for token in helper.doc.token[start: entity.token_start]:
        tokens.append(token)
    return tokens


def extract_right_token(helper, sentence, entity, word_num):
    end = entity.token_end + word_num
    if end > sentence.token_end:
        end = sentence.token_end

    tokens = []
    for token in helper.doc.token[entity.token_end+1: end+1]:
        tokens.append(token)
    return tokens

    

