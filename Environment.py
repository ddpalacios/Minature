import datetime
from SQlite import SQLLite
import pygame as pg
pg.init()
import random


class Environment:
    def __init__(self, env_width=50, env_height=50, total_population=100, total_energy_blocks=50, pixel_size=5,
                 frames_per_second=60):
        self.sql_db = SQLLite()
        self.entity_name = 'Environment'
        self.__isRunning = False
        self.pixelSize = pixel_size
        self.TotalPopulation = total_population
        self.TotalEnergyBlocks = total_energy_blocks
        self.TotalSpecies = 0
        self.frames_per_second = frames_per_second
        self.env_width = env_width
        self.env_height = env_height
        self.AverageSpeciesFitness = 0
        self.Duration = 0
        self.StartDateTime = "null"  # datetime in unix
        self.EndDateTime = "null"
        self.CreateDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        self.TotalGenerations = 0
        self.NodeCount = 0
        self.ConnectionCount = 0
        self.neat_environment = None
        self.create_new_environment_record()
        self.id = self.sql_db.execute_query("SELECT MAX(id) FROM {}".format(self.entity_name)).fetchone()[0]
        self.active_cell_entities = pg.sprite.Group()
        self.energy_cell_entities = pg.sprite.Group()
        self.currentDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        self.active_cell_dicts = {}
        self.energy_cell_dicts = {}

    def set_neat_environment(self, neat):
        self.neat_environment = neat
        neat.set_environment(self)

    def get_neat_environment(self):
        return self.neat_environment

    def get_random_position(self):
        attempts = 0
        while True:
            if attempts >= 100:
                return None
            rand = int(random.randint(0, self.env_width) / self.pixelSize) * self.pixelSize
            rand2 = int(random.randint(0, self.env_height) / self.pixelSize) * self.pixelSize
            if (rand, rand2) in self.active_cell_dicts or (rand, rand2) in self.energy_cell_dicts:
                attempts +=1
                continue
            else:
                return rand, rand2

    def add_active_cell(self):
        self.active_cell_dicts = {(cell.PosX, cell.PosY): cell for cell in self.active_cell_entities}

    def add_energy_cell(self):
        self.energy_cell_dicts = {(cell.PosX, cell.PosY): cell for cell in self.energy_cell_entities}

    def IsRunning(self):
        return self.__isRunning

    def terminate(self):
        self.sql_db.execute_query("UPDATE {} SET isRunning = 0 WHERE id = {}".format(self.entity_name, self.id))
        print("Environment terminated.")
        self.__isRunning = \
            self.sql_db.execute_query(
                "SELECT isRunning FROM {} WHERE id = {}".format(self.entity_name, self.id)).fetchone()[0]
        return self.IsRunning()

    def clear(self):
        """Update all sprites to have an end datetime (death time)"""
        currentDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000

        active_cells = self.sql_db.execute_query("SELECT * FROM Cell WHERE EnvID = {}".format(self.id)).fetchall()
        energy_cells = self.sql_db.execute_query("SELECT * FROM Energy WHERE EnvID = {}".format(self.id)).fetchall()

        for cell in active_cells:
            self.sql_db.execute_query("UPDATE Cell SET EndDateTime = {} WHERE id = {}".format(currentDateTime, cell[0]))
            self.sql_db.execute_query("UPDATE Cell SET IsAlive = 0 WHERE id = {}".format(cell[0]))

        for cell in energy_cells:
            self.sql_db.execute_query(
                "UPDATE Energy SET EndDateTime = {} WHERE id = {}".format(currentDateTime, cell[0]))

        self.active_cell_entities.empty()
        self.energy_cell_entities.empty()
        print("Active Cell", self.active_cell_entities)
        print('Energy', self.energy_cell_entities)

    def start(self):
        # update isRunning flag to TRUE
        self.sql_db.execute_query("UPDATE Environment SET isRunning = 1 WHERE id = {}".format(self.id))
        print("Environment started")
        self.__isRunning = \
            self.sql_db.execute_query("SELECT isRunning FROM Environment WHERE id = {}".format(self.id)).fetchone()[0]
        return self.IsRunning()

    def create_new_environment_record(self):
        cursor = self.sql_db.execute_query('SELECT * FROM {}'.format(self.entity_name))
        column_names = list(map(lambda x: x[0], cursor.description))
        print(len(column_names))
        column_names.remove("id")
        column_names = ",".join(column_names)
        query = '''
        INSERT INTO {17} ({0}) VALUES ({1},{2},{3},{4},{5},{6},{7},{8},{9}, {10}, {11} ,{12},{13},{14},{15},{16});
        '''.format(
            column_names,
            self.pixelSize,
            self.TotalPopulation,
            self.TotalEnergyBlocks,
            self.TotalSpecies,
            self.frames_per_second,
            self.env_width,
            self.env_height,
            self.AverageSpeciesFitness,
            self.Duration,
            self.StartDateTime,
            self.EndDateTime,
            self.CreateDateTime,
            self.TotalGenerations,
            self.NodeCount,
            self.ConnectionCount,
            self.IsRunning(),
            self.entity_name
        )
        self.sql_db.execute_query(query)
        print("{} Created!".format(self.entity_name))
