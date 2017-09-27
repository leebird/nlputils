# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from collections import defaultdict


def constraint(helper, arg_regex, entity_types):
    doc = helper.doc
    token_to_entity = defaultdict(set)

    for entity in doc.entity.values():
        # token_type = entity_type_to_str[entity.entity_type]
        for i in range(entity.token_start, entity.token_end+1):
            token_to_entity[i].add(entity.entity_type)

    arg_pattern = re.compile(arg_regex)

    invalid_deps = set()
    for sent in doc.sentence:
        for did, dep in enumerate(sent.dependency_extra):
            if (dep.relation.startswith(arg_regex) or
                    arg_pattern.match(dep.relation)):
                dep_token = doc.token[dep.dep_index]
                gov_token = doc.token[dep.gov_index]
                correct_type = False
                for ttype in entity_types:
                    if ttype in token_to_entity[dep_token.index]:
                        correct_type = True
                        break
                if not correct_type:
                    invalid_deps.add((sent.index, did))

    # return valid deps for each sentence.
    return invalid_deps


def constraint_args(helper, constraints):
    invalid_deps = set()
    for arg, cons in constraints.items():
        res = constraint(helper, arg, cons)
        invalid_deps |= res
    return invalid_deps
