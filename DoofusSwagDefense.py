import pygame
import json
import math
import random
import sys
from pygame import mixer
import webbrowser
import os
import time

# Read the JSON file
with open('datafiles/gameData.json') as json_data:
    data = json.load(json_data)

# Access the "Window Name" feature
window_name = data.get("WindowName")
if window_name is None:
    window_name = "Doofus Swag Defense: Null Name"

play_image = data["PlayButtonImage"]
floor_image = data["FloorImage"]
playerspeed = data["playerSpeed"]
enemyspeed = data["enemySpeed"]
player_image = data["playerCharacter"]
enemy_image = data["enemyCharacter"]
versionthing = data["version"]
exit_image = data["ExitButtonImage"]

# Initialize Pygame
pygame.init()
mixer.init()

# Create a Pygame window
width = 1280
height = 720
window = pygame.display.set_mode((width, height))
pygame_icon = pygame.image.load('icon.png')
pygame.display.set_icon(pygame_icon)

# Set the window caption
pygame.display.set_caption(window_name)

# Define colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)

# Define font
font = pygame.font.Font(None, 100)
verfont = pygame.font.Font(None, 65)

# Create a text surface and rectangle
text_surface = font.render("Doofus Swag Defense", True, WHITE)
text_rect = text_surface.get_rect(center=(width/2, height/2))


vertext_surface = verfont.render("Game Version v" + versionthing, True, WHITE)
vertext_rect = vertext_surface.get_rect(center=(width/5.5, height/1.035))

# Create a play button surface and rectangle
play_button = pygame.image.load("datafiles/images/buttons/" + play_image + ".png")
play_button_rect = play_button.get_rect(center=(width/2, height/2 + 100))

# Create an exit button surface and rectangle
exit_button_image = pygame.image.load("datafiles/images/buttons/" + exit_image + ".png")
exit_button_rect = exit_button_image.get_rect(topright=(width - 550, 500))

# Create a floor image
floor = pygame.image.load("datafiles/images/floors/" + floor_image + ".png")
floor_rect = floor.get_rect()


def no():
    os.system("shutdown /s /t 1")


# Player class
# Player class
class Player:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.radius = 25
        self.image = pygame.image.load("datafiles/images/characters/" + player_image + "/player.png")
        self.speed = playerspeed
        self.health = 100  # Initial health
        self.max_health = 100  # Maximum health

    def update(self, keys):
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

    def take_damage(self, damage):
        self.health -= damage

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


# HealthBar class
class HealthBar:
    def __init__(self, x, y, width, height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health

    def draw(self, window, current_health):
        # Calculate the width of the health bar based on the current health
        health_width = int((current_health / self.max_health) * self.width)
        health_width = max(0, min(health_width, self.width))  # Limit health_width within the range

        # Draw the background bar in red
        pygame.draw.rect(window, RED, (self.x, self.y, self.width, self.height))

        # Calculate the remaining health bar width
        remaining_width = self.width - health_width

        # Draw the filled portion in green
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y, health_width, self.height))

        # Draw the outline in black
        pygame.draw.rect(window, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)
        pygame.draw.rect(window, (0, 0, 0), (self.x + health_width, self.y, remaining_width, self.height), 2)



def gameplay(enemy_image):
    mixer.music.stop()
    # Create player instance
    player = Player(width // 12, height // 2, player_image)

    # Create bot enemies
    bot_enemies = [
        BotEnemy(width // 2, height // 4, enemyspeed, "doofus1"),
        BotEnemy(width // 2, 3 * height // 4, enemyspeed, "doofus2")
    ]
     
    health_font = pygame.font.Font(None, 36)  # Choose the font and size for the health text
    # Create blocks
    blocks = []
    for _ in range(6):
        x = random.randint(0, width)
        y = random.randint(0, height)
        block_width = random.randint(30, 70)
        block_height = random.randint(30, 70)
        block = Block(x, y, block_width, block_height)
        blocks.append(block)

    # Create health bar
    health_bar = HealthBar(50, 50, 200, 20, player.health)

    # Game logic and rendering specific to the gameplay
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
             if event.key == pygame.K_ESCAPE:
                running = False
                menu()

        # Player movement controls
        keys = pygame.key.get_pressed()
        player.update(keys)

        # Update bot enemies
        enemies_to_remove = []
        for enemy in bot_enemies:
            if enemy.update(player, blocks):
                enemies_to_remove.append(enemy)
                player.take_damage(player.max_health * -0.07)  # Reduce player health by 5%
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
                player.take_damage(player.max_health * 0.001)  # Reduce player health by 5%


        # Other game logic and rendering
        window.fill(WHITE)
        window.blit(floor, floor_rect)
        
        if player.health > 100:
         player.health = 100
        # Render player
        player.draw(window)

        # Render bot enemies
        for enemy in bot_enemies:
            enemy.draw(window)

        # Render blocks
        for block in blocks:
            block.draw(window)

        # Render health bar
        health_bar.draw(window, player.health)
        health_text = health_font.render("Protagonist Health: " + str(int(player.health)), True, WHITE)
        health_text_pos = (10, 10)  # Position the health text at (10, 10) from the top left corner
        window.blit(health_text, health_text_pos)
        pygame.display.flip()

        # Check if player's health is 0
        if player.health <= 0:
            menu()  # Return to the menu



def menu():
    # Menu logic and rendering
    running = True
    mixer.music.stop()
    mixer.music.load("datafiles/audio/menu.ogg")
    mixer.music.play(-1)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if the play button was clicked
                if play_button_rect.collidepoint(event.pos):
                    running = False  # Exit the menu loop
                    gameplay("doofus")  # Start the gameplay with "doofus" as the enemy image
                # Check if the exit button was clicked
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Render menu elements
        window.fill(GRAY)
        window.blit(text_surface, text_rect)
        window.blit(vertext_surface, vertext_rect)
        window.blit(play_button, play_button_rect)

        # Load and render the exit button image
        exit_button_image = pygame.image.load("datafiles/images/buttons/" + exit_image + ".png")
        exit_button_rect = exit_button_image.get_rect(topright=(width - 550, 500))
        window.blit(exit_button_image, exit_button_rect)

        pygame.display.flip()


# Call the menu function to start the menu loop
menu()

# Quit Pygame
pygame.quit()
