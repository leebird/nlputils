from protolib.python import document_pb2

entity_type_to_str = {
    document_pb2.Entity.MIRNA: 'MiRNA',
    document_pb2.Entity.GENE: 'Gene',
    document_pb2.Entity.TRIGGER: 'Trigger',
    document_pb2.Entity.SUBCELLULAR_LOCATION: 'Subcellular_location',
    document_pb2.Entity.UNSET: 'Entity',
    # document_pb2.Entity.DISEASE: 'Sentence'
}

str_to_entity_type = {
    'MiRNA': document_pb2.Entity.MIRNA,
    'Gene': document_pb2.Entity.GENE,
    'Protein': document_pb2.Entity.GENE,
    'Trigger': document_pb2.Entity.TRIGGER,
    'Localization': document_pb2.Entity.TRIGGER,
    'Subcellular_location': document_pb2.Entity.SUBCELLULAR_LOCATION,
    'Entity': document_pb2.Entity.UNSET,
    # 'Sentence': document_pb2.Entity.DISEASE
}
