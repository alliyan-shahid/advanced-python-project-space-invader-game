import pygame
import random
import math


class Star:
    """Background star"""

    def __init__(self, screen_width, screen_height):
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.size = random.uniform(0.5, 2.5)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.randint(150, 255)
        self.twinkle_speed = random.uniform(0.02, 0.1)
        self.twinkle = random.random() * math.pi * 2
        self.screen_height = screen_height
        self.screen_width = screen_width

    def update(self):
        self.y += self.speed
        self.twinkle += self.twinkle_speed
        self.brightness = 150 + int(math.sin(self.twinkle) * 105)

        if self.y > self.screen_height:
            self.y = 0
            self.x = random.randint(0, self.screen_width)

    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))