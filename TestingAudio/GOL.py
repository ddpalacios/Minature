import pygame
import numpy as np
import sys
# Define the simulation parameters
window_size = (640, 480)
cell_size = 10
grid_size = (window_size[0] // cell_size, window_size[1] // cell_size)
simulation_steps = 1000

# Define the initial state of the game
game_state = np.zeros(grid_size, dtype=int)
game_state[10, 10:13] = 1
game_state[11, 12] = 1
game_state[12, 11:13] = 1

# Initialize the Pygame graphics engine
pygame.init()
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption('Conway\'s Game of Life')

# Define the colors for the cells
dead_color = (0, 0, 0)
alive_color = (255, 255, 255)

# Define the game loop
for step in range(simulation_steps):
    # Copy the current state of the game to a new array
    new_game_state = np.copy(game_state)

    # Compute the next state of the game based on the current state
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            # Compute the number of live neighbors for the current cell
            neighbor_count = (
                game_state[(i-1) % grid_size[0], (j-1) % grid_size[1]] +
                game_state[(i-1) % grid_size[0], j] +
                game_state[(i-1) % grid_size[0], (j+1) % grid_size[1]] +
                game_state[i, (j-1) % grid_size[1]] +
                game_state[i, (j+1) % grid_size[1]] +
                game_state[(i+1) % grid_size[0], (j-1) % grid_size[1]] +
                game_state[(i+1) % grid_size[0], j] +
                game_state[(i+1) % grid_size[0], (j+1) % grid_size[1]]
            )

            # Update the state of the cell based on the rules of the game
            if game_state[i, j] == 0 and neighbor_count == 3:
                new_game_state[i, j] = 1
            elif game_state[i, j] == 1 and (neighbor_count < 2 or neighbor_count > 3):
                new_game_state[i, j] = 0

    # Update the state of the game to the new state
    game_state = new_game_state

    # Update the graphics of the game
    screen.fill(dead_color)
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            if game_state[i, j] == 1:
                pygame.draw.rect(screen, alive_color, (i*cell_size, j*cell_size, cell_size, cell_size))
    pygame.display.update()

    # Check for user input and exit the game if necessary
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
