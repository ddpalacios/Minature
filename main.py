import sys
from Environment import Environment
from SQlite import SQLLite
import pygame as pg
from Cell import Cell
from Energy import Energy

sql = SQLLite()
WindowWidth = 1600
WindowHeight = 1000
TotalPopulation = 10
TotalEnergyBlocks = TotalPopulation // 2
ActiveCellColor = (0, 0, 255)
BackgroundColor = (0, 0, 0)
EnergyCellColor = (255, 0, 0)
GridColor = (60, 60, 60)
PixelSize = 30
screen = pg.display.set_mode((WindowWidth, WindowHeight))
pg.display.set_caption("Miniature")
clock = pg.time.Clock()
FramesPerSecond = 90
total_population = 50
environment = Environment(env_width=WindowWidth,
                          env_height=WindowHeight,
                          frames_per_second=FramesPerSecond,
                          total_population=TotalPopulation,
                          total_energy_blocks=TotalEnergyBlocks,
                          pixel_size=PixelSize)


def get_total_environments():
    query_result = sql.execute_query("SELECT COUNT(*) FROM Environment")
    return query_result.fetchone()[0]


def delete_environments():
    query = '''DELETE FROM Environment '''
    sql.execute_query(query)
    print("Environments deleted!")


def get_mouse_position():
    """
    Function to return x and y coordinates of mouse position of window size
    :return:  int xpos, int ypos
    """

    x, y = pg.mouse.get_pos()

    x = int(x / environment.pixelSize) * environment.pixelSize
    y = int(y / environment.pixelSize) * environment.pixelSize

    return x, y


def check_events():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_SPACE:
                environment.clear()

            if event.key == pg.K_n:
                pos = environment.get_random_position()
                Cell(environment, pos[0], pos[1], ActiveCellColor)

            if event.key == pg.K_e:
                pos = environment.get_random_position()
                Energy(environment, pos[0], pos[1], EnergyCellColor)

            if event.key == pg.K_LEFT:
                environment.frames_per_second -= 10
                print(environment.frames_per_second)

            if event.key == pg.K_RIGHT:
                environment.frames_per_second += 10
                print(environment.frames_per_second)

            if event.key == pg.K_UP:
                environment.pixelSize += 10
                print(environment.pixelSize)

            if event.key == pg.K_DOWN:
                environment.pixelSize -= 10
                print(environment.pixelSize)

        if event.type == pg.MOUSEBUTTONDOWN:
            xpos, ypos = get_mouse_position()
            mouse_clicked = pg.mouse.get_pressed()
            if mouse_clicked:
                mouse_event = event.button
                if mouse_event == 1:
                    Cell(environment, xpos, ypos, ActiveCellColor)
                if mouse_event == 3:
                    Energy(environment, xpos, ypos, EnergyCellColor)


def draw_grid():
    for x in range(0, WindowWidth, environment.pixelSize):
        pg.draw.line(screen, GridColor, (x, 0), (x, WindowHeight))
    for y in range(0, WindowHeight, environment.pixelSize):
        pg.draw.line(screen, GridColor, (0, y), (WindowWidth, y))


def update():
    for idx, c in enumerate(environment.active_cell_entities):
        vision__inputs = c.scan()
        c.move_randomly()

    screen.fill(BackgroundColor)
    draw_grid()
    environment.active_cell_entities.update()
    environment.active_cell_entities.draw(screen)
    environment.energy_cell_entities.update()
    environment.energy_cell_entities.draw(screen)

    pg.display.update()


def generate_population(total_population=10):
    for i in range(total_population):
        random_grid_position = environment.get_random_position()
        if random_grid_position is None:
            break
        Cell(environment, random_grid_position[0], random_grid_position[1], ActiveCellColor)


def start():
    if not environment.IsRunning():
        environment.start()
    # generate_population(total_population=total_population)
    while environment.IsRunning():
        check_events()
        update()
        clock.tick(environment.frames_per_second)
    environment.terminate()
    return environment


if __name__ == '__main__':
    sql.create_miniature_environment_tables()
    print("Environment #", environment.id, "Was made")
    print("there are", get_total_environments(), 'Environment(s) Available')
    start()
