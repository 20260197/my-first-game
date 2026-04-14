import pygame
import sys
import random

# --- 초기화 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("무적 프레임 데모")
clock = pygame.time.Clock()

font = pygame.font.SysFont(
    ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 20
)
font_big = pygame.font.SysFont(
    ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 32
)

# --- 플레이어 ---
player = pygame.Rect(100, SCREEN_HEIGHT // 2 - 25, 40, 50)
player_speed = 4
lives = 5
MAX_LIVES = 5

# =====================================================
# 핵심: 무적 프레임 상태 변수
# =====================================================
invincible = False
invincible_timer = 0
INVINCIBLE_DURATION = 360  # 2초 (60fps 기준)


def take_damage():
    """피격 처리 — 무적 중이면 데미지 무시"""
    global invincible, invincible_timer, lives
    if not invincible:  # 무적이 아닐 때만 데미지
        lives -= 1
        invincible = True
        invincible_timer = INVINCIBLE_DURATION


def update_invincibility():
    """매 프레임 호출 — 타이머 감소, 0이 되면 무적 해제"""
    global invincible, invincible_timer
    if invincible:
        invincible_timer -= 1
        if invincible_timer <= 0:
            invincible = False


def draw_player():
    # 핵심: 4프레임마다 그리기를 건너뜀 → 깜빡임 효과
    if invincible and (invincible_timer // 4) % 2 == 0:
        return  # 이 프레임은 그리지 않음

    color = (100, 180, 255) if invincible else (255, 140, 0)
    pygame.draw.rect(screen, color, player)
    pygame.draw.rect(screen, (200, 100, 0), player, 2)
    screen.blit(font.render("P", True, (0, 0, 0)), (player.x + 12, player.y + 13))


# =====================================================

# --- 적 (일정 간격으로 오른쪽에서 날아옴) ---
enemies = []
enemy_timer = 0
ENEMY_INTERVAL = 60


def spawn_enemy():
    ey = random.randint(50, SCREEN_HEIGHT - 70)
    enemies.append(pygame.Rect(SCREEN_WIDTH + 10, ey, 28, 28))


# --- 무적 타이머 바 ---
def draw_iframe_bar():
    bar_x, bar_y = 10, SCREEN_HEIGHT - 30
    bar_w, bar_h = 200, 16

    # 배경
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))

    if invincible:
        # 남은 시간 비율로 바 길이 결정
        ratio = invincible_timer / INVINCIBLE_DURATION
        fill_w = int(bar_w * ratio)
        # 시간에 따라 색 변화: 파랑 → 노랑
        r = int(255 * (1 - ratio))
        g = int(200 * ratio)
        b = int(255 * ratio)
        pygame.draw.rect(screen, (r, g, b), (bar_x, bar_y, fill_w, bar_h))
        label = font.render(
            f"무적 중: {invincible_timer // 60}.{(invincible_timer % 60) * 10 // 60}초",
            True,
            (255, 255, 255),
        )
    else:
        label = font.render("일반 상태", True, (200, 200, 200))

    pygame.draw.rect(screen, (180, 180, 180), (bar_x, bar_y, bar_w, bar_h), 1)
    screen.blit(label, (bar_x + bar_w + 8, bar_y))


def draw_lives():
    for i in range(MAX_LIVES):
        color = (220, 60, 60) if i < lives else (80, 80, 80)
        pygame.draw.polygon(
            screen,
            color,
            [
                (30 + i * 36, 18),
                (20 + i * 36, 30),
                (30 + i * 36, 42),
                (40 + i * 36, 30),
            ],
        )


def draw_ui():
    draw_lives()
    draw_iframe_bar()

    if lives <= 0:
        msg = font_big.render("GAME OVER  (R키로 재시작)", True, (255, 80, 80))
        screen.blit(
            msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 20)
        )

    hint = font.render("화살표: 이동 | ESC: 종료", True, (150, 150, 180))
    screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 10, SCREEN_HEIGHT - 30))


# --- 메인 루프 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r:
                # 재시작
                lives = MAX_LIVES
                invincible = False
                invincible_timer = 0
                enemies.clear()
                player.topleft = (100, SCREEN_HEIGHT // 2 - 25)

    if lives > 0:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x = max(0, player.x - player_speed)
        if keys[pygame.K_RIGHT]:
            player.x = min(SCREEN_WIDTH - player.width, player.x + player_speed)
        if keys[pygame.K_UP]:
            player.y = max(0, player.y - player_speed)
        if keys[pygame.K_DOWN]:
            player.y = min(SCREEN_HEIGHT - player.height, player.y + player_speed)

    # 적 스폰
    enemy_timer += 1
    if enemy_timer >= ENEMY_INTERVAL:
        spawn_enemy()
        enemy_timer = 0

    # 적 이동 + 충돌
    for e in list(enemies):
        e.x -= 3
        if e.x < -30:
            enemies.remove(e)
            continue
        # =====================================================
        # 핵심: 충돌 시 take_damage() 호출 — 무적 중이면 내부에서 자동 무시
        # =====================================================
        if player.colliderect(e):
            enemies.remove(e)
            take_damage()

    update_invincibility()  # 매 프레임 타이머 감소
    # =====================================================

    # --- 그리기 ---
    screen.fill((20, 20, 40))

    # 적
    for e in enemies:
        pygame.draw.ellipse(screen, (220, 60, 60), e)
        pygame.draw.ellipse(screen, (180, 20, 20), e, 2)

    draw_player()  # 무적 중 깜빡임 처리 포함
    draw_ui()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
