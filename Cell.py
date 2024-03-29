import datetime
import pygame as pg

pg.init()
from SQlite import SQLLite
import random

import numpy as np
from sklearn.preprocessing import StandardScaler


class Cell(pg.sprite.Sprite):
    def __init__(self, environment, xpos, ypos, cell_color=(0, 0, 255)):
        self.sql_db = SQLLite()
        self.environment = environment
        pg.sprite.Sprite.__init__(self, environment.active_cell_entities)
        self.image = pg.Surface((self.environment.pixelSize, self.environment.pixelSize))
        self.image.fill(cell_color)
        self.rect = self.image.get_rect()
        self.entity_name = 'Cell'
        self.EnvID = self.environment.id
        self.Species = None
        self.genome = None
        self.SpeciesID = "null"
        self.AdjustedFitness = 0
        self.fitness = 0
        self.isAlive = True
        self.TotalTimeAliveInTicks = 0
        self.TimeAlive = 0
        self.TotalEnergyLevel = 0
        self.TotalEnergyObtained = 0
        self.TotalStepsTaken = 0
        self.PosX = xpos
        self.PosY = ypos
        self.DirX = 0
        self.DirY = 0
        self.HitBlock = False
        self.AteFood = False
        self.HitWall = False
        self.HitCell = False
        self.UpdateDateTime = "null"
        self.EndDateTime = 'null'
        self.CreateDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        self.GenerationNumber = 0
        self.TotalNodes = 0
        self.TotalConnections = 0
        # self.create_new_cell_record()
        # self.id = self.sql_db.execute_query("SELECT MAX(id) FROM {} ".format(self.entity_name)).fetchone()[0]
        self.rect.x = self.PosX
        self.rect.y = self.PosY
        # self.sql_db.execute_query(
        #     "UPDATE {1} SET EnvID = {0} WHERE id = {2}".format(self.EnvID, self.entity_name, self.id))

        self.environment.add_active_cell()

    def resetScore(self):
        # self.TotalStepsTaken = 0
        # self.TotalEnergyObtained = 0
        self.TotalEnergyLevel = 0
        self.getGenome().fitness_score = 0
        self.TotalTimeAliveInTicks = 0
        self.AteFood = False
        self.HitWall = False
        self.HitCell = False
        self.HitBlock = False


    def IsAlive(self, is_alive=None):
        if is_alive is not None:
            self.resetScore()
        else:
            return self.isAlive

    def getEnergyLevel(self):
        return self.TotalEnergyLevel

    def ChangeCellColor(self, rgb):
        self.image.fill(rgb)

    def getGenome(self):
        return self.genome

    def set_genome(self, genome):
        if genome is None:
            return
        genome.set_cell_body(self)
        self.genome = genome

    def hit_wall(self, new_x, new_y):
        width_boundary = self.environment.env_width - self.environment.pixelSize
        height_boundary = self.environment.env_height - self.environment.pixelSize
        if 0 <= new_x <= width_boundary and 0 <= new_y <= height_boundary:
            return False
        return True

    def hit_energy(self, new_x, new_y):
        if (new_x, new_y) in self.environment.energy_cell_dicts:
            return True
        else:
            return False

    def hit_block(self, new_x, new_y):
        if (new_x, new_y) in self.environment.wall_cell_dicts:
            return True
        else:
            return False

    def hit_active_cell(self, new_x, new_y):
        if (new_x, new_y) in self.environment.active_cell_dicts:
            return True
        else:
            return False

    def update_position(self, new_x, new_y):
        if not self.hit_wall(new_x, new_y) and not self.hit_active_cell(new_x, new_y):
            if self.hit_block(new_x, new_y):
                self.HitBlock = True
                return

            del self.environment.active_cell_dicts[(self.PosX, self.PosY)]
            self.PosX = new_x
            self.PosY = new_y
            self.environment.active_cell_dicts[(new_x, new_y)] = self
            self.rect.x = new_x
            self.rect.y = new_y
            if self.hit_energy(self.PosX, self.PosY):
                random_grid_position = self.environment.get_random_position()
                if random_grid_position is not None:
                    self.AteFood = True
                    energy_cell = self.environment.energy_cell_dicts[self.PosX, self.PosY]
                    energy_cell.update_position(random_grid_position[0], random_grid_position[1])

        else:
            if self.hit_active_cell(new_x, new_y):
                self.HitCell = True
            if self.hit_wall(new_x, new_y):
                self.HitWall = True

                if self.PosX - self.environment.pixelSize < 0:
                    self.update_position(self.environment.env_width - self.environment.pixelSize, self.PosY)
                elif self.PosX + self.environment.pixelSize > self.environment.env_width - self.environment.pixelSize:
                    self.update_position(0, self.PosY)

                if self.PosY - self.environment.pixelSize < 0:
                    self.update_position(self.PosX, self.environment.env_height - self.environment.pixelSize)
                elif self.PosY + self.environment.pixelSize > self.environment.env_height - self.environment.pixelSize:
                    self.update_position(self.PosX, 0)

    def move_randomly(self):
        rand = random.randint(1, 4)
        if rand == 1:
            self.move_up()
        elif rand == 2:
            self.move_down()
        elif rand == 3:
            self.move_left()
        elif rand == 4:
            self.move_right()
        else:
            return None

    def move_left(self):
        new_x = self.PosX - self.environment.pixelSize
        self.update_position(new_x, self.PosY)

    def move_right(self):
        new_x = self.PosX + self.environment.pixelSize
        self.update_position(new_x, self.PosY)

    def move_down(self):
        new_y = self.PosY + self.environment.pixelSize
        self.update_position(self.PosX, new_y)

    def move_up(self):
        new_y = self.PosY - self.environment.pixelSize
        self.update_position(self.PosX, new_y)

    def scan(self):
        """
        :return: 24 inputs for all 8 directions
        """
        vision_inputs = []  # 24 input values
        directions = [(-1, 0), (-1, -1), (-1, 1), (1, 0), (1, -1), (1, 1), (0, -1), (0, 1)]  # tuple of all 8 directions
        for dir in directions:  # iterate through all 8 directions
            vision_values = self.look(dir)  # list of 3 values returned of entity position statuses
            vision_inputs.append(vision_values)  # Extend 3 values to input values

        # if self.environment.neat_environment.include_bias:
        #     vision_inputs.insert(0, 1)
        vision_inputs = StandardScaler().fit_transform(np.array(vision_inputs).reshape(-1, 1))
        return vision_inputs

    def look(self, dir):
        """
        :return: 3 values in specified direction of entity positions
        """
        direction_y, direction_x = dir[0] * self.environment.pixelSize, dir[1] * self.environment.pixelSize
        hit_wall, hit_block, hit_active_cell, hit_energy_cell = False, False, False, False
        distance = 0
        current_xpos, current_ypos = self.PosX, self.PosY
        # iterate & update positions until wall is hit
        current_xpos += direction_x
        current_ypos += direction_y

        while not hit_block or not hit_wall:
            target_position = (current_xpos, current_ypos)
            if self.hit_block(target_position[0], target_position[1]):
                hit_block = True
                break
            if self.hit_wall(target_position[0], target_position[1]):
                hit_wall = True
                break
            distance += 1

            current_ypos, current_xpos = (current_ypos + direction_y, current_xpos + direction_x)

        vision_values = distance
        return vision_values
