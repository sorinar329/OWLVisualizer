import rdflib
from rdflib import OWL, RDF, RDFS, URIRef
from src.graph import types
from src.graph.graph_utility import recursive_pattern_matching

PREFIX_MAP = {
    str(RDF): 'rdf',
    str(RDFS): 'rdfs',
    str(OWL): 'owl',
    'http://www.ease-crc.org/ont/SOMA.owl#': 'SOMA',
    'http://www.ease-crc.org/ont/mixing#': 'mixing',
    'http://www.ease-crc.org/ont/food_cutting#': 'cutting'
}

triples = [['http://www.ease-crc.org/ont/SOMA.owl#Dicing', 'subClassOf', 'Res-60539982743#AND-50310'],
           ['Res-60539982743#AND-50310', 'hasInputObject some',
            'Res-950690259655#http://www.ease-crc.org/ont/food_cutting#Stripe'],
           [
               'Res-60539982743#AND-50310', 'hasResultObject exactly 1',
               'Res-319911140559#http://www.ease-crc.org/ont/food_cutting#Cube'],
           ]


class SparqlGenerator:
    def __init__(self, knowledge_graph: rdflib.Graph, triples: list[list]):
        self.knowledge_graph = knowledge_graph
        self.triples = triples
        self.sparql_triples = []
        self.sparql_prefixes = set()
        self.sparql_variables = {}
        self.node_counter = {'bnode': 0, 'head': 0, 'tail': 0}
        self.sparql_query = ""

    def generate_sparql_query(self):
        class_triples = []

        cls = self.triples[0][0]

        for triple in self.knowledge_graph.triples((URIRef(cls), None, None)):
            restrictions = []
            recursive_pattern_matching(self.knowledge_graph, triple[2], restrictions)
            class_triples.append(restrictions)
        class_restrictions = [triples2 for triples2 in class_triples if len(triples2) > 0]

        objs = []
        for s, p, o in self.triples:
            if o.startswith('Res'):
                objs.append(o.split('#', 1)[1])
            else:
                objs.append(o)
        idx, matching_obj = 0, 0
        for i in range(len(class_restrictions)):
            objs2 = []
            for _, _, o in class_restrictions[i]:
                objs2.append(str(o))
            if len(set(objs).intersection(set(objs2))) > matching_obj:
                matching_obj = len(set(objs).intersection(set(objs2)))
                idx = i

        matched_triples = class_restrictions[idx]
        matched_triples = [triple for triple in matched_triples if triple[1] != RDF.type]
        for s, p, o in self.knowledge_graph.triples((None, None, matched_triples[0][0])):
            matched_triples.insert(0, [s, p, o])

        # for i in range(len(self.triples)):
        #     _, p, _ = self.triples[i]
        #     objects = p.split(' ')
        #     objects.append(objs[i])
        #     print(objects)
        #     for o in objects:
        #         if types.get_cardinality_type(o):
        #             print(types.get_cardinality_type(o))
        #         if 'AND' in o:
        #            types.get_collection_type('AND')
        #         if 'OR' in o:
        #             types.get_restriction_type('OR')
        #         if types.get_restriction_type(o):
        #             print(types.get_restriction_type(o))

        for triple in matched_triples:
            print(triple)

        for triple in matched_triples:
            self.add_triple(triple)

        for prefix in self.sparql_prefixes:
            self.sparql_query += f'PREFIX {prefix}\n'
        self.sparql_query += "ASK WHERE { \n"
        for sparql_triple in self.sparql_triples:
            self.sparql_query += '    '
            s, p, o = sparql_triple
            self.sparql_query += f'{s} {p} {o}.\n'

        self.sparql_query += '}'
        print(self.sparql_query)

    def add_triple(self, triple: tuple):
        sparql_triple = []
        for el in triple:
            if isinstance(el, rdflib.BNode):
                if self.sparql_variables.get(el) is not None:
                    sparql_triple.append(self.sparql_variables[el])
                else:
                    count = self.node_counter.get("bnode")
                    var = f'?bnode{count}'
                    sparql_triple.append(var)
                    self.sparql_variables.update({el: var})
                    self.node_counter['bnode'] += 1
            else:
                if isinstance(el, URIRef):
                    prefix = self._add_prefix(el)
                    sparql_triple.append(f'{prefix}:{self._get_class_name(str(el))}')
                else:
                    sparql_triple.append(el)
        self.sparql_triples.append(sparql_triple)

    def _get_base_iri(self, el):
        if '#' in el:
            base_iri = el[:el.rindex('#') + 1]
        else:
            base_iri = el[:el.rindex('/') + 1]
        return base_iri

    def _get_class_name(self, el):
        if '#' in el:
            cls_name = el[el.rindex('#') + 1:]
        else:
            cls_name = el[el.rindex('#') + 1:]
        return cls_name

    def _add_prefix(self, el):
        base_iri = self._get_base_iri(str(el))
        prefix = PREFIX_MAP.get(base_iri)
        self.sparql_prefixes.add(f'{prefix}: <{base_iri}>')
        return prefix
    # TODO: Add prefixes not defined in PREFIX_MAP


knowledge_graph = rdflib.Graph().parse("../data/food_cutting.owl")
gen = SparqlGenerator(knowledge_graph, triples)
gen.generate_sparql_query()
