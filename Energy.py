import pygame as pg
import pygame.sprite
from SQlite import SQLLite
import datetime


class Energy(pygame.sprite.Sprite):
    def __init__(self, environment, xpos, ypos, cell_color):
        self.sql_db = SQLLite()

        self.environment = environment
        pg.sprite.Sprite.__init__(self, environment.energy_cell_entities)
        self.image = pg.Surface((self.environment.pixelSize, self.environment.pixelSize))
        self.image.fill(cell_color)
        self.rect = self.image.get_rect()
        self.EnvID = self.environment.id
        self.PosX = xpos
        self.PosY = ypos
        self.entity_name = "Energy"
        self.CreateDateTime = datetime.datetime.timestamp(datetime.datetime.now()) * 1000
        self.EndDateTime = "null"
        self.DurationInSec = 0
        self.create_new_cell_record()
        self.id = self.sql_db.execute_query("SELECT MAX(id) FROM {} ".format(self.entity_name)).fetchone()[0]
        self.rect.x = self.PosX
        self.rect.y = self.PosY

        self.sql_db.execute_query(
            "UPDATE {1} SET EnvID = {0} WHERE id = {2}".format(self.EnvID, self.entity_name, self.id))
        self.environment.add_energy_cell()

    def update_position(self, new_x, new_y):
        del self.environment.energy_cell_dicts[(self.PosX, self.PosY)]
        self.PosX = new_x
        self.PosY = new_y
        self.environment.energy_cell_dicts[(new_x, new_y)] = self
        self.rect.x = new_x
        self.rect.y = new_y

        # self.sql_db.execute_query(
        #     "UPDATE {} SET EndDateTime = {} WHERE id = {}".format(self.entity_name,
        #                                                              self.environment.currentDateTime, self.id))

    def create_new_cell_record(self):
        cursor = self.sql_db.execute_query('SELECT * FROM {}'.format(self.entity_name))
        column_names = list(map(lambda x: x[0], cursor.description))
        column_names.remove("id")
        column_names = ",".join(column_names)
        query = '''INSERT INTO {0} ({1}) VALUES ({2},{3}, {4}, {5}, {6}, {7});
                        '''.format(
            self.entity_name,  # 0
            column_names,  # 1
            self.EnvID,  # 2
            self.PosX,  # 3
            self.PosY,  # 4
            self.CreateDateTime,  # 5
            self.EndDateTime,  # 6
            self.DurationInSec)  # 7
        self.sql_db.execute_query(query)
        print("{} Created!".format(self.entity_name))
