import pygame
import random
import sys
from player import Player
from enemy import Enemy
from powerup import PowerUp
from particle import Particle
from star import Star
from countdown import CountdownAnimation

# Constants (keep only in game.py)
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors (keep only in game.py)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 50, 50)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
NEON_BLUE = (0, 200, 255)
NEON_GREEN = (57, 255, 20)
NEON_PINK = (255, 20, 147)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Invaders - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.player = Player()
        self.player.game = self  # Give player reference to game for particles

        self.enemies = []
        self.power_ups = []
        self.particles = []
        self.stars = [Star(SCREEN_WIDTH, SCREEN_HEIGHT) for _ in range(100)]

        self.wave = 1
        self.game_over = False
        self.wave_complete = False
        self.wave_timer = 0
        self.power_up_timer = 0
        self.countdown = CountdownAnimation(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.game_started = False
        self.pause_timer = 0
        self.show_power_up_info = False
        self.power_up_info_text = ""
        self.power_up_info_timer = 0

        self.create_wave()

    def create_wave(self):
        self.enemies.clear()
        rows = min(2 + self.wave // 3, 4)
        cols = min(6 + self.wave // 2, 8)

        for row in range(rows):
            enemy_type = min((row // 1) + 1, 3)
            for col in range(cols):
                x = 100 + col * 100
                y = 100 + row * 80
                self.enemies.append(Enemy(x, y, enemy_type))

        for enemy in self.enemies:
            enemy.speed = 0.8 + (self.wave - 1) * 0.1

    def spawn_power_up(self):
        power_types = ["double_shot", "shield", "rapid_fire", "extra_life", "score_boost"]
        weights = [0.25, 0.25, 0.2, 0.15, 0.15]

        power_type = random.choices(power_types, weights=weights)[0]
        x = random.randint(50, SCREEN_WIDTH - 100)

        self.power_ups.append(PowerUp(x, -50, power_type))

    def create_explosion(self, x, y, color, size=20):
        for _ in range(size):
            self.particles.append(Particle(x, y, color))

    def show_power_up_message(self, power_type):
        power = PowerUp(0, 0, power_type)
        self.power_up_info_text = f"{power.data['name']} ACQUIRED!"
        self.show_power_up_info = True
        self.power_up_info_timer = 120  # 2 seconds

    def draw_background(self):
        # Starfield background
        gradient_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            # Deep space gradient
            color_value = 5 + int(y / SCREEN_HEIGHT * 15)
            pygame.draw.line(gradient_surface, (color_value, color_value, 20 + color_value),
                             (0, y), (SCREEN_WIDTH, y))
        self.screen.blit(gradient_surface, (0, 0))

        # Draw moving stars
        for star in self.stars:
            star.draw(self.screen)

    def draw_ui(self):
        # Score with multiplier
        score_text = f"SCORE: {self.player.score}"
        if self.player.score_multiplier > 1:
            score_text += f" (x{self.player.score_multiplier})"
        score_render = self.font_medium.render(score_text, True, GREEN)
        self.screen.blit(score_render, (20, 20))

        # Lives display
        lives_text = f"LIVES: {self.player.lives}"
        lives_render = self.font_medium.render(lives_text, True, RED)
        self.screen.blit(lives_render, (SCREEN_WIDTH - 200, 20))

        # Wave
        wave_text = f"WAVE: {self.wave}"
        wave_render = self.font_medium.render(wave_text, True, CYAN)
        self.screen.blit(wave_render, (SCREEN_WIDTH // 2 - 70, 20))

        # Bullet level
        bullet_text = f"BULLET: {self.player.bullet_count}"
        bullet_render = self.font_small.render(bullet_text, True, NEON_BLUE)
        self.screen.blit(bullet_render, (20, 60))

        # Active power-ups with timers
        y_offset = 90
        for power_type in self.player.active_power_ups.keys():
            power = PowerUp(0, 0, power_type)

            # Draw icon and name
            power_font = pygame.font.Font(None, 20)
            power_text = power_font.render(f"{power.data['symbol']} {power.data['name']}", True, power.data['color'])
            self.screen.blit(power_text, (20, y_offset))

            # Draw timer bar if not permanent
            if "permanent" not in power.data or not power.data["permanent"]:
                data = self.player.active_power_ups[power_type]
                if "expire_time" in data and data["expire_time"] is not None:
                    current_time = pygame.time.get_ticks()
                    time_left = max(0, data["expire_time"] - current_time)

                    if power_type == "shield":
                        total_time = 10000
                    elif power_type == "rapid_fire":
                        total_time = 8000
                    elif power_type == "score_boost":
                        total_time = 15000
                    else:
                        total_time = 10000

                    bar_width = 120 * (time_left / total_time)

                    pygame.draw.rect(self.screen, (50, 50, 50),
                                     (150, y_offset + 5, 120, 8))
                    pygame.draw.rect(self.screen, power.data["color"],
                                     (150, y_offset + 5, bar_width, 8))

            y_offset += 30

        # Controls
        controls_bg = pygame.Surface((280, 160), pygame.SRCALPHA)
        controls_bg.fill((0, 0, 0, 180))
        self.screen.blit(controls_bg, (20, SCREEN_HEIGHT - 170))

        controls = [
            "🎮 CONTROLS:",
            "← → ↑ ↓ : MOVE",
            "SPACE : SHOOT",
            "CATCH POWER-UPS!",
            "R : RESTART GAME",
            "ESC : QUIT GAME"
        ]

        for i, text in enumerate(controls):
            if i == 0:
                color = YELLOW
                font = self.font_small
            else:
                color = GREEN
                font = pygame.font.Font(None, 22)

            control_text = font.render(text, True, color)
            self.screen.blit(control_text, (30, SCREEN_HEIGHT - 160 + i * 26))

    def draw_power_up_info(self):
        if self.show_power_up_info and self.power_up_info_timer > 0:
            alpha = min(255, self.power_up_info_timer * 2)
            info_surface = pygame.Surface((500, 80), pygame.SRCALPHA)
            info_surface.fill((0, 0, 0, alpha // 2))

            # Draw border
            pygame.draw.rect(info_surface, (255, 255, 255, alpha),
                             (0, 0, 500, 80), 3, border_radius=10)

            # Draw text
            font = pygame.font.Font(None, 36)
            text = font.render(self.power_up_info_text, True, (255, 255, 255, alpha))
            info_surface.blit(text, (250 - text.get_width() // 2, 40 - text.get_height() // 2))

            self.screen.blit(info_surface, (SCREEN_WIDTH // 2 - 250, 200))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("MISSION FAILED", True, RED)
        score_text = self.font_medium.render(f"FINAL SCORE: {self.player.score}", True, YELLOW)
        wave_text = self.font_medium.render(f"WAVES SURVIVED: {self.wave - 1}", True, CYAN)
        restart_text = self.font_medium.render("PRESS R TO RESTART", True, GREEN)

        self.screen.blit(game_over_text,
                         (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 120))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

    def draw_wave_complete(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 30, 60, 180))
        self.screen.blit(overlay, (0, 0))

        wave_text = self.font_large.render(f"WAVE {self.wave} COMPLETE!", True, YELLOW)
        bonus_text = self.font_medium.render(f"+{500 * self.player.score_multiplier} BONUS POINTS!", True, GREEN)

        # Show power-up timer during pause - reduced from 180 frames (3 seconds) to 60 frames (1 second)
        if self.pause_timer > 0:
            next_text = self.font_medium.render(f"NEXT WAVE IN: {self.pause_timer // 60 + 1}", True, CYAN)
            self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))
        else:
            next_text = self.font_medium.render("PREPARE FOR NEXT WAVE...", True, CYAN)
            self.screen.blit(next_text, (SCREEN_WIDTH // 2 - next_text.get_width() // 2, SCREEN_HEIGHT // 2 + 80))

        self.screen.blit(wave_text, (SCREEN_WIDTH // 2 - wave_text.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(bonus_text, (SCREEN_WIDTH // 2 - bonus_text.get_width() // 2, SCREEN_HEIGHT // 2))

    def run(self):
        running = True

        while running:
            current_time = pygame.time.get_ticks()

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if self.game_over:
                        if event.key == pygame.K_r:
                            self.__init__()
                            self.player.game = self
                    elif event.key == pygame.K_SPACE:
                        self.player.shoot()
                    elif event.key == pygame.K_r:
                        self.__init__()
                        self.player.game = self

            # Handle continuous key presses
            if not self.game_over and not self.wave_complete and self.game_started:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.player.move("left")
                if keys[pygame.K_RIGHT]:
                    self.player.move("right")
                if keys[pygame.K_UP]:
                    self.player.move("up")
                if keys[pygame.K_DOWN]:
                    self.player.move("down")
                if keys[pygame.K_SPACE] and self.player.shoot_cooldown == 0:
                    self.player.shoot()

            # Update game state
            if not self.game_over:
                if not self.game_started:
                    # Show countdown
                    if not self.countdown.update():
                        self.game_started = True
                elif self.wave_complete:
                    self.wave_timer += 1
                    # Reduced pause time from 180 to 60 frames (3 seconds to 1 second)
                    self.pause_timer = max(0, 60 - self.wave_timer)  # 1 second pause

                    if self.wave_timer > 60:  # End of pause (was 180)
                        self.wave += 1
                        self.wave_complete = False
                        self.wave_timer = 0
                        self.pause_timer = 0
                        self.create_wave()
                        self.countdown = CountdownAnimation(SCREEN_WIDTH, SCREEN_HEIGHT)
                        self.game_started = False
                else:
                    self.update_game(current_time)

            # Update power-up info timer
            if self.show_power_up_info:
                self.power_up_info_timer -= 1
                if self.power_up_info_timer <= 0:
                    self.show_power_up_info = False

            # Draw everything
            self.draw_background()

            # Update and draw stars
            for star in self.stars:
                star.update()
                star.draw(self.screen)

            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)

            # Draw power-ups
            for power_up in self.power_ups:
                power_up.draw(self.screen)

            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)

            # Draw player and bullets
            if self.player.death_explosion:
                self.player.death_explosion.draw(self.screen)
            self.player.draw(self.screen)
            for bullet in self.player.bullets:
                bullet.draw(self.screen)

            # Draw UI
            self.draw_ui()
            self.draw_power_up_info()

            # Draw countdown
            if not self.game_started and not self.game_over:
                self.countdown.draw(self.screen)

            # Draw game over or wave complete
            if self.game_over:
                self.draw_game_over()
            elif self.wave_complete:
                self.draw_wave_complete()

            # Update particles
            self.particles = [p for p in self.particles if p.update()]

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def update_game(self, current_time):
        # Update player
        self.player.update(current_time)

        # Spawn power-ups less frequently - reduced from every ~5 seconds to every ~10 seconds
        self.power_up_timer += 1
        if self.power_up_timer > 800 and random.random() < 0.005:  # Reduced frequency
            self.spawn_power_up()
            self.power_up_timer = 0

        # Update power-ups
        for power_up in self.power_ups[:]:
            if not power_up.update():
                self.power_ups.remove(power_up)
                continue

            # Check collision with player
            if (not power_up.collected and
                    power_up.get_rect().colliderect(pygame.Rect(self.player.x, self.player.y,
                                                                self.player.width, self.player.height))):
                power_up.collected = True
                self.player.add_power_up(power_up.type, current_time)
                self.power_ups.remove(power_up)
                self.show_power_up_message(power_up.type)

                # Create collection effect
                self.create_explosion(power_up.x + power_up.width // 2,
                                      power_up.y + power_up.height // 2,
                                      power_up.data["color"], 40)

                # Play sound effect (visual feedback)
                for _ in range(30):
                    self.particles.append(Particle(
                        power_up.x + power_up.width // 2,
                        power_up.y + power_up.height // 2,
                        power_up.data["color"],
                        size_range=(3, 7),
                        speed_range=(-3, 3),
                        life_range=(20, 40)
                    ))

        # Update enemies
        edge_hit = False
        for enemy in self.enemies[:]:
            enemy.update()

            if enemy.x <= 20 or enemy.x >= SCREEN_WIDTH - enemy.width - 20:
                edge_hit = True

            if enemy.y > SCREEN_HEIGHT - 150:
                if self.player.lose_life():
                    self.game_over = True
                self.enemies.remove(enemy)
                self.create_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, RED)
                continue

            if enemy.can_shoot():
                bullet = enemy.shoot()
                self.player.bullets.append(bullet)

        if edge_hit:
            for enemy in self.enemies:
                enemy.direction *= -1
                enemy.y += 15

        # Check bullet collisions
        for bullet in self.player.bullets[:]:
            bullet.update()

            if "player" in bullet.type:
                for enemy in self.enemies[:]:
                    if bullet.get_rect().colliderect(enemy.get_rect()):
                        if enemy.hit():
                            # Calculate score with multiplier
                            score_gain = enemy.value * self.player.score_multiplier
                            self.player.score += score_gain
                            self.enemies.remove(enemy)
                            self.create_explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2,
                                                  enemy.color)

                            # Chance to drop power-up when enemy is destroyed - reduced from 25% to 10%
                            if random.random() < 0.10:  # Reduced chance
                                power_types = ["double_shot", "shield", "rapid_fire", "score_boost"]
                                power_type = random.choice(power_types)
                                self.power_ups.append(PowerUp(enemy.x, enemy.y, power_type))

                        if bullet in self.player.bullets:
                            self.player.bullets.remove(bullet)
                        break
            else:
                player_rect = pygame.Rect(self.player.x, self.player.y,
                                          self.player.width, self.player.height)
                if (bullet.get_rect().colliderect(player_rect) and
                        self.player.invincible == 0 and
                        "shield" not in self.player.active_power_ups):
                    if self.player.lose_life():
                        self.game_over = True
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)

        # Remove bullets off screen
        for bullet in self.player.bullets[:]:
            if bullet.y < -50 or bullet.y > SCREEN_HEIGHT + 50:
                self.player.bullets.remove(bullet)

        # Check wave complete
        if not self.enemies and not self.wave_complete:
            self.wave_complete = True
            self.wave_timer = 0
            self.player.score += 500 * self.player.score_multiplier