import pygame
import sys
import random

# --- 초기화 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("화면 흔들기 데모")
clock = pygame.time.Clock()

font = pygame.font.SysFont(
    ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 20)

# =====================================================
# 핵심: 오프스크린 버퍼 — 모든 그림은 여기에 먼저 그린다
# =====================================================
buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
# =====================================================

# =====================================================
# 핵심: 화면 흔들기 상태와 함수
# =====================================================
shake_amount = 0

def trigger_shake(amount=10):
    """흔들기 시작 — 피격/폭발 시 호출"""
    global shake_amount
    shake_amount = amount

def get_shake_offset():
    """매 프레임 랜덤 오프셋 반환, shake_amount를 1씩 감소"""
    global shake_amount
    if shake_amount > 0:
        ox = random.randint(-shake_amount, shake_amount)
        oy = random.randint(-shake_amount, shake_amount)
        shake_amount = max(0, shake_amount - 1)
        return ox, oy
    return 0, 0
# =====================================================

# --- 플레이어 ---
player = pygame.Rect(SCREEN_WIDTH // 2 - 18, SCREEN_HEIGHT // 2 - 25, 36, 50)
player_speed = 4
lives = 5

# --- 적 (화면 좌우에서 날아오는 공) ---
enemies = []
enemy_timer = 0
ENEMY_INTERVAL = 90   # 프레임

def spawn_enemy():
    side = random.choice(["left", "right"])
    if side == "left":
        ex, evx = -20, random.uniform(2, 4)
    else:
        ex, evx = SCREEN_WIDTH + 20, -random.uniform(2, 4)
    ey = random.randint(80, SCREEN_HEIGHT - 80)
    enemies.append({"rect": pygame.Rect(ex, ey, 20, 20), "vx": evx})

# --- 파티클 (피격 이펙트) ---
particles = []

def spawn_particles(x, y):
    for _ in range(20):
        particles.append({
            "x": x, "y": y,
            "vx": random.uniform(-4, 4),
            "vy": random.uniform(-5, 1),
            "life": random.randint(20, 40),
            "color": random.choice([(255,80,80),(255,160,0),(255,255,100)]),
        })

def draw_scene():
    # 배경
    buffer.fill((30, 30, 50))

    # 격자 (흔들림이 더 잘 보이도록)
    for gx in range(0, SCREEN_WIDTH, 80):
        pygame.draw.line(buffer, (50, 50, 80), (gx, 0), (gx, SCREEN_HEIGHT))
    for gy in range(0, SCREEN_HEIGHT, 80):
        pygame.draw.line(buffer, (50, 50, 80), (0, gy), (SCREEN_WIDTH, gy))

    # 적
    for e in enemies:
        pygame.draw.ellipse(buffer, (220, 60, 60), e["rect"])
        pygame.draw.ellipse(buffer, (180, 20, 20), e["rect"], 2)

    # 파티클
    for p in particles:
        alpha = int(255 * p["life"] / 40)
        col = (*p["color"][:3],)
        pygame.draw.circle(buffer, col, (int(p["x"]), int(p["y"])), 3)

    # 플레이어
    col = (255, 140, 0) if lives > 0 else (150, 150, 150)
    pygame.draw.rect(buffer, col, player)
    pygame.draw.rect(buffer, (200, 100, 0), player, 2)
    buffer.blit(font.render("P", True, (0,0,0)), (player.x + 11, player.y + 13))

    # UI
    buffer.blit(font.render(f"목숨: {'♥ ' * lives}", True, (220, 80, 80)), (10, 10))
    buffer.blit(font.render(f"shake: {shake_amount}", True, (180, 180, 100)), (10, 36))

    hint_lines = [
        "SPACE: 약한 흔들기 (5)",
        "Z: 강한 흔들기 (20)",
        "화살표: 이동",
    ]
    for i, line in enumerate(hint_lines):
        txt = font.render(line, True, (150, 150, 180))
        buffer.blit(txt, (SCREEN_WIDTH - txt.get_width() - 10, 10 + i * 24))

# --- 메인 루프 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                trigger_shake(5)
            if event.key == pygame.K_z:
                trigger_shake(20)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  player.x = max(0, player.x - player_speed)
    if keys[pygame.K_RIGHT]: player.x = min(SCREEN_WIDTH - player.width, player.x + player_speed)
    if keys[pygame.K_UP]:    player.y = max(0, player.y - player_speed)
    if keys[pygame.K_DOWN]:  player.y = min(SCREEN_HEIGHT - player.height, player.y + player_speed)

    # 적 스폰
    enemy_timer += 1
    if enemy_timer >= ENEMY_INTERVAL:
        spawn_enemy()
        enemy_timer = 0

    # 적 이동 + 충돌
    for e in list(enemies):
        e["rect"].x += e["vx"]
        if e["rect"].x < -30 or e["rect"].x > SCREEN_WIDTH + 30:
            enemies.remove(e)
            continue
        if player.colliderect(e["rect"]):
            enemies.remove(e)
            lives = max(0, lives - 1)
            spawn_particles(player.centerx, player.centery)
            trigger_shake(12)   # ← 피격 시 흔들기 발동

    # 파티클 업데이트
    for p in list(particles):
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.3
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

    # =====================================================
    # 핵심: buffer에 씬 그리기 → 오프셋 계산 → screen에 blit
    # =====================================================
    # 1. buffer에 모든 씬 그리기
    draw_scene()

    # 2. 흔들기 오프셋 계산
    ox, oy = get_shake_offset()

    # 3. screen을 검정으로 지우고, buffer를 오프셋만큼 이동해서 blit
    screen.fill((0, 0, 0))
    screen.blit(buffer, (ox, oy))
    # =====================================================

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
