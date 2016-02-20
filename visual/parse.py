from flask import Flask, request, render_template, send_from_directory
from protolib.python import document_pb2
from utils.rpc.grpcapi import GrpcInterface
from utils.helper import DocHelper
import json

app = Flask(__name__, static_url_path='/brat', static_folder='brat')


def process_one_document(doc):
    interface = GrpcInterface(host='128.4.20.169')
    request = document_pb2.Request()
    request.request_type = document_pb2.Request.PARSE
    request.document.extend([doc])

    response = interface.process_document(request)
    assert len(response.document) == 1
    return response.document[0]


@app.route('/brat/<path:path>')
def send_js(path):
    return send_from_directory('brat', path)


@app.route("/", methods=['GET', 'POST'])
def parse():
    if request.method == 'POST':
        text = request.form['text']

        doc = document_pb2.Document()
        doc.text = text
        parsed = process_one_document(doc)
        helper = DocHelper(parsed)

        # Convert the dependency parse to json, which can be visualized by brat.
        # Support multiple sentences.
        brat_sentences = {}
        for sentence in parsed.sentence:
            brat_data = helper.dependencpy_for_brat(sentence)
            brat_sentences[sentence.index] = brat_data
            
        brat_string = json.dumps(brat_sentences)

        return render_template('index.html', text=text, brat_string=brat_string)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
