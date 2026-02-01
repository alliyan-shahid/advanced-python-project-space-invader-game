import pygame
import random


class Particle:
    """Particle for explosion effects"""

    def __init__(self, x, y, color, size_range=(2, 6), speed_range=(-3, 3), life_range=(20, 40)):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(*size_range)
        self.speed_x = random.uniform(*speed_range)
        self.speed_y = random.uniform(*speed_range)
        self.life = random.randint(*life_range)
        self.max_life = self.life

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0

    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color_with_alpha = (*self.color, alpha)
            particle_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color_with_alpha,
                               (self.size, self.size), self.size)
            screen.blit(particle_surface, (self.x - self.size, self.y - self.size))