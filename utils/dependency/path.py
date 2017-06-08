from __future__ import unicode_literals, print_function
from collections import namedtuple
from enum import Enum
from ..search.bfs import shortest_path


class PathDirection(Enum):
    """Define the search direction, either from governer to dependent, or
    from dependent to governer.
    """
    gov_to_dep = 1
    dep_to_gov = 2

PathNode = namedtuple('PathNode',
                      ['token_index',
                       'relation_with_prev',
                       'direction_from_prev'])


'''
class PathElement(object):
    def __init__(self, token_index, relation_with_prev, direction_from_prev):
        self.token_index = token_index
        self.relation_with_prev = relation_with_prev
        self.direction_from_prev = direction_from_prev
    
    def __eq__(self, other):
        """We only require the token index to be equal.
        """
        return self.token_index == other.token_index
'''

'''
class DependencyPath(object):
    def __init__(self):
        self.elements = []
    
    def __iter__(self):
        for ele in self.elements:
            yield ele
    
    def __getitem__(self, item):
        return self.elements[item]
    
    def append(self, element):
        self.elements.append(element)
    
    def add_element(self, token_index, relation, direction_from_prev):
        element = PathElement(token_index, relation, direction_from_prev)
        self.elements.append(element)

    @property
    def token_index(self):
        return [e.token_index for e in self.elements]
    
    @property
    def relation(self):
        return [e.relation for e in self.elements[1:]]
'''

def directed_shortest_path(graph, src, dst, direction=PathDirection.gov_to_dep):
    src_path = []
    src_path.append(PathNode(src, None, None))
    dst_element = PathNode(dst, None, None)

    # Sometimes a punctuation may be involved, and it may not
    # have governers (next_nodes = []).
    if direction is PathDirection.gov_to_dep:
        elements_map = graph.gov_to_dep
    elif direction is PathDirection.dep_to_gov:
        elements_map = graph.dep_to_gov
    else:
        raise ValueError

    def elements_getter(ele):
        for index, relation in elements_map[ele.token_index]:
            yield PathNode(index, relation, PathDirection.gov_to_dep)
    
    return shortest_path(graph, src_path, dst_element, elements_getter)
    

def undirected_shortest_dep_path(graph, src, dst, must_contain_other_node=False):
    # If src and dst are same node, return empty path.
    if src == dst:
        return []

    src_path = [PathNode(src, None, None)]
    dst_node = PathNode(dst, None, None)

    def elements_getter(ele):
        for index, relation in graph.gov_to_dep[ele.token_index]:
            yield PathNode(index, relation, PathDirection.gov_to_dep)
        for index, relation in graph.dep_to_gov[ele.token_index]:
            yield PathNode(index, relation, PathDirection.dep_to_gov)

    def node_equal(node1, node2):
        return node1.token_index == node2.token_index
            
    return shortest_path(src_path, dst_node, elements_getter, node_equal, must_contain_other_node)
