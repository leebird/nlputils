# coding=utf-8
import os
import bllipparser
import glog

# NOTE that this BLLIP parser is not thead-safe. See
# https://github.com/dmcc/bllip-parser/blob/master/python/bllipparser/RerankingParser.py#L537
# and first stage's README. So we can't use BLLIP parser in multi-threads. See
# bllip_process_pool.py for solution.


class BllipParser(object):
    def __init__(self, model_dir=None):
        """ Init the parser given the model folder.
        :param model_dir: Path to the folder storing the model, downloaded by
        RerankingParser.fetch_and_load() method.
        :type model_dir: str
        """
        if model_dir is None:
            # Use 'model/GENIA+PubMed' under current folder as default.
            filepath = os.path.realpath(__file__)
            dirpath = os.path.dirname(filepath)
            model_dir = os.path.join(dirpath, 'model/GENIA+PubMed')
        glog.setLevel(glog.INFO)
        glog.info('Loading model from ' + model_dir)

        # BLLIP parser doesn't support multi-thread parsing, and we will
        # run it as one thread in one process (in both nlputils and spark),
        # so this should be fine. It will raise a RunTimeError when initialize
        # twice.
        self.reranking_parser = \
            bllipparser.RerankingParser.from_unified_model_dir(model_dir)

    def parse_one_sentence(self, text):
        if type(text) is not unicode:
            raise ValueError('Input must be unicode string')
        sentence = bllipparser.Sentence(text.encode('utf8'))
        try:
            parse_tree = self.reranking_parser.simple_parse(sentence)
            return parse_tree.decode('utf8')
        except Exception as e:
            # If any error happens, just raise an RunTimeError.
            raise RuntimeError("Parsing failed: {0}".format(e))


if __name__ == '__main__':
    parser = BllipParser('./model/GENIA+PubMed')
    parse = parser.parse_one_sentence(u"I have a book")
    print(parse)
    parse = parser.parse_one_sentence(u"你好，test utf8字符串。")
    print(parse.encode('utf8'))
