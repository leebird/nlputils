from __future__ import unicode_literals, print_function
from protolib.python.rpc_pb2 import Request


def request_iter_docs(doc_iter, request_size=5,
                      request_type=Request.PARSE_STANFORD):
    # Form and yield requests.
    doc_list = []
    for doc in doc_iter:
        doc_list.append(doc)

        if len(doc_list) == request_size:
            request = Request()
            request.document.extend(doc_list)
            request.request_type = request_type
            doc_list = []
            yield request

    # Process the last slice.
    if len(doc_list) > 0:
        request = Request()
        request.document.extend(doc_list)
        request.request_type = request_type
        yield request