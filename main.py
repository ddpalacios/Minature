import sys
from Environment import Environment
from SQlite import SQLLite
import pygame as pg

pg.init()

from Cell import Cell
from Energy import Energy
from NEAT import NEAT

sql = SQLLite()
WindowWidth = 1500
WindowHeight = 900
TotalPopulation = 0
TotalEnergyBlocks = 0
ActiveCellColor = (0, 0, 255)
BackgroundColor = (0, 0, 0)
EnergyCellColor = (255, 0, 0)
GridColor = (60, 60, 60)
PixelSize = 10
screen = pg.display.set_mode((WindowWidth, WindowHeight))
pg.display.set_caption("Miniature")
clock = pg.time.Clock()
FramesPerSecond = 90
environment = Environment(env_width=WindowWidth,
                          env_height=WindowHeight,
                          frames_per_second=FramesPerSecond,
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
                environment.frames_per_second -= 1
                print(environment.frames_per_second)

            if event.key == pg.K_RIGHT:
                environment.frames_per_second += 1
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
                    active_cell = Cell(environment, xpos, ypos, ActiveCellColor)
                    genome = environment.neat_environment.generate_empty_genome()
                    active_cell.set_genome(genome)
                if mouse_event == 3:
                    Energy(environment, xpos, ypos, EnergyCellColor)


def draw_grid():
    for x in range(0, WindowWidth, environment.pixelSize):
        pg.draw.line(screen, GridColor, (x, 0), (x, WindowHeight))
    for y in range(0, WindowHeight, environment.pixelSize):
        pg.draw.line(screen, GridColor, (0, y), (WindowWidth, y))


def update(ticks):
    max_ticks_until_update = 100
    for active_cell in environment.active_cell_entities:

        active_cell.ChangeCellColor(ActiveCellColor)
        genome = active_cell.getGenome()
        vision_inputs = active_cell.scan()
        output = genome.forward(vision_inputs)

        if output == 1:
            active_cell.move_up()
        if output == 2:
            active_cell.move_down()
        if output == 3:
            active_cell.move_left()
        if output == 4:
            active_cell.move_right()
        else:
            genome.fitness_score = genome.fitness_score - 100

        genome.calculateFitness()
        active_cell.TotalTimeAliveInTicks += 1


    neat_environment.evolve(max_ticks_until_update)
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
        active_cell = Cell(environment, random_grid_position[0], random_grid_position[1], ActiveCellColor)

        if i == 0:
            user_cell = active_cell
        genome = environment.neat_environment.generate_empty_genome()
        active_cell.set_genome(genome)



def generate_energy(total_population=10):
    for i in range(total_population):
        random_grid_position = environment.get_random_position()
        if random_grid_position is None:
            break
        Energy(environment, random_grid_position[0], random_grid_position[1], EnergyCellColor)


def start():
    if not environment.IsRunning():
        environment.start()
    generate_population(total_population=TotalPopulation)
    generate_energy(total_population=TotalEnergyBlocks)
    ticks = 0
    while environment.IsRunning():
        check_events()
        update(ticks)
        clock.tick(environment.frames_per_second)
        ticks += 1
    environment.terminate()
    return environment


if __name__ == '__main__':
    # sql.create_miniature_environment_tables()
    # print("Environment #", environment.id, "Was made")
    # print("there are", get_total_environments(), 'Environment(s) Available')
    neat_environment = NEAT(
        total_input_nodes=24,
        total_output_nodes=5,
        add_node_probability=.1,
        add_connection_probability=.4,
        include_bias=False)
    environment.set_neat_environment(neat_environment)
    start()
