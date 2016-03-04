from bllipparser import Sentence, tokenize, RerankingParser, Tree
import os

# NOTE that this BLLIP parser is not thead-safe. See
# https://github.com/dmcc/bllip-parser/blob/master/python/bllipparser/RerankingParser.py#L537
# add first stage's README. So we can't use BLLIP parser
# in multi-threads.
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
        # If any error happens, just return None.
        try:
            parse_tree = self.rrp.simple_parse(sentence)
            return parse_tree.decode('utf8')
        except:
            return None

    '''
    def tag_one_sentence(self, text):
        if type(text) is not unicode:
            raise ValueError('Input must be unicode string')
        sentence = Sentence(text.encode('utf8'))
        tags = self.rrp.tag(sentence)
        return tags
    '''
