import sys
from Environment import Environment
from SQlite import SQLLite
import pygame as pg
import math

pg.init()

from Cell import Cell
from Energy import Energy
from NEAT import NEAT

sql = SQLLite()
WindowWidth = 900  # 1600
pg.font.init()  # you have to call this at the start,
# if you want to use this module.
font = pg.font.SysFont('Comic Sans MS', 15)
WindowHeight = 500  # 1000
TotalEnergyBlocks = 0
ActiveCellColor = (0, 0, 255)
BackgroundColor = (0, 0, 0)
EnergyCellColor = (255, 0, 0)
GridColor = (60, 60, 60)
I = iter([.01, .05, .1, .2, .3, .4, .45, .5, .55, .6, .7, .8, .9, .95, 1])
M = [i for i in range(0, 500, 10)]
minimum_time_alive = 10
HighestScore = 0
LowestScore = 0

PixelSize = 5
ShowMenu = True
evolving_time_in_ticks = 20
screen = pg.display.set_mode((WindowWidth, WindowHeight))
pg.display.set_caption("Miniature")
clock = pg.time.Clock()
FramesPerSecond = 90
ineligibility_rate = 0.5
environment = Environment(env_width=WindowWidth,
                          env_height=WindowHeight,
                          ineligibility_rate=ineligibility_rate,
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
    global I, minimum_time_alive, ShowMenu
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()

        if event.type == pg.KEYDOWN:

            if event.key == pg.K_SPACE:
                if ShowMenu:
                    ShowMenu = False
                else:
                    ShowMenu = True

            if event.key == pg.K_n:
                pos = environment.get_random_position()
                active_cell = Cell(environment, pos[0], pos[1], ActiveCellColor)
                genome = environment.neat_environment.generate_empty_genome()
                active_cell.set_genome(genome)

            if event.key == pg.K_e:
                pos = environment.get_random_position()
                Energy(environment, pos[0], pos[1], EnergyCellColor)

            # if event.key == pg.K_SPACE:
            #     try:
            #         if neat_environment.minimum_time_alive - 10 < 0:
            #             neat_environment.minimum_time_alive = 0
            #         else:
            #             neat_environment.minimum_time_alive -= 10
            #         print("Minimum time alive", neat_environment.minimum_time_alive)
            #     except TypeError:
            #         print("Minimum time alive", 0)
            #
            #         return

            if event.key == pg.K_RIGHT:
                environment.ineligibility_rate += .1
                # if environment.ineligibility_rate is None:
                #     environment.ineligibility_rate = 0
                #     I = iter([.01, .05, .1, .2, .3, .4, .45, .5, .55, .6, .7, .8, .9, .95, 1])

                print("ineligibility rate", environment.ineligibility_rate)

            if event.key == pg.K_LEFT:
                environment.ineligibility_rate -= .1  # next(minimum_time_alive, None)
                print("ineligibility rate", environment.ineligibility_rate)

            if event.key == pg.K_w:
                neat_environment.species_threshold += .5
                print("threshold", neat_environment.species_threshold)

            if event.key == pg.K_s:
                neat_environment.species_threshold -= .5
                print(neat_environment.species_threshold)
                print("threshold", neat_environment.species_threshold)

            if event.key == pg.K_UP:
                neat_environment.minimum_time_alive += 10
                print("Min. Time Alive", neat_environment.minimum_time_alive)

            if event.key == pg.K_DOWN:
                if neat_environment.minimum_time_alive - 10 < 0:
                    neat_environment.minimum_time_alive = 0
                else:
                    neat_environment.minimum_time_alive -= 10

                print("Min. Time Alive", neat_environment.minimum_time_alive)

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


def showMenu(ticks):
    global HighestScore, LowestScore

    generation_number_surface = font.render("Generation: " + str(ticks), False, (255, 255, 255))

    species_number_surface = font.render("Total Species: " + str(len(neat_environment.list_of_Species)), False,
                                         (255, 255, 255))

    ineligibility_rate_surface = font.render("Ineligibility Rate: " + str(environment.ineligibility_rate), False,
                                             (255, 255, 255))
    species_threshold_surface = font.render("Species Threshold: " + str(neat_environment.species_threshold), False,
                                            (255, 255, 255))

    min_time_alive_surface = font.render("Min. Time Alive: " + str(neat_environment.minimum_time_alive), False,
                                         (255, 255, 255))

    sorted_genomes = neat_environment.sort_genomes('adjusted_fitness_score')
    new_high_score = list(sorted_genomes.values())[len(sorted_genomes) - 1].fitness_score
    new_low_score = list(sorted_genomes.values())[0].fitness_score
    if new_high_score > HighestScore:
        HighestScore = new_high_score
    if new_low_score < LowestScore:
        LowestScore = new_low_score

    lowest_score_surface = font.render("Lowest Score " + str(LowestScore), False,
                                       (255, 255, 255))

    highest_score_surface = font.render("Highest Score " + str(HighestScore), False,
                                        (255, 255, 255))

    pos = 60
    for genome in list(sorted_genomes.values()):
        if genome.getCellBody().TotalTimeAliveInTicks > neat_environment.minimum_time_alive:
            genome_surface = font.render("Genome " + str(genome.ID) + " Fitness " + str(genome.getFitness()), False,
                                         (255, 255, 255))
            screen.blit(genome_surface, (10, pos))
            pos += 60

    screen.blit(species_number_surface, (10, 10))

    screen.blit(highest_score_surface, (WindowWidth - 200, 80))
    screen.blit(lowest_score_surface, (WindowWidth - 200, 110))

    screen.blit(generation_number_surface, ((WindowWidth // 2) - 60, 10))
    screen.blit(species_number_surface, (10, 10))
    screen.blit(ineligibility_rate_surface, (WindowWidth - 200, 10))
    screen.blit(species_threshold_surface, (WindowWidth - 200, 30))

    species = list(neat_environment.sort_species().values())
    if len(species) > 0:
        best_species = species[len(neat_environment.list_of_Species) - 1]
        highest_average_species_score_surface = font.render(
            "Best Species Fitness: " + str(best_species.average_fitness), False, (255, 255, 255))
        screen.blit(highest_average_species_score_surface, (10, 30))

    else:
        species_threshold_surface = font.render("Best Species Fitness: " + str(0), False, (255, 255, 255))
        screen.blit(species_threshold_surface, (10, 30))

    screen.blit(min_time_alive_surface, (WindowWidth - 200, 50))


def update(ticks):
    for active_cell in environment.active_cell_entities:
        genome = active_cell.getGenome()
        vision_inputs = active_cell.scan()
        output = genome.forward(vision_inputs)

        if output == 1:
            active_cell.TotalEnergyLevel =0
            active_cell.move_up()
        elif output == 2:

            active_cell.TotalEnergyLevel = 0

            active_cell.move_down()
        elif output == 3:
            active_cell.TotalEnergyLevel += 1
            active_cell.move_left()

        elif output == 4:
            active_cell.TotalEnergyLevel += 1
            active_cell.move_right()
        else:
            active_cell.TotalEnergyLevel = 0

        genome.calculateFitness()
        active_cell.TotalTimeAliveInTicks += 1

    number_of_ticks_to_evolve = get_evolution_rate(ineligibility_rate=environment.ineligibility_rate)
    if number_of_ticks_to_evolve > 0:
        if (ticks % number_of_ticks_to_evolve) == 0:
            neat_environment.evolve()

    screen.fill(BackgroundColor)
    if ShowMenu:
        draw_grid()
        showMenu(ticks)
    else:
        screen.fill(BackgroundColor)

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
    if ineligibility_rate == 0:
        return 0
    P = len(neat_environment.list_of_Genomes)
    min_time_alive = neat_environment.minimum_time_alive
    try:
        number_of_ticks_to_evolve = min_time_alive / (P * ineligibility_rate)
    except TypeError:
        return 0
    return math.ceil(number_of_ticks_to_evolve)


if __name__ == '__main__':
    TotalPopulation = 10
    species_threshold = 15
    neat_environment = NEAT(
        total_input_nodes=24,
        total_output_nodes=5,
        add_node_probability=.6,
        species_threshold=species_threshold,
        add_connection_probability=.8,
        weight_change_probability=0.1,
        weight_change_strength=.1,
        weight_shift_probability=.1,
        weight_shift_strength=1,
        minimum_time_alive=minimum_time_alive,
        include_bias=True)
    environment.set_neat_environment(neat_environment)
    start()
