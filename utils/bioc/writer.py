from __future__ import unicode_literals
import sys
import codecs
import json
from lxml import etree

# See http://lxml.de/api.html#incremental-xml-generation
# for incremental XML generation used below.


def write_entity(xf, entity):
    start = str(entity['charStart'])
    length = str(entity['charEnd'] - entity['charStart'] + 1)
    text = doc['text'][entity['charStart']:entity['charEnd'] + 1]
    with xf.element('annotation', id=entity['duid']):
        with xf.element('infon', key='type'):
            xf.write(entity['entityType'])
        with xf.element('infon', key='source'):
            xf.write(entity['source'])
        el = etree.Element('location',
                           offset=start,
                           length=length)
        xf.write(el)
        with xf.element('text'):
            xf.write(text)
        for entity_id in entity['entityId']:
            with xf.element('infon', key=entity_id['source']):
                xf.write(entity_id['idString'])

        for attr in entity['attribute']:
            with xf.element('infon', key=attr['key']):
                xf.write(attr['value'])


json_file_path, xml_file_path = sys.argv[1], sys.argv[2]

with codecs.open(json_file_path, 'r', 'utf8') as jf, \
        etree.xmlfile(xml_file_path, encoding='utf8') as xf:
    with xf.element('collection'):
        el = etree.Element('source')
        xf.write(el)
        el = etree.Element('date')
        xf.write(el)
        el = etree.Element('key')
        xf.write(el)
        for line in jf:
            doc = json.loads(line.strip())
            # if doc['docId'] != '25789565':
            #     continue

            sentences = [e for e in doc['entity'] if e['entityType'] == 'SENTENCE']
            # Sort sentences by its character offset.
            sentences = sorted(sentences, key=lambda s: s['charStart'])

            with xf.element('document'):
                with xf.element('id'):
                    xf.write(doc['docId'])
                with xf.element('passage'):
                    with xf.element('offset'):
                        # We only have abstract as the only one passage,
                        # so just write offset as 0 for it.
                        xf.write('0')

                    if len(sentences) == 0:
                        # If there are no sentences, just write the text
                        # and entities.
                        with xf.element('text'):
                            xf.write(doc['text'])

                        for entity in doc['entity']:
                            write_entity(xf, entity)
                    else:
                        # If there are sentences, write the entities to
                        # each corresponding sentence.
                        entities = [e for e in doc['entity'] if e['entityType'] != 'SENTENCE']
                        entities = sorted(entities, key=lambda e: e['charStart'])
                        entity_duids = set([e['duid'] for e in entities])

                        # Entity duid should be unique in the document.
                        assert len(entity_duids) == len(entities)

                        seen_duids = set()
                        for sent in sentences:
                            sent_text = doc['text'][sent['charStart']:sent['charEnd']+1]

                            with xf.element('sentence'):
                                with xf.element('offset'):
                                    xf.write(str(sent['charStart']))
                                with xf.element('text'):
                                    xf.write(sent_text)

                                for entity in entities:
                                    if entity['charStart'] > sent['charEnd']:
                                        break
                                    if entity['charStart'] < sent['charStart']:
                                        continue
                                    write_entity(xf, entity)
                                    seen_duids.add(entity['duid'])

                        # We should see all the entities.
                        # assert len(entity_duids) == len(seen_duids), doc['docId']
                        # There are a few problematic PMIDs, check later, may be
                        # alignment problems.
                        # 15621726, reader only returns 1 relation,
                        # why alchemy db has two?
                        # 12757110
                        # 25180620
                        # 25696812
                        # 25524638
                        # 26098770
                        # 26250785
                        # 26303353
                        # 26370665
                        # 26473405
                        # 26481868
                        # 26583473
                        # 26644403

                        if len(entity_duids) != len(seen_duids):
                            print(doc['docId'])

                    # Write the relations.
                    for relation in doc['relation']:
                        with xf.element('relation', id=relation['duid']):
                            with xf.element('infon', key='relation type'):
                                xf.write(relation['relationType'])
                            with xf.element('infon', key='source'):
                                xf.write(relation['source'])
                            for arg in relation['argument']:
                                el = etree.Element('node', refid=arg['entity_duid'], role=arg['role'])
                                xf.write(el)

                            for attr in relation['attribute']:
                                with xf.element('infon', key=attr['key']):
                                    xf.write(attr['value'])
