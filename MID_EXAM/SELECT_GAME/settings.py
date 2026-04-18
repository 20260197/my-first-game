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
# settings.py 내 LEVELS 수정
LEVELS = [
    {"spawn": 20, "label": "Lv.1", "mode": "normal", "min_speed": 5, "max_speed": 15},
    {"spawn": 10, "label": "Lv.2", "mode": "normal", "min_speed": 15, "max_speed": 30},
    {"spawn": 150, "label": "Lv.3", "mode": "laser"}, 
    {"spawn": 120, "label": "Lv.4", "mode": "laser"}, 
    {"spawn": 70, "label": "Lv.5", "mode": "laser_hell"}, # 💡 페이즈 5 추가 (생성 주기는 살짝 늦춤)
]