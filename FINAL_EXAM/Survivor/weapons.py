import pygame
import math
from Sub_config import *

class FireZone:
    def __init__(self, pos, damage):
        self.pos = pygame.math.Vector2(pos)
        self.damage = damage
        self.radius = 35
        self.life = 120 

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (230, 126, 34, 100), (self.radius, self.radius), self.radius)
        surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))

class Projectile:
    def __init__(self, spawn_pos, direction, damage, pierce=1, color=YELLOW, radius=PROJECTILE_RADIUS):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = PROJECTILE_SPEED
        self.radius = radius
        self.damage = damage
        self.color = color
        self.pierce = pierce
        self.hit_targets = [] 

    def update(self):
        self.pos += self.dir * self.speed

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)

class Boomerang:
    def __init__(self, spawn_pos, direction, damage):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 15
        self.damage = damage
        self.radius = 12
        self.state = "outward"
        self.timer = 30
        self.color = GREEN
        self.hit_targets = []

    def update(self, player_pos):
        if self.state == "outward":
            self.pos += self.dir * self.speed
            self.timer -= 1
            if self.timer <= 0:
                self.state = "returning"
                self.hit_targets = []
        else:
            target_dir = (player_pos - self.pos)
            if target_dir.length() < 30: return True
            self.dir = target_dir.normalize()
            self.pos += self.dir * self.speed
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius//2, 2)

class BouncingOrb:
    def __init__(self, pos, direction, damage):
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 10
        self.damage = damage
        self.radius = 10
        self.color = CYAN
        self.bounces = 3  
        self.hit_targets = []

    def update(self):
        self.pos += self.dir * self.speed
        bounced = False
        
        if self.pos.x <= self.radius:
            self.pos.x = self.radius
            self.dir.x *= -1
            bounced = True
        elif self.pos.x >= WORLD_WIDTH - self.radius:
            self.pos.x = WORLD_WIDTH - self.radius
            self.dir.x *= -1
            bounced = True
            
        if self.pos.y <= self.radius:
            self.pos.y = self.radius
            self.dir.y *= -1
            bounced = True
        elif self.pos.y >= WORLD_HEIGHT - self.radius:
            self.pos.y = WORLD_HEIGHT - self.radius
            self.dir.y *= -1
            bounced = True
            
        if bounced:
            self.bounces -= 1
            self.hit_targets = []
        return self.bounces < 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)

class Chakram:
    def __init__(self, spawn_pos, direction, damage):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 12
        self.damage = damage
        self.radius = 18
        self.state = "outward"
        self.timer = 40
        self.color = ORANGE
        self.hit_targets = []
        self.angle = 0 

    def update(self, player_pos):
        self.angle += 0.3 
        if self.state == "outward":
            self.pos += self.dir * self.speed
            self.timer -= 1
            if self.timer <= 0:
                self.state = "returning"
                self.hit_targets = []
        else:
            target_dir = (player_pos - self.pos)
            if target_dir.length() < 30: return True
            self.dir = target_dir.normalize()
            self.pos += self.dir * self.speed
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius, 4)
        p1 = (screen_pos[0] + math.cos(self.angle)*self.radius, screen_pos[1] + math.sin(self.angle)*self.radius)
        p2 = (screen_pos[0] + math.cos(self.angle+math.pi)*self.radius, screen_pos[1] + math.sin(self.angle+math.pi)*self.radius)
        pygame.draw.line(surface, self.color, p1, p2, 3)