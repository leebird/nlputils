from __future__ import unicode_literals, print_function
from multiprocessing import Queue, Process, current_process
from threading import Lock
import random
from bllip_parser import BllipParser
import glog
from time import sleep
import resource


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
    glog.info('Loading BLLIP parser: ' + worker_process)
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
            try:
                parse_tree = parser.parse_one_sentence(sentence)
            except RuntimeError:
                # Catch RuntimeError but not ValueError (caused by non-unicode
                # string).
                glog.info('RuntimeError {}, sentence: {}'.format(
                    worker_process, sentence))
                output_queue.put(None)
            else:
                output_queue.put(parse_tree)
        except (IOError, KeyboardInterrupt):
            # Unrecoverable errors.
            glog.info('BLLIP parser {} exits due to IOError or '
                      'KeyboardInterrupt'.format(worker_process))
            break

    # Output peak memory at the end.
    glog.info('Peak memory usage of {}: {}'.format(
        worker_process,
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024))


class BllipWorker(object):
    def __init__(self, name):
        self.name = name
        # If there are more than 50 sentences, then block the input queue.
        self.inqueue = Queue()

        # Output queue is associated with input queue.
        self.dequeue = Queue()

        # A lock to ensure input/output matching in multi-threading.
        self.lock = Lock()

        # Counter of parsed sentences.
        self.parsed_count = 0

        # At most parse this many sentences for one process.
        # Each 100 abstracts cost addtional 300 MB memory.
        self.max_sentence_limit = 2000

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

    def _parse_one_sentence(self, sentence):
        self.inqueue.put(sentence)
        # sleep(random.random())
        parse = self.dequeue.get()
        self.parsed_count += 1
        return parse

    def parse_one_sentence(self, sentence):
        # There may be multiple threads accessing this function from the
        # BllipManager. Use lock to ensure input/output matching.
        self.lock.acquire()
        if self.parsed_count >= self.max_sentence_limit:
            # Create a new parser process after 2000 sentences.
            glog.info(self.name + ' reached max sentence limit')
            glog.info('Shutting down ' + self.name)
            self.parsed_count = 0
            self.stop()
            self.init_worker()

        # Parse the sentence.
        parse = self._parse_one_sentence(sentence)

        # If parse is None, something wrong in the parser, probably caused
        # by the sentence. Restart the parser and return the None result.
        # Don't restart it for now. Most error sentences are ".".
        if parse is None:
            glog.warning('Parse error: {}'.format(sentence))
            #self.parsed_count = 0
            #self.stop()
            #self.init_worker()
        self.lock.release()
        return parse

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
            name = 'BllipWorker-{}'.format(i + 1)
            self.pool.append(BllipWorker(name))

    def parse_one_sentence(self, sentence):
        try:
            selected_worker = random.randint(0, self.process_pool_size - 1)
            parse = self.pool[selected_worker].parse_one_sentence(sentence)
            return parse
        except Exception as e:
            glog.error(e)

    def stop(self):
        for worker in self.pool:
            worker.stop()


if __name__ == '__main__':
    # If not use lock, the input/ouput will mismatch. Run this following
    # code to see an example. Uncomment the sleep() line and the lock-related
    # lines in BllipWorker.parse_one_sentence().
    from multiprocessing.pool import ThreadPool

    glog.setLevel(glog.INFO)
    manager = BllipManager(1)
    pool = ThreadPool(10)
    pool.map(lambda sentence: glog.info(
        sentence + ": " + manager.parse_one_sentence(sentence)),
             ['I have a book 1.', 'I have a book 2.',
              'I have a book 3.', 'I have a book 4.',
              'I have a book 5.', 'I have a book 6.',
              'I have a book 7.', 'I have a book 8.',
              'I have a book 9.', 'I have a book 10.'])
    manager.stop()
