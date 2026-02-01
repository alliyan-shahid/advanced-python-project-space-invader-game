import pygame
import random
import math

# Colors
RED = (255, 50, 50)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)


class DeathExplosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 100
        self.growth_rate = 8
        self.wave_radius = 0
        self.wave_speed = 15
        self.active = True
        self.particles = []
        self.shockwave_particles = []
        self.start_time = pygame.time.get_ticks()

        # Create initial explosion particles
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(5, 20)
            self.particles.append({
                'x': x,
                'y': y,
                'speed_x': math.cos(angle) * speed,
                'speed_y': math.sin(angle) * speed,
                'color': random.choice([RED, ORANGE, YELLOW, WHITE]),
                'size': random.uniform(3, 8),
                'life': random.randint(30, 60)
            })

    def update(self):
        self.radius += self.growth_rate
        self.wave_radius += self.wave_speed

        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            particle['life'] -= 1
            particle['size'] = max(0, particle['size'] - 0.1)
            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Create shockwave particles
        if self.wave_radius < 200:
            for _ in range(5):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(self.wave_radius - 10, self.wave_radius + 10)
                self.shockwave_particles.append({
                    'x': self.x + math.cos(angle) * dist,
                    'y': self.y + math.sin(angle) * dist,
                    'color': CYAN,
                    'size': random.uniform(2, 4),
                    'life': random.randint(20, 40)
                })

        # Update shockwave particles
        for particle in self.shockwave_particles[:]:
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.shockwave_particles.remove(particle)

        if self.radius > self.max_radius and len(self.particles) == 0:
            self.active = False

    def draw(self, screen):
        # Draw shockwave
        if self.wave_radius < 200:
            alpha = max(0, 100 - self.wave_radius)
            wave_surface = pygame.Surface((self.wave_radius * 2, self.wave_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(wave_surface, (*CYAN, alpha),
                               (self.wave_radius, self.wave_radius), self.wave_radius, 3)
            screen.blit(wave_surface, (self.x - self.wave_radius, self.y - self.wave_radius))

        # Draw main explosion
        explosion_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        # Core
        pygame.draw.circle(explosion_surface, (*YELLOW, 200),
                           (self.radius, self.radius), self.radius * 0.8)
        pygame.draw.circle(explosion_surface, (*ORANGE, 150),
                           (self.radius, self.radius), self.radius * 0.6)
        pygame.draw.circle(explosion_surface, (*RED, 100),
                           (self.radius, self.radius), self.radius * 0.4)

        screen.blit(explosion_surface, (self.x - self.radius, self.y - self.radius))

        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                pygame.draw.circle(screen, particle['color'],
                                   (int(particle['x']), int(particle['y'])),
                                   int(particle['size']))

        # Draw shockwave particles
        for particle in self.shockwave_particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / 40))
                color_with_alpha = (*particle['color'], alpha)
                particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2),
                                                  pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, color_with_alpha,
                                   (particle['size'], particle['size']), particle['size'])
                screen.blit(particle_surface, (particle['x'] - particle['size'],
                                               particle['y'] - particle['size']))