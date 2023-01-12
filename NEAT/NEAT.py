import operator
import random
import numpy as np
from NEAT.Node import Node
from NEAT.Genome import Genome
from NEAT.ConnectionGene import ConnectionGene
from NEAT.Species import Species


class NEAT:
    def __init__(self, environment=None, total_population=10, total_input_nodes=0, total_output_nodes=0,
                 add_connection_probability=.3,
                 add_node_probability=.2, include_bias=False,
                 species_threshold=3,
                 excess_coefficient=1,
                 disjoint_coefficient=1,
                 weight_coefficient=1
                 ):
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
        self.excess_coefficient = excess_coefficient
        self.disjoint_coefficient = disjoint_coefficient
        self.weight_coefficient = weight_coefficient
        self.species_threshold = species_threshold

        self.list_of_Connection_Genes = {}
        self.list_of_Nodes = {}
        self.list_of_Genomes = {}
        self.list_of_Species = {}
        self.initialize()

    def get_node(self, node_id):
        if node_id in self.list_of_Nodes:
            node = self.list_of_Nodes[node_id]
            return node
        else:
            node = Node(self, node_id)
            self.list_of_Nodes[node.ID] = node

        return node

    def set_environment(self, env):
        self.Environment = env

    def __sort_species(self):
        sorted_species = {}
        for species in (sorted(self.list_of_Species.values(), key=operator.attrgetter('average_fitness'))):
            sorted_species[species.ID] = species
        self.list_of_Species = sorted_species
        return self.list_of_Species

    def __reassign_species(self):
        for genome in list(self.list_of_Genomes.values()):
            genome.set_species(None)

            found_species = False
            for species in list(self.list_of_Species.values()):
                if species.is_compatible(genome=genome):
                    found_species = True
                    species.add_member(genome)
                    genome.set_species(species)
                    break
            if not found_species:
                new_species = self.__generate_new_species(genome=genome)
                self.list_of_Species[new_species.ID] = new_species

        print('done')

    def __generate_new_species(self, genome):
        species = Species(ID=len(self.list_of_Species) + 1, neat_environment=self)
        genome.set_species(species)
        species.set_representative(genome)
        return species

    def get_connection(self, in_node, out_node):
        if (in_node, out_node) in self.list_of_Connection_Genes:
            return self.list_of_Connection_Genes[in_node, out_node]
        else:
            self.InnovationNumber = len(self.list_of_Connection_Genes) + 1
            connection_gene = ConnectionGene(innovation_number=self.InnovationNumber,
                                             neat_environment=self,
                                             in_node=in_node,
                                             out_node=out_node,
                                             weight=np.random.randn(),
                                             is_expressed=True)

            self.list_of_Connection_Genes[connection_gene.in_node, connection_gene.out_node] = connection_gene
            sorted_genes = self.sort_connection_genes(self.list_of_Connection_Genes)
            self.list_of_Connection_Genes = sorted_genes
            return connection_gene

    def remove_worst_genome(self):
        sorted_genomes = {}
        senior_genomes = {}
        sorted_senior_genomes = {}
        worst_genome = None
        for genome in (sorted(self.list_of_Genomes.values(), key=operator.attrgetter('adjusted_fitness_score'))):
            sorted_genomes[genome.ID] = genome
            if genome.getCellBody().TotalTimeAliveInTicks >= 100:
                senior_genomes[genome.ID] = genome.getCellBody()
        self.list_of_Genomes = sorted_genomes

        if len(senior_genomes) > 0:
            for cell in (sorted(senior_genomes.values(), key=operator.attrgetter('TotalTimeAliveInTicks'))):
                genome = cell.getGenome()
                sorted_senior_genomes[genome.ID] = genome

            worst_genome = list(sorted_senior_genomes.values())[0]
            # del self.list_of_Genomes[worst_genome.ID]

        return worst_genome

    def sort_connection_genes(self, list_of_connection_genes):
        sorted_connection_genes = {}
        for conn in (sorted(list_of_connection_genes.values(), key=operator.attrgetter('InnovationNumber'))):
            pair = (conn.in_node, conn.out_node)
            sorted_connection_genes[pair] = conn
        list_of_connection_genes = sorted_connection_genes
        return list_of_connection_genes

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

    def generate_empty_genome(self):
        genome_id = len(self.list_of_Genomes) + 1
        initial_species = Species(ID=1, neat_environment=self)

        new_genome = Genome(neat_environment=self, ID=genome_id)
        new_genome.set_species(initial_species)

        for n_id in range(self.total_nodes):

            new_node = self.get_node(node_id=n_id + 1)
            new_genome.Node_Genes[new_node.ID] = new_node
            if n_id + 1 > self.total_sensor_nodes:
                new_genome.output_nodes[n_id + 1] = new_node
        self.list_of_Genomes[genome_id] = new_genome

        if initial_species.getRepresentative() is None:
            initial_species.set_representative(new_genome)
            self.list_of_Species[initial_species.ID] = initial_species

        return new_genome

    # def __generate_base_genomes(self):
    #     genome_id = 0
    #     initial_species = Species(ID=1, neat_environment=self)
    #     for g_id in range(self.total_population):
    #         new_genome = Genome(neat_environment=self, ID=genome_id)
    #         new_genome.set_species(initial_species)
    #
    #         for n_id in range(self.total_nodes):
    #             new_node = self.get_node(node_id=n_id + 1)
    #             new_genome.Node_Genes[new_node.ID] = new_node
    #             if n_id + 1 > self.total_sensor_nodes:
    #                 new_genome.output_nodes[n_id + 1] = new_node
    #         self.list_of_Genomes[genome_id] = new_genome
    #
    #         genome_id += 1
    #     random_genome = random.choice(list(initial_species.get_members().values()))
    #     initial_species.set_representative(random_genome)
    #     self.list_of_Species[initial_species.ID] = initial_species

    def initialize(self):
        self.__generate_base_nodes()
        # self.__generate_base_genomes()

    def evolve(self):
        for genome in list(self.list_of_Genomes.values()):
            genome.calculate_adjusted_fitness()
        worst_genome = self.remove_worst_genome()
        for species in list(self.list_of_Species.values()):
            species.calculate_average_fitness()
            self.__sort_species()
            if worst_genome is not None :
                species_for_breeding = random.choice(list(self.list_of_Species.values()))
                offspring = species_for_breeding.breed()
                del self.list_of_Genomes[worst_genome.ID]
                self.__reassign_species()


if __name__ == '__main__':
    neat_environment = NEAT(total_population=10,
                            total_input_nodes=3,
                            total_output_nodes=5,
                            include_bias=True)

    print("Total Nodes", neat_environment.total_nodes)
    # neat_environment.evolve()
    # for n in list(neat_environment.list_of_Genomes):
    #     genome = neat_environment.list_of_Genomes[n]
    #
    #     if n == 0:
    #         genome.add_connection()
    #         genome.add_node()
    #
    #         print("genome", 'total connection genes', len(genome.Connection_Genes),
    #               list(genome.Connection_Genes.keys()))
    #         print("genome", 'total nodes', len(genome.Node_Genes), list(genome.Node_Genes.keys()))
    #
    genome1 = neat_environment.generate_empty_genome()
    genome1.add_connection()
    genome1.add_connection()
    genome1.add_node()

    for node_gene_idx in range(len(genome1.Node_Genes)):
        node_gene = genome1.Node_Genes[node_gene_idx + 1]
        for connection_gene in list(node_gene.Connection_Genes.values()):
            print('node id:', node_gene.ID, node_gene.NodeType, 'in_node', connection_gene.in_node, 'out_node',
                  connection_gene.out_node, 'isExpressed', connection_gene.is_expressed)

    genome2 = neat_environment.generate_empty_genome()
    genome2.add_connection()
    genome2.add_connection()
    genome2.add_connection()
    genome2.add_node()

    offspring = genome2.mate(genome1)
    #
    # print(genome1, genome2)
    # print('offspring', offspring, 'Connections made', len(offspring.Connection_Genes))

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
