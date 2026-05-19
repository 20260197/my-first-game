# config.py

# 화면 및 시스템 설정
WIDTH = 800
HEIGHT = 600
FPS = 60

# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 50)
GREY = (200, 200, 200)
DARK_GREY = (50, 50, 50)  # 상점 메뉴 배경색용 추가

# 밸런스 데이터: 게임 기본 스탯
START_LIFE = 3
START_GOLD = 150  

# 밸런스 데이터: 적 (Enemy)
ENEMY_SPEED = 2
ENEMY_HEALTH = 100
ENEMY_RADIUS = 15
ENEMY_GOLD_REWARD = 40  
SPAWN_DELAY = 90  

# 밸런스 데이터: 타워 (Tower)
TOWER_RANGE = 150
TOWER_COOLDOWN = 30
TOWER_RADIUS = 20

# 밸런스 데이터: 투사체 (Projectile)
PROJECTILE_SPEED = 7
PROJECTILE_DAMAGE = 25
PROJECTILE_RADIUS = 5