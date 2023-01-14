import numpy as np


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class ConnectionGene:

    def __init__(self, innovation_number, neat_environment, genome=None, in_node=None, out_node=None, weight=None,
                 is_expressed=True):
        self.neat_environment = neat_environment
        self.ID = innovation_number
        self.Genome = genome
        self.InnovationNumber = innovation_number
        self.in_node = in_node
        self.out_node = out_node
        self.weight = weight
        self.is_expressed = is_expressed

    def calculate_connection(self):
        if self.is_expressed:
            output = self.in_node.getInput() * self.weight
            return sigmoid(output)

    def setWeight(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight

    def setGenome(self, genome):
        self.Genome = genome

