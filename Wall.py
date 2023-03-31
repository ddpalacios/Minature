import pygame as pg


class Wall(pg.sprite.Sprite):

    def __init__(self, environment, xpos, ypos, cell_color):
        pg.sprite.Sprite.__init__(self, environment.wall_cell_entities)
        self.environment = environment
        self.image = pg.Surface((self.environment.pixelSize, self.environment.pixelSize))
        self.image.fill(cell_color)
        self.rect = self.image.get_rect()
        self.EnvID = self.environment.id
        self.PosX = xpos
        self.PosY = ypos
        self.entity_name = "Wall"
        self.rect.x = self.PosX
        self.rect.y = self.PosY
        environment.add_wall_cell()

    def update_position(self, new_x, new_y):
        del self.environment.wall_cell_dicts[(self.PosX, self.PosY)]
        self.PosX = new_x
        self.PosY = new_y
        self.environment.wall_cell_dicts[(new_x, new_y)] = self
        self.rect.x = new_x
        self.rect.y = new_y
