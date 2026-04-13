import pygame
import math
import random
from settings import *

class Shield:
    def __init__(self, radius=75):
        self.radius = int(radius)
        self.color = BLUE
        self.active = False
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

    def update(self, player_center):
        self.rect.center = player_center
        keys = pygame.key.get_pressed()
        self.active = keys[pygame.K_SPACE]

    def check_collision(self, enemy_data):
        if not self.active: return False
        enemy_rect = enemy_data[0]
        dx = self.rect.centerx - enemy_rect.centerx
        dy = self.rect.centery - enemy_rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance < self.radius + 15:
            if enemy_data[2] > 0 and not enemy_data[3]:
                enemy_data[1] = random.uniform(-6, 6) 
                enemy_data[2] = random.uniform(-15, -19) 
                enemy_data[3] = True 
                enemy_data[5] = random.uniform(7, 12) * random.choice([-1, 1])
                enemy_data[6] = 45 
                return True
        return False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 3)
            overlay = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*self.color, 60), (self.radius, self.radius), self.radius)
            screen.blit(overlay, (self.rect.x, self.rect.y))

class Particle:
    def __init__(self, x, y, color, size=None, lifetime=20):
        self.x, self.y = x, y
        self.color = color
        self.dx, self.dy = random.uniform(-2, 2), random.uniform(-2, 2)
        self.lifetime = lifetime
        self.max_life = lifetime
        self.size = size if size else random.randint(2, 4)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surf):
        if self.lifetime > 0:
            alpha = max(0, int((self.lifetime / self.max_life) * 200))
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(alpha)
            s.fill(self.color)
            surf.blit(s, (self.x, self.y))