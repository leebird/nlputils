from flask import Flask, request, render_template, send_from_directory
from protolib.python import document_pb2, rpc_pb2
from utils.rpc.grpcapi import GrpcInterface
from utils.helper import DocHelper
import json

app = Flask(__name__, static_url_path='/brat', static_folder='brat')


def process_one_document(request):
    interface = GrpcInterface(host='128.4.20.169')
    # interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.process_document(request)
    assert len(response.document) == 1
    return response.document[0]


def parse_using_bllip(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.PARSE_BLLIP
    request.document.extend([doc])
    return process_one_document(request)


def parse_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.PARSE_STANFORD
    request.document.extend([doc])
    return process_one_document(request)


def get_brat_data(parsed_doc):
    helper = DocHelper(parsed_doc)
    # Convert the dependency parse to json, which can be visualized by brat.
    # Support multiple sentences.
    brat_sentences = {}
    for sentence in parsed_doc.sentence:
        brat_data = helper.dependencpy_for_brat(sentence)
        brat_sentences[sentence.index] = brat_data
    return brat_sentences


@app.route('/brat/<path:path>')
def send_js(path):
    return send_from_directory('brat', path)


@app.route("/", methods=['GET', 'POST'])
def parse():
    if request.method == 'POST':
        text = request.form['text']

        doc = document_pb2.Document()
        doc.text = text

        parse_bllip = parse_using_bllip(doc)
        parse_stanford = parse_using_stanford(doc)
        brat_bllip = json.dumps(get_brat_data(parse_bllip))
        brat_stanford = json.dumps(get_brat_data(parse_stanford))

        return render_template('index.html', text=text,
                               brat_string_bllip=brat_bllip,
                               brat_string_stanford=brat_stanford)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
