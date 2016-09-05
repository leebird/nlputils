from __future__ import unicode_literals, print_function
from multiprocessing import Queue, Process, current_process
import random
from bllip_parser import BllipParser
import glog

# Since BLLIP parser is not thread-safe, we use process to do parallel parsing.
# We create a pool of BLLIP parsers, each parser is held by an indepdendent
# process. Each process has an input queue and an output queue to accept
# request and send back result. The parallelism happens in the BllipManager,
# which itself is thread-safe. When a multi-thread application (e.g., a gRPC
# server in our case) calls parse_one_sentence() in BllipManager, it randomly
# selects a BLLIP worker to parse the sentence, communicating through the
# two queues.

# Python has at least 3 implementation of queue, and they are used in different
# circumstances.
# 1. Queue: shared by multi-threads.
# 2. multiprocessing.Queue: shared by multi-threads or multi-processes on the 
#    same machine.
# 3. multiprocessing.SyncManager.Queue: this is a basic Queue + proxy so that
#    it can be used to transfer information between remote client and server.
# In our case, we should just use multiprocessing.Queue as we don't need to
# communicate with remote machine. More information on Python documentation.

# Process.join() is a mimic for the same API in Thread. It means the caller
# will be blocked until the process exits. Note it may cause a deadlock if the
# child process itself is blocked on some other resources, like a queue.
# join() is used only when BllipWorker.stop() is called and the queues are
# closed. We don't want to block BllipWorker or BllipManager when the parser
# is still waiting on the input queue.


def _bllip_parser_worker(name, input_queue, output_queue):
    # If we just use name it will print the message twice, not sure why.
    # Maybe because it is a different process and the logging module is
    # not supported well across processes.
    worker_process = name + '_' + current_process().name
    glog.info('Loading BLLIP parser...')
    parser = BllipParser()
    output_queue.put(True)
    glog.info('BLLIP parser loaded')

    while True:
        try:
            sentence = input_queue.get()
            if sentence is None:
                # Exit if it receives None. Note that calling queue.close()
                # in the parent process won't cause an IOError, since the
                # child process is already blocked on get()! We need to
                # explicitly send a None or other indicator to break the
                # loop. 3605188/communicating-end-of-queue on StackOverflow
                # for details.
                break
            parse_tree = parser.parse_one_sentence(sentence)
            output_queue.put(parse_tree)
        except (IOError, KeyboardInterrupt):
            glog.info('BLLIP parser exits due to exception')
            break


class BllipWorker(object):
    def __init__(self, name):
        self.name = name

        # If there are more than 50 sentences, then block the input queue.        
        self.inqueue = Queue(50)
        # Output queue is associated with input queue.
        self.dequeue = Queue()
        # Start the corresponding worker in a new process.
        glog.info('Starting BLLIP worker...')
        self.init_worker()
        glog.info('BLLIP worker loaded')

    def init_worker(self):
        self.worker = Process(target=_bllip_parser_worker, 
                              args=(self.name, self.inqueue, self.dequeue))
        self.worker.start()
        # Block until the parser is inited. The parser will put a value
        # to dequeue after it is inited.
        init_message = self.dequeue.get()

    def parse_one_sentence(self, sentence):
        self.inqueue.put(sentence)
        return self.dequeue.get(sentence)

    def stop(self):
        self.inqueue.put(None)
        # We can only join after putting a None to the parser process.
        # The loop in parser process will break on receiving None.
        self.worker.join()


class BllipManager(object):
    def __init__(self, process_pool_size=1):
        self.process_pool_size = process_pool_size
        self.pool = []
        self.create_parser_pool()

    def create_parser_pool(self):
        for i in range(self.process_pool_size):
            name = 'BllipWorker-{}'.format(i+1)
            self.pool.append(BllipWorker(name))

    def parse_one_sentence(self, sentence):
        try:
            selected_worker = random.randint(0, self.process_pool_size-1)
            parse = self.pool[selected_worker].parse_one_sentence(sentence)
            return parse
        except Exception as e:
            glog.error(e)

    def stop(self):
        for worker in self.pool:
            worker.stop()

