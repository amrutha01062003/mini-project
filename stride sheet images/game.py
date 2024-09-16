import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 5
CELL_SIZE = 100
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
GOLD_COIN = (255, 215, 0)  # Gold color
HERO_COLOR = (0, 128, 0)    # Green color
OBSTACLE_COLOR = (128, 128, 128)  # Gray color

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hero's Adventure")

# Load images
hero_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
hero_image.fill(HERO_COLOR)

coin_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
coin_image.fill(GOLD_COIN)

obstacle_image = pygame.Surface((CELL_SIZE, CELL_SIZE))
obstacle_image.fill(OBSTACLE_COLOR)

# Function to draw grid lines
def draw_grid():
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (SCREEN_WIDTH, y))

# Function to place obstacles randomly
def place_obstacles():
    obstacles = set()
    while len(obstacles) < GRID_SIZE:  # Number of obstacles
        obstacle = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
        if obstacle != (0, 0):  # Exclude starting position
            obstacles.add(obstacle)
    return obstacles

# Function to generate a random position for the gold coin
def generate_coin_position(obstacles):
    while True:
        coin_position = (random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1))
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
    screen.fill((255, 255, 255))  # White background
    draw_grid()
    for obstacle in obstacles:
        screen.blit(obstacle_image, (obstacle[0] * CELL_SIZE, obstacle[1] * CELL_SIZE))
    screen.blit(coin_image, (coin_position[0] * CELL_SIZE, coin_position[1] * CELL_SIZE))
    screen.blit(hero_image, (hero_position[0] * CELL_SIZE, hero_position[1] * CELL_SIZE))
    pygame.display.flip()

# Function to move hero based on instructions from a file
def move_hero_from_file(file_path):
    global hero_position
    with open(file_path, "r") as file:
        instructions = file.readlines()
    move_hero(instructions)

# Main function
def main():
    global obstacles, coin_position, hero_position
    # Generate obstacles and coin position
    obstacles = place_obstacles()
    coin_position = generate_coin_position(obstacles)
    hero_position = [0, 0]  # Starting position for hero

    # Draw initial game state
    draw_game()

    # Allow user to input movement instructions into a text file
    file_path = input("Enter the path to the movement instructions file: ").strip('"')
    move_hero_from_file(file_path)

    pygame.quit()

if __name__ == "__main__":
    main()
