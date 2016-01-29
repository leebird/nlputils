from __future__ import unicode_literals, print_function
import sys
import codecs
import json
import uuid
from protolib.python import document_pb2
import shortuuid
from ..brat import parser, mapping
from collections import defaultdict, namedtuple


class DocHelper(object):
    def __init__(self, doc):
        self.doc = doc

    def char_range(self, sentence):
        token_start = sentence.token_start
        token_end = sentence.token_end
        char_start = self.doc.token[token_start].char_start
        char_end = self.doc.token[token_end].char_end
        return char_start, char_end

    def char_range_in_sentence(self, proto_obj, sentence):
        sent_char_start, _ = self.char_range(sentence)
        return proto_obj.char_start - sent_char_start, \
               proto_obj.char_end - sent_char_start

    def text(self, proto_obj):
        char_start, char_end = -1, -1
        if type(proto_obj) == document_pb2.Sentence:
            char_start, char_end = self.char_range(proto_obj)
        elif type(proto_obj) == document_pb2.Entity:
            char_start, char_end = proto_obj.char_start, proto_obj.char_end
        elif type(proto_obj) == document_pb2.Sentence.Constituent:
            char_start, char_end = proto_obj.char_start, proto_obj.char_end

        return self.doc.text[char_start: char_end + 1]

    def token(self, proto_obj):
        return self.doc.token[proto_obj.token_start:proto_obj.token_end + 1]

    def token_of_char_offset(self, offset):
        for token in self.doc.token:
            if token.char_start <= offset <= token.char_end:
                return token

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
            args[arg.role].append(self.doc.entity[arg.entity_duid])
        return args

    def entity_in_sentence(self, sentence):
        token_start = sentence.token_start
        token_end = sentence.token_end

        entities = []
        for entity in self.doc.entity.values():
            if entity.token_start >= token_start and entity.token_end <= token_end:
                entities.append(entity)

        return entities

    def entity_sentence_index(self, entity):
        index = set()
        for sentence in self.doc.sentence:
            if sentence.token_start <= entity.token_start and \
                            sentence.token_end >= entity.token_end:
                index.add(sentence.index)
        return index

    def entity_head_token(self, graph, entity):
        tokens = self.token(entity)
        # If the last token is a punctuation, it may not have heads.
        # So in the following codes we update the head with token that
        # has heads.
        head = tokens[-1]

        # Find head token.
        if len(tokens) > 1:
            for token in tokens:
                heads = graph.get_gov(token.index)
                #if len(heads) > 0:
                #    head = token
                for gov in heads:
                    if gov in tokens:
                        head = gov
                        break
        return head

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

    def char_offset_to_entity(self, char_offset):
        entities = []
        for entity_id, entity in self.doc.entity.items():
            if entity.char_start <= char_offset <= entity.char_end:
                entities.append(entity)
        return entities

    def add_entity(self, duid=None):
        if duid is None:
            while True:
                # duid = uuid.uuid4().hex
                # Use shorteuuid and length 4 uuid.
                duid = shortuuid.ShortUUID().random(length=4)

                if duid not in self.doc.entity:
                    break

        assert duid is not None
        assert duid not in self.doc.entity
        entity = self.doc.entity.get_or_create(duid)
        entity.duid = duid
        return entity

    def add_relation(self, relation_type, duid=None):
        if duid is None:
            while True:
                # duid = uuid.uuid4().hex
                duid = shortuuid.ShortUUID().random(length=4)

                if duid not in self.doc.relation:
                    break

        assert duid is not None
        assert duid not in self.doc.relation

        relation = self.doc.relation.get_or_create(duid)
        relation.duid = duid
        relation.relation_type = relation_type
        return relation

    def fill_entity_using_char_offset(self, entity):
        for token in self.doc.token:
            if token.char_start <= entity.char_start <= token.char_end:
                entity.token_start = token.index
            if token.char_start <= entity.char_end <= token.char_end:
                entity.token_end = token.index
                break

        assert entity.token_start <= entity.token_end, (str(entity),
                                                        self.text(entity),
                                                        str(self.doc.doc_id))

        for sentence in self.doc.sentence:
            if sentence.token_start <= entity.token_start and \
                            sentence.token_end >= entity.token_end:
                entity.sentence_index = sentence.index
                break

    def dependencpy_for_brat(self, sentence):
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
            rid = 'R' + str(count)
            dep = dep_relation.dep_index
            gov = dep_relation.gov_index
            relation = dep_relation.relation

            dep_tid = index2tid[dep]
            gov_tid = index2tid[gov]
            relations.append([rid, relation, [['Governer', gov_tid],
                                              ['Dependent', dep_tid]]])
            count += 1

        return {'Annotation': {'text': sent_text,
                               'entities': entities,
                               'relations': relations}}

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
                    line[0] == 'R' or line[0] == '*' or line[0] == 'M'

                if line[0] == 'T':
                    entity_id, entity_text, entity_type, entity_start, entity_end \
                        = parser.parse_entity(line)
                    if entity_type not in mapping.str_to_entity_type:
                        # Only consider entity types in mapping.
                        # print('Skip entity type:', entity_type, file=sys.stderr)
                        continue
                    entity = helper.add_entity(entity_id)
                    entity.char_start = entity_start
                    entity.char_end = entity_end - 1
                    entity.entity_type = mapping.str_to_entity_type[entity_type]

                elif line[0] == 'E':
                    events.append(parser.parse_event(line))
                elif line[0] == 'R':
                    relations.append(parser.parse_relation(line))

            for eid, etype, trigger_id, arguments, attrs in events:
                event = helper.add_relation(etype, eid)
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
                relation = helper.add_relation(rtype, rid)
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
                                              sent_end+1,
                                              self.text(sent))
                    f.write(line)
                    start_id += 1

            for entity_id, entity in self.doc.entity.items():
                if entity.entity_type not in mapping.entity_type_to_str:
                    print('Skip entity not in mapping', entity.entity_type,
                          file=sys.stderr)
                    continue
                entity_type = mapping.entity_type_to_str[entity.entity_type]
                entity_text = self.text(entity)
                line = entity_line.format(entity.duid,
                                          entity_type,
                                          entity.char_start,
                                          entity.char_end+1,
                                          entity_text)
                f.write(line)

            event_line = '{0}\t{1}:{2} {3}:{4} {5}:{6}\t{7}\n'
            rel_line = '{0}\t{1} {2}:{3} {4}:{5}\t{6}\n'
            for er_id, event_or_rel in self.doc.relation.items():
                arguments = defaultdict(list)
                for arg in event_or_rel.argument:
                    arguments[arg.role].append(arg.entity_duid)

                attributes = defaultdict(list)
                for attr in event_or_rel.attribute:
                    attributes[attr.key].append(attr.value)
                attributes_json = json.dumps(attributes)

                if event_or_rel.duid.startswith('E'):
                    assert len(arguments['Trigger']) == 1
                    line = event_line.format(event_or_rel.duid,
                                             event_or_rel.relation_type,
                                             arguments['Trigger'][0],
                                             'Agent', arguments['Agent'][0],
                                             'Theme', arguments['Theme'][0],
                                             attributes_json)
                    f.write(line)
                elif event_or_rel.duid.startswith('R'):
                    line = rel_line.format(event_or_rel.duid,
                                           event_or_rel.relation_type,
                                           'Arg1', arguments['Arg1'][0],
                                           'Arg2', arguments['Arg2'][0],
                                           attributes_json)
                    f.write(line)

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

    def tag_entity_in_sentence(self, sentence, entities):
        def close_tag(entity):
            return '</{0}>'.format(mapping.entity_type_to_str[entity.entity_type])

        def open_tag(entity):
            return '<{0}>'.format(mapping.entity_type_to_str[entity.entity_type])

        text = self.text(sentence)
        slices = []
        start = 0
        for entity in sorted(entities, key=lambda a: a.char_start):
            char_start, char_end = self.char_range_in_sentence(entity, sentence)
            slices.append(text[start:char_start])
            slices.append(open_tag(entity))
            slices.append(text[char_start:char_end+1])
            slices.append(close_tag(entity))
            start = char_end+1

        slices.append(text[start:])
        return ''.join(slices)

    def smart_tag_entity_in_sentence(self, sentence, entities):
        # Attributes start and end are offsets of the entity, not the tag's position.
        Tag = namedtuple('Tag', ['tag', 'start', 'end', 'type'])

        def get_tag(entity, sentence):
            char_start, char_end = self.char_range_in_sentence(entity, sentence)
            # Note char_end is offset of the last character of the entity.
            open_tag = Tag(mapping.entity_type_to_str[entity.entity_type],
                           char_start, char_end+1, 'open')
            close_tag = Tag(mapping.entity_type_to_str[entity.entity_type],
                            char_start, char_end+1, 'close')
            return open_tag, close_tag

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
                    
        text = self.text(sentence)
        tags = []

        # Get tags with start and end char-level offset.
        for entity in entities:
            open_tag, close_tag = get_tag(entity, sentence)
            tags.append(open_tag)
            tags.append(close_tag)

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
                    raise ValueError('Unmatched ppen and close tag:', '_EMPTY_', tag.tag)
                open_tag = open_tags.pop()
                if open_tag.tag != tag.tag:
                    raise ValueError('Unmatched ppen and close tag:', open_tag.tag, tag.tag)
                slices.append(text[start:tag.end])
                slices.append('</{0}>'.format(tag.tag))
                start = tag.end                

        if len(open_tags) > 0:
            raise ValueError('Non-empty open tags at the end')

        slices.append(text[start:])
        return ''.join(slices)

    def has_overlap_entity(self):
        for entity_id_1, entity_1 in self.doc.entity.items():
            for entity_id_2, entity_2 in self.doc.entity.items():
                if entity_id_1 == entity_id_2:
                    continue
                if RangeHelper.char_range_overlap(entity_1, entity_2):
                    return True
        return False

    def mask_entity(self, exclude_type=None):
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

            if exclude_type is not None and entity.entity_type in exclude_type:
                slices.append(self.text(entity))
            else:                              
                entity_type = mapping.entity_type_to_str[entity.entity_type].upper()
                slices.append(entity_type)

            entity_end = entity.char_end
            entity.char_start = mask_start
            entity.char_end = mask_start + len(slices[-1]) - 1            

            mask_start += len(slices[-1])
            start = entity_end + 1
            
        slices.append(self.doc.text[start:])

        masked.text = ''.join(slices)
        return masked


class RangeHelper(object):
    @staticmethod
    def equal(range1, range2):
        return range1[0] == range2[0] and \
               range1[1] == range2[1]

    @staticmethod
    def overlap(range1, range2):
        return range1[1] >= range2[0] and \
               range1[0] <= range2[1]

    @staticmethod
    def char_range_overlap(entity1, entity2):
        return RangeHelper.overlap((entity1.char_start, entity1.char_end),
                                   (entity2.char_start, entity2.char_end))

    @staticmethod
    def include(outer_range, inner_range):
        return outer_range[0] <= inner_range[0] and \
               outer_range[1] >= inner_range[1]

    @staticmethod
    def char_range_include(outer_entity, inner_entity):
        return RangeHelper.include((outer_entity.char_start,
                                    outer_entity.char_end),
                                   (inner_entity.char_start,
                                    inner_entity.char_end))

