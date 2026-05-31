import pygame
from Sub_config import *

class DamageText:
    def __init__(self, pos, amount):
        self.pos = pygame.math.Vector2(pos)
        self.amount = amount
        self.life = 40
        self.vy = -1.5

    def update(self):
        self.pos.y += self.vy
        self.life -= 1

    def draw(self, surface, cam, font):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        color = YELLOW if self.amount > 20 else WHITE
        txt = font.render(str(self.amount), True, color)
        txt.set_alpha(max(0, int((self.life / 40) * 255)))
        surface.blit(txt, (screen_pos[0] - txt.get_width()//2, screen_pos[1]))

class SlashEffect:
    def __init__(self, pos, radius):
        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        self.life = 8

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, PURPLE, screen_pos, self.radius, 3)

class LightningEffect:
    def __init__(self, points):
        self.points = [pygame.math.Vector2(p) for p in points]
        self.life = 10 

    def draw(self, surface, cam):
        screen_points = [(int(p.x - cam.x), int(p.y - cam.y)) for p in self.points]
        if len(screen_points) >= 2:
            pygame.draw.lines(surface, CYAN, False, screen_points, 5)
            pygame.draw.lines(surface, WHITE, False, screen_points, 2)

# [신규] 궤도 레이저 이펙트
class BeamEffect:
    def __init__(self, start_pos, end_pos, width):
        self.start_pos = pygame.math.Vector2(start_pos)
        self.end_pos = pygame.math.Vector2(end_pos)
        self.width = width
        self.life = 15
        
    def draw(self, surface, cam):
        s = (int(self.start_pos.x - cam.x), int(self.start_pos.y - cam.y))
        e = (int(self.end_pos.x - cam.x), int(self.end_pos.y - cam.y))
        pygame.draw.line(surface, CYAN, s, e, self.width)
        pygame.draw.line(surface, WHITE, s, e, max(1, self.width//3))

# [신규] 블리자드(눈보라) 이펙트
class BlizzardEffect:
    def __init__(self, pos, radius):
        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        self.life = 20
        
    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, CYAN, screen_pos, self.radius, 5)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius - 10, 2)