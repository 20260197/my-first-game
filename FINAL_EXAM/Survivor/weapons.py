import pygame
import math
from Sub_config import *

class MeteorDrop:
    def __init__(self, target_pos, damage, weapon_id="trail"):
        self.pos = pygame.math.Vector2(target_pos)
        self.damage = damage
        self.radius = 45 # 범위 약간 상향
        self.weapon_id = weapon_id
        
        # 상태 관리 (경고/추락 -> 화염 장판)
        self.state = "warning"
        self.delay = 45 # 45프레임 (약 0.75초) 후 추락 완료
        self.life = 120 # 폭발 후 장판 유지 시간
        
        # 하늘에서 떨어지는 시각 효과를 위한 시작 높이
        self.fall_y = self.pos.y - 800 

    def update(self):
        if self.state == "warning":
            self.delay -= 1
            # 목표 지점을 향해 점점 빠르게 떨어지는 애니메이션 연산
            self.fall_y += (self.pos.y - self.fall_y) * 0.15 
            if self.delay <= 0:
                self.state = "burning"
        elif self.state == "burning":
            self.life -= 1
            
        # 수명이 다하면 True를 반환하여 소멸시킴
        return self.state == "burning" and self.life <= 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        if self.state == "warning":
            # 바닥 경고 표시 (테두리와 옅은 붉은색 채우기)
            pygame.draw.circle(surface, RED, screen_pos, self.radius, 2)
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 0, 40), (self.radius, self.radius), self.radius)
            surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))
            
            # 하늘에서 떨어지는 메테오 본체 렌더링
            meteor_screen_y = int(self.fall_y - cam.y)
            pygame.draw.circle(surface, ORANGE, (screen_pos[0], meteor_screen_y), 15)
            pygame.draw.line(surface, YELLOW, (screen_pos[0], meteor_screen_y), (screen_pos[0], meteor_screen_y - 60), 5)
            
        elif self.state == "burning":
            # 기존 화염 장판 렌더링
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (230, 126, 34, 100), (self.radius, self.radius), self.radius)
            surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))

class Projectile:
    def __init__(self, spawn_pos, direction, damage, pierce=1, color=YELLOW, radius=PROJECTILE_RADIUS, weapon_id="ranged"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = PROJECTILE_SPEED
        self.radius = radius
        self.damage = damage
        self.color = color
        self.pierce = pierce
        self.hit_targets = [] 
        self.weapon_id = weapon_id

    def update(self):
        self.pos += self.dir * self.speed

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)

class Boomerang:
    def __init__(self, spawn_pos, direction, damage, weapon_id="boomerang"):
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
        self.weapon_id = weapon_id

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
    def __init__(self, pos, direction, damage, weapon_id="bounce"):
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 10
        self.damage = damage
        self.radius = 10
        self.color = CYAN
        self.bounces = 3  
        self.hit_targets = []
        self.weapon_id = weapon_id

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
    def __init__(self, spawn_pos, direction, damage, weapon_id="chakram"):
        self.spawn_pos = pygame.math.Vector2(spawn_pos) # [추가] 처음 던져진 위치 기억
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        
        self.speed = 12
        self.damage = damage
        self.radius = 18
        
        # [수정] 상태를 3단계로 세분화 (outward -> hover -> returning)
        self.state = "outward"
        self.timer = 25       # 앞으로 날아가는 시간 (조금 짧게 튜닝)
        self.hover_timer = 45 # 제자리에서 회전하며 머무는 시간 (약 0.75초)
        
        self.color = ORANGE
        self.hit_targets = []
        self.angle = 0 
        self.weapon_id = weapon_id

    def update(self, player_pos):
        self.angle += 0.4 # 체공 시 갈아버리는 느낌을 위해 회전 속도 약간 증가
        
        # 1단계: 앞으로 날아감
        if self.state == "outward":
            self.pos += self.dir * self.speed
            self.timer -= 1
            if self.timer <= 0:
                self.state = "hover"
                self.hit_targets = [] # 체공할 때 닿아있는 적을 다시 타격하기 위해 초기화
                
        # 2단계: 제자리에 멈춰서 회전 (블랙홀처럼 영역 장악)
        elif self.state == "hover":
            self.hover_timer -= 1
            if self.hover_timer <= 0:
                self.state = "returning"
                self.hit_targets = [] # 돌아올 때 다시 타격하기 위해 초기화
                
        # 3단계: 플레이어가 아닌 '처음 던져졌던 위치'로 귀환
        elif self.state == "returning":
            target_dir = (self.spawn_pos - self.pos)
            # 최초 위치에 도달하면 True를 반환하여 소멸시킴
            if target_dir.length() < self.speed: 
                return True 
            self.dir = target_dir.normalize()
            self.pos += self.dir * self.speed
            
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius, 4)
        p1 = (screen_pos[0] + math.cos(self.angle)*self.radius, screen_pos[1] + math.sin(self.angle)*self.radius)
        p2 = (screen_pos[0] + math.cos(self.angle+math.pi)*self.radius, screen_pos[1] + math.sin(self.angle+math.pi)*self.radius)
        pygame.draw.line(surface, self.color, p1, p2, 3)

# [신규] 스피릿 소드용 날아가는 검기
class SwordWave:
    def __init__(self, spawn_pos, direction, damage, weapon_id="melee"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 14
        self.damage = damage
        self.color = PURPLE
        self.hit_targets = []
        self.life = 35 # 프레임 수명 (사거리)
        self.weapon_id = weapon_id

    def update(self):
        self.pos += self.dir * self.speed
        self.life -= 1
        return self.life <= 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 진행 방향에 수직인 벡터 연산 (x, y 교차 및 한쪽 반전)
        right_dir = pygame.math.Vector2(-self.dir.y, self.dir.x)
        
        width = 50       # 양옆으로 퍼지는 날개 길이
        front_depth = 20 # 앞으로 뾰족하게 튀어나온 길이
        back_depth = 10  # 뒤로 파인 길이
        
        # 4개의 꼭짓점을 구하여 초승달/쐐기 형태의 폴리곤 생성
        p1 = (screen_pos[0] + self.dir.x * front_depth, screen_pos[1] + self.dir.y * front_depth)
        p2 = (screen_pos[0] + right_dir.x * width - self.dir.x * back_depth, screen_pos[1] + right_dir.y * width - self.dir.y * back_depth)
        p3 = (screen_pos[0], screen_pos[1])
        p4 = (screen_pos[0] - right_dir.x * width - self.dir.x * back_depth, screen_pos[1] - right_dir.y * width - self.dir.y * back_depth)
        
        pygame.draw.polygon(surface, self.color, [p1, p2, p3, p4])
        pygame.draw.polygon(surface, WHITE, [p1, p2, p3, p4], 2)