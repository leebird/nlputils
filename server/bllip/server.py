from __future__ import unicode_literals, print_function
import time
import sys
from bllip_process_pool import BllipManager
from protolib.python import rpc_pb2
from utils.logging.utils import get_logger


class BllipServicer(rpc_pb2.BetaBllipParserServicer):
    def __init__(self):
        self.pool_size = 15
        self.logger = get_logger('BllipServicer')
        self.logger.info('Waiting for BLLIP manager init...')
        self.manager = BllipManager(self.pool_size)
        self.logger.info('BLLIP manager inited')
        self.logger.info('BLLIP parser pool size: {}'.format(self.pool_size))


    def Parse(self, request, context):
        response = rpc_pb2.BllipParserResponse()
        for sid, sentence in request.sentence.items():
            parse_tree = self.manager.parse_one_sentence(sentence)
            if parse_tree is not None:
                response.parse[sid] = parse_tree
        return response

def serve():
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    server = rpc_pb2.beta_create_BllipParser_server(BllipServicer(),
                                                    pool_size=20,
                                                    default_timeout=600)
    server.add_insecure_port('[::]:8901')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
         
if __name__ == '__main__':
    serve()


