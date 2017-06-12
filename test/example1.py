# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protolib.python import document_pb2, rpc_pb2, edgRules_pb2
from utils.rpc import grpcapi
import collections
import re
from utils.helper import DocHelper
from utils.param_helper import ParamHelper

def process_one_document(request):
    # Use biotm2 as server.
    interface = grpcapi.GrpcInterface(host='128.4.20.169', port=8902)
    #interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.process_document(request)
    assert len(response.document) == 1
    return response.document[0]

def edg_process_one_document(request):
    # Use biotm2 as server.
    interface = grpcapi.GrpcInterface(host='128.4.20.169', port=8902)
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


def split_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.SPLIT
    request.document.extend([doc])
    return process_one_document(request)

def run():
    textFH = open(sys.argv[1],"r")
    text = textFH.read()
    textFH.close()
    #text = u'Surface expression of mir-21 activates tgif beta receptor type II expression. Expression of mir-21 and mir-132  directly mediates cell migration . mir-21 mediates cell migration and proliferation. mir-21 seems to mediate apoptosis. mir-21 is  involved in cellular processes, such as cell migration and cell proliferation. mir-21 regulates the ectopic expression of smad2 .'
    #text = u'transport of annexin 2 not only to dynamic actin-rich ruffles at the cell cortex but also to cytoplasmic and perinuclear vesicles.'
    doc_id = '99999999'
    rule_phase0_filename = sys.argv[2]
    rule_phase1_filename = sys.argv[3]
    rule_phase2_filename = sys.argv[4]
    fh0 = open(rule_phase0_filename, "r")
    rule0_lines = fh0.readlines()
    fh0.close()
    fh1 = open(rule_phase1_filename, "r")
    rule1_lines = fh1.readlines()
    fh1.close()
    fh2 = open(rule_phase2_filename, "r")
    rule2_lines = fh2.readlines()
    fh2.close()
    param_helper = ParamHelper(text,doc_id,rule0_lines,rule1_lines,rule2_lines)
    
    raw_doc = document_pb2.Document()
    edg_rules = edgRules_pb2.EdgRules()
  
    param_helper.setDocProtoAttributes(raw_doc) 
    param_helper.setRuleProtoAttributes(edg_rules) 

 
    # Parse using Bllip parser.
    #print (ruleList)
    # Parse using Bllip parser.
    result = parse_using_bllip(raw_doc,edg_rules)
    helper = DocHelper(result)
    sentences = result.sentence
    #print(edg_rules)
    for sentence in sentences:
        print (helper.text(sentence))
        for depExtra in sentence.dependency_extra:
            print(helper.printExtraDependency(sentence,depExtra))
        print("===============================")
    #print(result)

if __name__ == '__main__':
    run()
