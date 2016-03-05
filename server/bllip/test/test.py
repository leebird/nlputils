# coding=utf8
from __future__ import unicode_literals, print_function
from bllip_parser import BllipParser
from bllip_process_pool import _bllip_parser_worker, BllipManager
from multiprocessing import Queue


def test_bllip_parser():
    parser = BllipParser()
    sentences = ['I have a book.',
                 'The expressions of collagen I, collagen III, NADPH oxidase 4 '
                 '(NOX4) and nuclear factor-kappa B (NF-κB) were analyzed by '
                 'immunohistochemisty, qPCR and (or) Western blot.',
                 '[miR-126 inhibits colon cancer proliferation and invasion '
                 'through targeting IRS1, SLC7A5 and TOM1 gene].']
    
    for sent in sentences:
        parse_tree = parser.parse_one_sentence(sent)
        print(parse_tree)


def test_bllip_worker():
    q1 = Queue(10)
    q2 = Queue(10)

    _bllip_parser_worker('test', q1, q2)
    print(q2.get())
    q1.put('I have a book.')
    print(q2.get())


def test_bllip_manager():
    manager = BllipManager()
    print(manager.parse_one_sentence('I have a book.'))
    manager.stop()


if __name__ == '__main__':
    # Since model can be loaded only once in a process, we
    # skip this test. The _bllip_parser_worker() function is
    # tested in test_bllip_manager() implicitly.
    # test_bllip_worker()
    # Not sure why BllipParser will raise exception for loading
    # model twice in the process. test_bllip_parser() is run
    # in the main process, while test_bllip_manager() will
    # create a child process for the parser. Skip for now.
    # test_bllip_parser()
    test_bllip_manager()


'''
import os
print(__file__)
print(os.path.realpath(__file__))


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
