from rdflib import Graph, OWL, RDFS, BNode, URIRef

"""
Using the following color palette: https://coolors.co/palette/ee6055-60d394-aaf683-ffd97d-ff9b85
"""


class DefaultColors:
    def __init__(self, kg: Graph):
        self.node_colors = {}
        self.colors = ['#EE6055', '#60D394', '#AAF683', '#FF9B85', '#faa307', '#bfd7ea']
        self.kg = kg
        self.set_colors()

    def set_colors(self, color: str = ''):
        classes = list(self.kg.subjects(RDFS.subClassOf, OWL.Thing))
        for i in range(len(classes)):
            top_class = classes[i]
            color2 = color
            if color2 == '':
                color2 = self.colors[i % len(self.colors)]
            assert isinstance(top_class, URIRef)
            self.assign_colors2class(top_class, color2)

    def get_child_nodes(self, node, nodes):
        for child_class in self.kg.subjects(RDFS.subClassOf, node):
            if isinstance(child_class, BNode):
                break
            nodes.append(child_class)
            self.get_child_nodes(child_class, nodes)

    def get_node_colors(self):
        return self.node_colors

    def assign_colors2class(self, cls: URIRef, color: str):
        nodes = [cls]
        for subclass in self.kg.subjects(RDFS.subClassOf, cls):
            nodes.append(subclass)
            self.get_child_nodes(subclass, nodes)

        for node in nodes:
            self.node_colors.update({str(node): color})


class MixingColors(DefaultColors):
    def __init__(self, kg: Graph):
        super(MixingColors, self).__init__(kg)
        self.assign_colors2class(URIRef('http://www.ease-crc.org/ont/mixing#Motion'), '#EE6055')
        self.assign_colors2class(URIRef('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Task'), '#AAF683')
        self.assign_colors2class(URIRef('http://www.ease-crc.org/ont/SOMA.owl#DesignedTool'), '#FF9B85')
        self.assign_colors2class(URIRef('http://www.ease-crc.org/ont/mixing#Ingredient'), '#60D394')


class CuttingColors(DefaultColors):
    def __init__(self, kg: Graph):
        super(CuttingColors, self).__init__(kg)
        self.set_colors('#60D394')
        self.assign_colors2class(URIRef('http://www.ease-crc.org/ont/SOMA.owl#Disposition'), '#EE6055')
        self.assign_colors2class(URIRef('http://www.ontologydesignpatterns.org/ont/dul/DUL.owl#Task'), '#AAF683')
        self.assign_colors2class(URIRef('http://www.ease-crc.org/ont/food_cutting#Tool'), '#FF9B85')
