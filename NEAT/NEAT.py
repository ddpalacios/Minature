import random
import numpy as np
from Node import Node
from Genome import Genome
from ConnectionGene import ConnectionGene


class NEAT:
    def __init__(self, environment=None, total_population=10, total_input_nodes=0, total_output_nodes=0,
                 add_connection_probability=.3,
                 add_node_probability=.2, include_bias=False):
        self.ID = 0
        self.Environment = environment
        self.total_population = total_population
        self.total_sensor_nodes = total_input_nodes
        self.total_output_nodes = total_output_nodes
        self.include_bias = include_bias
        self.total_hidden_nodes = 0
        self.total_nodes = total_input_nodes + total_output_nodes
        self.add_connection_probability = add_connection_probability
        self.add_node_probability = add_node_probability
        self.InnovationNumber = 0

        self.list_of_Connection_Genes = {}
        self.list_of_Nodes = {}
        self.list_of_Genomes = {}

    def get_node(self, node_id):
        if node_id in self.list_of_Nodes:
            node = self.list_of_Nodes[node_id]
            return node
        else:
            node = Node(self, node_id)
            self.list_of_Nodes[node.ID] = node

        return node

    def get_connection(self, in_node, out_node):
        if (in_node, out_node) in self.list_of_Connection_Genes:
            return self.list_of_Connection_Genes[in_node, out_node]
        else:
            connection_gene = ConnectionGene(innovation_number=len(self.list_of_Connection_Genes) + 1,
                                             neat_environment=self,
                                             in_node=in_node,
                                             out_node=out_node,
                                             weight=np.random.randn(),
                                             is_expressed=True)

            self.list_of_Connection_Genes[connection_gene.in_node, connection_gene.out_node] = connection_gene
            return connection_gene

    def __generate_base_nodes(self):
        node_id = 1
        if self.include_bias:
            self.list_of_Nodes[node_id] = Node(self, node_id, 'bias')
            self.total_nodes += 1
            node_id += 1
        for n_id in range(self.total_sensor_nodes):
            self.list_of_Nodes[node_id] = Node(self, node_id, 'sensor')
            node_id += 1
        self.total_sensor_nodes = len(list(self.list_of_Nodes))
        for n_id in range(self.total_output_nodes):
            self.list_of_Nodes[node_id] = Node(self, node_id, 'output')
            node_id += 1

    def __generate_base_genomes(self):
        genome_id = 0
        for g_id in range(self.total_population):
            new_genome = Genome(neat_environment=self, ID=genome_id)
            for n_id in range(self.total_nodes):
                new_node = self.get_node(node_id=n_id + 1)
                new_genome.Node_Genes[new_node.ID] = new_node
            self.list_of_Genomes[genome_id] = new_genome
            genome_id += 1

    def initialize(self):
        self.__generate_base_nodes()
        self.__generate_base_genomes()


if __name__ == '__main__':
    neat_environment = NEAT(total_population=10,
                            total_input_nodes=3,
                            total_output_nodes=2,
                            include_bias=False)

    neat_environment.initialize()
    print("Total Nodes", neat_environment.total_nodes)
    for n in list(neat_environment.list_of_Genomes):
        genome = neat_environment.list_of_Genomes[n]

        if n == 0:
            genome.add_connection()
            genome.add_node()
            genome.add_node()


            print("genome", 'total connection genes', len(genome.Connection_Genes),
                  list(genome.Connection_Genes.keys()))
            print("genome", 'total nodes', len(genome.Node_Genes), list(genome.Node_Genes.keys()))

    # def __init__(self,
    #              ins,
    #              outs,
    #              bias=False,
    #              species_threshold=20,
    #              survival_percentage=.7,
    #              total_population=10,
    #
    #              probability_mutate_add_node=0.2,
    #              probability_mutate_add_conn=0.2,
    #
    #              probability_mutate_weight_random=0.8,
    #              probability_mutate_weight_shift=0.8,
    #
    #              probability_mutate_toggle_link=0.3,
    #              mutate_weight_random_strength=0.8,
    #              weight_shift_strength=0.8,
    #              generations=500,
    #              c1=1,
    #              c2=1,
    #              c3=1):
    #
    #     self.all_connections = {}  # all connections
    #     self.nodes = []  # all nodes
    #     self.species = []  # Our entire species
    #     self.genomes = []  # Our entire population
    #     self.env = None
    #
    #     self.bias = bias
    #     self.c1 = c1
    #     self.c2 = c2
    #     self.c3 = c3
    #     self.ins = ins
    #     self.outs = outs
    #     self.mutate_link_rate = probability_mutate_add_conn
    #     self.mutate_node_rate = probability_mutate_add_node
    #     self.survival_percentage = survival_percentage
    #     self.mutate_weight_random_strength = mutate_weight_random_strength
    #     self.PROBABILITY_MUTATE_WEIGHT_RANDOM_STRENGTH = probability_mutate_weight_random
    #     self.PROBABILITY_MUTATE_TOGGLE_LINK = probability_mutate_toggle_link
    #     self.weight_shift_strength = weight_shift_strength
    #     self.PROBABILITY_MUTATE_WEIGHT_SHIFT = probability_mutate_weight_shift
    #     self.total_population = total_population
    #     self.species_threshold = species_threshold
    #     self.generations = generations
    #     # self.reset()
    #
    # def get_avg_species_score(self):
    #     score = 0
    #     for i in self.species:
    #         score+= i.score
    #     return score / len(self.species)
    #
    # def setReplaceIndex(self, in_node, out_node, id):
    #     pair = (in_node, out_node)
    #     connection = self.all_connections[pair]
    #     connection.setReplaceIndex(id)
    #
    # def getReplaceIndex(self, in_node, out_node):
    #     pair = (in_node, out_node)
    #     connection = self.all_connections[pair]
    #     if connection is None:
    #         return 0
    #     else:
    #         return connection.getReplaceIndex()
    #
    # def empty_genome(self):
    #     genome = Genome()
    #     genome.neat = self
    #     total_inputs = self.ins + self.outs
    #     if self.bias:
    #         total_inputs = self.ins + 1 + self.outs
    #     for i in range(total_inputs):
    #         node_gene = self.get_node(id=i + 1)
    #         genome.node_genes.append(node_gene)
    #     return genome
    #
    # def reset(self):
    #     if self.bias:
    #         node_gene = self.get_node(id=len(self.nodes) + 1, node_type="bias")
    #         node_gene.x = 0.1
    #
    #     for i in range(self.ins):
    #         node_gene = self.get_node(id=len(self.nodes) + 1, node_type="sensor")
    #         node_gene.x = 0.1
    #         node_gene.y = (i + 1) / self.outs + 1
    #
    #     for i in range(self.outs):
    #         node_gene = self.get_node(id=len(self.nodes) + 1, node_type="output")
    #         node_gene.x = 0.9
    #         node_gene.y = (i + 1) / self.outs + 1
    #
    #     for i in range(self.total_population):
    #         genome = self.empty_genome()
    #         self.genomes.append(genome)
    #
    # def get_node(self, id, node_type=None):
    #     if id <= len(self.nodes):
    #         return self.nodes[id - 1]
    #     else:
    #         return self._generate_new_node(id, node_type=node_type)
    #
    # def _generate_new_node(self, id, node_type=None):
    #     new_node = NodeGene(id, node_type)
    #     self.nodes.append(new_node)
    #     return new_node
    #
    # def getConnection(self, conn):
    #     c = ConnectionGene(in_node=conn.in_node, out_node=conn.out_node)
    #     c.innovation_number = conn.innovation_number
    #     c.weight = conn.weight
    #     c.is_expressed = conn.is_expressed
    #     return c
    #
    # def get_connection_gene(self, in_node, out_node):
    #     connection_gene = ConnectionGene(in_node=in_node, out_node=out_node)
    #
    #     node_pairs = (connection_gene.in_node, connection_gene.out_node)
    #
    #     if node_pairs in self.all_connections:
    #         connection_gene.innovation_number = self.all_connections[node_pairs].innovation_number
    #     else:
    #         connection_gene.innovation_number = len(self.all_connections) + 1
    #         self.all_connections[node_pairs] = connection_gene
    #
    #     return connection_gene
    #
    # def generate_species(self):
    #     for genome in self.genomes:
    #         if genome.species is not None: continue
    #         found = False
    #         for idx, s in enumerate(self.species):
    #             if s.is_compatible(genome):
    #                 s.add(genome)
    #                 found = True
    #                 break
    #
    #         if not found:
    #             self.species.append(Species(genome))
    #
    # def evaluate_average_fitness_per_species(self):
    #     for species in self.species:
    #         if len(species.members) > 0:
    #             species.evaluate_score()  # evaluate score per species
    #
    # def reproduce(self):
    #     for idx, client in enumerate(self.genomes):
    #         if client.species is None:
    #             random_species = random.choice(self.species)
    #             offspring = random_species.breed()
    #             random_species.add(offspring)
    #             self.genomes[idx] = offspring
    #
    # def survival_of_the_fittest(self):
    #     for species in self.species:
    #         species.kill(1 - self.survival_percentage)
    #
    #     for i in range(len(self.species) - 1, -1, -1):  # checking which species to kill off
    #         existing_species = self.species[i]
    #         if len(existing_species.members) <= 1:
    #             existing_species.go_extinct()
    #             self.species.remove(existing_species)
    #
    # def mutate(self):
    #     for genome in self.genomes:
    #         genome.mutate()
    #
    # def regenerate_species(self):
    #     if len(self.species) > 0:
    #         for species in self.species:
    #             species.reset()
    #     self.generate_species()
    #
    # def evolve(self, entities):
    #
    #     self.regenerate_species()
    #     self.survival_of_the_fittest()
    #     self.reproduce()
    #     self.mutate()
    #
    #     for idx, genome in enumerate(self.genomes):
    #         genome.gen_calculator()
    #         entities[idx].genome = genome
    #
    #     return entities
