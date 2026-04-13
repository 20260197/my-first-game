import pygame

# 화면 설정
WIDTH, HEIGHT = 800, 600
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

# settings.py
LEVELS = [
    {"spawn": 40, "label": "Lv.1", "mode": "normal", "min_speed": 3, "max_speed": 5},
    {"spawn": 25, "label": "Lv.2", "mode": "normal", "min_speed": 5, "max_speed": 8},
    {"spawn": 50, "label": "Lv.3", "mode": "laser"}, # 레이저 모드 시작
    {"spawn": 35, "label": "Lv.4", "mode": "laser"}, # 더 빈번한 레이저
]