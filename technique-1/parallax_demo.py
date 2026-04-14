import pygame
import sys

# --- 초기화 ---
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("패럴랙스 스크롤링 데모")
clock = pygame.time.Clock()

# --- 레이어 이미지 생성 (색으로 구분) ---
def make_layer(color, elements):
    """배경 레이어 Surface 생성"""
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    surf.fill(color)
    for rect in elements:
        pygame.draw.rect(surf, rect[0], rect[1])
    return surf

# 하늘 레이어: 단색 하늘 + 구름
sky_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
sky_surf.fill((135, 206, 235))
for cx, cy in [(100, 60), (300, 40), (550, 70), (720, 50)]:
    pygame.draw.ellipse(sky_surf, (255, 255, 255), (cx, cy, 120, 50))
    pygame.draw.ellipse(sky_surf, (255, 255, 255), (cx + 30, cy - 20, 80, 45))

# 산 레이어
mountain_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
mountain_surf.fill((0, 0, 0, 0))
for mx, mh in [(50, 200), (180, 260), (320, 180), (460, 240), (600, 200), (720, 260)]:
    pts = [(mx, SCREEN_HEIGHT), (mx + 100, SCREEN_HEIGHT - mh), (mx + 200, SCREEN_HEIGHT)]
    pygame.draw.polygon(mountain_surf, (100, 130, 100), pts)

# 나무 레이어
tree_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
tree_surf.fill((0, 0, 0, 0))
for tx in range(0, SCREEN_WIDTH, 80):
    # 기둥
    pygame.draw.rect(tree_surf, (101, 67, 33), (tx + 35, 280, 10, 60))
    # 잎
    pygame.draw.polygon(tree_surf, (34, 139, 34),
        [(tx + 20, 280), (tx + 40, 220), (tx + 60, 280)])
    pygame.draw.polygon(tree_surf, (0, 100, 0),
        [(tx + 25, 255), (tx + 40, 200), (tx + 55, 255)])

# 지면 레이어
ground_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
ground_surf.fill((0, 0, 0, 0))
pygame.draw.rect(ground_surf, (139, 115, 85), (0, 340, SCREEN_WIDTH, 60))
pygame.draw.rect(ground_surf, (86, 130, 3), (0, 340, SCREEN_WIDTH, 15))

# =====================================================
# 핵심: 레이어 정의 — image, x 위치, 스크롤 속도
# =====================================================
layers = [
    {"image": sky_surf,      "x": 0, "speed": 0.3},   # 하늘 (가장 느림)
    {"image": mountain_surf, "x": 0, "speed": 0.8},   # 산
    {"image": tree_surf,     "x": 0, "speed": 2.0},   # 나무
    {"image": ground_surf,   "x": 0, "speed": 3.5},   # 지면 (가장 빠름)
]
# =====================================================

# --- 플레이어 (화면 고정) ---
player_rect = pygame.Rect(100, 290, 40, 50)

# =====================================================
# 핵심: 매 프레임 x를 speed만큼 줄이고, 끝에 닿으면 리셋
# =====================================================
def update_parallax():
    for layer in layers:
        layer["x"] -= layer["speed"]
        # 이미지가 왼쪽으로 완전히 나가면 리셋
        if layer["x"] + SCREEN_WIDTH <= 0:
            layer["x"] = 0

# =====================================================
# 핵심: 이미지를 두 장 나란히 blit → 무한 반복처럼 보임
# =====================================================
def draw_parallax():
    for layer in layers:
        screen.blit(layer["image"], (layer["x"], 0))
        # 이어붙인 두 번째 이미지
        screen.blit(layer["image"], (layer["x"] + SCREEN_WIDTH, 0))
# =====================================================

def draw_player():
    pygame.draw.rect(screen, (255, 140, 0), player_rect)
    pygame.draw.rect(screen, (200, 100, 0), player_rect, 2)
    font = pygame.font.SysFont(None, 24)
    screen.blit(font.render("P", True, (0, 0, 0)),
                (player_rect.x + 14, player_rect.y + 14))

def draw_ui():
    font = pygame.font.SysFont(
        ["malgungothic", "applegothic", "nanumgothic", "notosanscjk", None], 20)
    labels = [
        (layers[0]["speed"], "하늘"),
        (layers[1]["speed"], "산"),
        (layers[2]["speed"], "나무"),
        (layers[3]["speed"], "지면"),
    ]
    colors = [(100, 180, 255), (100, 160, 100), (34, 139, 34), (139, 115, 85)]
    for i, ((spd, name), col) in enumerate(zip(labels, colors)):
        txt = font.render(f"{name}: 속도 {spd}", True, col)
        screen.blit(txt, (10, 10 + i * 24))
    hint = font.render("← → 방향키로 속도 조절 | ESC 종료", True, (50, 50, 50))
    screen.blit(hint, (SCREEN_WIDTH - hint.get_width() - 10, 10))

# --- 메인 루프 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # 방향키로 전체 속도 배율 조절
            if event.key == pygame.K_RIGHT:
                for layer in layers:
                    layer["speed"] = min(layer["speed"] * 1.5, 20)
            if event.key == pygame.K_LEFT:
                for layer in layers:
                    layer["speed"] = max(layer["speed"] * 0.7, 0.1)

    update_parallax()
    draw_parallax()
    draw_player()
    draw_ui()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
