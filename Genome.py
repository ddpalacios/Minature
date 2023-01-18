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
import numpy as np

from ConnectionGene import ConnectionGene
from Node import Node


class Genome:
    def __init__(self, ID, neat_environment):
        self.ID = ID
        self.neat_environment = neat_environment
        self.fitness_score = 0
        self.adjusted_fitness_score = 0
        self.Node_Genes = {}
        self.sensor_nodes = {}
        self.hidden_nodes = {}
        self.output_nodes = {}
        self.Connection_Genes = {}
        self.Species = None
        self.CellBody = None

    def getAdjustedFitness(self):
        return self.adjusted_fitness_score

    def set_cell_body(self, cell):
        self.CellBody = cell

    def getCellBody(self):
        return self.CellBody

    def forward(self, inputs):

        for node_idx, sensor_node in enumerate(list(self.sensor_nodes.values())):
            if sensor_node.NodeType_Code == .1:
                sensor_node.set_input(inputs[node_idx])

        for hidden_node in list(self.hidden_nodes.values()):
            hidden_node.calculate()

        output_probability = []
        for output_node in list(self.output_nodes.values()):
            input_value = output_node.calculate()
            output_probability.append(input_value)

        output = output_probability.index(max(output_probability))
        return output

    def mutate(self):
        if self.neat_environment.add_connection_probability > np.random.rand():
            self.add_connection()

        if self.neat_environment.add_node_probability > np.random.rand():
            self.add_node()

        if self.neat_environment.weight_shift_probability > np.random.rand():
            self.shift_random_weight()

        if self.neat_environment.weight_change_probability > np.random.rand():
            self.mutate_random_weight()

    def mutate_random_weight(self):
        if len(self.Connection_Genes) == 0:
            return
        random_connection = random.choice(list(self.Connection_Genes.values()))
        new_weight = (np.random.randn()) * self.neat_environment.weight_change_strength
        random_connection.setWeight(new_weight)


    def shift_random_weight(self):
        if len(self.Connection_Genes) == 0:
            return
        random_connection = random.choice(list(self.Connection_Genes.values()))
        old_weight = random_connection.getWeight()
        new_weight = (old_weight + np.random.randn()) * self.neat_environment.weight_shift_strength
        random_connection.setWeight(new_weight)

    def add_node_to_phenotype(self, node):
        node = Node(self.neat_environment, node.ID, node_type=node.NodeType)
        if node.NodeType == 'sensor' or node.NodeType == 'bias':
            self.sensor_nodes[node.ID] = node
        if node.NodeType == 'hidden':
            self.hidden_nodes[node.ID] = node
        if node.NodeType == 'output':
            self.output_nodes[node.ID] = node

        self.Node_Genes[node.ID] = node

        return node

    def add_node(self):
        if len(self.Connection_Genes) == 0:
            return
        for attempt in range(100):

            random_connection = random.choice(list(self.Connection_Genes.values()))
            random_connection.is_expressed = False

            new_node = self.neat_environment.get_node(len(self.Node_Genes) + 1)
            if random_connection.in_node == new_node.ID or random_connection.out_node == new_node.ID:
                continue
            new_node.NodeType = 'hidden'
            new_node = self.add_node_to_phenotype(new_node)

            in_node = self.Node_Genes[random_connection.in_node]
            out_node = self.Node_Genes[random_connection.out_node]

            new_node.NodeType_Code = (in_node.NodeType_Code + out_node.NodeType_Code) / 2

            # print('nodes to connect', in_node.ID , '=>', new_node.ID,'=>',out_node.ID)

            new_connection1 = self.neat_environment.get_connection(in_node.ID, new_node.ID)
            # print('conn1',new_connection1.in_node, '=>', new_connection1.out_node)

            new_connection2 = self.neat_environment.get_connection(new_node.ID, out_node.ID)
            # print('conn2', new_connection2.in_node, '=>', new_connection2.out_node)

            new_connection1 = self.add_connection_to_phenotype(new_connection1)
            new_connection2 = self.add_connection_to_phenotype(new_connection2)
            new_connection1.setWeight(1)
            new_connection2.setWeight(random_connection.getWeight())

            new_node.add_connection_gene(new_connection1)
            # in_node.add_connection_gene(new_connection1)
            out_node.add_connection_gene(new_connection2)

            return new_node

    def add_connection_to_phenotype(self, connection_gene):
        new_connection = ConnectionGene(innovation_number=connection_gene.ID,
                                        neat_environment=self.neat_environment,
                                        in_node=connection_gene.in_node,
                                        out_node=connection_gene.out_node,
                                        weight=np.random.randn(),
                                        is_expressed=True)
        new_connection.setGenome(self)
        self.Connection_Genes[new_connection.in_node, new_connection.out_node] = new_connection
        sorted_genes = self.neat_environment.sort_connection_genes(self.Connection_Genes)
        self.Connection_Genes = sorted_genes
        return new_connection

    def add_connection(self):
        total_attempts = 100
        for attempt in range(total_attempts):
            node1 = random.choice(list(self.Node_Genes.values()))
            node2 = random.choice(list(self.Node_Genes.values()))
            if node1.NodeType_Code == node2.NodeType_Code:
                continue
            if node1.NodeType_Code < node2.NodeType_Code:
                new_connection = self.neat_environment.get_connection(in_node=node1.ID, out_node=node2.ID)
            else:
                new_connection = self.neat_environment.get_connection(in_node=node2.ID, out_node=node1.ID)

            if (new_connection.in_node, new_connection.out_node) in self.Connection_Genes:
                continue
            else:
                new_connection = self.add_connection_to_phenotype(new_connection)
                node2.add_connection_gene(new_connection)
                return

    def mate(self, genome):
        genome_innovation_number_idx = 0
        mate_genome_innovation_number_idx = 0
        matching_genes = 0
        disjoint_genes = 0
        excess_genes = 0
        offspring_genome = self.neat_environment.generate_empty_genome()

        while genome_innovation_number_idx < len(self.Connection_Genes) and mate_genome_innovation_number_idx < len(
                genome.Connection_Genes):
            parent1_connection_gene = list(self.Connection_Genes.values())[genome_innovation_number_idx]
            parent2_connection_gene = list(genome.Connection_Genes.values())[mate_genome_innovation_number_idx]

            parent1_innovation_number = parent1_connection_gene.InnovationNumber
            parent2_innovation_number = parent2_connection_gene.InnovationNumber

            if parent1_innovation_number == parent2_innovation_number:
                matching_genes += 1
                random_connection = random.choice([parent1_connection_gene, parent2_connection_gene])
                offspring_genome.Connection_Genes[
                    (random_connection.in_node, random_connection.out_node)] = random_connection
                genome_innovation_number_idx += 1
                mate_genome_innovation_number_idx += 1

            elif parent1_innovation_number > parent2_innovation_number:
                disjoint_genes += 1
                mate_genome_innovation_number_idx += 1
            else:
                disjoint_genes += 1
                genome_innovation_number_idx += 1
                offspring_genome.Connection_Genes[
                    (parent1_connection_gene.in_node, parent1_connection_gene.out_node)] = parent1_connection_gene

        while genome_innovation_number_idx < len(self.Connection_Genes):
            excess_connection_gene = list(self.Connection_Genes.values())[genome_innovation_number_idx]
            offspring_genome.Connection_Genes[
                (excess_connection_gene.in_node, excess_connection_gene.out_node)] = excess_connection_gene
            genome_innovation_number_idx += 1
            excess_genes += 1

        return offspring_genome

    def printGenotype(self):
        print("\nGenome #{}\n".format(self.ID))
        for node_genes in list(self.Node_Genes.values()):
            print("Node ID: {} Type {}".format(node_genes.ID, node_genes.NodeType))
        print()
        for con_genes in list(self.Connection_Genes.values()):
            print("Innovation Number: {}\nPair: ({}=>{})\nWeight: {}\nIsExpressed: {}\n".format(con_genes.ID,
                                                                                                con_genes.in_node,
                                                                                                con_genes.out_node,
                                                                                                con_genes.weight,
                                                                                                con_genes.is_expressed))

    def set_species(self, species):
        self.Species = species
        if species is not None:
            species.add_member(genome=self)

    def getSpecies(self):
        return self.Species

    def calculateFitness(self):
        self.fitness_score = self.getCellBody().TotalStepsTaken **2 - self.getCellBody().getEnergyLevel()#(self.getCellBody().TotalEnergyObtained+ self.getCellBody().getEnergyLevel()) + self.getCellBody().TotalStepsTaken ** 2
        # self.getCellBody().getEnergyLevel() + (
        #         self.getCellBody().TotalStepsTaken + self.getCellBody().TotalEnergyObtained)

    def getFitness(self):
        return self.fitness_score

    def calculate_adjusted_fitness(self):
        if self.Species is not None:
            species_member_size = len(self.Species.get_members())
            self.adjusted_fitness_score = self.fitness_score / species_member_size
        else:
            species_member_size = len(self.neat_environment.list_of_Genomes)
            self.adjusted_fitness_score = self.fitness_score / species_member_size
