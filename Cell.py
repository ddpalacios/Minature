import datetime
import pygame as pg
from SQlite import SQLLite
import random


class Cell(pg.sprite.Sprite):
    def __init__(self, environment, xpos, ypos, cell_color=(255, 0, 0)):
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
        self.isAlive = 1
        self.TotalTimeAliveInTicks = 0
        self.TotalEnergyRemaining = 0
        self.TotalEnergyObtained = 0
        self.PosX = xpos
        self.PosY = ypos
        self.DirX = 0
        self.DirY = 0
        self.UpdateDateTime = "null"
        self.EndDateTime = 'null'
        self.CreateDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        self.GenerationNumber = 0
        self.TotalNodes = 0
        self.TotalConnections = 0
        self.create_new_cell_record()
        self.id = self.sql_db.execute_query("SELECT MAX(id) FROM {} ".format(self.entity_name)).fetchone()[0]
        self.rect.x = self.PosX
        self.rect.y = self.PosY
        self.sql_db.execute_query(
            "UPDATE {1} SET EnvID = {0} WHERE id = {2}".format(self.EnvID, self.entity_name, self.id))
        self.environment.add_active_cell()

    def set_genome(self, genome):
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

    def hit_active_cell(self, new_x, new_y):
        if (new_x, new_y) in self.environment.active_cell_dicts:
            return True
        else:
            return False

    def update_position(self, new_x, new_y):
        if not self.hit_wall(new_x, new_y) and not self.hit_active_cell(new_x, new_y):
            del self.environment.active_cell_dicts[(self.PosX, self.PosY)]
            self.PosX = new_x
            self.PosY = new_y
            self.environment.active_cell_dicts[(new_x, new_y)] = self
            self.rect.x = new_x
            self.rect.y = new_y
            if self.hit_energy(self.PosX, self.PosY):
                random_grid_position = self.environment.get_random_position()
                if random_grid_position is not None:
                    energy_cell = self.environment.energy_cell_dicts[self.PosX, self.PosY]
                    energy_cell.update_position(random_grid_position[0], random_grid_position[1])

        self.sql_db.execute_query(
            "UPDATE {} SET UpdateDateTime = {} WHERE id = {}".format(self.entity_name,
                                                                     self.environment.currentDateTime, self.id))

    def move_randomly(self):
        rand = random.randint(0, 5)
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

    def create_new_cell_record(self):
        cursor = self.sql_db.execute_query('SELECT * FROM {}'.format(self.entity_name))
        column_names = list(map(lambda x: x[0], cursor.description))
        column_names.remove("id")
        column_names = ",".join(column_names)
        query = '''INSERT INTO {0} ({1}) VALUES ({2},{3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19});
                        '''.format(
            self.entity_name,  # 0
            column_names,  # 1
            self.EnvID,  # 2
            self.AdjustedFitness,  # 3
            self.fitness,  # 4
            self.isAlive,  # 5
            self.TotalTimeAliveInTicks,  # 6
            self.TotalEnergyRemaining,  # 7
            self.TotalEnergyObtained,  # 8
            self.PosX,  # 9
            self.PosY,  # 10
            self.DirX,  # 11
            self.DirY,  # 12
            self.UpdateDateTime,  # 13
            self.CreateDateTime,  # 14
            self.EndDateTime,  # 15
            self.GenerationNumber,  # 16
            self.TotalNodes,  # 17
            self.TotalConnections,  # 18
            self.SpeciesID)  # 19
        self.sql_db.execute_query(query)

    def scan(self):
        """
        :return: 24 inputs for all 8 directions
        """
        vision_inputs = []  # 24 input values
        directions = [(1, 0), (1, -1), (1, 1), (-1, 0), (-1, -1), (-1, 1), (0, -1), (0, 1)]  # tuple of all 8 directions
        for dir in directions:  # iterate through all 8 directions
            vision_values = self.look(dir)  # list of 3 values returned of entity position statuses
            vision_inputs.extend(vision_values)  # Extend 3 values to input values

        return vision_inputs  # all 24 inputs for all 8 direction (8*3)

    def look(self, dir):
        """
        :return: 3 values in specified direction of entity positions
        """
        vision_values = [0, 0, 0]
        direction_y, direction_x = dir[0], dir[1]
        hit_wall, hit_active_cell, hit_energy_cell = False, False, False
        distance = 0
        current_xpos, current_ypos = self.PosX, self.PosY
        # iterate & update positions until wall is hit
        current_xpos += direction_x
        current_ypos += direction_y

        while not hit_wall:
            if self.hit_wall(current_xpos, current_ypos):
                hit_wall = True
                break

            target_position = (current_xpos, current_ypos)

            if not hit_energy_cell and target_position in self.environment.energy_cell_dicts:
                vision_values[0] = 1
                hit_energy_cell = True

            if not hit_active_cell and target_position in self.environment.active_cell_dicts:
                try:
                    vision_values[1] = 1 / distance
                except ZeroDivisionError:
                    vision_values[1] = 0
                hit_active_cell = True

            distance += 1
            current_ypos, current_xpos = (current_ypos + direction_y, current_xpos + direction_x)

        if hit_wall:
            try:
                vision_values[2] = 1 / distance
            except ZeroDivisionError:
                vision_values[2] = 0
        return vision_values
