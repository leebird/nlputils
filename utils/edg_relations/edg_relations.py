from __future__ import unicode_literals, print_function
import sys
import codecs
import json
import uuid
from protolib.python import document_pb2, edgRules_pb2
from utils.helper import DocHelper
import shortuuid
from collections import defaultdict, namedtuple
import re

class EdgArg(object):
    def __init__(self, rule_id, arg_number, edge_name, token_index, head_noun, base_np, np, edg_type):
        self.rule_id = rule_id
        self.arg_number = arg_number
        self.edge_name = edge_name
        self.token_index = token_index
        self.head_noun = head_noun
        self.base_np = base_np
        self.np = np
        self.edg_type = edg_type

    def __repr__(self):
        return 'EdgArg('+ self.rule_id +  ", " + self.arg_number + ", " + self.head_noun + \
                        ", " + self.np + ", " +  ")" + "\n"

class EdgRelation(object):
    def __init__(self, name, trigger_index, trigger_head, trigger_phrase, args):
        self.name = name
        self.trigger_index = trigger_index
        self.trigger_head = trigger_head
        self.trigger_phrase = trigger_phrase
        self.args = args
        self.arg0s = list() 
        self.arg1s = list() 
        self.arg2s = list() 

    def __repr__(self):
        return 'EdgRelation(' + self.name + ", " +self.trigger_phrase + "\n" + \
                                "ARG0s :" + repr(self.arg0s) + "\n\n" + \
                                "ARG1s :" + repr(self.arg1s) + "\n\n" + \
                                "ARG2s :" + repr(self.arg2s) + "\n\n"

    def getEdgRelationNumArgsIndex(self):
        arg0s_set = set()
        arg1s_set = set()
        arg2s_set = set()
        for arg in self.arg0s:
            arg_key = arg.token_index
            arg0s_set.add(arg_key)
        for arg in self.arg1s:
            arg_key = arg.token_index
            arg1s_set.add(arg_key)
        for arg in self.arg2s:
            arg_key = arg.token_index
            arg2s_set.add(arg_key)
        if not arg0s_set:
            arg0s_set.add("NA")
        if not arg1s_set:
            arg1s_set.add("NA")
        if not arg2s_set:
            arg2s_set.add("NA")

        numb_args_list = list()
        numb_args_list = [[a0,a1,a2] for a0 in arg0s_set for a1 in arg1s_set for a2 in arg2s_set]
        
        return numb_args_list
 
    def getEdgRelationNumArgs(self):
        arg0s_set = set()
        arg1s_set = set()
        arg2s_set = set()
        for arg in self.arg0s:
            arg_key = arg.head_noun+"\t"+arg.base_np+"\t"+arg.np
            arg0s_set.add(arg_key)
        for arg in self.arg1s:
            arg_key = arg.head_noun+"\t"+arg.base_np+"\t"+arg.np
            arg1s_set.add(arg_key)
        for arg in self.arg2s:
            arg_key = arg.head_noun+"\t"+arg.base_np+"\t"+arg.np
            arg2s_set.add(arg_key)
        if not arg0s_set:
            arg0s_set.add("NA\tNA\tNA")
        if not arg1s_set:
            arg1s_set.add("NA\tNA\tNA")
        if not arg2s_set:
            arg2s_set.add("NA\tNA\tNA")

        numb_args_list = list()
        numb_args_list = [[a0,a1,a2] for a0 in arg0s_set for a1 in arg1s_set for a2 in arg2s_set]
        
        return numb_args_list 
        #toPrintRel = ["inv", "reg", "ass", "exp" , "cmp"]
        #if self.name in toPrintRel:
        #    print ("Relation Name: "+self.name)
        #    print ("Trigger: "+self.trigger_head+"\t"+self.trigger_phrase+"\n")
        #    for numb_args in numb_args_list:
        #        print ("Arg0: "+numb_args[0])
        #        print ("Arg1: "+numb_args[1])
        #        print ("Arg2: "+numb_args[2])
        #    print ("\n")


    def populateNumberedArgs(self):
        for arg in self.args:
            arg_number = arg.arg_number
            if arg_number == "arg0":
                self.arg0s.append(arg)
            elif arg_number == "arg1":
                self.arg1s.append(arg)
            elif arg_number == "arg2":
                self.arg2s.append(arg)
            else:
                arg_error = arg

class EdgRelations(object):
    def __init__(self, doc_id, sent_id):
        self.doc_id = doc_id
        self.sent_id = sent_id
        self.relations = list() 

    def __repr__(self):
        return str(self.doc_id) + "-" + str(self.sent_id) + "\n" + repr(self.relations)



    def setRelations(self, doc_helper, sentence, dependencies):
        doc_id = self.doc_id
        sent_id = self.sent_id
        relation_dict = {}
        vp_labels = ["VP", "ADVP", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        for dependency in dependencies:
            gov_index = dependency.gov_index
            dep_index = dependency.dep_index
            edge_name = dependency.relation
            rule_id = dependency.rule_id
           
            gov_head = doc_helper.doc.token[gov_index].word    
            #gov_next_head = doc_helper.doc.token[gov_index+1].word    
            #gov_next_next_head = doc_helper.doc.token[gov_index+2].word    
            dep_head = doc_helper.doc.token[dep_index].word
            gov_pos = doc_helper.doc.token[gov_index].pos    
            dep_pos = doc_helper.doc.token[dep_index].pos

            #pos_ignore_list = ["JJR", "JJ"]
            #es_ignore_list = ["than", "versus", "vs."]
            #jjr_ruleid_igore_list = ["cmp1_than_2", "cmp1_than_1", "cmp1_vs_1"]
            #dt_not_ignore_list = ["that", "those", "this"]
            #if gov_pos in pos_ignore_list and gov_next_head in es_ignore_list and rule_id in jjr_ruleid_igore_list and gov_next_next_head not in dt_not_ignore_list:
            #    #print ("Samir: " + gov_head + "\t" + dep_head + "\t" + edge_name + "\t" + rule_id)
            #    continue 
            gov_np = "NA"
            if gov_pos in vp_labels:
                gov_np = doc_helper.getTokenVG(sentence, gov_index)
            else:
                gov_np = doc_helper.getTokenNP(sentence, gov_index)
            dep_np = "NA" 
            if dep_pos in vp_labels:
                dep_np = doc_helper.getTokenVG(sentence, dep_index)
            else:
                dep_np = doc_helper.getTokenNP(sentence, dep_index)
            dep_base_np = doc_helper.getTokenBaseNP(sentence, dep_index)
            #print ("Samir: " + gov_head + "\t" + dep_head + "\t" + edge_name + "\t" + rule_id)
            relName = "NA"
            arg_number = "arg3"
            if re.search(r'arg[0-9]+_',edge_name):
                tokens = edge_name.split("_")
                relName = tokens[1]
                arg_number = tokens[0]
            #new_trigger = TriggerTuple(rel_name = relName, trigger_index = gov_index)
            new_trigger = relName + "\t" + str(gov_index)
            if new_trigger in relation_dict:
                relation = relation_dict[new_trigger]
                new_arg = EdgArg(rule_id, arg_number, edge_name, dep_index, dep_head, dep_base_np, dep_np, "NONE")
                relation.args.append(new_arg)
            else:
                new_arg = EdgArg(rule_id, arg_number, edge_name, dep_index, dep_head, dep_base_np, dep_np, "NONE")
                relation = EdgRelation(relName, gov_index, gov_head, gov_np, [new_arg])
                self.relations.append(relation)
                relation_dict[new_trigger] = relation

        for relation in self.relations:
            relation.populateNumberedArgs()
