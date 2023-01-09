import random
from NEAT.Genome import Genome


class Species:
    def __init__(self, genome):
        genome.species = self
        self.representative = genome
        self.members = [self.representative]
        self.score = 0.0

    def get_species_size(self):
        return len(self.members)

    def kill(self, diminish_percentage=0.0):
        kill_amount = len(self.members) * diminish_percentage
        self.members = list(sorted(self.members, key=lambda x: x.fitness, reverse=False))
        for i in range(round(kill_amount)):
            self.members[0].species = None
            self.members.pop(0)

    def go_extinct(self):
        for genome in self.members:
            genome.species = None

    def reset(self):
        self.representative = random.choice(self.members)
        for c in self.members:
            c.species = None

        self.members.clear()
        self.members.append(self.representative)
        self.representative.species = self
        self.score = 0

    def remove_member(self, client):
        extinct = False
        self.members.remove(client)
        if len(self.members) <= 1:
            extinct = True
            return extinct
        else:
            return extinct

    def add(self, new_client):
        new_client.species = self
        self.members.append(new_client)

    def evaluate_score(self):
        score = 0
        for mem in self.members:
            score += mem.fitness
        self.score = score / len(self.members)

    def is_compatible(self, genome):
        if self.representative.calc_distance(genome) < genome.neat.species_threshold:
            return True
        else:
            return False

    def breed(self):

        random_member1 = random.choice(self.members)
        random_member2 = random.choice(self.members)

        if random_member1.fitness > random_member2.fitness:
            offspring = Genome.mate(random_member1, random_member2)
            return offspring

        else:
            offspring = Genome.mate(random_member2, random_member1)
            return offspring
