from __future__ import unicode_literals, print_function
from collections import defaultdict


class DependencyGraph(object):
    def __init__(self, graph_name=None):
        self.name = graph_name
        self.nodes = set()
        # The value is a set of <dep, relation> pairs.
        self.gov_to_dep = defaultdict(set)
        # The value is a set of <gov, relation> pairs.
        self.dep_to_gov = defaultdict(set)
        # The value is the relation between the gov and dep.
        self.pair_to_relation = defaultdict(str)
        
    def __repr__(self):
        triples = []
        for gov, dep_relations in self.gov_to_dep.items():
            for dep, relation in dep_relations:
                triples.append((gov, dep, relation))
        return str(triples)

    def add_node(self, node):
        self.nodes.add(node)

    @staticmethod
    def build_from_proto(dep_list):
        graph = DependencyGraph()
        for dep in dep_list:
            graph.add_node(dep.gov_index)
            graph.add_node(dep.dep_index)
            graph.add_edge(dep.gov_index, dep.dep_index, dep.relation)
        return graph
            
    def add_edge(self, gov_node, dep_node, relation):
        self.gov_to_dep[gov_node].add((dep_node, relation))
        self.dep_to_gov[dep_node].add((gov_node, relation))
        self.pair_to_relation[(gov_node, dep_node)] = relation

    def get_gov(self, dep_node):
        if dep_node in self.dep_to_gov:
            return [e[0] for e in self.dep_to_gov[dep_node]]
        else:
            # Punctuation may not have heads.
            return []

    def get_dep(self, gov_node):
        if gov_node in self.gov_to_dep:
            return [e[0] for e in self.gov_to_dep[gov_node]]
        else:
            # Leaf nodes have no governer.
            return []
        
    def is_root(self, node):
        next_nodes = self.dep_to_gov.get(node)
        if next_nodes and (node, 'root') in next_nodes:
            return True
        return False

    def get_root(self):
        # Note that there may be multiple roots, not sure why yet.
        return [n for n in self.nodes if self.is_root(n)]
