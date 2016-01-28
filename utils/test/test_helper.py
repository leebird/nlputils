from __future__ import unicode_literals, print_function

import os
from protolib.python import document_pb2
from nlprpc import grpcapi
from nlp.helper import DocHelper, RangeHelper

def test_one_file():
    txtfile = 'data/abstracts_results/16166262.txt'
    annfile = 'data/abstracts_results/16166262.ann'
    filename = os.path.basename(txtfile)
    doc_id = filename.split('.')[0]
    doc = DocHelper.load_from_brat_file(doc_id, txtfile, annfile)
    
    excluded = set([document_pb2.Entity.TRIGGER])
    masked = DocHelper(doc).mask_entity(excluded)
    
    helper = DocHelper(masked)
    print(masked)
    for entity in masked.entity.values():
        print(helper.text(entity))


def test_mirtex_result():
    count = 0
    overlap = 0
    for root, _, files in os.walk('data/abstracts_results'):
        for f in files:
            if not f.endswith('.txt'):
                continue
            count += 1
            print(count, overlap, end='\r')
            txtfile = os.path.join(root, f)
            annfile = os.path.join(root, f[:-4] + '.ann')
            filename = os.path.basename(f)
            doc_id = filename.split('.')[0]
            doc = DocHelper.load_from_brat_file(doc_id, txtfile, annfile)
            excluded = set([document_pb2.Entity.TRIGGER])
            try:
                masked = DocHelper(doc).mask_entity(excluded)
            except ValueError:
                overlap += 1
    print(count, overlap)
    
if __name__ == '__main__':
    test_mirtex_result()
