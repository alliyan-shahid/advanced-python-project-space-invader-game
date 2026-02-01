import pygame
import random
import math
from particle import Particle

# Colors
RED = (255, 50, 50)
BLUE = (0, 120, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)


class CountdownAnimation:
    """Countdown animation at start of each wave"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stage = 0  # 0: 3, 1: 2, 2: 1, 3: FIGHT!, 4: Done
        self.timer = 0
        self.max_time = 60  # 1 second per stage
        self.particles = []

    def update(self):
        self.timer += 1

        if self.timer >= self.max_time:
            self.stage += 1
            self.timer = 0

            # Create particle burst for number changes
            if self.stage < 4:
                for _ in range(50):
                    self.particles.append(Particle(
                        self.screen_width // 2 + random.uniform(-100, 100),
                        self.screen_height // 2 + random.uniform(-100, 100),
                        random.choice([RED, BLUE, GREEN, YELLOW, PURPLE]),
                        size_range=(3, 8),
                        speed_range=(-5, 5),
                        life_range=(20, 40)
                    ))

        # Update particles
        self.particles = [p for p in self.particles if p.update()]

        return self.stage < 4

    def draw(self, screen):
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

        # Draw countdown number
        if self.stage < 3:
            number = 3 - self.stage
            font_size = 200 - self.timer * 2
            alpha = 255

            if self.timer > 45:  # Fade out
                alpha = int(255 * (1 - (self.timer - 45) / 15))

            font = pygame.font.Font(None, int(font_size))
            text = font.render(str(number), True, (255, 255, 255, alpha))
            text_surface = pygame.Surface(text.get_size(), pygame.SRCALPHA)
            text_surface.blit(text, (0, 0))

            screen.blit(text_surface, (self.screen_width // 2 - text.get_width() // 2,
                                       self.screen_height // 2 - text.get_height() // 2))

        elif self.stage == 3:
            font = pygame.font.Font(None, 120)
            text = font.render("FIGHT!", True, RED)

            # Pulse effect
            scale = 1 + math.sin(pygame.time.get_ticks() * 0.01) * 0.2
            scaled_text = pygame.transform.scale(text,
                                                 (int(text.get_width() * scale), int(text.get_height() * scale)))

            # Draw main text
            screen.blit(scaled_text, (self.screen_width // 2 - scaled_text.get_width() // 2,
                                      self.screen_height // 2 - scaled_text.get_height() // 2))