from flask import Flask, request, render_template, send_from_directory, redirect, url_for, safe_join
from werkzeug import secure_filename
from protolib.python import document_pb2, rpc_pb2, edgRules_pb2
from utils.rpc.grpcapi import GrpcInterface
from utils.helper import DocHelper
from utils.param_helper import ParamHelper
import json
import collections
import re
import os.path

app = Flask(__name__, static_url_path='/brat', static_folder='brat')

app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'text'])
#app.config['MAX_FILE_SIZE'] = 1000000 #1MB limit
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def validateFileSize(file):
    chunk = 10 #chunk size to read per loop iteration; 10 bytes
    data = None
    size = 0

    #keep reading until out of data
    while data != b'':
        data = file.read(chunk)
        print(data)
        size += len(data)
        #return false if the total size of data parsed so far exceeds MAX_FILE_SIZE
        if size > app.config['MAX_FILE_SIZE']:
            return False
    return True

def process_one_document(request):
    interface = GrpcInterface(host='128.4.20.169', port=8902)
    # interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.process_document(request)
    assert len(response.document) == 1
    return response.document[0]

def edg_process_one_document(request):
    # Use biotm2 as server.
    interface = GrpcInterface(host='128.4.20.169', port=8902)
    #interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.edg_process_document(request)
    assert len(response.document) == 1
    return response.document[0]

def parse_using_bllip(doc,rules):
    request = rpc_pb2.EdgRequest()
    request.request_type = rpc_pb2.Request.PARSE_BLLIP
    request.document.extend([doc])
    request.edg_rules.CopyFrom(rules)
    #return process_one_document(request)
    return edg_process_one_document(request)

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
        brat_data = helper.dependency_for_brat(sentence)
        brat_sentences[sentence.index] = brat_data
    return brat_sentences


def get_brat_data_added(parsed_doc):
    helper = DocHelper(parsed_doc)
    # Convert the dependency parse to json, which can be visualized by brat.
    # Support multiple sentences.
    brat_sentences = {}
    for sentence in parsed_doc.sentence:
        brat_data = helper.dependency_extra_for_brat(sentence)
        brat_sentences[sentence.index] = brat_data
    return brat_sentences


def save_read_uploaded_file(file):
    #if file and allowed_file(file.filename) and validateFileSize(file):
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #file.save(safe_join(app.config['UPLOAD_FOLDER'], filename))
        filename = safe_join(app.config['UPLOAD_FOLDER'], filename)
        with open(filename, 'rb') as fd:
            rule_text = fd.read()
        return rule_text
    return ""

@app.route('/brat/<path:path>')
def send_js(path):
    return send_from_directory('brat', path)


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        # Get the name of the uploaded file
        file0 = request.files['ruleFile0']
        file1 = request.files['ruleFile1']
        file2 = request.files['ruleFile2']
        rules0 = save_read_uploaded_file(file0)
        rules1 = save_read_uploaded_file(file1)
        rules2 = save_read_uploaded_file(file2)

        text = request.form['text']
        if rules0 == "":
            rules0 = request.form['rules0']
        if rules1 == "":
            rules1 = request.form['rules1']
        if rules2 == "":
            rules2 = request.form['rules2']
        rule0_lines = rules0.split("\n")
        rule1_lines = rules1.split("\n")
        rule2_lines = rules2.split("\n")
        doc_id = "9999999" 
        param_helper = ParamHelper(text,doc_id,rule0_lines,rule1_lines,rule2_lines)
        raw_doc = document_pb2.Document()
        edg_rules = edgRules_pb2.EdgRules()
        param_helper.setDocProtoAttributes(raw_doc)
        param_helper.setRuleProtoAttributes(edg_rules)
        ##########################
        parse_bllip = parse_using_bllip(raw_doc,edg_rules)
        #print parse_bllip 
        brat_bllip = json.dumps(get_brat_data(parse_bllip))
        brat_bllip_added = json.dumps(get_brat_data_added(parse_bllip))

        return render_template('index_edg.html', text=text, rules0=rules0,rules1=rules1,rules2=rules2,
                               brat_string_bllip=brat_bllip,
                               brat_string_bllip_added=brat_bllip_added)
    else:
        return render_template('index_edg.html')

@app.route("/", methods=['GET', 'POST'])
def parse():
    if request.method == 'POST':
        text = request.form['text']
        doc_id = '99999999'
        print text
        #if text == "readfile":
        #    with open('test.txt', 'r') as myfile:
        #        text=myfile.read()

        rules0 = request.form['rules0']
        rule0_lines = rules0.split("\n")
        rules1 = request.form['rules1']
        rule1_lines = rules1.split("\n")
        rules2 = request.form['rules2']
        rule2_lines = rules2.split("\n")
        
        param_helper = ParamHelper(text,doc_id,rule0_lines,rule1_lines,rule2_lines)
        raw_doc = document_pb2.Document()
        edg_rules = edgRules_pb2.EdgRules()
        param_helper.setDocProtoAttributes(raw_doc)
        param_helper.setRuleProtoAttributes(edg_rules)
        ##########################
        parse_bllip = parse_using_bllip(raw_doc,edg_rules)
        #print parse_bllip 
        brat_bllip = json.dumps(get_brat_data(parse_bllip))
        brat_bllip_added = json.dumps(get_brat_data_added(parse_bllip))

        return render_template('index_edg.html', text=text, rules0=rules0,rules1=rules1,rules2=rules2,
                               brat_string_bllip=brat_bllip,
                               brat_string_bllip_added=brat_bllip_added)
    else:
        return render_template('index_edg.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5003)
