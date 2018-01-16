from __future__ import unicode_literals, print_function
import codecs
import json
from collections import defaultdict, namedtuple
import shortuuid
import glog
import re
from protolib.python import document_pb2
from ..brat import parser
from .range_helper import RangeHelper

class DocHelper(object):
    def __init__(self, doc):
        self.doc = doc

    def char_range(self, sentence):
        # token_start = sentence.token_start
        # token_end = sentence.token_end
        # char_start = self.doc.token[token_start].char_start
        # char_end = self.doc.token[token_end].char_end
        # return char_start, char_end
        return sentence.char_start, sentence.char_end

    def char_range_in_sentence(self, proto_obj, sentence):
        sent_char_start, _ = self.char_range(sentence)
        return proto_obj.char_start - sent_char_start, \
               proto_obj.char_end - sent_char_start

    def text(self, proto_obj):
        char_start, char_end = -1, -1
        if type(proto_obj) == document_pb2.Sentence:
            char_start, char_end = self.char_range(proto_obj)
        elif type(proto_obj) == document_pb2.Sentence.Constituent:
            token_start = self.doc.token[proto_obj.token_start]
            token_end = self.doc.token[proto_obj.token_end]
            char_start = token_start.char_start
            char_end = token_end.char_end
        elif type(proto_obj) == document_pb2.Entity or type(proto_obj) == document_pb2.Token:
            char_start, char_end = proto_obj.char_start, proto_obj.char_end

        return self.doc.text[char_start: char_end + 1]

    def getConstituentIndexFromTokenIndex(self, sentence, index):
        constituents = sentence.constituent
        for constituent in constituents:
            childrens = constituent.children
            if not childrens:
                label = constituent.label
                token_start = constituent.token_start
                token_end = constituent.token_end
                if index == token_start and index == token_end:
                    return constituent.index

    def getParentNPIndexFromLeafTokenIndex(self, sentence, index):
        constituentIndex = self.getConstituentIndexFromTokenIndex(sentence,
                                                                  index)
        constituent = sentence.constituent[constituentIndex]
        parentConstIndex = constituent.parent
        childConst = constituent
        constituent = sentence.constituent[parentConstIndex]
        label = constituent.label
        vp_labels = ["VP", "ADVP", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        np_labels = ["NN", "NP", "NNS", "FW"]
        isVP = 0
        constituentLabelsToCheck = np_labels
        if label in vp_labels:
            isVP = 1
            constituentLabelsToCheck = vp_labels
        while (label in constituentLabelsToCheck):
            # if label == "NP":
            # return constituent.index
            crossedCC = self.constituentContainsCC(sentence, constituent.index)
            if crossedCC == 1:
                return childConst.index
            constituentIndex = constituent.index
            parentConstIndex = constituent.parent
            childConst = constituent
            constituent = sentence.constituent[parentConstIndex]
            label = constituent.label
        return childConst.index
    
    def getParentVPIndexFromLeafTokenIndex(self, sentence, index):
        constituentIndex = self.getConstituentIndexFromTokenIndex(sentence,
                                                                  index)
        constituent = sentence.constituent[constituentIndex]
        parentConstIndex = constituent.parent
        childConst = constituent
        constituent = sentence.constituent[parentConstIndex]
        label = constituent.label
        vp_labels = ["VP", "ADVP", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
        while (label in vp_labels):
            # if label == "NP":
            # return constituent.index
            constituentIndex = constituent.index
            parentConstIndex = constituent.parent
            childConst = constituent
            constituent = sentence.constituent[parentConstIndex]
            label = constituent.label
        return childConst.index

    def constituentContainsCC(self, sentence, index):
        constituent = sentence.constituent[index]
        children = constituent.children
        for child in children:
            cLabel = sentence.constituent[child].label
            if cLabel == "CC":
                return 1
            if cLabel == ",":
                return 1
        return 0

    def getParentNPIndexFromLeafTokenIndex1(self, sentence, index):
        constituentIndex = self.getConstituentIndexFromTokenIndex(sentence,
                                                                  index)
        constituent = sentence.constituent[constituentIndex]
        parentConstIndex = constituent.parent
        constituent = sentence.constituent[parentConstIndex]
        label = constituent.label
        while (label == "NP" or label == "NN" or label == "NNS" or label == "FW"):
            if label == "NP":
                return constituent.index
            constituentIndex = constituent.index
            parentConstIndex = constituent.parent
            constituent = sentence.constituent[parentConstIndex]
            label = constituent.label
        return constituentIndex

    def printExtraDependency(self, sentence, depExtra):
        govIndex = depExtra.gov_index
        depIndex = depExtra.dep_index
        relation = depExtra.relation
        ruleID = depExtra.rule_id

        govNode = self.doc.token[govIndex].word
        depNode = self.doc.token[depIndex].word

        govParentNPIndex = self.getParentNPIndexFromLeafTokenIndex(sentence,
                                                                   govIndex)
        depParentNPIndex = self.getParentNPIndexFromLeafTokenIndex(sentence,
                                                                   depIndex)

            
        govParentNP = self.printConstituent(sentence, govParentNPIndex)
        depParentNP = self.printConstituent(sentence, depParentNPIndex)

        return "Rule ID: " + ruleID + "\nGov: " + govNode + "\t" + govParentNP + "\nRelEdge: " + relation + "\nDep: " + depNode + "\t" + depParentNP + "\n";

    def printEmptyExtraDependencyAnalysis(self, sentence):
        return "NA" + "\t" + "NA" + "\t" + "-1" + "\t" + "NA" + "\t" + "NA" + "\t" \
                                        + "-1" + "\t" + "NA" + "\t" + "NA" 
    def printExtraDependencyAnalysis(self, sentence, depExtra):
        govIndex = depExtra.gov_index
        depIndex = depExtra.dep_index
        relation = depExtra.relation
        ruleID = depExtra.rule_id
       
        text = self.text(sentence)
        govNode = self.doc.token[govIndex]
        depNode = self.doc.token[depIndex]
        govNodePos = govNode.pos
        depNodePos = depNode.pos
        govNodeWord = govNode.word
        depNodeWord = depNode.word
        govParentNPIndex = self.getParentNPIndexFromLeafTokenIndex(sentence,
                                                                   govIndex)
        depParentNPIndex = self.getParentNPIndexFromLeafTokenIndex(sentence,
                                                                   depIndex)
        if relation == "member_collection":
            govParentNPIndex = self.getParentNPIndexFromLeafTokenIndex1(sentence,
                                                                   govIndex)
        govParentNP = self.printConstituentTokens(sentence, govParentNPIndex)
        depParentNP = self.printConstituentTokens(sentence, depParentNPIndex)
        sentenceTagged = self.tag_tokens_in_sentence(sentence, govNode, depNode)
        return ruleID + "\t" + relation + "\t" + str(govIndex) + "\t" + govNodeWord + "\t" + govParentNP.strip()+ "\t" \
                                        + str(depIndex) + "\t" + depNodeWord + "\t" + depParentNP.strip()


    def getTokenBaseNP(self, sentence, token_index):
        base_parentNPIndex = self.getParentNPIndexFromLeafTokenIndex1(sentence, token_index)
        base_parentNP = self.printConstituentTokens(sentence, base_parentNPIndex)
        return base_parentNP.strip()
    
    def getTokenNP(self, sentence, token_index):
        parentNPIndex = self.getParentNPIndexFromLeafTokenIndex(sentence, token_index)
        parentNP = self.printConstituentTokens(sentence, parentNPIndex)
        return parentNP.strip()

    def getTokenVG(self, sentence, token_index):
        parentVPIndex = self.getParentVPIndexFromLeafTokenIndex(sentence, token_index)
        parentVG = self.printConstituentTokens(sentence, parentVPIndex)
        return parentVG.strip()
    
    def printConstituent(self, sentence, constituentIndex):
        constituent = sentence.constituent[constituentIndex]
        label = constituent.label
        childrens = constituent.children
        # returnStr = "( " + label
        if not childrens:
            returnStr = " " + label
            # returnStr = returnStr + " )"
            return returnStr
        else:
            returnStr = "( " + label
            for children in childrens:
                returnStr = returnStr + self.printConstituent(sentence,
                                                              children)
            returnStr = returnStr + " )"
            return returnStr

    def printConstituentTokens(self, sentence, constituentIndex):
        isVP = 0
        constituent = sentence.constituent[constituentIndex]
        label = constituent.label
        childrens = constituent.children
        if label == "VP":
            isVP = 1
        if not childrens:
            returnStr = " " + label
            return returnStr
        else:
            returnStr = "";
            for children in childrens:
                childLabel = sentence.constituent[children].label
                if isVP == 1 and (childLabel == "NP" or childLabel == "PP"):
                    returnStr = returnStr + self.printConstituentTokens(sentence,children)
                    #returnStr = returnStr
                else:
                    returnStr = returnStr + self.printConstituentTokens(sentence,children)
            return returnStr

    def token(self, proto_obj):
        return self.doc.token[proto_obj.token_start:proto_obj.token_end + 1]

    def token_of_char_offset(self, offset):
        for token in self.doc.token:
            if token.char_start <= offset <= token.char_end:
                return token

    def entity_with_offset(self, char_start, char_end):
        entities = []
        for t in self.doc.entity.values():
            if t.char_start == char_start and t.char_end == char_end:
                entities.append(t)
        return entities

    @staticmethod
    def all_attribute(proto_obj, key):
        attrs = []
        for attr in proto_obj.attribute:
            if attr.key == key:
                attrs.append(attr.value)
        return attrs

    @staticmethod
    def entity_all_id(entity, source):
        ids = []
        for entity_id in entity.entity_id:
            if entity_id.source == source:
                ids.append(entity_id.id_string)
        return ids

    @staticmethod
    def entity_first_id(entity, source):
        for entity_id in entity.entity_id:
            if entity_id.source == source:
                return entity_id.id_string

    def relation_argument(self, relation):
        args = defaultdict(list)
        for arg in relation.argument:
            if arg.entity_duid not in self.doc.entity:
                glog.warning('{}: Entity {} in relation {} not found in entity list'.format(
                    self.doc.doc_id, arg.entity_duid, relation.duid))
                continue
            args[arg.role].append(self.doc.entity[arg.entity_duid])
        return args

    def entity_in_sentence(self, sentence):
        # token_start = sentence.token_start
        # token_end = sentence.token_end

        char_start = sentence.char_start
        char_end = sentence.char_end
        entities = []
        for entity in self.doc.entity.values():
            if entity.char_start >= char_start and entity.char_end <= char_end:
                entities.append(entity)

        return entities

    def entity_sentence_index(self, entity):
        index = set()
        for sentence in self.doc.sentence:
            if sentence.char_start <= entity.char_start and \
                            sentence.char_end >= entity.char_end:
                index.add(sentence.index)
        return index

    def entity_head_token(self, graph, entity):
        if type(entity) == document_pb2.Token:
            # If entity itself is a token.
            return entity

        tokens = self.token(entity)
        token_ids = {t.index for t in tokens}
        # If the last token is a punctuation, it may not have heads.
        # So in the following codes we update the head with token that
        # has heads.

        head = tokens[-1].index

        # Find head token.
        if len(tokens) > 1:
            for token in tokens:
                heads = graph.get_gov(token.index)
                # if len(heads) > 0:
                #    head = token
                for gov in heads:
                    if gov in token_ids:
                        head = gov
                        break

        return self.doc.token[head]

    def has_entity_type(self, entity_type):
        for entity_id, entity in self.doc.entity.items():
            if entity.entity_type == entity_type:
                return True
        return False

    def entity_type(self, entity_type):
        entity_list = []
        for entity_id, entity in self.doc.entity.items():
            if entity.entity_type == entity_type:
                entity_list.append(entity)
        return entity_list

    def del_entity_type(self, entity_type):
        entity_list = []
        for entity_id, entity in self.doc.entity.items():
            if entity.entity_type == entity_type:
                entity_list.append(entity_id)

        for entity_id in entity_list:
            del self.doc.entity[entity_id]

    def char_offset_to_entity(self, char_start, char_end):
        entities = []
        for entity_id, entity in self.doc.entity.items():
            if RangeHelper.overlap((entity.char_start, entity.char_end),
                                   (char_start, char_end)):
                entities.append(entity)
        return entities

    def entity_equiv(self, entity):
        entity_id = entity.duid
        equivs = set()
        for relation_id, relation in self.doc.relation.items():
            if relation.relation_type != 'Equiv':
                continue
            arg_entity_id = [arg.entity_duid for arg in relation.argument]
            if entity_id in arg_entity_id:
                arg_entity_id.remove(entity_id)
                equivs |= set(arg_entity_id)
        equiv_entities = [e for e in self.doc.entity.values() if
                          e.duid in equivs]
        return equiv_entities

    def add_entity(self, prefix=None, duid=None):
        if duid is None:
            while True:
                # duid = uuid.uuid4().hex
                # Use shorteuuid and length 4 uuid.
                duid = shortuuid.ShortUUID().random(length=4)

                if prefix is not None:
                    duid = prefix + duid

                if duid not in self.doc.entity:
                    break

        assert duid is not None
        assert duid not in self.doc.entity
        entity = self.doc.entity.get_or_create(duid)
        entity.duid = duid
        return entity

    def add_relation(self, relation_type, prefix=None, duid=None):
        if duid is None:
            while True:
                # duid = uuid.uuid4().hex
                duid = shortuuid.ShortUUID().random(length=4)

                if prefix is not None:
                    duid = prefix + duid

                if duid not in self.doc.relation:
                    break

        assert duid is not None
        assert duid not in self.doc.relation

        relation = self.doc.relation.get_or_create(duid)
        relation.duid = duid
        relation.relation_type = relation_type
        return relation

    def fill_entity_using_char_offset(self, entity):
        for sentence in self.doc.sentence:
            if sentence.char_start <= entity.char_start and \
                            sentence.char_end >= entity.char_end:
                entity.sentence_index = sentence.index
                break

        found_token_range = False
        for token in self.doc.token:
            if token.char_start <= entity.char_start <= token.char_end:
                entity.token_start = token.index
            if token.char_start <= entity.char_end <= token.char_end:
                entity.token_end = token.index
                found_token_range = True
                break

        if not found_token_range:
            entity.token_start = -1
            entity.token_end = -1
            # entity.sentence_index = -1
            # glog.warning('Entity token range not found: {} {} {}'.format(
            #     self.doc.doc_id, entity.duid, self.text(entity)))
            return

        assert entity.token_start <= entity.token_end, (str(entity),
                                                        self.text(entity),
                                                        str(self.doc.doc_id))

    def fill_all_entity_using_char_offset(self):
        for entity_id, entity in self.doc.entity.items():
            self.fill_entity_using_char_offset(entity)

    def dependency_for_brat(self, sentence):
        count = 1
        entities = []
        sent_text = self.text(sentence)
        index2tid = {}
        for token in self.token(sentence):
            tid = 'T' + str(count)
            char_start, char_end = self.char_range_in_sentence(token, sentence)
            pos = token.pos
            entities.append([tid, pos, [[char_start, char_end + 1]]])
            index2tid[token.index] = tid
            count += 1

        count = 1
        relations = []
        for dep_relation in sentence.dependency:
            if re.search(r'_opn',dep_relation.relation):
                continue
            if re.search(r'arg',dep_relation.relation):
                continue
            if re.search(r'is_a',dep_relation.relation):
                continue
            if re.search(r'added',dep_relation.relation):
                continue
            if re.search(r'_null',dep_relation.relation):
                continue
            rid = 'R' + str(count)
            dep = dep_relation.dep_index
            gov = dep_relation.gov_index
            relation = dep_relation.relation
            if relation == 'root':
                continue
            dep_tid = index2tid[dep]
            gov_tid = index2tid[gov]
            relations.append([rid, relation, [['Governer', gov_tid],
                                              ['Dependent', dep_tid]]])
            count += 1

        return {
            'text': sent_text,
            'entities': entities,
            'relations': relations
        }

    def dependency_extra_for_brat(self, sentence):
        count = 1
        entities = []
        sent_text = self.text(sentence)
        index2tid = {}
        for token in self.token(sentence):
            tid = 'T' + str(count)
            char_start, char_end = self.char_range_in_sentence(token, sentence)
            pos = token.pos
            entities.append([tid, pos, [[char_start, char_end + 1]]])
            index2tid[token.index] = tid
            count += 1

        count = 1
        relations = []
        duplicateCheckSet = dict()
        for dep_relation in sentence.dependency_extra:
            if re.search(r'_opn',dep_relation.relation):
                continue
            duplicateCheckKey = str(dep_relation.dep_index)+":"+str(dep_relation.gov_index)+":"+dep_relation.relation
            if duplicateCheckKey in duplicateCheckSet:
                continue
            else:
                duplicateCheckSet[duplicateCheckKey] = 1
            rid = 'R' + str(count)
            dep = dep_relation.dep_index
            gov = dep_relation.gov_index
            relation = dep_relation.relation

            dep_tid = index2tid[dep]
            gov_tid = index2tid[gov]
            relations.append([rid, relation, [['Governer', gov_tid],
                                              ['Dependent', dep_tid]]])
            count += 1

        return {
            'text': sent_text,
            'entities': entities,
            'relations': relations
        }

    @staticmethod
    def has_conjunction(sentence, constituent):
        for child in constituent.children:
            if sentence.constituent[child].label == 'CC':
                return True
        return False

    @staticmethod
    def load_from_brat_file(doc_id, text_file, annotation_file):
        doc = document_pb2.Document()
        doc.doc_id = doc_id
        helper = DocHelper(doc)
        with codecs.open(text_file, 'r', encoding='utf8') as f:
            # Replace newlines with spaces.
            text = f.read().replace('\n', ' ')
            doc.text = text

        with codecs.open(annotation_file, 'r', encoding='utf8') as f:
            entities, events, relations = [], [], []

            for line in f:
                line = line.strip('\r\n')

                assert len(line.strip()) > 0
                assert line[0] == 'T' or line[0] == 'E' or \
                       line[0] == 'R' or line[0] == '*' or \
                       line[0] == 'M' or line[0] == 'A'

                if line[0] == 'T':
                    entity_id, entity_text, entity_type, entity_start, entity_end \
                        = parser.parse_entity(line)

                    entity = helper.add_entity(duid=entity_id)
                    entity.char_start = entity_start
                    entity.char_end = entity_end - 1
                    entity.entity_type = entity_type

                elif line[0] == 'E':
                    events.append(parser.parse_event(line))
                elif line[0] == 'R' or line[0] == '*':
                    relations.append(parser.parse_relation(line))

            for eid, etype, trigger_id, arguments, attrs in events:
                event = helper.add_relation(relation_type=etype, duid=eid)
                trigger = event.argument.add()
                trigger.entity_duid = trigger_id
                trigger.role = 'Trigger'
                for role, arg_id in arguments:
                    arg = event.argument.add()
                    arg.role = role
                    arg.entity_duid = arg_id

                if attrs is not None:
                    for key, values in attrs.items():
                        for value in values:
                            attr = event.attribute.add()
                            attr.key = key
                            attr.value = value

            for rid, rtype, arguments, attrs in relations:
                if rid.startswith('R'):
                    relation = helper.add_relation(relation_type=rtype, duid=rid)
                else:
                    relation = helper.add_relation(relation_type=rtype)
                for role, arg_id in arguments:
                    arg = relation.argument.add()
                    arg.role = role
                    arg.entity_duid = arg_id

                if attrs is not None:
                    for key, values in attrs.items():
                        for value in values:
                            attr = relation.attribute.add()
                            attr.key = key
                            attr.value = value
        return doc

    def dump_to_brat_file(self, text_file, annotation_file,
                          dump_sentence=False):
        with codecs.open(text_file, 'w', encoding='utf8') as f:
            f.write(self.doc.text)

        with codecs.open(annotation_file, 'w', encoding='utf8') as f:
            entity_line = '{0}\t{1} {2} {3}\t{4}\n'
            if dump_sentence:
                start_id = len(self.doc.entity) + 50
                for sent in self.doc.sentence:
                    sid = 'T' + str(start_id)
                    sent_start, sent_end = self.char_range(sent)
                    line = entity_line.format(sid, 'Sentence',
                                              sent_start,
                                              sent_end + 1,
                                              self.text(sent))
                    f.write(line)
                    start_id += 1
            
            trigger_types = {}
            for rel_id, rel in self.doc.relation.items():
                arguments = defaultdict(list)
                for arg in rel.argument:
                    arguments[arg.role].append(arg.entity_duid)

                if 'Trigger' in arguments:
                    for trigger in arguments['Trigger']:
                        trigger_types[trigger] = rel.relation_type

            # start_id = 1
            for entity_id, entity in self.doc.entity.items():
                # Note that the entity id may not be of brat format, e.g., T1.
                # sid = 'T' + str(start_id)
                # start_id += 1
                entity_type = entity.entity_type
                if entity_type == 'TRIGGER' and entity.duid in trigger_types:
                    entity_type = trigger_types[entity.duid]
                entity_text = self.text(entity)
                line = entity_line.format(entity.duid,
                                          # sid,
                                          entity_type,
                                          entity.char_start,
                                          entity.char_end + 1,
                                          entity_text)
                f.write(line)

            event_line = '{0}\t{1}:{2} {3}\t{4}'
            rel_line = '{0}\t{1} {2}\t{3}'
            for er_id, event_or_rel in self.doc.relation.items():
                arguments = defaultdict(list)
                for arg in event_or_rel.argument:
                    arguments[arg.role].append(arg.entity_duid)

                attributes = defaultdict(list)
                for attr in event_or_rel.attribute:
                    attributes[attr.key].append(attr.value)
                attributes_json = ''
                if len(attributes) > 0:
                    attributes_json = json.dumps(attributes)

                all_args = []
                for role, args in arguments.items():
                    if role == 'Trigger':
                        continue
                    for arg in args:
                        one_arg = '{}:{}'.format(role, arg)
                        all_args.append(one_arg)

                if len(arguments['Trigger']) > 0:
                    assert len(arguments['Trigger']) == 1

                if event_or_rel.duid.startswith('E'):
                    assert len(arguments['Trigger']) == 1
                    line = event_line.format(event_or_rel.duid,
                                             event_or_rel.relation_type,
                                             arguments['Trigger'][0],
                                             ' '.join(all_args),
                                             attributes_json).strip()
                    f.write(line+'\n')
                else:
                    line = rel_line.format(event_or_rel.duid,
                                           event_or_rel.relation_type,
                                           ' '.join(all_args),
                                           attributes_json).strip()
                    f.write(line+'\n')

    def base_phrase_and_head(self):
        base_phrase = []
        for cst in self.doc.constituency:
            overlap = False
            for phrase in sorted(base_phrase,
                                 key=lambda a: (a.char_end - a.char_start),
                                 reverse=True):
                if RangeHelper.overlap((cst.char_start, cst.char_end),
                                       (phrase.char_start, phrase.char_end)):
                    overlap = True
                    break
            if not overlap:
                base_phrase.append(cst)

        return sorted(base_phrase, key=lambda a: a.char_start)

    def get_base_noun_phrase_head(self, constituents, token):
        # Return token's base NP's head.
        min_range = float('inf')
        head = token.index
        for cst in constituents:
            if not cst.label.startswith('NP'):
                continue
            if cst.token_start <= token.index <= cst.token_end:
                if cst.token_end - cst.token_start + 1 < min_range:
                    head = cst.head_token_index
                    min_range = cst.token_end - cst.token_start + 1
        return self.doc.token[head]

    def get_max_noun_phrase(self, constituents, token):
        # Return token's base NP's head.
        head = token.index
        basic_cst = None
        for cst in constituents:
            if len(cst.children) == 0:
                # Skip text node.
                continue
            if cst.token_start == head == cst.token_end:
                basic_cst = cst

        if basic_cst is not None:
            curr = basic_cst
            while True:
                if curr.parent == curr.index:
                    break
                parent = constituents[curr.parent]
                if not parent.label.startswith('N') and not parent.label.startswith('J') and not parent.label.startswith('P'):
                    break
                curr = parent

            if curr is not None and curr.label.startswith('N'):
                return curr

    def get_noun_phrase_head(self, constituents, token):
        # Return token's largest NP's head.
        # E.g., full name (short name) cell, cell is the head.
        min_range = float('inf')
        min_np = None
        for cst in constituents:
            if not cst.label.startswith('NP'):
                continue
            if cst.token_start <= token.index <= cst.token_end:
                if cst.token_end - cst.token_start + 1 < min_range:
                    min_np = cst

        if min_np is not None:
            curr_np = min_np
            max_np = min_np
            while True:
                parent = curr_np.parent
                if parent == 0:
                    break
                parent_cp = constituents[parent]

                if (parent_cp.label.startswith('NP') or
                    parent_cp.label == 'PRN'):
                    curr_np = parent_cp
                else:
                    break

                if parent_cp.label.startswith('NP'):
                    max_np = parent_cp

            return self.doc.token[max_np.head_token_index]

    def get_noun_phrase_head_by_dependency(self, graph, token, trigger):
        head = token.index
        visited = {head}
        while True:
            govs = graph.dep_to_gov[head]
            if len(govs) == 0:
                break

            should_continue = True
            for gov, relation in govs:
                if not self.doc.token[gov].pos.startswith('N'):
                    should_continue = False
                if relation == 'root':
                    should_continue = False
                if gov == trigger.index:
                    should_continue = False
                if gov in visited:
                    should_continue = False
                visited.add(gov)

            if not should_continue:
                break

            for gov, relation in govs:
                head = gov

        return self.doc.token[head]

    def tag_tokens_in_sentence(self, sentence, token1, token2):
        text = self.text(sentence)
        slices = []
        entities = list()
        entities.append(token1)
        entities.append(token2)
        start = 0
        for entity in sorted(entities, key=lambda a: a.char_start):
            char_start, char_end = self.char_range_in_sentence(entity, sentence)
            slices.append(text[start:char_start])
            slices.append("[")
            slices.append(text[char_start:char_end + 1])
            slices.append("]")
            start = char_end + 1

        slices.append(text[start:])
        return ''.join(slices)

    def naive_tag_entity_in_sentence(self, sentence, entities):
        def close_tag(entity):
            return '</{0}>'.format(entity.entity_type)

        def open_tag(entity):
            return '<{0}>'.format(entity.entity_type)

        text = self.text(sentence)
        slices = []
        start = 0
        for entity in sorted(entities, key=lambda a: a.char_start):
            char_start, char_end = self.char_range_in_sentence(entity, sentence)
            slices.append(text[start:char_start])
            slices.append(open_tag(entity))
            slices.append(text[char_start:char_end + 1])
            slices.append(close_tag(entity))
            start = char_end + 1

        slices.append(text[start:])
        return ''.join(slices)

    def smart_tag_entity_in_sentence(self, sentence, entities):
        # Attributes start and end are offsets of the entity, not the tag's position.
        Tag = namedtuple('Tag', ['tag', 'start', 'end', 'type'])

        def get_tag(entity, sentence):
            char_start, char_end = self.char_range_in_sentence(entity, sentence)
            # Note char_end is offset of the last character of the entity.
            open_tag = Tag(entity.entity_type, char_start, char_end + 1, 'open')
            close_tag = Tag(entity.entity_type, char_start, char_end + 1, 'close')
            return open_tag, close_tag

        text = self.text(sentence)
        tags = []

        # Get tags with start and end char-level offset.
        for entity in entities:
            open_tag, close_tag = get_tag(entity, sentence)
            tags.append(open_tag)
            tags.append(close_tag)
        return self.tag_tags_in_text(text, tags)

    def smart_tag_entity_in_text(self, text, entities):
        # Attributes start and end are offsets of the entity, not the tag's position.
        Tag = namedtuple('Tag', ['tag', 'start', 'end', 'type'])

        def get_tag(entity):
            # Note char_end is offset of the last character of the entity.
            open_tag = Tag(entity.entity_type, entity.char_start, entity.char_end + 1, 'open')
            close_tag = Tag(entity.entity_type, entity.char_start, entity.char_end + 1, 'close')
            return open_tag, close_tag

        tags = []

        # Get tags with start and end char-level offset.
        for entity in entities:
            open_tag, close_tag = get_tag(entity)
            tags.append(open_tag)
            tags.append(close_tag)

        return self.tag_tags_in_text(text, tags)

    def tag_tags_in_text(self, text, tags):
        def compare_tag(tag_1, tag_2):
            if tag_1.type == tag_2.type:
                if tag_1.type == 'open':
                    # If two open tags' start positions are the same,
                    # the one with larger end position should be the first.
                    if tag_1.start == tag_2.start:
                        return -(tag_1.end - tag_2.end)
                    else:
                        return tag_1.start - tag_2.start
                else:
                    # If two close tags' end position are the same,
                    # the one with larger start position should be the first.
                    if tag_1.end == tag_2.end:
                        return -(tag_1.start - tag_2.start)
                    else:
                        return tag_1.end - tag_2.end
            elif tag_1.type == 'open' and tag_2.type == 'close':
                # Compare exact positions of the two tags.
                return tag_1.start - tag_2.end
            elif tag_1.type == 'close' and tag_2.type == 'open':
                return tag_1.end - tag_2.start
            else:
                raise ValueError('Unknown smart tagging error.')

        tags = sorted(tags, cmp=compare_tag)
        start = 0
        open_tags = []
        slices = []
        for tag in tags:
            if tag.type == 'open':
                open_tags.append(tag)
                slices.append(text[start:tag.start])
                slices.append('<{0}>'.format(tag.tag))
                start = tag.start
            else:
                if len(open_tags) == 0:
                    raise ValueError('Unmatched ppen and close tag:', '_EMPTY_',
                                     tag.tag)
                open_tag = open_tags.pop()
                if open_tag.tag != tag.tag:
                    raise ValueError('Unmatched ppen and close tag:',
                                     open_tag.tag, tag.tag)
                slices.append(text[start:tag.end])
                slices.append('</{0}>'.format(tag.tag))
                start = tag.end

        if len(open_tags) > 0:
            raise ValueError('Non-empty open tags at the end')

        slices.append(text[start:])
        return ''.join(slices)

    def tag_entity_in_sentence(self, sentence, entities):
        entities = [t for t in entities if t.sentence_index == sentence.index]
        try:
            tagged = self.smart_tag_entity_in_sentence(sentence, entities)
        except Exception:
            tagged = self.naive_tag_entity_in_sentence(sentence, entities)

        return tagged

    def has_overlap_entity(self, mask_duids=None):
        entities = self.doc.entity.values()
        if mask_duids is not None:
            entities = [t for t in self.doc.entity.values() if t.duid in mask_duids]
        for entity_1 in entities:
            for entity_2 in entities:
                if entity_1.duid == entity_2.duid:
                    continue
                if RangeHelper.char_range_overlap(entity_1, entity_2):
                    # print(entity_1, entity_2)
                    # print(self.text(entity_1), self.text(entity_2))
                    return True
        return False

    def mask_entity(self, mask_duids=None):
        if self.has_overlap_entity():
            raise ValueError('Overlapped entities: ' + self.doc.doc_id)

        masked = document_pb2.Document()
        masked.CopyFrom(self.doc)

        slices = []
        start = 0
        mask_start = 0

        # Sort by char start.
        entities = masked.entity.values()
        entities = sorted(entities, key=lambda a: a.char_start)

        for entity in entities:
            slices.append(self.doc.text[start:entity.char_start])
            mask_start += len(slices[-1])

            if mask_duids is not None and entity.duid not in mask_duids:
                slices.append(self.text(entity))
            else:
                # Not using entity type as replacement because it may change
                # the parsing, ENTITY seems to affect the parsing less.
                if self.text(entity).endswith('s'):
                    slices.append('ENTITIES')
                else:
                    slices.append('BIOENTITY')

            entity_end = entity.char_end
            entity.char_start = mask_start
            entity.char_end = mask_start + len(slices[-1]) - 1

            mask_start += len(slices[-1])
            start = entity_end + 1

        slices.append(self.doc.text[start:])

        masked.text = ''.join(slices)
        return masked

    @staticmethod
    def recover_mask_entity(masked_doc, original_doc):
        ori_helper = DocHelper(original_doc)
        masked_entities = sorted(masked_doc.entity.values(), key=lambda t:t.char_start)

        # for token in masked_doc.token:
        #     print(token.word, token.char_start, token.char_end, sep='|', end=' ')
        # print()

        for index, t in enumerate(masked_entities):
            if t.duid not in original_doc.entity:
                # Usually t is a trigger recognized by EDG, so it's
                # not in the original doc.
                continue

            # Add original entity snippet.
            ori_entity = original_doc.entity[t.duid]
            ori_text = ori_helper.text(ori_entity)

            # Calculate diff.
            diff = len(ori_text) - (t.char_end - t.char_start + 1)

            # Update masked text and entity char_end.
            masked_doc.text = masked_doc.text[:t.char_start] + ori_text \
                              + masked_doc.text[t.char_end+1:]
            t.char_end = t.char_start + len(ori_text) - 1

            token = masked_doc.token[t.token_start]
            # No need to update char_start, as it's already updated in
            # latter loop. And if we update char_start here, it will
            # be a problem if two entities in a token, e.g., H3-Lys9.
            # Lys-9's char_start is not the token's char_start.
            #token.char_start = t.char_start
            token.char_end += diff

            token.word = token.word.replace('BIOENTITY', ori_text, 1)
            token.word = token.word.replace('ENTITIES', ori_text, 1)
            # lemma could be upper or lower case.
            token.lemma = token.lemma.replace('bioentity', ori_text, 1)
            token.lemma = token.lemma.replace('entities', ori_text, 1)
            token.lemma = token.lemma.replace('BIOENTITY', ori_text, 1)
            token.lemma = token.lemma.replace('ENTITIES', ori_text, 1)

            sent = masked_doc.sentence[t.sentence_index]
            sent.char_end += diff

            # Update latter tokens char_start and char_end.
            for token in masked_doc.token[t.token_end+1:]:
                if token.char_start < 0 or token.char_end < 0:
                    continue
                token.char_start += diff
                token.char_end += diff

            # Update latter sentences char_start and char_end.
            for sent in masked_doc.sentence[t.sentence_index+1:]:
                sent.char_start += diff
                sent.char_end += diff

            # Update latter entities char_start and char_end.
            for latter in masked_entities[index+1:]:
                latter.char_start += diff
                latter.char_end += diff

