from __future__ import unicode_literals, print_function
from protolib.python import rpc_pb2
from bllip_parser import BllipParser
import time
import sys


class BllipServicer(rpc_pb2.BetaBllipParserServicer):
    def __init__(self):
        print('Wait for creating parser...', file=sys.stderr)
        self.parser = BllipParser()    
        print('Parser created...', file=sys.stderr)

    def Parse(self, request, context):
        result = {}
        response = rpc_pb2.BllipParserResponse()
        for sid, sentence in request.sentence.items():
            parse_tree = self.parser.parse_one_sentence(sentence)
            response.parse[sid] = parse_tree
        return response


def serve():
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    server = rpc_pb2.beta_create_BllipParser_server(BllipServicer(), pool_size=20)
    server.add_insecure_port('[::]:8901')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
         
if __name__ == '__main__':
    serve()


