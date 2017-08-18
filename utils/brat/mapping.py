from protolib.python import document_pb2

entity_type_to_str = {
    document_pb2.Entity.MIRNA: 'MiRNA',
    document_pb2.Entity.GENE: 'Gene',
    document_pb2.Entity.TRIGGER: 'Trigger',
    document_pb2.Entity.SUBCELLULAR_LOCATION: 'Subcellular_location',
    document_pb2.Entity.UNDEFINED_TYPE: 'Entity',
    document_pb2.Entity.SITE: 'Site',
    document_pb2.Entity.DISEASE: 'Disease',
    document_pb2.Entity.CHEMICAL: 'Chemical',
    document_pb2.Entity.SPECIES: 'Species',
}

str_to_entity_type = {
    'mirna': document_pb2.Entity.MIRNA,
    'gene': document_pb2.Entity.GENE,
    'protein': document_pb2.Entity.GENE,
    'family': document_pb2.Entity.GENE,
    'complex': document_pb2.Entity.GENE,
    # BioInfer corpus types.
    'gene/protein/rna': document_pb2.Entity.GENE,
    'individual_protein': document_pb2.Entity.GENE,
    'protein_family_or_group': document_pb2.Entity.GENE,
    'protein_complex': document_pb2.Entity.GENE,
    'dna_family_or_group': document_pb2.Entity.GENE,
    # BioNLP corpus types.
    'trigger': document_pb2.Entity.TRIGGER,
    'phosphorylation': document_pb2.Entity.TRIGGER,
    'site': document_pb2.Entity.SITE,
    'anaphora': document_pb2.Entity.UNDEFINED_TYPE,
    'localization': document_pb2.Entity.TRIGGER,
    'phosphorylation': document_pb2.Entity.TRIGGER,
    'subcellular_location': document_pb2.Entity.SUBCELLULAR_LOCATION,
    'entity': document_pb2.Entity.UNDEFINED_TYPE,
    # 'Sentence': document_pb2.Entity.DISEASE
}
