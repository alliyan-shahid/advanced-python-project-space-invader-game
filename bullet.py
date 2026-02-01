import pygame
import math
import random

# Colors
NEON_BLUE = (0, 200, 255)
CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
PURPLE = (200, 0, 255)
RED = (255, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)


class Bullet:
    def __init__(self, x, y, bullet_type):
        self.x = x
        self.y = y
        self.type = bullet_type
        self.speed = -18 if "player" in bullet_type else 8
        self.size = 10 if "player" in bullet_type else 8
        self.angle = 0
        self.glow_intensity = 0
        self.trail = []
        self.spark_timer = 0

        # Different colors for different bullet types
        self.colors = {
            "player_single": NEON_BLUE,
            "player_double": CYAN,
            "player_triple": NEON_GREEN,
            "player_quad": PURPLE,
            "enemy": RED
        }

        self.color = self.colors.get(bullet_type, NEON_BLUE)

    def draw(self, screen):
        self.glow_intensity += 0.4
        self.angle += 0.3
        self.spark_timer += 1

        # Draw glow effect
        glow_size = self.size + math.sin(self.glow_intensity) * 4
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)

        # Multiple glow layers
        for i in range(4):
            radius = glow_size - i * 1.5
            alpha = 80 - i * 20
            glow_color = (*self.color, alpha)
            pygame.draw.circle(glow_surface, glow_color,
                               (glow_size, glow_size), int(radius))

        screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))

        # Draw bullet based on type
        if "player" in self.type:
            # Player bullet - advanced design
            bullet_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

            # Main body
            pygame.draw.circle(bullet_surface, WHITE,
                               (self.size, self.size), self.size)
            pygame.draw.circle(bullet_surface, self.color,
                               (self.size, self.size), self.size * 0.7)

            # Core
            pygame.draw.circle(bullet_surface, YELLOW,
                               (self.size, self.size), self.size * 0.4)

            # Spinning rings
            for ring in range(2):
                ring_radius = self.size * 0.8
                points = []
                for i in range(6):
                    angle = self.angle + (i * math.pi / 3) + (ring * math.pi / 6)
                    px = self.size + math.cos(angle) * ring_radius
                    py = self.size + math.sin(angle) * ring_radius
                    points.append((px, py))

                if len(points) >= 3:
                    pygame.draw.polygon(bullet_surface, CYAN, points, 2)

            # Sparks
            if self.spark_timer % 3 == 0:
                for i in range(2):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = self.size * 1.5
                    spark_x = self.size + math.cos(angle) * distance
                    spark_y = self.size + math.sin(angle) * distance
                    pygame.draw.circle(bullet_surface, YELLOW,
                                       (int(spark_x), int(spark_y)), 2)

            screen.blit(bullet_surface, (self.x - self.size, self.y - self.size))

        else:
            # Enemy bullet - menacing design
            bullet_surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)

            # Spiked design
            pygame.draw.circle(bullet_surface, RED,
                               (self.size, self.size), self.size)
            pygame.draw.circle(bullet_surface, (255, 100, 100),
                               (self.size, self.size), self.size * 0.7)

            # Spikes
            for i in range(8):
                angle = i * (2 * math.pi / 8) + self.angle
                inner_x = self.size + math.cos(angle) * (self.size * 0.5)
                inner_y = self.size + math.sin(angle) * (self.size * 0.5)
                outer_x = self.size + math.cos(angle) * (self.size * 1.3)
                outer_y = self.size + math.sin(angle) * (self.size * 1.3)
                pygame.draw.line(bullet_surface, ORANGE,
                                 (inner_x, inner_y), (outer_x, outer_y), 3)

            screen.blit(bullet_surface, (self.x - self.size, self.y - self.size))

        # Draw trail
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = 255 * (1 - i / len(self.trail))
            size = self.size * (1 - i / len(self.trail)) * 0.7
            trail_surf = pygame.Surface((int(size * 2), int(size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (*self.color, int(alpha)),
                               (int(size), int(size)), int(size))
            screen.blit(trail_surf, (trail_x - size, trail_y - size))

        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

    def update(self):
        self.y += self.speed

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size,
                           self.size * 2, self.size * 2)