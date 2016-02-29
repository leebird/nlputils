from bllipparser import Sentence, tokenize, RerankingParser, Tree
import os


class BllipParser(object):
    def __init__(self):
        curr_path = os.path.realpath(__file__)
        model_dir = os.path.join(os.path.dirname(curr_path), 'model')
        
        self.rrp = RerankingParser.fetch_and_load('GENIA+PubMed',
                                                  models_directory=model_dir,
                                                  verbose=False)

    def parse_one_sentence(self, text):
        if type(text) is not unicode:
            raise ValueError('Input must be unicode string')
        sentence = Sentence(text.encode('utf8'))
        parse_tree = self.rrp.simple_parse(sentence)
        return parse_tree.decode('utf8')    

    '''
    def tag_one_sentence(self, text):
        if type(text) is not unicode:
            raise ValueError('Input must be unicode string')
        sentence = Sentence(text.encode('utf8'))
        tags = self.rrp.tag(sentence)
        return tags
    '''
