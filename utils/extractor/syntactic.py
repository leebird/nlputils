from __future__ import unicode_literals, print_function
import sys
from ..dependency.path import undirected_shortest_dep_path
from ..dependency.graph import DependencyGraph
from ..dependency.path import PathDirection
from ..constituent.path import undirected_shortest_const_path
from ..helper import RangeHelper
# from ..brat.mapping import entity_type_to_str
from nltk.stem import PorterStemmer


STEMMER = PorterStemmer()


def extract_dep_lemma_path(helper, graph, src_entity, dst_entity):
    src_head = helper.entity_head_token(graph, src_entity)
    dst_head = helper.entity_head_token(graph, dst_entity)

    path = undirected_shortest_dep_path(graph, src_head.index, dst_head.index)

    if path is None:
        return path
    if len(path) == 0:
        return ''
    
    result = []
    prev_direction = None
    # The first element stores the relation from the src_entity head
    # to a previous token, which is not on the path. The last element
    # stores the relation from the token to the dst_entity head.
    for e in path[1:-1]:
        # No need for the separator in dep lemma path, the root lemma is
        # used as separator.
        # if prev_direction is not None and prev_direction != e.direction_from_prev:
            # Add a separator when the direction changes.
            # result.append('__')
            
        if e.direction_from_prev == PathDirection.dep_to_gov:
            result.append('<-r:'+e.relation_with_prev+'<-')
            result.append(helper.doc.token[e.token_index].lemma)
        else:
            result.append('->r:'+e.relation_with_prev+'->')
            result.append(helper.doc.token[e.token_index].lemma)
        
        prev_direction = e.direction_from_prev
        
    if path[-1].direction_from_prev == PathDirection.dep_to_gov:
        result.append('<-r:' + path[-1].relation_with_prev + '<-')
    else:
        result.append('->r:' + path[-1].relation_with_prev + '->')
            
    return ''.join(result)


def extract_dep_path(graph, src_token, dst_token):
    path = undirected_shortest_dep_path(graph, src_token.index, dst_token.index)

    if path is None:
        return path
    if len(path) == 0:
        return ''

    result = []
    prev_direction = None
    
    for e in path[1:]:
        if prev_direction is not None and prev_direction != e.direction_from_prev:
            # Add a separator when the direction changes.
            result.append('__')
        if e.direction_from_prev == PathDirection.dep_to_gov:
            result.append(e.relation_with_prev)
            result.append('<-')
        else:
            result.append('->')
            result.append(e.relation_with_prev)
        prev_direction = e.direction_from_prev
        
    return ''.join(result)


def extract_word_on_dep_path(helper, graph, src_entity, dst_entity):
    src_head = helper.entity_head_token(graph, src_entity)
    dst_head = helper.entity_head_token(graph, dst_entity)

    path = undirected_shortest_dep_path(graph, src_head.index, dst_head.index)
    if path is None or len(path) == 0:
        return path
    
    result = []
    for e in path[1:-1]:
        result.append(helper.doc.token[e.token_index].word)
    #result.append(path[-1].relation)

    return result


def extract_lemma_on_dep_path(helper, graph, src_entity, dst_entity):
    src_head = helper.entity_head_token(graph, src_entity)
    dst_head = helper.entity_head_token(graph, dst_entity)

    path = undirected_shortest_dep_path(graph, src_head.index, dst_head.index)
    if path is None or len(path) == 0:
        return path

    result = []
    for e in path[1:-1]:
        result.append(helper.doc.token[e.token_index].lemma)
    # result.append(path[-1].relation)

    return result

# def extract_ev_walk_features(helper, graph, src_entity, dst_entity):
#     src_head = helper.entity_head_token(graph, src_entity)
#     dst_head = helper.entity_head_token(graph, dst_entity)
#
#     src_type = entity_type_to_str[src_entity.entity_type]
#     dst_type = entity_type_to_str[dst_entity.entity_type]
#
#     path = undirected_shortest_dep_path(graph, src_head.index, dst_head.index)
#     if path is None or len(path) == 0:
#         return path, path
#
#     result = ['t:{}'.format(src_type)]
#
#     # The first element stores the relation from the src_entity head
#     # to a previous token, which is not on the path. The last element
#     # stores the relation from the token to the dst_entity head.
#     for e in path[1:-1]:
#         if e.direction_from_prev == PathDirection.dep_to_gov:
#             result.append('<-')
#             result.append(e.relation_with_prev)
#             result.append('<-')
#             result.append(helper.doc.token[e.token_index].lemma)
#         else:
#             result.append('->')
#             result.append(e.relation_with_prev)
#             result.append('->')
#             result.append(helper.doc.token[e.token_index].lemma)
#
#     if path[-1].direction_from_prev == PathDirection.dep_to_gov:
#         result.append('<-')
#         result.append(path[-1].relation_with_prev)
#         result.append('<-')
#         result.append('t:{}'.format(dst_type))
#     else:
#         result.append('->')
#         result.append(path[-1].relation_with_prev)
#         result.append('->')
#         result.append('t:{}'.format(dst_type))
#
#     e_walk = []
#     v_walk = []
#     for i in range(0, len(result), 4):
#         if len(result[i:i+5]) == 5:
#             v_walk.append(''.join(result[i:i+5]))
#
#     for i in range(2, len(result), 4):
#         if len(result[i:i+5]) == 5:
#             e_walk.append(''.join(result[i:i+5]))
#     # print(result)
#     return e_walk, v_walk


def extract_relation_dep_lemma_path(helper, relation, role_1, role_2):
    assert role_1 != role_2
    arg_1 = []
    arg_2 = []
    for arg in relation.argument:
        if arg.role == role_1:
            arg_1.append(helper.doc.entity[arg.entity_duid])

        if arg.role == role_2:
            arg_2.append(helper.doc.entity[arg.entity_duid])
            
    assert len(arg_1) == 1
    assert len(arg_2) == 1
    if arg_1[0].sentence_index != arg_2[0].sentence_index:
        print(helper.doc.doc_id, 'multiple sentences', file=sys.stderr)
        return None
    
    sentence = helper.doc.sentence[arg_1[0].sentence_index]
    graph = DependencyGraph.build_from_proto(sentence.dependency)

    src_head = helper.entity_head_token(graph, arg_1[0])
    dst_head = helper.entity_head_token(graph, arg_2[0])

    path = undirected_shortest_dep_path(graph, src_head.index, dst_head.index)
    if path is None:
        return None

    result = []
    for e in path[1:-1]:
        result.append(e.relation)
        result.append(helper.doc.token[e.token_index].lemma)
    result.append(path[-1].relation)

    return '/'.join(result)


def get_mininal_cover_constituent(constituents, entity):
    target = None

    for constituent in constituents:
        if RangeHelper.token_range_include(constituent, entity):
            if target is None:
                target = constituent
            else:
                if target.token_end - target.token_start > \
                   constituent.token_end - constituent.token_start:
                    target = constituent

    if target is None:
        print(entity)
        print(constituents[0])
        for c in constituents:
            print(c.head_token_index, c.token_start, c.token_end)
        sys.exit()

    return target


def get_all_cover_constituent(constituents, entity):
    targets = []

    for constituent in constituents:
        if RangeHelper.char_range_include(constituent, entity):
            targets.append(constituent)
    return targets


class SyntaticExtractor(object):
    def __init__(self, doc, sentence, src_token, dst_token):
        self.doc = doc
        self.sentence = sentence
        self.src_token = src_token
        self.dst_token = dst_token
        self.graph = DependencyGraph.build_from_proto(sentence.dependency)

    def extract_unlex_shortest_dep_path(self):
        self.dep_path = undirected_shortest_dep_path(
            self.graph, self.src_token.index, self.dst_token.index)
        if self.dep_path is None:
            raise ValueError

    def extract_unlex_shortest_dep_path_with_a_token(self):
        self.dep_path = undirected_shortest_dep_path(
            self.graph, self.src_token.index, self.dst_token.index, True)
        if self.dep_path is None:
            raise ValueError

    def extract_unlex_dep_path_length(self):
        if len(self.dep_path) == 0:
            return 0
        return len(self.dep_path) - 1

    def extract_unlex_dep_path(self):
        src_to_root = []
        root_to_src = []

        for e in self.dep_path[1:]:
            if e.direction_from_prev == PathDirection.dep_to_gov:
                src_to_root.append(e.relation_with_prev)
            else:
                root_to_src.append(e.relation_with_prev)

        src_to_root_str = '<-{}<-'.format('<-'.join(src_to_root))
        root_to_src_str = '->{}->'.format('->'.join(root_to_src))

        if len(src_to_root) == 0 and len(root_to_src) == 0:
            return ''
        elif len(src_to_root) == 0:
            return root_to_src_str
        elif len(root_to_src) == 0:
            return src_to_root_str
        else:
            return '{}__{}'.format(src_to_root_str, root_to_src_str)

    def extract_one_lex_dep_path(self):
        paths = []
        for curr_lex in range(len(self.dep_path) - 2):
            src_to_root = []
            root_to_src = []

            root = '__'
            for index, e in enumerate(self.dep_path[1:]):
                lemma = self.doc.token[e.token_index].lemma
                if e.direction_from_prev == PathDirection.dep_to_gov:
                    src_to_root.append(e.relation_with_prev)
                    if index == curr_lex:
                        src_to_root.append('w:'+STEMMER.stem(lemma))
                else:
                    root_to_src.append(e.relation_with_prev)
                    if index == curr_lex:
                        root_to_src.append('w:'+STEMMER.stem(lemma))

            if curr_lex == len(src_to_root) - 2:
                root = src_to_root.pop()

            src_to_root_str = '<-{}<-'.format('<-'.join(src_to_root))
            root_to_src_str = '->{}->'.format('->'.join(root_to_src))

            if len(src_to_root) == 0 and len(root_to_src) == 0:
                path = ''
            elif len(src_to_root) == 0:
                path = root_to_src_str
            elif len(root_to_src) == 0:
                path = src_to_root_str
            else:
                path = '{}{}{}'.format(src_to_root_str, root, root_to_src_str)
            paths.append(path)

        return paths

    def extract_v_walk(self, first_word, last_word):
        vwalks = []
        if len(self.dep_path) == 0:
            vwalks.append('{}{}{}'.format(first_word, 'EMPTY', last_word))
            return vwalks

        prev = self.dep_path[0]
        for e in self.dep_path[1:]:
            prev_token = self.doc.token[prev.token_index]
            prev_stem = STEMMER.stem(prev_token.lemma.lower())
            if len(vwalks) == 0:
                prev_stem = first_word

            curr_token = self.doc.token[e.token_index]
            curr_stem = STEMMER.stem(curr_token.lemma.lower())
            if len(vwalks) == len(self.dep_path) - 2:
                curr_stem = last_word

            relation = e.relation_with_prev
            if e.direction_from_prev == PathDirection.dep_to_gov:
                arrow = '<-'
            else:
                arrow = '->'
            vwalk = '{}{}{}{}{}'.format(prev_stem, arrow, relation, arrow, curr_stem)
            vwalks.append(vwalk)
            prev = e
        return vwalks

    def extract_e_walk(self):
        ewalks = []
        if len(self.dep_path) <= 2:
            return ewalks

        prev = self.dep_path[1]
        for e in self.dep_path[2:]:
            prev_relation = prev.relation_with_prev
            prev_token = self.doc.token[prev.token_index]
            prev_stem = STEMMER.stem(prev_token.lemma.lower())
            if prev.direction_from_prev == PathDirection.dep_to_gov:
                prev_arrow = '<-'
            else:
                prev_arrow = '->'

            curr_relation = e.relation_with_prev
            if e.direction_from_prev == PathDirection.dep_to_gov:
                curr_arrow = '<-'
            else:
                curr_arrow = '->'
            ewalk = '{}{}{}{}{}'.format(prev_relation, prev_arrow,
                                        prev_stem, curr_arrow, curr_relation)
            ewalks.append(ewalk)
            prev = e
        return ewalks

    def extract_pos_relation_on_dep_path(self):
        result = []
        if len(self.dep_path) == 0:
            return result
        for e in self.dep_path[1:-1]:
            result.append('rel:' + e.relation_with_prev)
            result.append('pos:' + self.doc.token[e.token_index].pos)
        result.append('rel:' + self.dep_path[-1].relation_with_prev)
        return result

    def extract_token_on_dep_path(self, include_arg=False):
        # Not include src_token and dst_token.
        tokens = []
        dep_path = self.dep_path
        if not include_arg:
            dep_path = self.dep_path[1:-1]
        for e in dep_path:
            tokens.append(self.doc.token[e.token_index])
        return tokens

    def extract_constituent_path(self):
        constituents = self.sentence.constituent

        src_cst, dst_cst = None, None
        for cst in constituents:
            if len(cst.children) == 0:
                continue
            if cst.token_start == cst.token_end == self.src_token.index:
                src_cst = cst
            if cst.token_start == cst.token_end == self.dst_token.index:
                dst_cst = cst
        if src_cst is None or dst_cst is None:
            return None

        path = undirected_shortest_const_path(constituents, src_cst, dst_cst)

        if path is None:
            return None

        if len(path) == 0:
            return ''

        results = []
        prev = None
        for cst in path:
            if prev is not None:
                if prev.index in cst.children:
                    results.append('<-')
                elif cst.index in prev.children:
                    results.append('->')
                else:
                    raise ValueError(''.join([str(e) for e in path]) + str(prev) + str(cst))
            results.append(cst.label)
            prev = cst

        return ''.join(results)
