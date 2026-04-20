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
        
        # 💡 스택형 쉴드 변수 설정
        self.max_uses = 3
        self.remaining_uses = 3
        self.duration_max = 5 * 60  # 5초 지속
        self.timer = 0
        
        # 💡 충전(리차지) 시스템 변수
        self.recharge_timer = 0
        self.recharge_max = 15 * 60  # 1개 충전당 10초 소요

    def update(self, player_center):
        self.rect.center = player_center
        keys = pygame.key.get_pressed()

        # 1. 쉴드 활성화 상태 관리
        if self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.active = False
        
        # 2. 쉴드 스택 충전 로직 (수정된 부분)
        # 쉴드가 꺼져 있고(not self.active), 스택이 가득 차지 않았을 때만 쿨다운이 진행됩니다.
        if not self.active and self.remaining_uses < self.max_uses:
            self.recharge_timer += 1
            if self.recharge_timer >= self.recharge_max:
                self.remaining_uses += 1
                self.recharge_timer = 0
        
        # 스택이 이미 가득 찼다면 타이머를 초기화합니다.
        if self.remaining_uses >= self.max_uses:
            self.recharge_timer = 0

        # 3. 쉴드 발동 (스페이스바)
        if keys[pygame.K_SPACE] and not self.active and self.remaining_uses > 0:
            self.active = True
            self.remaining_uses -= 1
            self.timer = self.duration_max

    # game_objects.py 내 Shield 클래스의 check_collision 메서드 수정
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
                
                if len(enemy_data) > 7:
                    enemy_data[7] = 90 
                return True
        return False

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, self.color, self.rect.center, self.radius, 3)
            overlay = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(overlay, (*self.color, 60), (self.radius, self.radius), self.radius)
            screen.blit(overlay, (self.rect.x, self.rect.y))
        
        self.draw_ui(screen)

    def draw_ui(self, screen):
        ui_x, ui_y = WIDTH - 80, 150
        icon_radius = 30
        
        pygame.draw.circle(screen, (50, 50, 50), (ui_x, ui_y), icon_radius)
        
        font = pygame.font.SysFont("malgungothic", 20, bold=True)
        count_txt = font.render(str(self.remaining_uses), True, WHITE)
        screen.blit(count_txt, (ui_x - count_txt.get_width()//2, ui_y - count_txt.get_height()//2))

        if self.active:
            ratio = self.timer / self.duration_max
            self.draw_sector(screen, (ui_x, ui_y), icon_radius + 5, ratio, (0, 200, 255))
        elif self.remaining_uses < self.max_uses:
            ratio = self.recharge_timer / self.recharge_max
            self.draw_sector(screen, (ui_x, ui_y), icon_radius + 5, ratio, (100, 255, 100))

    def draw_sector(self, screen, center, radius, ratio, color):
        if ratio <= 0: return
        points = [center]
        for angle in range(-90, int(360 * ratio) - 90):
            rad = math.radians(angle)
            x = center[0] + math.cos(rad) * radius
            y = center[1] + math.sin(rad) * radius
            points.append((x, y))
        if len(points) > 2:
            temp_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surf, (*color, 150), points)
            screen.blit(temp_surf, (0, 0))

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