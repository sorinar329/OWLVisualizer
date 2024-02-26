from rdflib.term import URIRef, Literal, Node
from typing import Union


def uri_or_literal_2label(node: Union[URIRef, Literal, Node, str]) -> str:
    if isinstance(node, Literal):
        return str(node)
    else :
        if '#' in str(node):
            return str(node).split('#')[-1]
        else:
            return str(node).split('/')[-1]

