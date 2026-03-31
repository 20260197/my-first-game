import pygame
import random
import sys
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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shield Dodger")
clock = pygame.time.Clock()
font = get_korean_font(36)
font_big = get_korean_font(72)

# 레벨 설정
LEVELS = [
    {"min_speed": 3, "max_speed": 5,  "spawn": 40, "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8,  "spawn": 25, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 12, "spawn": 15, "label": "Lv.3"},
]

PLAYER_W, PLAYER_H = 50, 30
ENEMY_W, ENEMY_H = 30, 30

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    speed = random.randint(level_cfg["min_speed"], level_cfg["max_speed"])
    return pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H), speed

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
    enemies = [] # [Rect, speed]
    score = 0
    lives = 3
    spawn_timer = 0
    invincible = 0

    while True:
        clock.tick(FPS)
        level_idx = min(score // 100, len(LEVELS) - 1)
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

        # 2. 방어막 업데이트
        my_shield.update(player.center)

        # 3. 적 생성
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(list(spawn_enemy(level_cfg)))

        # 4. 적 이동 및 로직 (가장 중요한 부분)
        alive_enemies = []
        for pair in enemies:
            pair[0].y += pair[1] # 이동

            # 방어막 충돌 체크
            my_shield.check_collision(pair)

            # 화면 밖으로 나가는 적 처리
            if pair[1] < 0: # 튕겨 올라가는 적
                if pair[0].bottom < 0:
                    score += 10 # 반격 성공!
                    continue
            else: # 내려오는 적
                if pair[0].top > HEIGHT:
                    score += 1 # 회피 성공!
                    continue

            alive_enemies.append(pair)
        enemies = alive_enemies

        # 5. 충돌 판정 (플레이어 vs 적)
        if invincible > 0:
            invincible -= 1
        else:
            for pair in enemies:
                if player.colliderect(pair[0]):
                    lives -= 1
                    invincible = 90
                    enemies.clear() # 화면 청소
                    if lives <= 0:
                        if game_over_screen(score):
                            main()   
                        return
                    break

        # 6. 그리기
        screen.fill(GRAY)
        
        # 방어막 그리기
        my_shield.draw(screen)

        # 플레이어 깜빡임 연출
        if (invincible // 10) % 2 == 0:
            pygame.draw.rect(screen, BLUE, player)

        # 적 그리기
        for pair in enemies:
            # 튕겨 나가는 적은 노란색으로 강조 (선택 사항)
            color = YELLOW if pair[1] < 0 else RED
            pygame.draw.rect(screen, color, pair[0])

        draw_hud(score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()