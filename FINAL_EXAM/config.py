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
START_GOLD = 150  

# 밸런스 데이터: 적 (Enemy)
ENEMY_SPEED = 2
ENEMY_HEALTH = 100
ENEMY_RADIUS = 15
ENEMY_GOLD_REWARD = 40  
SPAWN_DELAY = 60  # 전장이 넓어졌으므로 스폰 간격을 90 -> 60으로 단축

# 밸런스 데이터: 투사체 (Projectile)
PROJECTILE_SPEED = 10  # 화면 크기에 맞춰 탄환 속도 상향 (7 -> 10)
PROJECTILE_RADIUS = 5

# 격자 크기 설정
GRID_SIZE = 40

# 3종 포탑 스탯 데이터 (넓어진 화면에 맞게 사거리 전면 상향)
TOWER_TYPES = {
    "Basic": {
        "range": 200,
        "cooldown": 30,
        "radius": 16,
        "color": (50, 50, 255),
        "bullet_color": (255, 255, 50),
        "damage": 25,
        "cost": 0
    },
    "Sniper": {
        "range": 380,
        "cooldown": 75,
        "radius": 18,
        "color": (150, 50, 200),
        "bullet_color": (255, 100, 100),
        "damage": 70,
        "cost": 0
    },
    "Rapid": {
        "range": 130,
        "cooldown": 12,
        "radius": 14,
        "color": (50, 200, 200),
        "bullet_color": (100, 255, 100),
        "damage": 8,
        "cost": 0
    }
}

# 웨이브 시스템 데이터
MAX_WAVES = 3
WAVE_ENEMY_COUNTS = [6, 12, 18]          # 맵이 넓어진 만큼 물량 상향
WAVE_HEALTH_MULTIPLIERS = [1.0, 1.7, 2.5] # 후반 웨이브 몹 체력 강화

# [변경] 1600x900 스케일에 맞춘 복잡한 3대 진입 경로 (우측 하단으로 수렴)
RAW_PATHS = [
    # 경로 1 (Wave 1부터 활성화): 좌측 상단 진입 -> 중앙 S자 순회
    [(0, 240), (480, 240), (480, 520), (1080, 520), (1080, 760), (1600, 760)],
    
    # 경로 2 (Wave 2부터 활성화): 상단 중앙 진입 -> 수직 하강 후 우회
    [(800, 0), (800, 360), (1360, 360), (1360, 760), (1600, 760)],
    
    # 경로 3 (Wave 3부터 활성화): 좌측 하단 진입 -> 상단 우회 루프
    [(0, 680), (280, 680), (280, 120), (1360, 120), (1360, 440), (1480, 440), (1480, 760), (1600, 760)]
]