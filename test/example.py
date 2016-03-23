# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from protolib.python import document_pb2, rpc_pb2
from utils.rpc import grpcapi


def process_one_document(request):
    # Use biotm2 as server.
    interface = grpcapi.GrpcInterface(host='128.4.20.169')
    # interface = grpcapi.GrpcInterface(host='localhost')
    response = interface.process_document(request)
    assert len(response.document) == 1
    return response.document[0]


def parse_using_bllip(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.PARSE_BLLIP
    request.document.extend([doc])
    return process_one_document(request)


def parse_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.PARSE_STANFORD
    request.document.extend([doc])
    return process_one_document(request)


def split_using_stanford(doc):
    request = rpc_pb2.Request()
    request.request_type = rpc_pb2.Request.SPLIT
    request.document.extend([doc])
    return process_one_document(request)


def run():
    text = u'MicroRNAs (miRNAs) are small non-coding RNAs of ∼19-24 ' \
           'nucleotides (nt) in length and considered as potent ' \
           'regulators of gene expression at transcriptional and ' \
           'post-transcriptional levels. Here we report the identification ' \
           'and characterization of 15 conserved miRNAs belonging to 13 ' \
           'families from Rauvolfia serpentina through in silico analysis ' \
           'of available nucleotide dataset. The identified mature R. ' \
           'serpentina miRNAs (rse-miRNAs) ranged between 20 and 22nt in ' \
           'length, and the average minimal folding free energy index (MFEI) ' \
           'value of rse-miRNA precursor sequences was found to be ' \
           '-0.815kcal/mol. Using the identified rse-miRNAs as query, their ' \
           'potential targets were predicted in R. serpentina and other plant ' \
           'species. Gene Ontology (GO) annotation showed that predicted ' \
           'targets of rse-miRNAs include transcription factors as well as ' \
           'genes involved in diverse biological processes such as primary ' \
           'and secondary metabolism, stress response, disease resistance, ' \
           'growth, and development. Few rse-miRNAs were predicted to target ' \
           'genes of pharmaceutically important secondary metabolic pathways ' \
           'such as alkaloids and anthocyanin biosynthesis. Phylogenetic ' \
           'analysis showed the evolutionary relationship of rse-miRNAs and ' \
           'their precursor sequences to homologous pre-miRNA sequences from ' \
           'other plant species. The findings under present study besides giving ' \
           'first hand information about R. serpentina miRNAs and their targets, ' \
           'also contributes towards the better understanding of miRNA-mediated ' \
           'gene regulatory processes in plants.'

    raw_doc = document_pb2.Document()
    raw_doc.doc_id = '26815768'
    raw_doc.text = text

    # Parse using Bllip parser.
    result = parse_using_bllip(raw_doc)
    print(result)

    # Parse Using Stanford CoreNLP parser.
    result = parse_using_stanford(raw_doc)
    print(result)

    # Only split sentences using Stanford CoreNLP.
    for i in range(100):
        result = split_using_stanford(raw_doc)
        print('Split {} documents'.format(i))

if __name__ == '__main__':
    run()
