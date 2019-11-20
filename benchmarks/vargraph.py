#!/usr/bin/python

from enum import Enum

import json
import networkx as nx
import matplotlib.pyplot as plt

from benchmarks.relater import Relater


class VarType(Enum):
    V = 1,
    T = 2


class Variable:
    def __init__(self, index, var_type: VarType):
        self.__name = str(var_type.name) + str(index)
        self.__type = var_type
        self.__index = index

    def __hash__(self):
        return hash((self.__name, self.__type))

    def __eq__(self, other):
        if other is None:
            return False
        return self.__name == other.__name and self.__type == other.__type

    def __str__(self):
        return self.__name

    def __repr__(self):
        return self.__str__()

    @property
    def index(self):
        return self.__index

    @property
    def type(self) -> VarType:
        return self.__type

    @property
    def name(self) -> str:
        return self.__name

    def is_of_type(self, var_type: VarType) -> bool:
        return self.__type == var_type


def __parse_assignment(graph, op, level):
    level = op[1]
    conditional_path = op[2]
    index = op[3]
    left = op[4][0]
    right = op[4][1]

    res_node = Variable(index, VarType.V)
    res_node_temp = Variable(index, VarType.T)

    left_op, left_nodes, left_top = __parse_default(graph, left, level)
    right_op, right_nodes, right_top = __parse_default(graph, right, level)

    left_nodes.extend(right_nodes)
    nodes = list(set(left_nodes))

    if res_node_temp in nodes:
        res_node = res_node_temp
    if left_top is not None and left_top != res_node and left_top != res_node_temp:
        graph.add_edge(left_top, res_node, weight=level)
    if right_top is not None and right_top != res_node and right_top != res_node_temp:
        graph.add_edge(right_top, res_node, weight=level)

    return op[0], nodes, res_node


def __parse_expression(graph, op, level):
    op_type = op[1]
    conditional_path = op[2]
    index = op[2]
    left = op[3]
    right = None
    if 5 == len(op):
        right = op[4]

    res_node = Variable(index, VarType.V)
    res_node_temp = Variable(index, VarType.T)

    left_op, left_nodes, left_top = __parse_default(graph, left, level)
    right_op, right_nodes, right_top = __parse_default(graph, right, level)

    left_nodes.extend(right_nodes)
    nodes = list(set(left_nodes))

    if res_node not in nodes and res_node_temp not in nodes:
        nodes.append(res_node)
        graph.add_node(res_node)
    if res_node_temp in nodes:
        res_node = res_node_temp
    if left_top is not None and left_top != res_node and left_top != res_node_temp:
        graph.add_edge(left_top, res_node, weight=level)
    if right_top is not None and right_top != res_node and right_top != res_node_temp:
        graph.add_edge(right_top, res_node, weight=level)

    return op[0], nodes, res_node


def __parse_conditional_exp(graph, op, level):
    level = op[1]
    conditional_path = op[2]
    op_type = op[3]
    index = op[4]
    left = op[5][0]
    right = op[5][1]
    node = Variable(index, VarType.V)
    return op[0], [], node


def __parse_primitive(graph, op, level):
    op_type = op[1]
    return op[0], [], None


def __parse_var(graph, op, level):
    node = Variable(op[1], VarType.V)
    if node not in graph.nodes():
        graph.add_node(node)
    return op[0], [node], node


def __parse_temp(graph, op, level):
    content = op[2]

    node = Variable(op[1], VarType.T)
    if node not in graph.nodes():
        graph.add_node(node)
    nodes = [node]
    cast_op, cast_nodes, _ = __parse_default(graph, content, level)
    nodes.extend(cast_nodes)
    if cast_op in ['VV', 'V', 'F', 'E']:
        for n in cast_nodes:
            graph.add_edge(n, node, weight=level)
            nodes.remove(n)
    nodes = list(set(nodes))
    return op[0], nodes, node


def __parse_function(graph, op, level):
    return_type = op[1]
    _, nodes, top_node = __parse_default(graph, return_type, level)
    return op[0], nodes, top_node


def __parse_constant(graph, op, level):
    const_type = op[1]
    value = op[2]
    return op[0], [], None


__parser = {
    'A': __parse_assignment,
    'R': __parse_conditional_exp,
    'P': __parse_primitive,
    'V': __parse_var,
    'E': __parse_expression,
    'T': __parse_temp,
    'F': __parse_function,
    'C': __parse_constant
}


def __parse_default(graph, op, level):
    if op is None or op[0] is None:
        return 'VV', [], None
    if 1 == len(op):
        op = op[0]
    return __parser[op[0]](graph, op, level)


def __merge_nodes(graph):
    tnodes = []
    vnodes = []
    for node in graph.nodes():
        if node.is_of_type(VarType.T):
            tnodes.append(node)
        else:
            vnodes.append(node)
    for tn in tnodes:
        for vn in vnodes:
            if tn.index == vn.index:
                graph = nx.contracted_nodes(graph, vn, tn)
                break
    return graph


def parse_vars_file(file: str) -> nx.DiGraph:
    with open(file) as jfile:
        data = json.load(jfile)
    graph = nx.DiGraph()
    for op in data:
        __parse_default(graph, op, 0)
    return __merge_nodes(graph)


def plot(graph: nx.DiGraph):
    # Creates the figure the draw call will use
    fig = plt.figure()
    nx.draw_kamada_kawai(graph, with_labels=True, node_size=512, alpha=1, font_weight='bold')
    plt.show()


def extract_leq_relations(graph: nx.DiGraph) -> Relater:
    rels = []
    for n in graph.nodes:
        for nn in graph.successors(n):
            # ALERT: it doesn't count those relations where the right variable is temporary (T)
            # if (not only_temp or n.is_of_type(VarType.T)) and not n.is_of_type(VarType.T):
            # if not n.is_of_type(VarType.T):
            rels.append((n, nn))
    return Relater('leq', rels, (lambda v1, v2: v1 <= v2[0]))


def extract_cast_to_temp_relations(graph: nx.DiGraph) -> Relater:
    rels = []
    for n in graph.nodes:
        if n.is_of_type(VarType.T) and 0 < len(list(graph.predecessors(n))):
            rels.append((n, list(graph.predecessors(n))))
    return Relater('cast', rels, (lambda v1, v2: v1 == min(v2)))


if __name__ == '__main__':
    g = parse_vars_file('../flexfloat-benchmarks/correlation/program_vardeps.json')
    plot(g)
