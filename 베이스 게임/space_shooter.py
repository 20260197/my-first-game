import pygame
import random
import sys

# 1. 초기화 및 설정
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

# 색상 정의
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (20,  20,  40)
BLUE   = (50,  150, 255)
RED    = (220, 50,  50)
YELLOW = (240, 220, 0)
GREEN  = (50,  220, 80)
ORANGE = (240, 140, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter - Enhanced")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 설정 (레벨업 기준을 score // 200으로 완만하게 조정) ---
LEVELS = [
    {"enemy_speed_min": 2, "enemy_speed_max": 3, "spawn": 60, "label": "Lv.1"},
    {"enemy_speed_min": 3, "enemy_speed_max": 5, "spawn": 40, "label": "Lv.2"},
    {"enemy_speed_min": 5, "enemy_speed_max": 8, "spawn": 25, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 40, 40
ENEMY_W,  ENEMY_H  = 36, 36
BULLET_W, BULLET_H = 6,  14

# --- 그리기 함수들 ---
def draw_player(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, BLUE, [
        (cx, rect.top),
        (rect.left, rect.bottom),
        (cx, rect.bottom - 8),
        (rect.right, rect.bottom),
    ])
    pygame.draw.rect(surf, YELLOW, (cx - 4, rect.bottom - 10, 8, 10))

def draw_enemy(surf, rect):
    cx = rect.centerx
    pygame.draw.polygon(surf, RED, [
        (cx, rect.bottom),
        (rect.left, rect.top),
        (cx, rect.top + 8),
        (rect.right, rect.top),
    ])

def draw_stars(surf, stars):
    for s in stars:
        # s[2]는 별의 크기(반지름)
        pygame.draw.circle(surf, WHITE, (int(s[0]), int(s[1])), s[2])

# --- 로직 함수들 ---
def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    # 적이 생성될 때 해당 레벨의 속도 범위 내에서 개별 속도를 부여함 (핵심 수정)
    speed = random.uniform(level_cfg["enemy_speed_min"], level_cfg["enemy_speed_max"])
    return {"rect": pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H), "speed": speed}

def draw_hud(score, lives, level_cfg):
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"Lives: {'♥ ' * lives}", True, RED), (WIDTH - 180, 10))
    screen.blit(font.render(level_cfg["label"], True, YELLOW), (WIDTH // 2 - 25, 10))

def game_over_screen(score):
    screen.fill((10, 10, 30))
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

# --- 메인 루프 ---
def main():
    player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 70, PLAYER_W, PLAYER_H)
    bullets = []
    enemies = [] # 이제 사각형이 아니라 딕셔너리 {"rect":..., "speed":...}를 담음
    score = 0
    lives = 3
    shoot_cd = 0
    spawn_timer = 0
    invincible = 0

    # 별 데이터 (x, y, size)
    stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)]
             for _ in range(80)]

    while True:
        clock.tick(FPS)
        level_idx = min(score // 200, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        # 1. 입력 및 플레이어 이동
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]  and player.left  > 0:      player.x -= 6
        if keys[pygame.K_RIGHT] and player.right < WIDTH:   player.x += 6
        if keys[pygame.K_UP]    and player.top   > 0:      player.y -= 6
        if keys[pygame.K_DOWN]  and player.bottom < HEIGHT: player.y += 6

        # 2. 별 이동 (배경 흐름 효과 추가)
        for s in stars:
            s[1] += 2 # 아래로 이동
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, WIDTH)

        # 3. 총알 발사 및 이동
        shoot_cd -= 1
        if keys[pygame.K_SPACE] and shoot_cd <= 0:
            b = pygame.Rect(player.centerx - BULLET_W // 2, player.top, BULLET_W, BULLET_H)
            bullets.append(b)
            shoot_cd = 15

        bullets = [b for b in bullets if b.bottom > 0]
        for b in bullets:
            b.y -= 10

        # 4. 적 생성 및 이동 (개별 속도 적용)
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg))

        alive_enemies = []
        for en in enemies:
            en["rect"].y += en["speed"] # 각 적의 고유 속도 사용
            # 적의 몸통이 화면 아래로 완전히 나갈 때까지 유지 (en["rect"].top < HEIGHT)
            if en["rect"].top < HEIGHT:
                alive_enemies.append(en)
        enemies = alive_enemies

        # 5. 충돌 판정 (총알 vs 적)
        hit_bullets = set()
        hit_enemies = set()
        for bi, b in enumerate(bullets):
            for ei, en in enumerate(enemies):
                if b.colliderect(en["rect"]):
                    hit_bullets.add(bi)
                    hit_enemies.add(ei)
                    score += 10
        
        bullets = [b for i, b in enumerate(bullets) if i not in hit_bullets]
        enemies = [en for i, en in enumerate(enemies) if i not in hit_enemies]

        # 6. 충돌 판정 (플레이어 vs 적)
        if invincible > 0:
            invincible -= 1
        else:
            for en in enemies:
                if player.colliderect(en["rect"]):
                    lives -= 1
                    invincible = 90
                    enemies.clear()
                    if lives <= 0:
                        if game_over_screen(score):
                            main()
                        return
                    break

        # 7. 그리기
        screen.fill(GRAY)
        draw_stars(screen, stars)

        for b in bullets:
            pygame.draw.rect(screen, YELLOW, b)

        for en in enemies:
            draw_enemy(screen, en["rect"])

        if (invincible // 10) % 2 == 0:
            draw_player(screen, player)

        draw_hud(score, lives, level_cfg)
        pygame.display.flip()

if __name__ == "__main__":
    main()