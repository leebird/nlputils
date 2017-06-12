# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import os
import sys

# nlputis codes.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protolib.python import document_pb2, rpc_pb2, edgRules_pb2
from utils.rpc.iterator import request_iter_docs, edg_request_iter_docs
from utils.rpc import grpcapi
from utils.helper import DocHelper
from utils.param_helper import ParamHelper
from utils.edg_relations import EdgArg, EdgRelation, EdgRelations 
import glob

def run():
    
    #####Iterate through all files in Input directory and create doc_list
    input_dir_path = sys.argv[1]
    glob_path = input_dir_path + "/*";
    input_files = glob.glob(glob_path)
    document_list = list()
    for input_file in input_files:
        textFH = open(input_file,"r")
        text = textFH.read()
        textFH.close()
        raw_doc = document_pb2.Document()
        raw_doc = document_pb2.Document()
        doc_id = os.path.splitext(os.path.basename(input_file))[0]
        raw_doc.text = text 
        raw_doc.doc_id = doc_id 
        document_list.append(raw_doc)

    rule_phase0_filename = sys.argv[2]
    fh0 = open(rule_phase0_filename, "r")
    rule0_lines = fh0.readlines()
    fh0.close()
    
    ####NEED TO UPDDATE PARAM_HELPER
    param_helper = ParamHelper("NA","NA",rule0_lines,[],[])
    edg_rules = edgRules_pb2.EdgRules()

    param_helper.setRuleProtoAttributes(edg_rules)
    #param_helper.setDocProtoAttributes(raw_doc)

    # This is a simple function to make requests out of a list of documents. We
    # put 5 documents in each request.
    requests = edg_request_iter_docs(document_list, edg_rules,
                                 request_size=5,
                                 request_type=rpc_pb2.EdgRequest.PARSE_BLLIP)

    # Given a request iterator, send requests in parallel and get responses.
    responses_queue = grpcapi.get_queue(server='128.4.20.169',
                                        port=8902,
                                        request_thread_num=10,
                                        iterable_request=requests,
                                        edg_request_processor=True)
    count = 0
    for response in responses_queue:
        for doc in response.document:
            #print(doc)
            helper = DocHelper(doc)
            sentences = doc.sentence
            doc_id = doc.doc_id
            #print(edg_rules)
            sentNum = 0
            for sentence in sentences:
                flag = 0
                sentText = helper.text(sentence)
                for depExtra in sentence.dependency_extra:
                    flag = 1
                    print(doc_id+"\t"+str(sentNum)+"\t"+helper.printExtraDependencyAnalysis(sentence,depExtra)+"\t"+sentText)
                if flag == 0:
                    print(doc_id+"\t"+str(sentNum)+"\t"+helper.printEmptyExtraDependencyAnalysis(sentence)+"\t"+sentText)
                sentNum = sentNum + 1
            count += 1


if __name__ == '__main__':
    run()
