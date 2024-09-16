import pygame
import sys
import random
import time
import os
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((500, 567))
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
def place_obstacles_and_coin():
    while True:
        obstacles = set()
        num_obstacles = random.randint(15, 25)  # Random number of obstacles

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
    global sprite_x, sprite_y, current_frames, frame_index

    for instruction in instructions:
        instruction = instruction.strip().lower()
        parts = instruction.split()
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
                        return  # End movement if gold coin collected
                else:
                    print("Obstacle detected! Cannot move.")
                    sprite_x, sprite_y = old_x, old_y  # Revert to previous position
            else:
                print("Invalid move! Out of bounds.")
                sprite_x, sprite_y = old_x, old_y  # Revert to previous position

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
    draw_button()
    pygame.display.update()

# Function to draw the button
def draw_button():
    font = pygame.font.Font(None, 36)
    button_rect = pygame.Rect(10, 10, 100, 50)
    pygame.draw.rect(screen, (0, 255, 0), button_rect)
    text_surface = font.render("Play", True, (255, 255, 255))
    screen.blit(text_surface, (button_rect.x + 10, button_rect.y + 10))

# Function to check if the button is pressed
def button_pressed(mouse_pos):
    button_rect = pygame.Rect(10, 10, 100, 50)
    return button_rect.collidepoint(mouse_pos)

# Function to move hero based on instructions from a file
def move_hero_from_file(file_path):
    with open(file_path, "r") as file:
        instructions = file.readlines()
    move_hero(instructions)

def clear_text_file():
    with open("detected_text.txt", "w") as file:
        file.write("")    

# Main function
def main():
    global obstacles, coin_position, hero_position
    obstacles, coin_position = place_obstacles_and_coin()
    hero_position = [0, 8]  # Starting position for hero
    draw_game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_pressed(event.pos):
                    os.system('python app.py')
                    move_hero_from_file("detected_text.txt")
                    #clear_text_file()
                    draw_game()
        
        screen.blit(current_frames[frame_index], (sprite_x, sprite_y))
        pygame.display.flip()

    pygame.quit()

main()
