"""
    Genomes are linear representations of network connectivity
    Each Genome includes a LIST of CONNECTION GENES
    each of which refers to two NODE GENES being connected.

    Each CONNECTION GENE specifies the 'in-node', 'out-node', the 'weight' of the connection,
    whether or not the connection 'is expressed', and 'innovation number' (which allows to find corresponding genes)


  conn_gene =  Connection Gene:
        in-node: node
        out-node: node
        weight: 0.5
        is_expressed: True
        innovation_number: 1


    Genome.connection_genes.append(conn_gene)

     for connection_gene in Genome.connection_genes:
        print(connection_gene.in_node.id ' => ' connection_gene.out_node.id)


    """

import random


class Genome:
    def __init__(self, ID, neat_environment):
        self.ID = ID
        self.neat_environment = neat_environment
        self.Node_Genes = {}
        self.Connection_Genes = {}

    def add_node(self):
        total_attempts = 100
        for attempt in range(total_attempts):
            random_connection = random.choice(list(self.Connection_Genes.values()))
            if not random_connection.is_expressed:
                continue
            random_connection.is_expressed = False
            new_node = self.neat_environment.get_node(len(self.Node_Genes) + 1)
            new_node.NodeType = 'hidden'
            in_node = self.neat_environment.get_node(random_connection.in_node)
            out_node = self.neat_environment.get_node(random_connection.out_node)
            new_node.NodeType_Code = (in_node.NodeType_Code + out_node.NodeType_Code) / 2
            new_connection1 = self.neat_environment.get_connection(in_node.ID, new_node.ID)
            new_connection2 = self.neat_environment.get_connection(new_node.ID, out_node.ID)
            new_connection1.Genome = self
            new_connection2.Genome = self
            self.Node_Genes[new_node.ID] = new_node
            self.Connection_Genes[new_connection1.in_node, new_connection1.out_node] = new_connection1
            self.Connection_Genes[new_connection2.in_node, new_connection2.out_node] = new_connection2
            return new_node

    def add_connection(self):
        total_attempts = 100
        for attempt in range(total_attempts):
            node1 = random.choice(list(self.Node_Genes.values()))
            node2 = random.choice(list(self.Node_Genes.values()))
            if node1.NodeType_Code == node2.NodeType_Code:
                continue
            if node1.NodeType_Code < node2.NodeType_Code:
                new_connection = self.neat_environment.get_connection(in_node=node1.ID, out_node=node2.ID)
                new_connection.Genome = self
            else:
                new_connection = self.neat_environment.get_connection(in_node=node2.ID, out_node=node1.ID)
                new_connection.Genome = self

            if (new_connection.in_node, new_connection.out_node) in self.Connection_Genes:
                continue
            else:
                new_connection.Genome = self
                self.Connection_Genes[new_connection.in_node, new_connection.out_node] = new_connection
                return

        # self.SpeciesID = None
        # self.Species = None
        # self.Fitness = 0
        # self.hidden_nodes = {}
        # self.sensor_nodes = {}
        # self.output_nodes = {}

    # def getNodeGenes(self):
    #     pass
    #
    # def GetConnectionGenes(self):
    #     pass

    # def add_node(self):
    #     pass
    #
    # def add_connection(self):
    #     pass
    #
    # def mate(self):
    #     pass
    #
    # def initialize_network(self):
    #     pass

    # def __init__(self):
    #     self.generated_calculator = False
    #     self.fitness = 0
    #     self.species = None
    #     self.hidden_nodes = []
    #     self.sensor_nodes = []
    #     self.out_nodes = []
    #     self.connection_genes = {}  # Current connections
    #     self.node_genes = []  # contains inputs, outputs, hidden
    #     self.entity = None
    #     self.neat = None
    #
    # def getEntity(self):
    #     return self.entity
    #
    # def get_species_size(self):
    #     if self.species is None:
    #         return None
    #     else:
    #         return self.species.get_species_size()
    #
    # def get_nodeGenes(self):
    #     return self.node_genes
    #
    # def HasCalculator(self):
    #     return self.generated_calculator
    #
    # def gen_calculator(self):
    #     calc_nodes = {}
    #     self.hidden_nodes = []
    #     self.sensor_nodes = []
    #     self.out_nodes = []
    #
    #     for node_gene in self.node_genes:
    #         # print(node_gene.id)
    #         node = Node(x=node_gene.x)
    #         node.id = node_gene.id
    #         calc_nodes[node_gene.id] = node
    #
    #         if node_gene.x <= .1:
    #             self.sensor_nodes.append(node)
    #         elif node_gene.x >= .9:
    #             self.out_nodes.append(node)
    #         else:
    #             self.hidden_nodes.append(node)
    #
    #     self.hidden_nodes = list(sorted(self.hidden_nodes, key=lambda x: x.id, reverse=False))
    #
    #     for pair in list(self.connection_genes):
    #         con = self.connection_genes[pair]
    #         in_node, out_node = con.in_node, con.out_node # unique genome connections
    #         # print((in_node.id,in_node.x), (out_node.id, out_node.x))
    #         nodeA, nodeB = calc_nodes[in_node.id], calc_nodes[out_node.id]
    #         new_connection = ConnectionGene(in_node=nodeA, out_node=nodeB)
    #         new_connection.weight = con.weight
    #         new_connection.is_expressed = con.is_expressed
    #         nodeB.connections[(new_connection.in_node, new_connection.out_node)] = new_connection
    #
    #     self.generated_calculator = True
    #
    # def calc_distance(self, g2):
    #     g1 = self
    #     highest_innovation_gene1 = 0
    #     if len(list(g1.connection_genes)) != 0:
    #         highest_innovation_gene1 = g1.connection_genes[
    #             list(g1.connection_genes)[len(list(g1.connection_genes)) - 1]].innovation_number
    #
    #     highest_innovation_gene2 = 0
    #     if len(list(g2.connection_genes)) != 0:
    #         highest_innovation_gene2 = g2.connection_genes[
    #             list(g2.connection_genes)[len(list(g2.connection_genes)) - 1]].innovation_number
    #
    #     if highest_innovation_gene1 < highest_innovation_gene2:
    #         g = g1
    #         g1 = g2
    #         g2 = g
    #
    #     index_g1 = 0
    #     index_g2 = 0
    #
    #     disjoint = 0
    #     excess = 0
    #     weight_diff = 0
    #     similar = 0
    #     while index_g1 < len(list(g1.connection_genes)) and index_g2 < len(list(g2.connection_genes)):
    #         gene1 = g1.connection_genes[list(g1.connection_genes)[index_g1]]
    #         gene2 = g2.connection_genes[list(g2.connection_genes)[index_g2]]
    #
    #         in1 = gene1.innovation_number
    #         in2 = gene2.innovation_number
    #
    #         if in1 == in2:
    #             # similar gene
    #             similar += 1
    #             weight_diff += abs(gene1.weight - gene2.weight)
    #             index_g1 += 1
    #             index_g2 += 1
    #         elif in1 > in2:
    #             disjoint += 1
    #             index_g2 += 1
    #         else:
    #             disjoint += 1
    #             index_g1 += 1
    #
    #     weight_diff /= max(1, similar)
    #     excess = len(list(g1.connection_genes)) - index_g1
    #     N = max(len(list(g1.connection_genes)), len(list(g2.connection_genes)))
    #
    #     if N < 20:
    #         N = 1
    #     return self.neat.c1 * disjoint / N + self.neat.c2 * excess / N + self.neat.c3 * weight_diff
    #
    # def mutate(self):
    #     if self.neat.mutate_link_rate > np.random.rand():
    #         self.add_connection()
    #
    #     if self.neat.mutate_node_rate > np.random.rand():
    #         self.add_node()
    #
    #     if self.neat.PROBABILITY_MUTATE_WEIGHT_SHIFT > np.random.rand():
    #         self.mutate_weight_shift()
    #
    #     if self.neat.PROBABILITY_MUTATE_WEIGHT_RANDOM_STRENGTH > np.random.rand():
    #         self.mutate_weight_random()
    #
    #     if self.neat.PROBABILITY_MUTATE_TOGGLE_LINK > np.random.rand():
    #         self.mutate_link_toggle()
    #
    # @staticmethod
    # def mate(g1, g2):
    #     neat = g1.neat
    #     offspring = neat.empty_genome()
    #     index_g1 = 0
    #     index_g2 = 0
    #     while index_g1 < len(g1.connection_genes) and index_g2 < len(g2.connection_genes):
    #         gene1 = list(g1.connection_genes.values())[index_g1]
    #         gene2 = list(g2.connection_genes.values())[index_g2]
    #
    #         in1 = gene1.innovation_number
    #         in2 = gene2.innovation_number
    #
    #         if in1 == in2:
    #             # similar gene
    #             if random.uniform(0, 1) > .5:
    #                 chosen_conn = neat.getConnection(gene1)
    #                 offspring.connection_genes[(chosen_conn.in_node, chosen_conn.out_node)] = chosen_conn
    #             else:
    #                 chosen_conn = neat.getConnection(gene2)
    #                 offspring.connection_genes[(chosen_conn.in_node, chosen_conn.out_node)] = chosen_conn
    #
    #             index_g1 += 1
    #             index_g2 += 1
    #
    #         elif in1 > in2:
    #             index_g2 += 1
    #         else:
    #             chosen_conn = neat.getConnection(gene1)
    #             offspring.connection_genes[(chosen_conn.in_node, chosen_conn.out_node)] = chosen_conn
    #
    #             index_g1 += 1
    #
    #     while index_g1 < len(g1.connection_genes):
    #         gene1 = list(g1.connection_genes.values())[index_g1]
    #         chosen_conn = neat.getConnection(gene1)
    #         offspring.connection_genes[(chosen_conn.in_node, chosen_conn.out_node)] = chosen_conn
    #         index_g1 += 1
    #
    #     for pair in list(offspring.connection_genes):
    #         c = offspring.connection_genes[pair]
    #         if c.in_node not in offspring.node_genes:
    #             offspring.node_genes.append(c.in_node)
    #         if c.out_node not in offspring.node_genes:
    #             offspring.node_genes.append(c.out_node)
    #     return offspring
    #
    # def _add_connection_sorted(self, new_conn):
    #     pair = (new_conn.in_node, new_conn.out_node)
    #     self.connection_genes[pair] = new_conn
    #     sorted_dic = {}
    #     for conn in (sorted(self.connection_genes.values(), key=operator.attrgetter('innovation_number'))):
    #         pair = (conn.in_node, conn.out_node)
    #         sorted_dic[pair] = conn
    #     self.connection_genes = sorted_dic
    #
    # def add_connection(self):
    #     for i in range(100):
    #         nodeA = random.choice(self.node_genes)
    #         nodeB = random.choice(self.node_genes)
    #         if nodeA.x == nodeB.x:
    #             continue
    #         if nodeA.x < nodeB.x:
    #             new_connection = ConnectionGene(in_node=nodeA, out_node=nodeB)
    #         else:
    #             new_connection = ConnectionGene(in_node=nodeB, out_node=nodeA)
    #
    #         if (new_connection.in_node, new_connection.out_node) in self.connection_genes:
    #             continue
    #         else:
    #             new_connection = self.neat.get_connection_gene(in_node=new_connection.in_node,
    #                                                            out_node=new_connection.out_node)
    #             new_connection.weight = (np.random.rand()*2) * self.neat.mutate_weight_random_strength
    #             self._add_connection_sorted(new_connection)
    #
    #             return
    #
    # def add_node(self):
    #     if len(list(self.connection_genes)) > 0:
    #         middle_node = None
    #         random_connection = random.choice(list(self.connection_genes))
    #         random_connection = self.connection_genes[random_connection]
    #         replace_index = self.neat.getReplaceIndex(random_connection.in_node, random_connection.out_node)
    #         if replace_index == 0:
    #             middle_node = self.neat.get_node(id=len(self.neat.nodes) + 1, node_type="hidden")
    #             middle_node.x = ((random_connection.in_node.x + random_connection.out_node.x) / 2)
    #             middle_node.y = ((random_connection.in_node.y + random_connection.out_node.y) / 2 + np.random.rand() * 0.1 - 0.05)
    #             self.neat.setReplaceIndex(random_connection.in_node, random_connection.out_node, middle_node.id)
    #         else:
    #             middle_node = self.neat.get_node(id=replace_index, node_type="hidden")
    #
    #         conn1 = self.neat.get_connection_gene(random_connection.in_node, middle_node)
    #         conn2 = self.neat.get_connection_gene(middle_node, random_connection.out_node)
    #         conn1.weight = 1
    #         conn2.weight = random_connection.weight
    #         conn2.is_expressed = random_connection.is_expressed
    #         if random_connection.in_node.type != "bias":
    #             random_connection.is_expressed = False
    #         self.connection_genes.pop((random_connection.in_node, random_connection.out_node))
    #         self.connection_genes[(conn1.in_node, conn1.out_node)] = conn1
    #         self.connection_genes[(conn2.in_node, conn2.out_node)] = conn2
    #
    #         self.node_genes.append(middle_node)
    #
    # def forward(self, X):
    #     self.gen_calculator()
    #     for index, x_input in enumerate(X):
    #         node = self.sensor_nodes[index]
    #         if index == 0:
    #             node.input = 1
    #             node.output = 1
    #         else:
    #             node.input = x_input
    #             node.output = x_input[0]
    #
    #     for hidden_node in self.hidden_nodes:
    #         hidden_node.calculate()  # sets output calculation for current node
    #
    #     outputs = []
    #     for output_node in self.out_nodes:
    #         output = output_node.calculate()
    #         outputs.append(output)
    #
    #     return outputs
    #
    # def mutate_link_toggle(self):
    #     con_genes = list(self.connection_genes)
    #
    #     if len(con_genes) > 0:
    #         random_connection = random.choice(con_genes)
    #         random_connection = self.connection_genes[random_connection]
    #         if random_connection is not None:
    #             random_connection.is_expressed = False
    #
    # def mutate_weight_random(self):
    #     con_genes = list(self.connection_genes)
    #
    #     if len(con_genes) > 0:
    #         random_connection = random.choice(con_genes)
    #         random_connection = self.connection_genes[random_connection]
    #         if random_connection is not None:
    #             old_weight = random_connection.weight
    #             random_connection.weight = (np.random.rand()*2) * self.neat.mutate_weight_random_strength
    #
    # def mutate_weight_shift(self):
    #     con_genes = list(self.connection_genes)
    #     if len(con_genes) > 0:
    #         random_connection = random.choice(con_genes)
    #         random_connection = self.connection_genes[random_connection]
    #         if random_connection is not None:
    #             old_weight = random_connection.weight
    #             new_weight = old_weight + (np.random.rand()*2) * self.neat.weight_shift_strength
    #
    #             random_connection.weight = new_weight
