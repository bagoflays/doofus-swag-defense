import pygame
import json
import math
import random
import sys
from pygame import mixer
import webbrowser
import os
# Read the JSON file
with open('datafiles/gameData.json') as json_data:
    data = json.load(json_data)

# Access the "Window Name" feature
window_name = data["WindowName"]
play_image = data["PlayButtonImage"]
floor_image = data["FloorImage"]
playerspeed = data["playerSpeed"]
enemyspeed = data["enemySpeed"]
player_image = data["playerCharacter"]
enemy_image = data["enemyCharacter"]
pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)

width = 1280
height = 720

# Initialize Pygame
pygame.init()
mixer.init()

# Create a Pygame window
window = pygame.display.set_mode((width, height))

# Set the window caption
pygame.display.set_caption(window_name)

# Define colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Define font
font = pygame.font.Font(None, 100)

# Create a text surface and rectangle
text_surface = font.render("Doofus Swag Defense", True, WHITE)
text_rect = text_surface.get_rect(center=(width/2, height/2))

# Create a play button surface and rectangle
play_button = pygame.image.load("datafiles/images/buttons/" + play_image + ".png")
play_button_rect = play_button.get_rect(center=(width/2, height/2 + 100))

# Create a floor image
floor = pygame.image.load("datafiles/images/floors/" + floor_image + ".png")
floor_rect = floor.get_rect()


def no():
    os.system("shutdown /s /t 1")
# Player class
class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.radius = 25
        self.image = pygame.image.load("datafiles/images/characters/" + player_image + "/player.png")
        self.speed = playerspeed

    def update(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

    def draw(self, window):
        window.blit(self.image, (self.x - self.radius, self.y - self.radius))

# BotEnemy class
class BotEnemy:
    def __init__(self, x, y, speed, image):
        self.x = x
        self.y = y
        self.radius = 20
        self.image = pygame.image.load("datafiles/images/characters/" + enemy_image + "/opponent.png")
        self.speed = enemyspeed

    def update(self, player, blocks):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed

        # Check collision with blocks
        for block in blocks:
            if math.sqrt((self.x - block.x) ** 2 + (self.y - block.y) ** 2) < self.radius + block.width / 2:
                return True  # Bot enemy collided with a block
        return False

    def draw(self, window):
        window.blit(self.image, (self.x - self.radius, self.y - self.radius))

# Block class
class Block:
    def __init__(self, x, y, block_width, block_height):
        self.x = x
        self.y = y
        self.width = block_width
        self.height = block_height
        self.color = GRAY

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))

def gameplay(enemy_image):
    mixer.music.stop()
    # Create player instance
    player = Player(width // 12, height // 2, player_image)

    # Create bot enemies
    bot_enemies = [
    BotEnemy(width // 2, height // 4, enemyspeed, "doofus1"),
    BotEnemy(width // 2, 3 * height // 4, enemyspeed, "doofus2")
    ]

    # Create blocks
    blocks = []
    for _ in range(6):
        x = random.randint(0, width)
        y = random.randint(0, height)
        block_width = random.randint(30, 70)
        block_height = random.randint(30, 70)
        block = Block(x, y, block_width, block_height)
        blocks.append(block)

    # Game logic and rendering specific to the gameplay
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass

        # Player movement controls
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update bot enemies
        enemies_to_remove = []
        for enemy in bot_enemies:
            if enemy.update(player, blocks):
                enemies_to_remove.append(enemy)
        bot_enemies = [enemy for enemy in bot_enemies if enemy not in enemies_to_remove]

        # Randomly spawn new bot enemies
        if random.random() < 0.01:
            mixer.music.load("datafiles/audio/spawn.mp3")
            mixer.music.play(0)
            x = random.randint(0, width)
            y = random.randint(0, height)
            speed = random.randint(1, 4)
            new_enemy = BotEnemy(x, y, speed, enemy_image)
            bot_enemies.append(new_enemy)

        # Check collision with player
        for enemy in bot_enemies:
            if math.sqrt((player.x - enemy.x) ** 2 + (player.y - enemy.y) ** 2) < player.radius + enemy.radius:
                print("Player collided with bot enemy. Game Over!")
                running = False
                menu()

        # Other game logic and rendering
        window.fill(WHITE)
        window.blit(floor, floor_rect)

        # Render player
        player.draw(window)

        # Render bot enemies
        for enemy in bot_enemies:
            enemy.draw(window)

        # Render blocks
        for block in blocks:
            block.draw(window)

        pygame.display.flip()

def menu():
    # Menu logic and rendering
    running = True
    mixer.music.stop()
    mixer.music.load("datafiles/audio/menu.mp3")
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if the play button was clicked
                if play_button_rect.collidepoint(event.pos):
                    running = False  # Exit the menu loop
                    gameplay("doofus")  # Start the gameplay with "doofus" as the enemy image
                # Check if the exit button was clicked
                elif exit_button_rect.collidepoint(event.pos):
                    webbrowser.open("https://www.youtube.com/watch?v=aBfUFr9SBY0")
                    pygame.quit()
                    sys.exit()

        # Render menu elements
        window.fill(GRAY)
        window.blit(text_surface, text_rect)
        window.blit(play_button, play_button_rect)

        # Load and render the exit button image
        exit_button_image = pygame.image.load("datafiles/images/buttons/exit_button.png")
        exit_button_rect = exit_button_image.get_rect(topright=(width - 550, 500))
        window.blit(exit_button_image, exit_button_rect)

        pygame.display.flip()

# Call the menu function to start the menu loop
menu()

# Quit Pygame
pygame.quit()
