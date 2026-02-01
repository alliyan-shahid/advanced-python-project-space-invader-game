import pygame
import random
import math

# Colors
WHITE = (255, 255, 255)
NEON_BLUE = (0, 200, 255)
CYAN = (0, 255, 255)
NEON_GREEN = (57, 255, 20)
RED = (255, 50, 50)
GOLD = (255, 215, 0)


class PowerUp:
    """Power-up that falls from the sky"""

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.width = 50
        self.height = 50
        self.speed = random.uniform(2, 4)
        self.animation = 0
        self.collected = False
        self.rotation = 0

        # Define power-up types with better visuals
        self.power_types = {
            "double_shot": {"color": NEON_BLUE, "symbol": "🔫", "name": "DOUBLE SHOT", "permanent": True},
            "shield": {"color": CYAN, "symbol": "🛡️", "name": "SHIELD", "duration": 10000},
            "rapid_fire": {"color": NEON_GREEN, "symbol": "⚡", "name": "RAPID FIRE", "duration": 8000},
            "extra_life": {"color": RED, "symbol": "❤️", "name": "EXTRA LIFE", "permanent": True},
            "score_boost": {"color": GOLD, "symbol": "⭐", "name": "SCORE X2", "duration": 15000}
        }

        self.data = self.power_types[power_type]
        self.pulse = 0

    def update(self):
        self.y += self.speed
        self.animation += 0.1
        self.rotation += 2
        self.pulse += 0.1
        return self.y < 768 + 50  # SCREEN_HEIGHT is 768

    def draw(self, screen):
        if self.collected:
            return

        # Floating animation with pulse
        float_offset = math.sin(self.animation) * 8
        pulse_size = 1 + math.sin(self.pulse) * 0.2

        # Draw power-up container with rotation
        power_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Outer glow
        glow_radius = self.width // 2 + 5
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.circle(power_surface, (*self.data["color"], alpha),
                               (self.width // 2, self.height // 2),
                               int(glow_radius * pulse_size))

        # Main circle
        pygame.draw.circle(power_surface, self.data["color"],
                           (self.width // 2, self.height // 2), self.width // 2 - 5)

        # Inner circle
        pygame.draw.circle(power_surface, WHITE,
                           (self.width // 2, self.height // 2), self.width // 2 - 10)

        # Draw symbol with rotation
        symbol_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        font = pygame.font.Font(None, 35)
        text = font.render(self.data["symbol"], True, self.data["color"])
        symbol_surface.blit(text, (self.width // 2 - text.get_width() // 2,
                                   self.height // 2 - text.get_height() // 2))

        # Rotate the symbol surface
        rotated_symbol = pygame.transform.rotate(symbol_surface, self.rotation)
        symbol_rect = rotated_symbol.get_rect(center=(self.width // 2, self.height // 2))
        power_surface.blit(rotated_symbol, symbol_rect)

        # Rotate the entire power-up
        rotated_power = pygame.transform.rotate(power_surface, self.rotation)
        power_rect = rotated_power.get_rect(center=(self.x + self.width // 2,
                                                    self.y + float_offset + self.height // 2))

        screen.blit(rotated_power, power_rect)

        # Draw name below power-up
        name_font = pygame.font.Font(None, 20)
        name_text = name_font.render(self.data["name"], True, WHITE)
        screen.blit(name_text, (self.x + self.width // 2 - name_text.get_width() // 2,
                                self.y + float_offset + self.height + 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)