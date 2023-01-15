import operator
import random
import numpy as np

from Cell import Cell
from NEAT.Node import Node
from NEAT.Genome import Genome
from NEAT.ConnectionGene import ConnectionGene
from NEAT.Species import Species


class NEAT:
    def __init__(self, environment=None, total_population=10, total_input_nodes=0, total_output_nodes=0,
                 add_connection_probability=.9,
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

    def sort_species(self):
        sorted_species = {}
        for species in (sorted(self.list_of_Species.values(), key=operator.attrgetter('average_fitness'))):
            sorted_species[species.ID] = species
        self.list_of_Species = sorted_species
        return self.list_of_Species

    def reassign_species(self):
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
                new_species = self.generate_new_species(genome=genome)
                self.list_of_Species[new_species.ID] = new_species

    def generate_new_species(self, genome):
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

    def remove_worst_genome(self, maxTicks):
        sorted_genomes = {}
        senior_genomes = {}
        sorted_senior_genomes = {}
        worst_genome = None
        for genome in (sorted(self.list_of_Genomes.values(), key=operator.attrgetter('adjusted_fitness_score'))):
            sorted_genomes[genome.ID] = genome
            if genome.getCellBody().TotalTimeAliveInTicks >= maxTicks:
                senior_genomes[genome.ID] = genome
        self.list_of_Genomes = sorted_genomes

        if len(senior_genomes) > 0:
            for genome in (sorted(senior_genomes.values(), key=operator.attrgetter('adjusted_fitness_score'))):
                sorted_senior_genomes[genome.ID] = genome
            worst_genome = list(sorted_senior_genomes.values())[0]

            worst_genome.getCellBody().isAlive = False
            del self.Environment.active_cell_dicts[worst_genome.getCellBody().PosX, worst_genome.getCellBody().PosY]
            worst_genome.getSpecies().remove_member(worst_genome)
            del self.list_of_Genomes[worst_genome.ID]
            worst_genome.getCellBody().kill()

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
        attempts = 100
        genome_id = len(self.list_of_Genomes) + 1
        for attempt in range(attempts):
            if genome_id not in self.list_of_Genomes:
                break
            else:
                genome_id += 1
        new_genome = Genome(neat_environment=self, ID=genome_id)
        if self.include_bias:
            new_node = self.get_node(node_id=1)
            new_genome.add_node_to_phenotype(new_node)

        for n_id in range(self.total_nodes):
            new_node = self.get_node(node_id=n_id + 1)

            if n_id + 1 > self.total_sensor_nodes:
                new_genome.add_node_to_phenotype(new_node)
            else:
                new_genome.add_node_to_phenotype(new_node)

        self.list_of_Genomes[genome_id] = new_genome

        return new_genome

    def initialize(self):
        self.__generate_base_nodes()

    def evolve(self, max_ticks_until_update):
        for genome in list(self.list_of_Genomes.values()):
            genome.calculate_adjusted_fitness()

        worst_genome = self.remove_worst_genome(max_ticks_until_update)

        for species in list(self.list_of_Species.values()):
            species.calculate_average_fitness()

        if len(self.list_of_Species) > 0 and worst_genome is not None:
            self.sort_species()
            species_for_breeding = random.choice(list(self.list_of_Species.values()))
            offspring = species_for_breeding.breed()
            active_cell = Cell(self.Environment, worst_genome.getCellBody().PosX, worst_genome.getCellBody().PosY)
            offspring.set_cell_body(active_cell)
            active_cell.set_genome(offspring)
            offspring.getCellBody().ChangeCellColor((0, 255, 255))

        self.reassign_species()


def printGlobalGenes():
    print("Global Genes\n")
    for node_genes in list(neat_environment.list_of_Nodes.values()):
        print("Node ID: {} Type {}".format(node_genes.ID, node_genes.NodeType))
    print()
    for con_genes in list(neat_environment.list_of_Connection_Genes.values()):
        print("Innovation # {}: ({}=>{})".format(con_genes.ID, con_genes.in_node, con_genes.out_node))

    print()


if __name__ == '__main__':
    neat_environment = NEAT(total_population=10,
                            total_input_nodes=3,
                            total_output_nodes=5,
                            include_bias=True)

    print()
    genome = neat_environment.generate_empty_genome()
    genome.add_connection()
    genome.add_node()
    genome.add_node()

    genome2 = neat_environment.generate_empty_genome()
    genome2.add_connection()
    genome2.add_connection()

    printGlobalGenes()
    genome.printGenotype()
    genome2.printGenotype()
