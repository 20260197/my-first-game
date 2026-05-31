# config.py

# 화면 및 시스템 설정
WIDTH = 1600
HEIGHT = 900
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GREY = (220, 220, 220)
DARK_GREY = (50, 50, 50)  

# 밸런스 데이터: 게임 기본 스탯
START_LIFE = 3
START_GOLD = 300  # 복합 시스템 테스트를 위해 초기 자금 상향

# 밸런스 데이터: 적 (Enemy)
ENEMY_SPEED = 2.5
ENEMY_HEALTH = 100
ENEMY_RADIUS = 15
ENEMY_GOLD_REWARD = 40  
SPAWN_DELAY = 60  

# 밸런스 데이터: 투사체 (Projectile)
PROJECTILE_SPEED = 10  
PROJECTILE_RADIUS = 5

# 격자 크기 설정
GRID_SIZE = 40

# 3종 포탑 스탯 데이터
TOWER_TYPES = {
    "Basic": {
        "range": 200,
        "cooldown": 30,
        "radius": 16,
        "color": (50, 50, 255),
        "bullet_color": (255, 255, 50),
        "damage": 25
    },
    "Sniper": {
        "range": 380,
        "cooldown": 75,
        "radius": 18,
        "color": (150, 50, 200),
        "bullet_color": (255, 100, 100),
        "damage": 70
    },
    "Rapid": {
        "range": 130,
        "cooldown": 12,
        "radius": 14,
        "color": (50, 200, 200),
        "bullet_color": (100, 255, 100),
        "damage": 8
    }
}

# [추가] 경제 시스템 경제 지표 변수 선언
TOWER_COSTS = {"Basic": 50, "Sniper": 100, "Rapid": 80}
EQUIP_COSTS = {"Ice Gem": 60, "Explosive Ammo": 80}

# 웨이브 시스템 데이터
MAX_WAVES = 10 # 테스트를 위해 웨이브 수를 3으로 제한
WAVE_ENEMY_COUNTS = [3,6,9,12,15,18,21,24,27,30] # 테스트를 위해 각 웨이브마다 1마리씩만 등장하도록 설정
WAVE_HEALTH_MULTIPLIERS = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0] # test

# 복잡한 3대 진입 경로
RAW_PATHS = [
    [(0, 240), (480, 240), (480, 520), (1080, 520), (1080, 760), (1600, 760)],
    [(800, 0), (800, 360), (1360, 360), (1360, 760), (1600, 760)],
    [(0, 680), (280, 680), (280, 120), (1360, 120), (1360, 440), (1480, 440), (1480, 760), (1600, 760)]
]