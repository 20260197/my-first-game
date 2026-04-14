import pygame
import sys

# --- 초기화 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
WORLD_WIDTH = 2400  # 화면보다 3배 넓은 월드
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("카메라 추적 데모")
clock = pygame.time.Clock()

font = pygame.font.SysFont(
    ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 20
)
font_small = pygame.font.SysFont(
    ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 18
)

# --- 월드 오브젝트 (모두 월드 좌표) ---
# 지형 타일
tiles = []
for tx in range(0, WORLD_WIDTH, 60):
    tiles.append(pygame.Rect(tx, 340, 60, 60))

# 장애물 (나무, 바위)
obstacles = [
    {"rect": pygame.Rect(200, 290, 30, 50), "color": (34, 139, 34)},
    {"rect": pygame.Rect(400, 300, 50, 40), "color": (120, 100, 80)},
    {"rect": pygame.Rect(650, 270, 25, 70), "color": (34, 139, 34)},
    {"rect": pygame.Rect(900, 295, 60, 45), "color": (120, 100, 80)},
    {"rect": pygame.Rect(1100, 280, 30, 60), "color": (34, 139, 34)},
    {"rect": pygame.Rect(1400, 300, 55, 40), "color": (120, 100, 80)},
    {"rect": pygame.Rect(1700, 275, 30, 65), "color": (34, 139, 34)},
    {"rect": pygame.Rect(2000, 295, 50, 45), "color": (120, 100, 80)},
    {"rect": pygame.Rect(2200, 285, 30, 55), "color": (34, 139, 34)},
]

# 코인
coins = []
for cx in range(300, WORLD_WIDTH - 100, 250):
    coins.append({"rect": pygame.Rect(cx, 300, 20, 20), "collected": False})

# --- 플레이어 (월드 좌표) ---
player = pygame.Rect(100, 290, 36, 50)
player_speed = 4
player_vy = 0
GRAVITY = 0.5
JUMP_POWER = -12
on_ground = False

# =====================================================
# 핵심: 카메라 상태 — 값 하나로 전체 뷰를 제어
# =====================================================
camera_x = 0


def update_camera():
    global camera_x
    # 플레이어를 화면 중앙에 유지
    camera_x = player.centerx - SCREEN_WIDTH // 2
    # 월드 경계 클램프 (끝에서 더 나가지 않도록)
    camera_x = max(0, min(camera_x, WORLD_WIDTH - SCREEN_WIDTH))


def world_to_screen(world_rect):
    """핵심: 월드 좌표 → 화면 좌표 변환  (screen_x = world_x - camera_x)"""
    return pygame.Rect(
        world_rect.x - camera_x, world_rect.y, world_rect.width, world_rect.height
    )


# =====================================================


def draw_world():
    # 하늘
    screen.fill((135, 206, 235))

    # 지형 타일
    for tile in tiles:
        s = world_to_screen(tile)
        if -60 < s.x < SCREEN_WIDTH + 60:  # 화면 밖은 스킵
            pygame.draw.rect(screen, (86, 130, 3), s)
            pygame.draw.rect(screen, (60, 100, 2), s, 2)

    # 장애물
    for obs in obstacles:
        s = world_to_screen(obs["rect"])
        if -60 < s.x < SCREEN_WIDTH + 60:
            pygame.draw.rect(screen, obs["color"], s)

    # 코인
    for coin in coins:
        if not coin["collected"]:
            s = world_to_screen(coin["rect"])
            if -20 < s.x < SCREEN_WIDTH + 20:
                pygame.draw.ellipse(screen, (255, 215, 0), s)

    # 플레이어
    s = world_to_screen(player)
    pygame.draw.rect(screen, (255, 140, 0), s)
    pygame.draw.rect(screen, (200, 100, 0), s, 2)
    screen.blit(font.render("P", True, (0, 0, 0)), (s.x + 11, s.y + 13))


def draw_ui():
    # 미니맵
    map_w, map_h = 200, 20
    map_x, map_y = SCREEN_WIDTH - map_w - 10, 10
    pygame.draw.rect(screen, (200, 200, 200), (map_x, map_y, map_w, map_h))
    # 카메라 위치 표시
    cam_ratio = camera_x / max(1, WORLD_WIDTH - SCREEN_WIDTH)
    cam_bar_x = map_x + int(cam_ratio * (map_w - 30))
    pygame.draw.rect(screen, (100, 100, 255), (cam_bar_x, map_y, 30, map_h))
    # 플레이어 위치
    p_ratio = player.x / WORLD_WIDTH
    pygame.draw.rect(
        screen, (255, 140, 0), (map_x + int(p_ratio * map_w), map_y, 4, map_h)
    )
    screen.blit(
        font_small.render("미니맵", True, (50, 50, 50)), (map_x, map_y + map_h + 2)
    )

    # 좌표 정보
    info = [
        f"world_x  = {player.x}",
        f"camera_x = {int(camera_x)}",
        f"screen_x = {player.x - int(camera_x)}",
    ]
    colors = [(150, 150, 150), (220, 80, 80), (80, 120, 220)]
    for i, (txt, col) in enumerate(zip(info, colors)):
        screen.blit(font.render(txt, True, col), (10, 10 + i * 24))

    hint = font.render("← → 이동 | ↑ 점프 | ESC 종료", True, (50, 50, 50))
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 30))


# --- 메인 루프 ---
score = 0
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_UP and on_ground:
                player_vy = JUMP_POWER
                on_ground = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.x = max(0, player.x - player_speed)
    if keys[pygame.K_RIGHT]:
        player.x = min(WORLD_WIDTH - player.width, player.x + player_speed)

    # 중력/점프
    player_vy += GRAVITY
    player.y += int(player_vy)
    if player.y >= 290:
        player.y = 290
        player_vy = 0
        on_ground = True

    # 코인 수집
    for coin in coins:
        if not coin["collected"] and player.colliderect(coin["rect"]):
            coin["collected"] = True
            score += 1

    update_camera()
    draw_world()
    draw_ui()

    # 점수
    screen.blit(font.render(f"코인: {score}", True, (255, 215, 0)), (10, 82))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
