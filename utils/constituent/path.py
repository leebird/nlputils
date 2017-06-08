from __future__ import unicode_literals, print_function
from ..search.bfs import shortest_path


def undirected_shortest_const_path(parse, src, dst):
    # Note that this function only accepts non-terminal nodes.
    # It will return None if the dst is a terminal node as
    # it will never reach those which are filtered out.
    if src == dst:
        return []

    src_path = [src]

    def elements_getter(ele):
        yield parse[ele.parent]
        for child in ele.children:
            if len(parse[child].children) == 0:
                # Filter out terminal nodes.
                break
            yield parse[child]

    def node_equal(node1, node2):
        return node1.index == node2.index

    return shortest_path(src_path, dst, elements_getter, node_equal)
