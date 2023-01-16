import sys
from Environment import Environment
from SQlite import SQLLite
import pygame as pg

pg.init()

from Cell import Cell
from Energy import Energy
from NEAT import NEAT

sql = SQLLite()
WindowWidth = 900

WindowHeight = 900
TotalEnergyBlocks = 0
ActiveCellColor = (0, 0, 255)
BackgroundColor = (0, 0, 0)
EnergyCellColor = (255, 0, 0)
GridColor = (60, 60, 60)
PixelSize = 10
evolving_time_in_ticks = 20
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
                active_cell = Cell(environment, pos[0], pos[1], ActiveCellColor)
                genome = environment.neat_environment.generate_empty_genome()
                active_cell.set_genome(genome)

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
                neat_environment.species_threshold +=1
                # environment.pixelSize += 10
                print(neat_environment.species_threshold)

            if event.key == pg.K_DOWN:
                neat_environment.species_threshold -= 1
                print(neat_environment.species_threshold)

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
    for active_cell in environment.active_cell_entities:
        active_cell.TotalTimeAliveInTicks += 1
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
            active_cell.TotalEnergyLevel -= 1

        genome.calculateFitness()

    if (ticks % get_evolution_rate(ineligibility_rate=ineligibility_rate)) == 0:
        neat_environment.evolve()
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


def get_evolution_rate(ineligibility_rate):
    P = len(neat_environment.list_of_Genomes)
    if P == 0:
        return 1
    min_time_alive = neat_environment.minimum_time_alive
    number_of_ticks_to_evolve = min_time_alive / (P * ineligibility_rate)
    return int(number_of_ticks_to_evolve)


if __name__ == '__main__':
    # sql.create_miniature_environment_tables()
    # print("Environment #", environment.id, "Was made")
    # print("there are", get_total_environments(), 'Environment(s) Available')
    TotalPopulation = 5
    minimum_time_alive = 100
    species_threshold = 5
    ineligibility_rate = .5
    neat_environment = NEAT(
        total_input_nodes=24,
        total_output_nodes=5,
        add_node_probability=.1,
        species_threshold=species_threshold,
        add_connection_probability=.1,
        weight_change_probability=.1,
        weight_change_strength = .1,
        weight_shift_probability = .1,
        weight_shift_strength=.1,
        minimum_time_alive=minimum_time_alive,
        include_bias=True)
    environment.set_neat_environment(neat_environment)
    start()
