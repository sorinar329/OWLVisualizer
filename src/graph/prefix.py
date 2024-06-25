from rdflib import OWL, RDF, RDFS

PREFIX_MAP = {
    str(OWL): 'owl',
    str(RDF): 'rdf',
    str(RDFS): 'rdfs',
    'http://www.ease-crc.org/ont/SOMA.owl#': 'SOMA',
    'http://www.ease-crc.org/ont/mixing#': 'mixing',
    'http://www.ease-crc.org/ont/food_cutting#': 'cutting'
}


def get_base_iri(el):
    if '#' in el:
        base_iri = el[:el.rindex('#') + 1]
    else:
        base_iri = el[:el.rindex('/') + 1]
    return base_iri


def get_class_name(el):
    if '#' in el:
        cls_name = el[el.rindex('#') + 1:]
    else:
        cls_name = el[el.rindex('/') + 1:]
    return cls_name


def get_prefix(base_iri):
    prefix = PREFIX_MAP.get(base_iri)
    if prefix is None:
        prefix = base_iri[:-1]
        prefix = prefix[prefix.rindex('/') + 1:]
        prefix = prefix.split('.owl')[0]
        if '_' in prefix:
            prefix = prefix.split('_')[-1]
        PREFIX_MAP.update({base_iri: prefix})
        print(base_iri, prefix)
