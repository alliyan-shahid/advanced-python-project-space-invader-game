import pygame
import random
import math
from bullet import Bullet

# Colors (should be imported from game.py or defined centrally)
RED = (255, 50, 50)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)  # Added missing color


class Enemy:
    def __init__(self, x, y, enemy_type=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.width = 50
        self.height = 40
        self.speed = 0.8 + (enemy_type * 0.2)
        self.direction = 1
        self.health = enemy_type
        self.animation = 0
        self.hit_flash = 0
        self.shoot_cooldown = random.randint(60, 180)

        if enemy_type == 1:
            self.color = RED
            self.shape = "fighter"
        elif enemy_type == 2:
            self.color = PURPLE
            self.shape = "bomber"
        else:
            self.color = ORANGE
            self.shape = "scout"

        self.value = enemy_type * 150

    def draw(self, screen):
        self.animation = (self.animation + 0.1) % (2 * math.pi)
        wave_offset = math.sin(self.animation) * 3

        # Draw based on shape
        if self.shape == "fighter":
            body_rect = pygame.Rect(self.x + 10, self.y + wave_offset + 5,
                                    self.width - 20, self.height - 10)
            pygame.draw.ellipse(screen, self.color, body_rect)

            wing_left = [(self.x, self.y + wave_offset + self.height // 2),
                         (self.x + 20, self.y + wave_offset + self.height - 5),
                         (self.x + 15, self.y + wave_offset + self.height // 2)]

            wing_right = [(self.x + self.width, self.y + wave_offset + self.height // 2),
                          (self.x + self.width - 20, self.y + wave_offset + self.height - 5),
                          (self.x + self.width - 15, self.y + wave_offset + self.height // 2)]

            pygame.draw.polygon(screen, self.color, wing_left)
            pygame.draw.polygon(screen, self.color, wing_right)

            pygame.draw.circle(screen, BLACK,
                               (self.x + self.width // 2,
                                self.y + wave_offset + self.height // 3), 6)

        elif self.shape == "bomber":
            body_points = [
                (self.x + 5, self.y + wave_offset + self.height // 2),
                (self.x + self.width - 5, self.y + wave_offset + self.height // 2),
                (self.x + self.width - 15, self.y + wave_offset + self.height),
                (self.x + 15, self.y + wave_offset + self.height)
            ]
            pygame.draw.polygon(screen, self.color, body_points)

            pygame.draw.rect(screen, self.color,
                             (self.x - 10, self.y + wave_offset + self.height // 2 - 5,
                              self.width + 20, 10))

            for i in range(2):
                engine_x = self.x + 15 + i * (self.width - 30)
                pygame.draw.circle(screen, YELLOW,
                                   (engine_x, self.y + wave_offset + self.height), 8)

        else:
            pygame.draw.ellipse(screen, self.color,
                                (self.x, self.y + wave_offset, self.width, self.height))

            pygame.draw.polygon(screen, self.color,
                                [(self.x + self.width, self.y + wave_offset + self.height // 2),
                                 (self.x + self.width + 10, self.y + wave_offset + self.height // 2),
                                 (self.x + self.width, self.y + wave_offset + self.height // 2 - 5)])

        if self.hit_flash > 0:
            self.hit_flash -= 1
            flash_rect = pygame.Rect(self.x - 5, self.y + wave_offset - 5,
                                     self.width + 10, self.height + 10)
            pygame.draw.ellipse(screen, WHITE, flash_rect, 3)

    def update(self):
        self.x += self.speed * self.direction
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)

    def can_shoot(self):
        return self.shoot_cooldown == 0 and random.random() < 0.001

    def shoot(self):
        self.shoot_cooldown = random.randint(120, 300)
        return Bullet(self.x + self.width // 2, self.y + self.height, "enemy")

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def hit(self):
        self.health -= 1
        self.hit_flash = 10
        return self.health <= 0