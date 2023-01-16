import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class Node:
    def __init__(self, neat_environment, ID, node_type=None):
        self.neat_environment = neat_environment
        self.ID = ID
        self.NodeType = node_type
        self.input = 0
        self.Connection_Genes = {}
        if self.NodeType == 'sensor' or self.NodeType == 'bias':
            self.NodeType_Code = .1
        else:
            self.NodeType_Code = .9

    def add_connection_gene(self, connection_gene):
        in_node, out_node = connection_gene.in_node, connection_gene.out_node
        self.Connection_Genes[in_node, out_node] = connection_gene
        sorted_genes = self.neat_environment.sort_connection_genes(self.Connection_Genes)
        self.Connection_Genes = sorted_genes

    def calculate(self):
        z = 0.0
        for connection_gene in list(self.Connection_Genes.values()):
            if not connection_gene.is_expressed:
                continue
            in_node = connection_gene.getGenome().Node_Genes[connection_gene.in_node]
            output = in_node.getInput() * connection_gene.weight
            z += output
        self.set_input(sigmoid(z))
        return self.input

    def set_input(self, input):
        self.input = input

    def getInput(self):
        return self.input

# import numpy as np
#
#
# def sigmoid(z):
#     return 1 / (1 + np.exp(-z))
#
#
# class Node:
#     def __init__(self, x):
#         self.id = None
#         self.x = x
#         self.connections = {}
#         self.output = 0
#
#     def calculate(self):
#         z = 0.0
#         for connection in list(self.connections):
#             in_node_out = self.connections[connection].in_node.output
#             weight = self.connections[connection].weight
#             is_expressed = self.connections[connection].is_expressed
#             if is_expressed:
#                 z += in_node_out * weight
#
#         self.output = sigmoid(z)
#
#         return self.output
