import pygame
import sys
import random
import os
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((360, 567))
background = pygame.image.load('background.jpg')

# Constants
GRID_SIZE = 9
CELL_SIZE = 40
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 567
HEADER_HEIGHT = 107

# Load and scale images
coin_image = pygame.image.load('coin.png')
obstacle_image = pygame.image.load('brick.png')
coin_image = pygame.transform.scale(coin_image, (CELL_SIZE, CELL_SIZE))
obstacle_image = pygame.transform.scale(obstacle_image, (CELL_SIZE, CELL_SIZE))

# Load spritesheet
sprite_sheet = pygame.image.load('spriteimg.png').convert_alpha()
sprite_width = 64
sprite_height = 64

# Extract and scale frames
frames_down = [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(sprite_width * i, 0, sprite_width, sprite_height)), (CELL_SIZE, CELL_SIZE)) for i in range(4)]
frames_left = [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(sprite_width * i, sprite_height, sprite_width, sprite_height)), (CELL_SIZE, CELL_SIZE)) for i in range(4)]
frames_right = [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(sprite_width * i, sprite_height * 2, sprite_width, sprite_height)), (CELL_SIZE, CELL_SIZE)) for i in range(4)]
frames_up = [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(sprite_width * i, sprite_height * 3, sprite_width, sprite_height)), (CELL_SIZE, CELL_SIZE)) for i in range(4)]

# Sprite properties
sprite_x, sprite_y = 0, 8 * CELL_SIZE + HEADER_HEIGHT
move_speed = 5
current_frames = frames_right
frame_index = 0
animation_speed = 0.2
clock = pygame.time.Clock()
coin_collected = False
level = 1

# Function to draw grid lines
def draw_grid():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 107), (x, SCREEN_HEIGHT - 100))
    for y in range(HEADER_HEIGHT, SCREEN_HEIGHT - 99, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y))

# Pathfinding using A* algorithm
def a_star(start, goal, obstacles):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not open_set.empty():
        _, current = open_set.get()

        if current == goal:
            return True

        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in neighbors:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE and neighbor not in obstacles:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                    open_set.put((f_score[neighbor], neighbor))

    return False

# Function to place obstacles randomly and ensure a path exists
def place_obstacles_and_coin(level):
    while True:
        obstacles = set()
        num_obstacles = random.randint(15, 25) + (level - 1) * 5  # Increase number of obstacles with level

        while len(obstacles) < num_obstacles:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            if (x, y) != (0, 8) and (x, y) != (8, 0):  # Ensure not to place on start or coin position
                obstacles.add((x, y))

        coin_position = place_coin(obstacles)
        if a_star((0, 8), coin_position, obstacles):
            return obstacles, coin_position

# Function to place the gold coin randomly
def place_coin(obstacles):
    while True:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) not in obstacles and (x, y) != (0, 8):
            return (x, y)

# Function to move hero based on instructions
def move_hero(instructions):
    global sprite_x, sprite_y, current_frames, frame_index, coin_collected

    i = 0
    while i < len(instructions):
        instruction = instructions[i].strip().lower()
        parts = instruction.split()

        if parts[0] == 'while':
            loop_count = int(parts[1])
            loop_instructions = []
            i += 1
            while i < len(instructions) and not instructions[i].strip().lower().startswith('end'):
                loop_instructions.append(instructions[i])
                i += 1

            for _ in range(loop_count):
                move_hero(loop_instructions)
        else:
            if len(parts) == 1:  # Regular movement
                direction = parts[0]
                steps = 1
            elif len(parts) == 2:  # Movement with specified number of steps
                direction = parts[0]
                try:
                    steps = int(parts[1])
                except ValueError:
                    print("Invalid instruction:", instruction)
                    continue
            else:
                print("Invalid instruction:", instruction)
                continue

            for _ in range(steps):
                old_x, old_y = sprite_x, sprite_y
                if direction == 'up':
                    sprite_y -= CELL_SIZE
                    current_frames = frames_up
                elif direction == 'down':
                    sprite_y += CELL_SIZE
                    current_frames = frames_down
                elif direction == 'left':
                    sprite_x -= CELL_SIZE
                    current_frames = frames_left
                elif direction == 'right':
                    sprite_x += CELL_SIZE
                    current_frames = frames_right
                else:
                    print("Invalid instruction:", instruction)
                    continue

                # Check if new position is within the grid bounds
                grid_x = sprite_x // CELL_SIZE
                grid_y = (sprite_y - HEADER_HEIGHT) // CELL_SIZE
                new_position = (grid_x, grid_y)
                if 0 <= grid_x < GRID_SIZE and 0 <= grid_y < GRID_SIZE:
                    # Check if new position is not an obstacle
                    if new_position not in obstacles:
                        animate_movement()
                        hero_position[0] = grid_x
                        hero_position[1] = grid_y
                        # Check if hero collects the gold coin
                        if new_position == coin_position:
                            print("Congratulations! You collected the gold coin!")
                            coin_collected = True
                            return  # End movement if gold coin collected
                    else:
                        print("Obstacle detected! Cannot move.")
                        sprite_x, sprite_y = old_x, old_y  # Revert to previous position
                else:
                    print("Invalid move! Out of bounds.")
                    sprite_x, sprite_y = old_x, old_y  # Revert to previous position

        i += 1

# Function to animate sprite movement
def animate_movement():
    global frame_index
    animate = True
    while animate:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.blit(background, (0, 0))
        draw_game()
        screen.blit(current_frames[frame_index], (sprite_x, sprite_y))
        frame_index = (frame_index + 1) % len(current_frames)
        pygame.display.flip()
        clock.tick(10)  # Adjust the frame rate here
        # Check if animation is complete
        if frame_index == 0:
            animate = False

# Function to draw the game
def draw_game():
    screen.blit(background, (0, 0))
    draw_grid()
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0] * CELL_SIZE, obstacle[1] * CELL_SIZE + HEADER_HEIGHT))
    screen.blit(coin_image, (coin_position[0] * CELL_SIZE, coin_position[1] * CELL_SIZE + HEADER_HEIGHT))
    screen.blit(current_frames[frame_index], (sprite_x, sprite_y))
    draw_buttons()
    pygame.display.update()

# Function to draw the buttons
def draw_buttons():
    font = pygame.font.Font(None, 24)
    play_button_rect = pygame.Rect(10, 10, 80, 40)
    reset_button_rect = pygame.Rect(100, 10, 80, 40)
    level_up_button_rect = pygame.Rect(190, 10, 80, 40)
    pygame.draw.rect(screen, (0, 128, 255), play_button_rect)  # Blue color
    pygame.draw.rect(screen, (255, 165, 0), reset_button_rect)  # Orange color
    if coin_collected:
        pygame.draw.rect(screen, (0, 255, 0), level_up_button_rect)  # Green color when coin collected
    else:
        pygame.draw.rect(screen, (128, 128, 128), level_up_button_rect)  # Grey color when coin not collected
    play_text_surface = font.render("Play", True, (255, 255, 255))
    reset_text_surface = font.render("Reset", True, (255, 255, 255))
    level_up_text_surface = font.render("Level Up", True, (255, 255, 255))
    screen.blit(play_text_surface, (20, 20))
    screen.blit(reset_text_surface, (110, 20))
    screen.blit(level_up_text_surface, (200, 20))

# Main game loop
def main():
    global coin_collected, level, obstacles, coin_position, sprite_x, sprite_y, hero_position

    obstacles, coin_position = place_obstacles_and_coin(level)
    hero_position = [0, 8]
    sprite_x, sprite_y = 0, 8 * CELL_SIZE + HEADER_HEIGHT

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 10 <= mouse_x <= 90 and 10 <= mouse_y <= 50:
                    # Play button pressed
                    os.system('python ocr.py')
                    with open('detected_text.txt', 'r') as file:
                        instructions = file.readlines()
                    move_hero(instructions)
                elif 100 <= mouse_x <= 180 and 10 <= mouse_y <= 50:
                    # Reset button pressed
                    coin_collected = False
                    obstacles, coin_position = place_obstacles_and_coin(level)
                    hero_position = [0, 8]
                    sprite_x, sprite_y = 0, 8 * CELL_SIZE + HEADER_HEIGHT
                elif coin_collected and 190 <= mouse_x <= 270 and 10 <= mouse_y <= 50:
                    # Level Up button pressed
                    coin_collected = False
                    level += 1
                    obstacles, coin_position = place_obstacles_and_coin(level)
                    hero_position = [0, 8]
                    sprite_x, sprite_y = 0, 8 * CELL_SIZE + HEADER_HEIGHT

        screen.blit(background, (0, 0))
        draw_game()
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()
