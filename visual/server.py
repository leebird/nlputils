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


def split_sentence_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.SPLIT
    request.document.extend([doc])
    return process_one_document(request)


def get_brat_data(parsed_doc):
    helper = DocHelper(parsed_doc)
    # Convert the dependency parse to json, which can be visualized by brat.
    # Support multiple sentences.
    brat_sentences = {}
    for sentence in parsed_doc.sentence:
        brat_data = helper.dependency_for_brat(sentence)
        brat_sentences[sentence.index] = brat_data
    return brat_sentences


@app.route('/brat/<path:path>')
def send_js(path):
    return send_from_directory('brat', path)


@app.route("/", methods=['GET', 'POST'])
def parse():
    if request.method == 'POST':
        text = request.form['text']
        split = request.form.getlist('split')
        
        doc = document_pb2.Document()
        doc.text = text

        parse_doc_bllip_brat = ''
        parse_doc_stanford_brat = ''
        split_doc_brat = ''
        cst_parses = ''

        if len(split) == 0:
            parse_doc_bllip = parse_using_bllip(doc)
            parse_doc_stanford = parse_using_stanford(doc)
            parse_doc_bllip_brat = json.dumps(get_brat_data(parse_doc_bllip))
            parse_doc_stanford_brat = json.dumps(get_brat_data(parse_doc_stanford))
            parses = {}
            for sentence in parse_doc_bllip.sentence:
                parses[sentence.index] = sentence.parse
            cst_parses = json.dumps(parses)
        else:
            split_doc = split_sentence_using_stanford(doc)
            split_doc_brat = json.dumps(get_brat_data(split_doc))


        return render_template('index.html', text=text,
                               parse_bllip=parse_doc_bllip_brat,
                               parse_stanford=parse_doc_stanford_brat,
                               split_stanford=split_doc_brat,
                               bllip_cst_parses=cst_parses)
    else:
        return render_template('index.html')

@app.route('/highlight', methods=['GET', 'POST'])
def highlight():
    if request.method == 'POST':
        text = request.form['text'].strip()
        text = text.replace('<Gene>', '<span style="color:blue; font-weight:bold;">')
        text = text.replace('</Gene>', '</span>')
        text = text.replace('<MiRNA>', '<span style="color:red; font-weight:bold;">')
        text = text.replace('</MiRNA>', '</span>')
        text = text.replace('<Subcellular_location>', '<span style="color:red; font-weight:bold">')
        text = text.replace('</Subcellular_location>', '</span>')

        lines = text.split('\n')
        return render_template('highlight.html', lines=lines)
    else:
        return render_template('highlight.html')

if __name__ == "__main__":
    app.debug = False
    app.run(host='0.0.0.0')
