import base64
import io
import pygame
import random
import sys
import math
from shield import Shield

# 8x8 사이즈의 아주 작은 우주선 예시 데이터
SHEET_B64 = "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<truncated>"

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
    return [rect, 0, speed, False, 0, 0, 30, 90]

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
    
    # Base64 데이터 로드
    import io, base64
    sheet_bytes = base64.b64decode(SHEET_B64)
    player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

    # 💡 스프라이트 시트에서 프레임 추출 (총 4개)
    player_frames = []
    # 8x8 크기의 프레임이 가로로 나열되어 있다고 가정
    for i in range(4):
        # 정확히 i번째 프레임을 잘라냅니다.
        rect = pygame.Rect(i * 8, 0, 8, 8) 
        frame_img = player_sheet.subsurface(rect)
        # 게임 크기에 맞게 확대
        frame_img = pygame.transform.scale(frame_img, (PLAYER_W, PLAYER_H))
        player_frames.append(frame_img)

    # 애니메이션 변수
    current_frame = 0
    last_update = pygame.time.get_ticks()
    animation_speed = 100 # 속도를 조금 더 빠르게 조절

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

        # 💡 1. 입력 처리 (AD 키 및 화살표 키 동시 지원)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.left > 0:
            player.x -= 7
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.right < WIDTH:
            player.x += 7
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.top > 0:
            player.y -= 7
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.bottom < HEIGHT:
            player.y += 7

        # 2. 방어막 상태 업데이트
        my_shield.update(player.center)

        # 3. 적 생성
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg))

        # 4. 로직 업데이트
        alive_enemies = []
        hit_enemies = set()
        
        # 💡 애니메이션 프레임 업데이트
        now = pygame.time.get_ticks()
        if now - last_update > animation_speed:
            last_update = now
            # len(player_frames)를 사용하여 4개의 프레임이 모두 순환되도록 함
            current_frame = (current_frame + 1) % len(player_frames)

        # [유도 및 조향 로직]
        for i, en_data in enumerate(enemies):
            if en_data[3]: 
                if en_data[6] > 0:
                    en_data[6] -= 1
                else:
                    target = None
                    min_y = HEIGHT
                    for other in enemies:
                        if not other[3] and other[0].y < min_y:
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
            rect, dx, dy, is_deflected, angle, rot_speed, homing_delay, missile_lifetime = en_data
            rect.x += dx
            rect.y += dy

            if is_deflected:
                en_data[7] -= 1
                if en_data[7] <= 0:
                    for _ in range(8):
                        particles.append(Particle(rect.centerx, rect.centery, DARK_GRAY))
                    continue 

                if en_data[6] > 0:
                    en_data[2] += GRAVITY
                en_data[4] += rot_speed
                
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies:
                        if rect.colliderect(other[0]):
                            hit_enemies.add(i); hit_enemies.add(j)
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

        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)

        # 5. 플레이어 충돌 판정
        if invincible > 0:
            invincible -= 1
        else:
            for en_data in enemies:
                if not en_data[3] and player.colliderect(en_data[0]):
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

        # 💡 플레이어 이미지 그리기
        if (invincible // 10) % 2 == 0:
            screen.blit(player_frames[current_frame], player)

        for en_data in enemies:
            rect, _, _, is_deflected, angle, _, _, missile_lifetime = en_data
            if is_deflected:
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