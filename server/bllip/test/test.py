# coding=utf8
from __future__ import unicode_literals
from bllip_parser import BllipParser
from bllipparser import Sentence, tokenize, RerankingParser, Tree

import os

print(__file__)
print(os.path.realpath(__file__))

parser = BllipParser()

sentences = ['I have a book.',
             'The expressions of collagen I, collagen III, NADPH oxidase 4 '
             '(NOX4) and nuclear factor-kappa B (NF-κB) were analyzed by '
             'immunohistochemisty, qPCR and (or) Western blot.']

for sent in sentences:
    parse_tree = parser.parse_one_sentence(sent)
    tags = parser.tag_one_sentence(sent)
    print(parse_tree)
    print(tags)

'''
sentence = Sentence('I have a book (CS).')
print(sentence.sentrep.getWord(0).lexeme())

lexeme() is the only API exposed by swig, check first-stage/PARSE/swig/wrapper.i.
In first-stage/PARSE/utils.C we can see the escape is very simple.
Copy the function here,
void escapeParens(string& word) {
    findAndReplace(word, "(", "-LRB-");
    findAndReplace(word, ")", "-RRB-");
    findAndReplace(word, "{", "-LCB-");
    findAndReplace(word, "}", "-RCB-");
    findAndReplace(word, "[", "-LSB-");
    findAndReplace(word, "]", "-RSB-");
}
'''
