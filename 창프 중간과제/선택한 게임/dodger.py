import pygame
import random
import sys
import math
from shield import Shield

# 초기화
pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0:
            return font
    return pygame.font.SysFont(None, size)

WIDTH, HEIGHT = 800, 600
FPS = 60

# 색상
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE  = (50, 120, 220)
RED   = (220, 50, 50)
YELLOW = (240, 200, 0)
GRAY  = (40, 40, 40)
ORANGE = (255, 165, 0)
DARK_GRAY = (80, 80, 80)

# 물리 상수
GRAVITY = 0.5

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shield Dodger: Missile Fuel System")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 파티클 클래스 ---
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.dx = random.uniform(-5, 5)
        self.dy = random.uniform(-5, 5)
        self.lifetime = 25
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1

    def draw(self, surf):
        if self.lifetime > 0:
            alpha = max(0, int((self.lifetime / 25) * 255))
            s = pygame.Surface((self.size, self.size))
            s.set_alpha(alpha)
            s.fill(self.color)
            surf.blit(s, (self.x, self.y))

particles = []

# --- 레벨 설정 ---
LEVELS = [
    {"min_speed": 3, "max_speed": 5,  "spawn": 40, "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8,  "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 50, 30
ENEMY_W, ENEMY_H = 30, 30

enemy_surface = pygame.Surface((ENEMY_W, ENEMY_H), pygame.SRCALPHA)
pygame.draw.rect(enemy_surface, RED, (0, 0, ENEMY_W, ENEMY_H))

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    rect = pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)
    # 💡 데이터 구조: [Rect, dx, dy, is_deflected, angle, rot_speed, homing_delay, missile_lifetime]
    # 마지막 인덱스 180은 유도탄의 수명 (3초 @ 60FPS)
    return [rect, 0, speed, False, 0, 0, 30, 180]

def draw_hud(score, level_cfg, lives):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"{level_cfg['label']}", True, YELLOW), (10, 40))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 200, 10))

def game_over_screen(score):
    screen.fill(GRAY)
    screen.blit(font_big.render("GAME OVER", True, RED), (220, 220))
    screen.blit(font.render(f"Final Score: {score}", True, WHITE), (330, 310))
    screen.blit(font.render("R: Restart   Q: Quit", True, WHITE), (270, 360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: pygame.quit(); sys.exit()

def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)
    my_shield = Shield(radius=75)
    enemies = [] 
    score = 0
    lives = 3
    spawn_timer = 0
    invincible = 0

    while True:
        clock.tick(FPS)
        level_idx = min(score // 300, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # 1. 입력 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.left  > 0:      player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH:   player.x += 7
        if keys[pygame.K_UP]    and player.top   > 0:      player.y -= 7
        if keys[pygame.K_DOWN]  and player.bottom < HEIGHT: player.y += 7

        # 2. 방어막 상태 업데이트
        my_shield.update(player.center)

        # 3. 적 생성 스폰
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg))

        # 4. 로직 업데이트 (이동 및 적간 충돌)
        alive_enemies = []
        hit_enemies = set()

        # [유도 및 조향(Steering) 로직]
        for i, en_data in enumerate(enemies):
            if en_data[3]: # 튕겨나간 적
                if en_data[6] > 0:
                    en_data[6] -= 1 # Launch Delay
                else:
                    target = None
                    min_y = HEIGHT
                    for other in enemies:
                        if not other[3]: # 일반 적 중에서
                            if other[0].y < min_y:
                                min_y = other[0].y
                                target = other
                    
                    if target:
                        target_pos = pygame.math.Vector2(target[0].center)
                        current_pos = pygame.math.Vector2(en_data[0].center)
                        desired_vel = (target_pos - current_pos).normalize() * 15
                        en_data[1] += (desired_vel.x - en_data[1]) * 0.08
                        en_data[2] += (desired_vel.y - en_data[2]) * 0.08

        # [이동 및 충돌 체크]
        for i, en_data in enumerate(enemies):
            if i in hit_enemies: continue
            # rect, dx, dy, is_deflected, angle, rot_speed, homing_delay, missile_lifetime
            rect, dx, dy, is_deflected, angle, rot_speed, homing_delay, missile_lifetime = en_data
            
            rect.x += dx
            rect.y += dy

            if is_deflected:
                # 💡 수명(연료) 감소 로직
                en_data[7] -= 1
                if en_data[7] <= 0:
                    # 수명이 다하면 회색 연기 파티클 생성 후 소멸
                    for _ in range(8):
                        particles.append(Particle(rect.centerx, rect.centery, DARK_GRAY))
                    continue # 소멸했으므로 alive_enemies에 추가하지 않음

                if en_data[6] > 0:
                    en_data[2] += GRAVITY
                en_data[4] += rot_speed
                
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies:
                        if rect.colliderect(other[0]):
                            hit_enemies.add(i)
                            hit_enemies.add(j)
                            score += 50
                            for _ in range(15):
                                particles.append(Particle(rect.centerx, rect.centery, YELLOW))
                            break
            
            my_shield.check_collision(en_data)

            if rect.top > HEIGHT + 100 or rect.bottom < -100 or rect.left < -100 or rect.right > WIDTH + 100:
                if not is_deflected and rect.top > HEIGHT: score += 1
                continue
            
            if i not in hit_enemies:
                alive_enemies.append(en_data)
        
        enemies = alive_enemies

        # 파티클 업데이트
        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)

        # 5. 플레이어 충돌 판정
        if invincible > 0:
            invincible -= 1
        else:
            for en_data in enemies:
                if not en_data[3]: 
                    if player.colliderect(en_data[0]):
                        lives -= 1
                        invincible = 90
                        enemies.clear()
                        if lives <= 0:
                            if game_over_screen(score): main()
                            return
                        break

        # 6. 그리기 섹션
        screen.fill(GRAY)
        my_shield.draw(screen)

        for p in particles:
            p.draw(screen)

        if (invincible // 10) % 2 == 0:
            pygame.draw.rect(screen, BLUE, player)

        for en_data in enemies:
            rect, _, _, is_deflected, angle, _, _, missile_lifetime = en_data
            if is_deflected:
                # 💡 수명이 얼마 안 남았을 때 깜빡거리는 효과 (선택 사항)
                if missile_lifetime > 30 or (missile_lifetime // 5) % 2 == 0:
                    rotated_img = pygame.transform.rotate(enemy_surface, angle)
                    new_rect = rotated_img.get_rect(center=rect.center)
                    screen.blit(rotated_img, new_rect.topleft)
            else:
                pygame.draw.rect(screen, RED, rect)

        draw_hud(score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()