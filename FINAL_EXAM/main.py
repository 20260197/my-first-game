import pygame
import sys
from config import *

# 1. 적이 이동할 고정 경로 (Waypoints)
PATH = [
    pygame.math.Vector2(0, 300),
    pygame.math.Vector2(200, 300),
    pygame.math.Vector2(200, 100),
    pygame.math.Vector2(500, 100),
    pygame.math.Vector2(500, 500),
    pygame.math.Vector2(800, 500)
]

# 2. 클래스 정의

class Enemy:
    """ 경로를 따라 이동하는 적 클래스 """
    def __init__(self):
        self.pos = pygame.math.Vector2(PATH[0]) 
        self.waypoint_index = 1                 
        self.speed = ENEMY_SPEED                
        self.health = ENEMY_HEALTH              
        self.max_health = ENEMY_HEALTH          
        self.radius = ENEMY_RADIUS              

    def move(self):
        if self.waypoint_index < len(PATH):
            target = PATH[self.waypoint_index]
            direction = target - self.pos 
            
            if direction.length() < self.speed:
                self.pos = pygame.math.Vector2(target)
                self.waypoint_index += 1 
            else:
                direction.normalize_ip() 
                self.pos += direction * self.speed
        else:
            return True 
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # 체력바 그리기
        bar_width = 30
        bar_height = 5
        bar_x = self.pos.x - bar_width // 2
        bar_y = self.pos.y - self.radius - 10
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


class Tower:
    """ 적을 자동 조준하여 투사체를 발사하는 타워 클래스 """
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.range = TOWER_RANGE                
        self.cooldown = TOWER_COOLDOWN          
        self.cooldown_tracker = 0
        self.radius = TOWER_RADIUS              
        
        self.range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_surface, (100, 100, 255, 40), (self.range, self.range), self.range)

    def update(self, enemies, projectiles):
        if self.cooldown_tracker > 0:
            self.cooldown_tracker -= 1

        target_enemy = None
        closest_dist = float('inf') 

        for enemy in enemies:
            dist = self.pos.distance_to(enemy.pos)
            
            if dist < self.range + enemy.radius:
                if dist < closest_dist:
                    closest_dist = dist
                    target_enemy = enemy

        if target_enemy and self.cooldown_tracker == 0:
            projectiles.append(Projectile(self.pos.x, self.pos.y, target_enemy))
            self.cooldown_tracker = self.cooldown

    def draw(self, surface):
        surface.blit(self.range_surface, (self.pos.x - self.range, self.pos.y - self.range))
        pygame.draw.circle(surface, BLUE, (int(self.pos.x), int(self.pos.y)), self.radius)


class Projectile:
    """ 타워가 발사하는 투사체(총알) 클래스 """
    def __init__(self, x, y, target):
        self.pos = pygame.math.Vector2(x, y)
        self.target = target 
        self.speed = PROJECTILE_SPEED          
        self.damage = PROJECTILE_DAMAGE        
        self.radius = PROJECTILE_RADIUS        

    def move(self):
        if self.target not in enemies:
            return True

        direction = self.target.pos - self.pos
        if direction.length() < self.speed:
            self.target.health -= self.damage
            return True
        else:
            direction.normalize_ip()
            self.pos += direction * self.speed
        return False

    def draw(self, surface):
        pygame.draw.circle(surface, YELLOW, (int(self.pos.x), int(self.pos.y)), self.radius)


class ShopMenu:
    """ 하단에서 부드럽게 슬라이드 업/다운되는 상점 UI 클래스 """
    def __init__(self):
        self.width = WIDTH
        self.height = 150              # 완전히 열렸을 때의 메뉴 높이
        self.visible_in_hidden = 30    # 닫혔을 때 살짝 보여줄 탭의 높이
        
        # Y 좌표 기준점 설정
        self.y_open = HEIGHT - self.height                  # 열린 상태 Y (450)
        self.y_hidden = HEIGHT - self.visible_in_hidden     # 닫힌 상태 Y (570)
        
        self.current_y = self.y_hidden # 시작 상태는 닫힘
        self.target_y = self.y_hidden
        self.lerp_speed = 0.15         # 애니메이션 속도 (0에 가까울수록 부드럽고 느려짐)
        
        self.font = pygame.font.SysFont(None, 28)

    def update(self, shop_phase_active):
        mouse_pos = pygame.mouse.get_pos()
        
        # 조건 1: 마우스가 화면 맨 하단 영역(Y > 550)에 진입했거나
        # 조건 2: 상점 페이즈(shop_phase_active)가 켜져 있다면 열기
        if mouse_pos[1] > HEIGHT - 50 or shop_phase_active:
            self.target_y = self.y_open
        else:
            self.target_y = self.y_hidden

        # 선형 보간(Lerp) 공식을 활용한 부드러운 좌표 이동 애니메이션
        self.current_y += (self.target_y - self.current_y) * self.lerp_speed

    def draw(self, surface):
        # 상점 판넬 그리기
        shop_rect = pygame.Rect(0, int(self.current_y), self.width, self.height)
        pygame.draw.rect(surface, DARK_GREY, shop_rect)
        pygame.draw.rect(surface, BLACK, shop_rect, 3) # 테두리 선
        
        # 상점 가이드 텍스트
        text_str = "SHOP PHASE ACTIVE (Press 'S' to Toggle)" if self.target_y == self.y_open else "SHOP (Hover Mouse Here)"
        text_color = YELLOW if self.target_y == self.y_open else WHITE
        text_surface = self.font.render(text_str, True, text_color)
        surface.blit(text_surface, (WIDTH // 2 - text_surface.get_width() // 2, int(self.current_y) + 8))


# 3. 메인 게임 루프 설정
pygame.init()
pygame.font.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Tower Defense Assignment - Prototype")
clock = pygame.time.Clock()

ui_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

# 게임 스탯 변수
life = START_LIFE
gold = START_GOLD
shop_phase = False # 상점 페이즈 On/Off 토글 변수

enemies = []
towers = [
    Tower(150, 200),  
    Tower(400, 250)   
]
projectiles = []
shop_menu = ShopMenu() # 상점 인스턴스 생성

spawn_timer = 0

running = True
while running:
    clock.tick(FPS) 
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 키보드 이벤트 처리
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s: # 'S' 키를 누르면 상점 페이즈 토글
                shop_phase = not shop_phase

    # --- 데이터 업데이트 ---
    if life > 0:
        spawn_timer += 1
        if spawn_timer >= SPAWN_DELAY: 
            enemies.append(Enemy())
            spawn_timer = 0

        for enemy in enemies[:]:
            is_escaped = enemy.move()
            if is_escaped:
                life -= 1
                gold += ENEMY_GOLD_REWARD // 2
                enemies.remove(enemy)
            elif enemy.health <= 0:
                gold += ENEMY_GOLD_REWARD
                enemies.remove(enemy)

        for tower in towers:
            tower.update(enemies, projectiles)

        for projectile in projectiles[:]:
            hit = projectile.move()
            if hit:
                if projectile in projectiles:
                    projectiles.remove(projectile)
        
        # 상점 애니메이션 업데이트
        shop_menu.update(shop_phase)

    # --- 화면 그리기 ---
    if len(PATH) > 1:
        pygame.draw.lines(screen, GREY, False, [ (p.x, p.y) for p in PATH ], 40) 

    for tower in towers:
        tower.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for projectile in projectiles:
        projectile.draw(screen)

    # UI 그리기 (텍스트 레이어)
    life_text = ui_font.render(f"LIFE: {max(0, life)}", True, BLACK)
    gold_text = ui_font.render(f"GOLD: {gold}G", True, BLACK)
    screen.blit(life_text, (20, 20))
    screen.blit(gold_text, (20, 55))

    # 최상단 레이어에 상점 UI 그리기 (게임 오브젝트들 위에 덮여야 하므로 가장 나중에 그립니다)
    if life > 0:
        shop_menu.draw(screen)

    # 게임 오버 연출
    if life <= 0:
        game_over_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        game_over_surface.fill((0, 0, 0, 100)) 
        screen.blit(game_over_surface, (0, 0))
        
        go_text = game_over_font.render("GAME OVER", True, RED)
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()