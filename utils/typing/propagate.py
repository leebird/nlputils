# -*- coding: utf-8 -*-
from __future__ import print_function
from collections import defaultdict
from enum import Enum


_NP_EDGES = {'compound'}


class HeadType(Enum):
    EXPRESSION = 1
    PROTEIN = 2
    PROTEIN_PART = 3
    OTHER = 10


_HEADS = {
    HeadType.EXPRESSION: {'expression', 'level'},
    HeadType.PROTEIN: {'gene', 'protein', 'complex', 'kinase'},
    HeadType.PROTEIN_PART: {'domain', 'component', 'subunit'},
    HeadType.OTHER: {'sequence', 'member', 'dimer', 'trimer', 'proteasome'}
}


_SELECTED_HEADS = None


def get_token_in_np(helper, sent_id, token_id):
    same_np_token = []
    for dep in helper.doc.sentence[sent_id].dependency:
        if dep.relation in _NP_EDGES and dep.gov_index == token_id:
            same_np_token.append(helper.doc.token[dep.dep_index])
    return same_np_token


def make_head_words(head_types=None):
    heads = set()
    if head_types:
        for head in head_types:
            heads |= _HEADS[head]
    else:
        for group in _HEADS.values():
            heads |= group
    return heads


# Propagate EDG arg edge inside noun phrase.
def propagate(helper, constraints, invalid_edges):
    global _SELECTED_HEADS
    if _SELECTED_HEADS is None:
        _SELECTED_HEADS = make_head_words()

    doc = helper.doc
    token_to_entity = defaultdict(set)
    added_edges = set()

    for entity in doc.entity.values():
        # token_type = entity_type_to_str[entity.entity_type]
        for i in range(entity.token_start, entity.token_end + 1):
            token_to_entity[i].add(entity.entity_type)

    for sent_id, dep_id in invalid_edges:
        dep = helper.doc.sentence[sent_id].dependency_extra[dep_id]

        dep_token = helper.doc.token[dep.dep_index]
        if dep_token.lemma not in _SELECTED_HEADS:
            continue

        arg_types = None
        for arg, typings in constraints.items():
            if dep.relation.startswith(arg):
                arg_types = typings
        if not arg_types:
            continue

        np_tokens = get_token_in_np(helper, sent_id, dep.dep_index)
        for token in np_tokens:
            token_typings = token_to_entity[token.index]

            if len(token_typings & arg_types) > 0:
                added_edges.add(
                    (sent_id, dep.gov_index, dep.relation + '_np', token.index))

    print(added_edges)
    for sent_id, gov_index, relation, dep_index in added_edges:
        edge = helper.doc.sentence[sent_id].dependency_extra.add()
        edge.gov_index = gov_index
        edge.dep_index = dep_index
        edge.relation = relation
