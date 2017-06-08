from __future__ import unicode_literals, print_function
import json


def parse_entity(line):
    fields = line.split('\t')
    info = fields[1].split(' ')
    tid = fields[0]
    text = fields[2]
    category = info[0]
    start = int(info[1])
    end = int(info[2])
    return tid, text, category, start, end


def parse_event(line):
    fields = line.split('\t')
    eid = fields[0]
    info = fields[1].split(' ')
    category = info[0].split(':')
    trigger_id = category[1]
    category_text = category[0]

    arguments = []
    for arg in info[1:]:
        if len(arg) == 0:
            continue
        arg_category, arg_entity_id = arg.split(':')
        arguments.append((arg_category, arg_entity_id))

    attrs = None
    if len(fields) > 2:
        attrs = json.loads(fields[2])
    return eid, category_text, trigger_id, arguments, attrs


def parse_relation(line):
    fields = line.split('\t')
    rid = fields[0]
    info = fields[1].split(' ')
    category_text = info[0]

    arguments = []
    for arg in info[1:]:
        if rid.startswith('R'):
            arg_category, arg_entity_id = arg.split(':')
        else:
            arg_category, arg_entity_id = 'Entity', arg
        arguments.append((arg_category, arg_entity_id))

    attrs = None
    if len(fields) > 2:
        if len(fields[2].strip()) > 0:
            attrs = json.loads(fields[2])

    return rid, category_text, arguments, attrs