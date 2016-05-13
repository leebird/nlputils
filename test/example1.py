# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protolib.python import document_pb2, rpc_pb2
from utils.rpc import grpcapi
import collections
import re
from utils.helper import DocHelper

def process_one_document(request):
    # Use biotm2 as server.
    interface = grpcapi.GrpcInterface(host='128.4.20.169', port=8902)
    #interface = grpcapi.GrpcInterface(host='localhost')
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


def split_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.SPLIT
    request.document.extend([doc])
    return process_one_document(request)

def parse_rules(rule_filename):
    fh = open(rule_filename, "r")
    lines = fh.readlines()
    lines.append("RuleID : END\n")
    RuleTuple = collections.namedtuple('RuleTuple', 'ident regex actions')
    ActionTuple = collections.namedtuple('ActionTuple', 'govNode depNode label')
    #############parsing file and populating
    ruleID = "NA"
    ruleRegex = "NA"
    actionsList = list()
    ruleCounter = 0
    ruleList = list()
    for line in lines:
        line = line.rstrip()
        if line == "":
            continue
        tokens = re.split(' : ',line,1)
        lineIdent = tokens[0]
        lineStr = tokens[1]
        if lineIdent == "RuleID":
            if ruleID != "NA":
                new_rule = RuleTuple(ident = ruleID, regex = ruleRegex, actions = actionsList)
                ruleList.append(new_rule)
                ruleRegex = "NA"
                actionsList = list()
            ruleID = lineStr
            ruleCounter = ruleCounter + 1
        if re.search(r'^Cond_[0-9]+$',lineIdent):
            if ruleRegex == "NA":
                ruleRegex = lineStr
            else:
                ruleRegex = ruleRegex + " : " + lineStr
        if re.search(r'^Action_[0-9]+$',lineIdent):
            actionStrTokens = re.split(' >> ',lineStr,2)
            action_tuple = ActionTuple(govNode = actionStrTokens[0], depNode = actionStrTokens[2], label = actionStrTokens[1])
            actionsList.append(action_tuple)
    fh.close()
    return ruleList 

def run():
    text = u'Expression of mir-21 and mir-132  directly mediates cell migration . mir-21 mediates cell migration and proliferation. mir-21 seems to mediate apoptosis. mir-21 is  involved in cellular processes, such as cell migration and cell proliferation. mir-21 regulates the ectopic expression of smad2 .'
    raw_doc = document_pb2.Document()
    #raw_doc.rules.extend(ruleList)
    raw_doc.doc_id = '26815768'
    raw_doc.text = text
    ruleList = parse_rules(sys.argv[1])
    #print (ruleList)   
 
    for rule in ruleList:
        ruleID = rule.ident
        ruleRegex = rule.regex
        raw_doc.rules.add(ident = ruleID, regex = ruleRegex)
    ruleCounter = 0
    for rule in ruleList:
        actionsList = rule.actions
        for action in actionsList:
            govNode = action.govNode
            depNode = action.depNode
            label = action.label
            raw_doc.rules[ruleCounter].actions.add(gov_node = govNode, dep_node = depNode, edge_label = label)
            #print (raw_doc)
        ruleCounter = ruleCounter + 1
    
    # Parse using Bllip parser.
    #print (ruleList)
    # Parse using Bllip parser.
    result = parse_using_bllip(raw_doc)
    helper = DocHelper(result)
    sentences = result.sentence
    for sentence in sentences:
        print (helper.text(sentence))
        for depExtra in sentence.dependency_extra:
            print(helper.printExtraDependency(sentence,depExtra))
        print("===============================")
    #print(result)

if __name__ == '__main__':
    run()
