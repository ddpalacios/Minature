import operator
import random



class Species:
    def __init__(self, ID, neat_environment):
        self.ID = ID
        self.neat_environment = neat_environment
        self.representative = None
        self.members = {}
        self.average_fitness = 0.0

    def breed(self):
        random_genome1 = random.choice(list(self.members.values()))
        random_genome2 = random.choice(list(self.members.values()))
        random_genome1.getCellBody().ChangeCellColor((255,255,255))
        random_genome2.getCellBody().ChangeCellColor((255,255,255))

        if random_genome1.getFitness() > random_genome2.getFitness():
            offspring = random_genome1.mate(random_genome2)
        else:
            offspring = random_genome2.mate(random_genome1)

        offspring.mutate()


        return offspring

    def calculate_average_fitness(self):
        total_fitness = 0
        for genome in list(self.members.values()):
            if not genome.getCellBody().isAlive:
                continue
            total_fitness += genome.getFitness()

        try:
            self.average_fitness = total_fitness / len(self.members)
        except ZeroDivisionError:
            self.average_fitness = 0

    def get_compatibility_distance(self, genome):
        genome_innovation_number_idx = 0
        mate_genome_innovation_number_idx = 0
        matching_genes = 0
        disjoint_genes = 0
        excess_genes = 0
        representative_genome = self.representative
        average_weight_difference = 0

        while genome_innovation_number_idx < len(representative_genome.Connection_Genes) \
                and mate_genome_innovation_number_idx < len(genome.Connection_Genes):

            parent1_connection_gene = list(representative_genome.Connection_Genes.values())[
                genome_innovation_number_idx]
            parent2_connection_gene = list(genome.Connection_Genes.values())[mate_genome_innovation_number_idx]

            parent1_innovation_number = parent1_connection_gene.InnovationNumber
            parent2_innovation_number = parent2_connection_gene.InnovationNumber

            if parent1_innovation_number == parent2_innovation_number:
                matching_genes += 1
                average_weight_difference += abs(
                    parent1_connection_gene.getWeight() - parent2_connection_gene.getWeight())

                genome_innovation_number_idx += 1
                mate_genome_innovation_number_idx += 1

            elif parent1_innovation_number > parent2_innovation_number:
                disjoint_genes += 1
                mate_genome_innovation_number_idx += 1

            else:
                disjoint_genes += 1
                genome_innovation_number_idx += 1

        while genome_innovation_number_idx < len(representative_genome.Connection_Genes):
            genome_innovation_number_idx += 1
            excess_genes += 1

        average_weight_difference /= max(1, matching_genes)
        representative_genes_length = len(representative_genome.Connection_Genes)
        genome_genes_length = len(genome.Connection_Genes)
        normalized_genome_size = 1
        if representative_genes_length > 20 and genome_genes_length > 20:
            if representative_genes_length >= genome_genes_length:
                normalized_genome_size = len(representative_genome.Connection_Genes)
            else:
                normalized_genome_size = len(genome.Connection_Genes)

        compatibility_distance = ((self.neat_environment.excess_coefficient * excess_genes) / normalized_genome_size) + \
                                 ((
                                          self.neat_environment.disjoint_coefficient * disjoint_genes) / normalized_genome_size) + \
                                 self.neat_environment.weight_coefficient * average_weight_difference

        return compatibility_distance

    def is_compatible(self, genome):
        compatibility_distance = self.get_compatibility_distance(genome)
        if compatibility_distance < self.neat_environment.species_threshold:
            return True
        else:
            return False

    def get_members(self):
        return self.members

    def remove_member(self, genome):
        del self.members[genome.ID]

    def add_member(self, genome):
        self.members[genome.ID] = genome

    def getRepresentative(self):
        return self.representative

    def set_representative(self, genome):
        self.representative = genome

    def set_average_fitness(self, average_fitness):
        self.average_fitness = average_fitness

    # def get_species_size(self):
    #     return len(self.members)
    #
    # def kill(self, diminish_percentage=0.0):
    #     kill_amount = len(self.members) * diminish_percentage
    #     self.members = list(sorted(self.members, key=lambda x: x.fitness, reverse=False))
    #     for i in range(round(kill_amount)):
    #         self.members[0].species = None
    #         self.members.pop(0)
    #
    # def go_extinct(self):
    #     for genome in self.members:
    #         genome.species = None
    #
    # def reset(self):
    #     self.representative = random.choice(self.members)
    #     for c in self.members:
    #         c.species = None
    #
    #     self.members.clear()
    #     self.members.append(self.representative)
    #     self.representative.species = self
    #     self.score = 0
    #
    # def remove_member(self, client):
    #     extinct = False
    #     self.members.remove(client)
    #     if len(self.members) <= 1:
    #         extinct = True
    #         return extinct
    #     else:
    #         return extinct
    #
    # def add(self, new_client):
    #     new_client.species = self
    #     self.members.append(new_client)
    #
    # def evaluate_score(self):
    #     score = 0
    #     for mem in self.members:
    #         score += mem.fitness
    #     self.score = score / len(self.members)
    #
    # def is_compatible(self, genome):
    #     if self.representative.calc_distance(genome) < genome.neat.species_threshold:
    #         return True
    #     else:
    #         return False
    #
    # def breed(self):
    #
    #     random_member1 = random.choice(self.members)
    #     random_member2 = random.choice(self.members)
    #
    #     if random_member1.fitness > random_member2.fitness:
    #         offspring = Genome.mate(random_member1, random_member2)
    #         return offspring
    #
    #     else:
    #         offspring = Genome.mate(random_member2, random_member1)
    #         return offspring
