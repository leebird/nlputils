from __future__ import unicode_literals, print_function

from grpc.beta import implementations
from grpc.framework.interfaces.face.face import ExpirationError
from protolib.python import document_pb2
import multiprocessing as mp
import threading
import logging


class GrpcInterface(object):
    def __init__(self, host='localhost', port=8900, timeout_seconds=1500,
                 thread_pool_size=20):
        self.port = port
        self.timeout_seconds = timeout_seconds
        self.thread_pool_size = thread_pool_size
        self.host = host
        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = document_pb2.beta_create_NlpService_stub(self.channel,
                                                             pool_size=self.thread_pool_size)
        
    def process_document(self, request):
        try:
            return self.stub.ProcessDocument(request, self.timeout_seconds)
        except ExpirationError:
            logging.warning('Expiration:' + '\t' + ','.join([d.doc_id for d in request.document]))
            return document_pb2.Response()


def _request_processor(interface, inqueue, dequeue):
    while True:
        request_bytes = inqueue.get()
        if request_bytes is None:
            dequeue.put(None)
            break
        request = document_pb2.Request()
        request.ParseFromString(request_bytes)
        response = interface.process_document(request)
        dequeue.put(response.SerializeToString())


def _serialize(iterable, inqueue, writer_num):
    for i in iterable:
        inqueue.put(i.SerializeToString())
    for _ in xrange(writer_num):
        inqueue.put(None)
    print('Input read done')


def get_queue(host, request_thread_num, iterable_request):
    interface = GrpcInterface(host)
    manager = mp.Manager()
    inqueue = manager.Queue(request_thread_num * 4)
    dequeue = manager.Queue(request_thread_num)

    print('Start input reading thread')
    thread = threading.Thread(target=_serialize, args=(iterable_request, inqueue, request_thread_num))
    thread.start()

    print('Start', request_thread_num, 'request processor threads')
    for i in xrange(request_thread_num):
        thread = threading.Thread(target=_request_processor, args=(interface, inqueue, dequeue))
        thread.start()

    print('Read from output queue...')
    while True:
        bytes = dequeue.get()
        if bytes is None:
            break
        response = document_pb2.Response()
        response.ParseFromString(bytes)
        yield response        

    
    # Note that using mp.Pool is problematic since we can only share interface
    # among threads but not processes.

    # Using ThreadPool is also problematic.
    # Note that imap_unordered will keep reading data, although it will
    # use only writer_num threads. For example, if you keep two counters,
    # one in iterable_request, the other in the response processor, the
    # counter in iterable_request will keep increasing, while the one in
    # response processor will only increase once a result is processed
    # and returned by the remote server.
    # This will cause an internal queue filled up with contents from the
    # iterator and then cause some other problems when memory is used up.
    # See http://stackoverflow.com/questions/5318936/python-multiprocessing-pool-lazy-iteration
    # pool = ThreadPool(writer_num, _init_request, (interface, queue))
    # result = pool.imap_unordered(_send_request,
    #                             _serialize(iterable_request))


def _request_processor_masked(interface, inqueue, dequeue):
    while True:
        request_bytes = inqueue.get()
        if request_bytes is None:
            dequeue.put(None)
            break

        request = document_pb2.Request()
        request.ParseFromString(request_bytes[0])
        original_response = interface.process_document(request)

        request = document_pb2.Request()
        request.ParseFromString(request_bytes[1])
        response = interface.process_document(request)

        dequeue.put((original_response.SerializeToString(),
                     response.SerializeToString()))


def _serialize_masked(iterable, inqueue, writer_num):
    for request, masked_request in iterable:
        inqueue.put((request.SerializeToString(),
                     masked_request.SerializeToString()))
    for _ in xrange(writer_num):
        inqueue.put(None)
    print('Input read done.')


def get_queue_masked(host, request_thread_num, iterable_request):
    interface = GrpcInterface(host)
    manager = mp.Manager()
    inqueue = manager.Queue(request_thread_num * 4)
    dequeue = manager.Queue(request_thread_num)

    print('Start input reading thread')
    thread = threading.Thread(target=_serialize_masked,
                              args=(iterable_request, inqueue, request_thread_num))
    thread.start()

    print('Start', request_thread_num, 'request processor threads')
    for i in xrange(request_thread_num):
        thread = threading.Thread(target=_request_processor_masked,
                                  args=(interface, inqueue, dequeue))
        thread.start()

    print('Read from output queue...')
    while True:
        bytes = dequeue.get()
        if bytes is None:
            break

        # Original response.
        original_response = document_pb2.Response()
        original_response.ParseFromString(bytes[0])

        # Masked response.
        response = document_pb2.Response()
        response.ParseFromString(bytes[1])

        yield original_response, response        
