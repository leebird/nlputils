from __future__ import unicode_literals, print_function
import sys
import codecs
import json
import uuid
from protolib.python import document_pb2, edgRules_pb2
import shortuuid
from collections import defaultdict, namedtuple
import re

class ParamHelper(object):
    def __init__(self, doc_txt, doc_id, rule0_lines, rule1_lines, rule2_lines):
        self.doc_txt = doc_txt
        self.doc_id = doc_id
        self.rule0_lines = rule0_lines
        self.rule1_lines = rule1_lines
        self.rule2_lines = rule2_lines
        self.rule_lines = list() 
        self.rule_lines.extend(rule0_lines + rule1_lines + rule2_lines) 

    def setDocProtoAttributes(self,doc_proto):
        doc_proto.doc_id = self.doc_id
        doc_proto.text = self.doc_txt


    def setRuleProtoAttributes(self,edg_rules_proto):
        ruleList = self.parse_rules()
        for rule in ruleList:
            ruleID = rule.ident
            ruleRegex = rule.regex
            edg_rules_proto.rules.add(ident = ruleID, regex = ruleRegex)
        ruleCounter = 0
        for rule in ruleList:
            actionsList = rule.actions
            for action in actionsList:
                govNode = action.govNode
                depNode = action.depNode
                label = action.label
                edg_rules_proto.rules[ruleCounter].actions.add(gov_node = govNode, dep_node = depNode, edge_label = label)
            ruleCounter = ruleCounter + 1
    
    def parse_rules(self):
        #fh = open(rule_filename, "r")
        #lines = fh.readlines()
        lines = self.rule_lines 
        lines.append("RuleID : END\n")
        RuleTuple = namedtuple('RuleTuple', 'ident regex actions')
        ActionTuple = namedtuple('ActionTuple', 'govNode depNode label')
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
            if re.search(r'^#',line):
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
        return ruleList

