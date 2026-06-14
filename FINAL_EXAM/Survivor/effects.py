import math

import pygame
from resource_manager import *
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
        self.life = 20
        self.frame_index = 0
        self.animation_timer = 0
        
        # 💡 [핵심] 256x128 사이즈의 프레임 4개를 가로로 불러옵니다.
        # 파일 경로가 실제 assets 폴더 위치와 맞는지 확인하세요.
        self.frames = load_sprite_sheet("assets\Weapon\Lightning\Lightning_Sheet.png", 256, 128, 4, 1)

    def draw(self, surface, cam):
        # 애니메이션 속도 제어
        self.animation_timer += 1
        if self.animation_timer >= 4: # 속도가 너무 빠르면 이 숫자를 키우세요
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 4
            
        current_image = self.frames[0][self.frame_index]

        for i in range(len(self.points) - 1):
            start = self.points[i]
            end = self.points[i+1]
            dist = start.distance_to(end)
            angle = math.degrees(math.atan2(end.y - start.y, end.x - start.x))
            
            # 💡 번개의 두께(40)를 이미지의 세로 비율에 맞춰 조정하세요
            scaled_img = pygame.transform.scale(current_image, (int(dist), 64))
            rotated_img = pygame.transform.rotate(scaled_img, -angle)
            
            rect = rotated_img.get_rect(center=((start.x + end.x)/2 - cam.x, (start.y + end.y)/2 - cam.y))
            surface.blit(rotated_img, rect.topleft)

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