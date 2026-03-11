import pygame
import math
import random
from bullet import Bullet
from powerup import PowerUp
from death_explosion import DeathExplosion
from particle import Particle

# Colors
NEON_BLUE = (0, 200, 255)
CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 50, 50)
GOLD = (255, 215, 0)

# Screen dimensions (these should match game.py)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768


class Player:
    def __init__(self):
        self.width = 70
        self.height = 50
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT + 100  # Start off screen
        self.speed = 8
        self.color = NEON_BLUE
        self.lives = 3  # Fixed to always start with 3 lives
        self.score = 0
        self.bullets = []
        self.shoot_cooldown = 0
        self.invincible = 0
        self.invincible_timer = 0
        self.engine_glow = 0
        self.active_power_ups = {}
        self.spawn_timer = 180  # 3 seconds spawn time
        self.spawning = True
        self.spawn_shield = 150  # 2.5 seconds spawn shield
        self.bullet_count = 1  # Start with single shot
        self.permanent_bullet_upgrade = 1  # Permanent bullet level
        self.score_multiplier = 1
        self.death_explosion = None
        self.game = None  # Will be set by Game class

        # Movement boundaries
        self.min_x = 20
        self.max_x = SCREEN_WIDTH - self.width - 20
        self.min_y = SCREEN_HEIGHT // 2
        self.max_y = SCREEN_HEIGHT - 150

    def draw(self, screen):
        if self.spawning:
            # Don't draw while spawning
            return

        # Draw main fighter jet body
        # Fuselage with gradient
        for i in range(self.width - 20):
            color_shade = (
                max(0, self.color[0] - i // 3),
                max(0, self.color[1] - i // 3),
                self.color[2]
            )
            pygame.draw.rect(screen, color_shade,
                             (self.x + 10 + i, self.y + 5, 1, self.height - 10))

        # Cockpit with glow
        pygame.draw.circle(screen, NEON_BLUE,
                           (self.x + self.width // 2, self.y + self.height // 3), 12)
        pygame.draw.circle(screen, WHITE,
                           (self.x + self.width // 2, self.y + self.height // 3), 8)
        pygame.draw.circle(screen, CYAN,
                           (self.x + self.width // 2, self.y + self.height // 3), 4)

        # Wings (swept back) with gradient
        left_wing = [(self.x, self.y + self.height // 2),
                     (self.x + 40, self.y + self.height - 10),
                     (self.x + 20, self.y + self.height // 2)]

        right_wing = [(self.x + self.width, self.y + self.height // 2),
                      (self.x + self.width - 40, self.y + self.height - 10),
                      (self.x + self.width - 20, self.y + self.height // 2)]

        pygame.draw.polygon(screen, self.color, left_wing)
        pygame.draw.polygon(screen, self.color, right_wing)

        # Wing outlines
        pygame.draw.polygon(screen, CYAN, left_wing, 2)
        pygame.draw.polygon(screen, CYAN, right_wing, 2)

        # Tail fins
        tail_points = [(self.x + self.width // 2 - 5, self.y),
                       (self.x + self.width // 2 + 5, self.y),
                       (self.x + self.width // 2, self.y - 20)]
        pygame.draw.polygon(screen, self.color, tail_points)
        pygame.draw.polygon(screen, CYAN, tail_points, 2)

        # Engine glow with animation
        self.engine_glow += 0.3
        glow_size = 12 + math.sin(self.engine_glow) * 8

        for i in range(2):
            engine_x = self.x + (self.width // 3) + (i * (self.width // 3))
            # Outer glow
            pygame.draw.circle(screen, YELLOW,
                               (engine_x, self.y + self.height), int(glow_size))
            # Middle glow
            pygame.draw.circle(screen, ORANGE,
                               (engine_x, self.y + self.height), int(glow_size * 0.7))
            # Inner core
            pygame.draw.circle(screen, RED,
                               (engine_x, self.y + self.height), int(glow_size * 0.4))

        # Draw spawn shield
        if self.spawn_shield > 0:
            alpha = 150 + (math.sin(pygame.time.get_ticks() * 0.01) * 100)
            shield_surface = pygame.Surface((self.width + 80, self.height + 80), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*GOLD, int(alpha)),
                               (self.width // 2 + 40, self.height // 2 + 40),
                               self.width // 2 + 30, 8)
            screen.blit(shield_surface, (self.x - 40, self.y - 40))

        # Draw active power-up effects
        if "shield" in self.active_power_ups:
            alpha = 150 + (math.sin(self.invincible_timer * 0.5) * 100)
            shield_surface = pygame.Surface((self.width + 60, self.height + 60), pygame.SRCALPHA)
            pygame.draw.circle(shield_surface, (*CYAN, int(alpha)),
                               (self.width // 2 + 30, self.height // 2 + 30),
                               self.width // 2 + 20, 5)
            screen.blit(shield_surface, (self.x - 30, self.y - 30))
            self.invincible_timer += 1

        # Draw bullet level indicator
        bullet_indicator = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(bullet_indicator, (*NEON_BLUE, 200), (20, 20), 18)
        font = pygame.font.Font(None, 24)
        bullet_text = font.render(f"{self.bullet_count}", True, WHITE)
        bullet_indicator.blit(bullet_text, (20 - bullet_text.get_width() // 2,
                                            20 - bullet_text.get_height() // 2))
        screen.blit(bullet_indicator, (self.x + self.width + 10, self.y))

    def move(self, direction):
        if self.spawning:
            return

        if direction == "left" and self.x > self.min_x:
            self.x -= self.speed
        if direction == "right" and self.x < self.max_x:
            self.x += self.speed
        if direction == "up" and self.y > self.min_y:
            self.y -= self.speed
        if direction == "down" and self.y < self.max_y:
            self.y += self.speed

    def shoot(self):
        if self.spawning or self.shoot_cooldown > 0:
            return

        # Calculate cooldown based on power-ups
        base_cooldown = 12  # Faster default
        if "rapid_fire" in self.active_power_ups:
            base_cooldown = 6

        self.shoot_cooldown = base_cooldown

        # Determine bullet positions based on bullet count
        offsets = []
        bullet_type = "player"

        if self.bullet_count == 1:
            offsets = [0]
            bullet_type = "player_single"
        elif self.bullet_count == 2:
            offsets = [-12, 12]
            bullet_type = "player_double"
        elif self.bullet_count == 3:
            offsets = [-20, 0, 20]
            bullet_type = "player_triple"
        elif self.bullet_count >= 4:
            offsets = [-25, -8, 8, 25]
            bullet_type = "player_quad"

        for offset in offsets:
            self.bullets.append(Bullet(self.x + self.width // 2 - 2 + offset,
                                       self.y, bullet_type))

    def update(self, current_time):
        # Handle spawning
        if self.spawning:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                # Move player into position
                target_y = SCREEN_HEIGHT - 120
                if self.y > target_y:
                    self.y -= 5
                else:
                    self.y = target_y
                    self.spawning = False
            return

        # Update spawn shield
        if self.spawn_shield > 0:
            self.spawn_shield -= 1
            self.invincible = self.spawn_shield  # Invincible during spawn shield

        # Update power-ups
        expired_power_ups = []
        for power_type, data in self.active_power_ups.items():
            if "expire_time" in data and data["expire_time"] is not None and current_time > data["expire_time"]:
                expired_power_ups.append(power_type)

        for power_type in expired_power_ups:
            self.deactivate_power_up(power_type)
            del self.active_power_ups[power_type]

        # Update shooting
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update invincibility
        if self.invincible > 0 and "shield" not in self.active_power_ups:
            self.invincible -= 1
            # Blink effect
            if self.invincible % 8 < 4:
                self.color = NEON_BLUE
            else:
                self.color = (0, 150, 255)
        else:
            self.color = NEON_BLUE
            self.invincible_timer = 0

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < -20:
                self.bullets.remove(bullet)

        # Update death explosion
        if self.death_explosion:
            self.death_explosion.update()
            if not self.death_explosion.active:
                self.death_explosion = None

    def add_power_up(self, power_type, current_time):
        if power_type == "extra_life":
            self.lives += 1
            self.lives = min(self.lives, 5)  # Cap maximum lives at 5
            self.create_explosion_effect(self.x + self.width // 2, self.y + self.height // 2, RED, 50)
        elif power_type == "score_boost":
            self.score_multiplier = 2
            power_data = {
                "expire_time": current_time + 15000  # 15 seconds
            }
            self.active_power_ups[power_type] = power_data
        elif power_type == "double_shot":
            # Permanent until death
            self.permanent_bullet_upgrade = min(self.permanent_bullet_upgrade + 1, 4)
            self.bullet_count = self.permanent_bullet_upgrade
        else:
            # Timed power-ups
            power_up_instance = PowerUp(0, 0, power_type)
            if "duration" in power_up_instance.power_types[power_type]:
                power_data = {
                    "expire_time": current_time + power_up_instance.power_types[power_type]["duration"]
                }
                self.active_power_ups[power_type] = power_data

    def deactivate_power_up(self, power_type):
        if power_type == "score_boost":
            self.score_multiplier = 1
        elif power_type == "shield":
            self.invincible = 0

    def lose_life(self):
        self.lives -= 1
        self.death_explosion = DeathExplosion(self.x + self.width // 2, self.y + self.height // 2)
        # Reset bullet upgrades on death
        self.permanent_bullet_upgrade = 1
        self.bullet_count = 1
        self.active_power_ups.clear()
        self.score_multiplier = 1
        return self.lives <= 0

    def create_explosion_effect(self, x, y, color, particle_count):
        if self.game and hasattr(self.game, 'particles'):
            for _ in range(particle_count):
                self.game.particles.append(Particle(x, y, color))
