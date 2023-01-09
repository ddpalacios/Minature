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

    def setWeight(self, weight):
        self.weight = weight

    def getWeight(self):
        return self.weight

    def setGenome(self, genome):
        self.Genome = genome

        # self.in_node = in_node
        # self.out_node = out_node
        # self.weight = weight
        # self.is_expressed = is_expressed
        # self.replace_index = 0
        # self.innovation_number = innovation_number

    # def setReplaceIndex(self, idx):
    #     self.replace_index = idx
    #
    # def getReplaceIndex(self):
    #     return self.replace_index
