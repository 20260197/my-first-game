import pygame

# 화면 설정
WIDTH, HEIGHT = 1600, 900
FPS = 60
GRAVITY = 0.35

# 플레이어 및 적 크기
PLAYER_W, PLAYER_H = 50, 30
ENEMY_W, ENEMY_H = 30, 30

# 색상 정의
WHITE     = (255, 255, 255)
RED       = (220, 50, 50)
YELLOW    = (240, 200, 0)
GRAY      = (40, 40, 40)
DARK_GRAY = (80, 80, 80)
BLUE      = (50, 150, 255)
BOOSTER_COLOR = (255, 160, 50) 
SMOKE_COLOR   = (140, 140, 140)
CYAN = (0, 255, 255)

# settings.py
# settings.py 예시
LEVELS = [
    {"label": "Phase 1", "mode": "normal", "spawn": 60, "min_speed": 3, "max_speed": 7},
    {"label": "Phase 2", "mode": "normal", "spawn": 40, "min_speed": 5, "max_speed": 12},
    {"label": "Phase 3: Laser", "mode": "laser", "spawn": 60, "min_speed": 3, "max_speed": 7},
    {"label": "Phase 4: Hybrid", "mode": "laser_hell", "spawn": 80, "min_speed": 3, "max_speed": 7},
    {"label": "Phase 5: HELL", "mode": "laser_hell", "spawn": 50, "min_speed": 3, "max_speed": 7},
]