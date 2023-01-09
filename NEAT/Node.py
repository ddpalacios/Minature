class Node:
    def __init__(self,neat_environment, ID, node_type=None):
        self.neat_environment = neat_environment
        self.ID = ID
        self.NodeType = node_type
        if self.NodeType == 'sensor' or self.NodeType == 'bias':
            self.NodeType_Code = .1
        else:
            self.NodeType_Code = .9


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