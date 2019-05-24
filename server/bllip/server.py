from __future__ import unicode_literals, print_function
import time
from bllip_process_pool import BllipManager
from protolib.python import rpc_pb2, rpc_pb2_grpc
import glog
import sys
import grpc
from concurrent import futures

class BllipServicer(rpc_pb2_grpc.BllipParserServicer):
    def __init__(self, pool_size=1):
        self.pool_size = pool_size
        glog.info('Waiting for BLLIP manager init...')
        self.manager = BllipManager(self.pool_size)
        glog.info('BLLIP manager inited')
        glog.info('BLLIP parser pool size: {}'.format(self.pool_size))

    def Parse(self, request, context):
        response = rpc_pb2.BllipParserResponse()
        for sid, sentence in request.sentence.items():
            parse_tree = self.manager.parse_one_sentence(sentence)
            if parse_tree is not None:
                response.parse[sid] = parse_tree
        return response


def serve(pool_size=1):
    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc_pb2_grpc.add_BllipParserServicer_to_server(BllipServicer(pool_size), server)
    server.add_insecure_port('[::]:8901')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)
         
if __name__ == '__main__':
    glog.setLevel(glog.DEBUG)
    try:
        pool_size = int(sys.argv[1])
    except:
        pool_size = 1
    serve(pool_size)


