"""This file contains breadth-first search utility for dependency graph.
"""

from __future__ import unicode_literals, print_function
import sys
import copy


def _has_node(path, node, node_equal):
    for n in path:
        if node_equal(n, node):
            return True
    return False


def shortest_path(src_path, dst_node, next_nodes_getter, node_equal, must_contain_other_node=False):
    """Find the shortest path from src to dst. The direction of the search is
    defined in the next nodes getter, and transparent to the search algorithm.
    """
    queue = [src_path]

    while len(queue) > 0:
        partial = queue.pop(0)
        last_node = partial[-1]

        next_nodes = next_nodes_getter(last_node)
        for next_node in next_nodes:
            if node_equal(next_node, dst_node):
                partial.append(next_node)
                if must_contain_other_node and len(partial) < 3:
                    continue
                return partial
            elif _has_node(partial, next_node, node_equal):
            #elif next_node in partial:
                # Sometimes a sentence with conjuction will have
                # a circle on the first conjuncted node, with the circle
                # tagged as "conj:and" or similar. This is possibly
                # created by the ccprocessed option. We don't add its
                # branch into the queue.
                # print(graph.name, "circle detected,",
                #       "duplicate ndoe:", next_node,
                #       " is root:", graph.is_root(next_node),
                #       file=sys.stderr)
                pass
            else:
                # We need to copy the list here, since partial may be used
                # multiple times in this loop.
                # branch = copy.deepcopy(partial)
                branch = partial + [next_node]
                # branch.append(next_node)
                queue.append(branch)
    return None
