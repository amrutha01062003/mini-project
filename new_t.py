import pygame
import random
import sys
import time
import os

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((360, 567))
background = pygame.image.load('backgroundimg.jpg')

# Constants
GRID_SIZE = 10
CELL_SIZE = 36
SCREEN_WIDTH = 360
SCREEN_HEIGHT = 567

coin_image1 = pygame.image.load('coin.png')
hero_image1 = pygame.image.load('panda-bear.png')
obstacle_image1 = pygame.image.load('brick.png')

coin_image = pygame.transform.scale(coin_image1, (CELL_SIZE, CELL_SIZE))
hero_image = pygame.transform.scale(hero_image1, (CELL_SIZE, CELL_SIZE))
obstacle_image = pygame.transform.scale(obstacle_image1, (CELL_SIZE, CELL_SIZE))

# Function to draw grid lines
def draw_grid():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 107), (x, SCREEN_HEIGHT - 100))
    for y in range(107, SCREEN_HEIGHT - 99, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y))

# Function to place obstacles randomly
def place_obstacles():
    obstacles = set()
    while len(obstacles) < GRID_SIZE:  # Number of obstacles
        obstacle = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if obstacle != (0, 0):  # Exclude starting position
            obstacles.add(obstacle)
    return obstacles

# Function to generate a random position for the gold coin
def generate_coin_position(obstacles):
    while True:
        coin_position = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if coin_position not in obstacles and coin_position != (0, 0):  # Exclude obstacles and starting position
            return coin_position

# Function to move hero based on instructions
def move_hero(instructions):
    global hero_position
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
            if direction == 'up':
                new_position = (hero_position[0], hero_position[1] - 1)
            elif direction == 'down':
                new_position = (hero_position[0], hero_position[1] + 1)
            elif direction == 'left':
                new_position = (hero_position[0] - 1, hero_position[1])
            elif direction == 'right':
                new_position = (hero_position[0] + 1, hero_position[1])
            else:
                print("Invalid instruction:", instruction)
                continue

            # Check if new position is within the grid bounds
            if 0 <= new_position[0] < GRID_SIZE and 0 <= new_position[1] < GRID_SIZE:
                # Check if new position is not an obstacle
                if new_position not in obstacles:
                    # Update hero position
                    hero_position = new_position
                    pygame.display.update()
                    draw_game()
                    time.sleep(0.5)  # Delay for visualization
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                    # Check if hero collects the gold coin
                    if hero_position == coin_position:
                        print("Congratulations! You collected the gold coin!")
                        return  # End movement if gold coin collected
                else:
                    print("Obstacle detected! Cannot move.")
            else:
                print("Invalid move! Out of bounds.")

# Function to draw the game
def draw_game():
    global hero_position
    pygame.display.update()
    draw_grid()
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0] * CELL_SIZE, (obstacle[1] * CELL_SIZE) + 107))
    screen.blit(coin_image, (coin_position[0] * CELL_SIZE, (coin_position[1] * CELL_SIZE) + 107))
    screen.blit(hero_image, (hero_position[0] * CELL_SIZE, (hero_position[1] * CELL_SIZE) + 107))
    pygame.display.update()

# Function to move hero based on instructions from a file
def move_hero_from_file(file_path):
    global hero_position
    with open(file_path, "r") as file:
        instructions = file.readlines()
    move_hero(instructions)

# Main function
def main():
    screen.blit(background, (0, 0))
    global obstacles, coin_position, hero_position
    # Generate obstacles and coin position
    obstacles = place_obstacles()
    coin_position = generate_coin_position(obstacles)
    hero_position = [0, 0]  # Starting position for hero

    # Draw initial game state
    draw_game()

    # OCR Detection
    os.system('python file.py')

    # Automatically move hero
    move_hero_from_file("detected_text.txt")
    pygame.quit()

if __name__ == "__main__":
    main()
