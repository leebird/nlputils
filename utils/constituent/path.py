from __future__ import unicode_literals, print_function
from ..search.bfs import shortest_path


def undirected_shortest_const_path(parse, src, dst):
    src_path = [src]

    def elements_getter(ele):
        yield parse[ele.parent]
        for child in ele.children:
            if len(parse[child].children) == 0:
                # Ignore terminal nodes.
                break
            yield parse[child]

    def node_equal(node1, node2):
        return node1.index == node2.index

    return shortest_path(src_path, dst, elements_getter, node_equal)
