# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from protolib.python import document_pb2, rpc_pb2, edgRules_pb2
from google.protobuf import json_format
from utils.rpc import grpcapi
from utils.helper import DocHelper
from utils.param_helper import ParamHelper
from constraint import constraint_args
from propagate import propagate


def edg_process_one_document(request):
    # Use biotm2 as server.
    interface = grpcapi.GrpcInterface(host='128.4.20.169', port=8902)
    # interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.edg_process_document(request)
    assert len(response.document) == 1
    return response.document[0]


def parse_using_bllip(doc, rules):
    request = rpc_pb2.EdgRequest()
    request.request_type = rpc_pb2.Request.PARSE_BLLIP
    request.document.extend([doc])
    request.edg_rules.CopyFrom(rules)
    # return process_one_document(request)
    return edg_process_one_document(request)


def run():
    # text = u'Surface expression of mir-21 activates tgif beta receptor type II expression. Expression of mir-21 and mir-132  directly mediates cell migration . mir-21 mediates cell migration and proliferation. mir-21 seems to mediate apoptosis. mir-21 is  involved in cellular processes, such as cell migration and cell proliferation. mir-21 regulates the ectopic expression of smad2 .'
    # text = u'transport of annexin 2 not only to dynamic actin-rich ruffles at the cell cortex but also to cytoplasmic and perinuclear vesicles.'
    doc_id = '99999999'
    rule_phase0_filename = '/home/leebird/Projects/nlputils/visual/uploads/rules_phase0.txt'
    rule_phase1_filename = '/home/leebird/Projects/nlputils/visual/uploads/rules_phase1.txt'
    rule_phase2_filename = '/home/leebird/Projects/nlputils/visual/uploads/rules_phase2.txt'
    fh0 = open(rule_phase0_filename, "r")
    rule0_lines = fh0.readlines()
    fh0.close()
    fh1 = open(rule_phase1_filename, "r")
    rule1_lines = fh1.readlines()
    fh1.close()
    fh2 = open(rule_phase2_filename, "r")
    rule2_lines = fh2.readlines()
    fh2.close()

    with open('/home/leebird/Projects/nlputils/utils/typing/test.json') as f:
        json_doc = json.load(f)
        for t in json_doc['entity'].values():
            t['entityType'] = t['entityType'].upper()
        text = json.dumps(json_doc)
        raw_doc = json_format.Parse(text, document_pb2.Document(), True)

    param_helper = ParamHelper(text, doc_id, rule0_lines, rule1_lines,
                               rule2_lines)

    # raw_doc = document_pb2.Document()
    edg_rules = edgRules_pb2.EdgRules()

    # param_helper.setDocProtoAttributes(raw_doc)
    param_helper.setRuleProtoAttributes(edg_rules)

    # Parse using Bllip parser.
    doc = parse_using_bllip(raw_doc, edg_rules)
    helper = DocHelper(doc)
    invalid_deps = constraint_args(helper, {'arg0': {document_pb2.Entity.GENE}})
    print(invalid_deps)
    propagate(helper, {'arg0': {document_pb2.Entity.GENE}}, invalid_deps)


if __name__ == '__main__':
    run()
