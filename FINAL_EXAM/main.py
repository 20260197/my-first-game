import pygame
import sys
import random
from config import *

# 1. 원시 경로 데이터를 Pygame Vector2 2차원 리스트로 변환
PATHS = [[pygame.math.Vector2(pt) for pt in raw_p] for raw_p in RAW_PATHS]

# 2. 고급 수학 연산 함수 (벡터 선분 거리 계산)
def dist_to_segment(p, a, b):
    """ 점 P에서 선분 AB 사이의 최단 거리를 반환 (경로 설치 불가 영역 판정용) """
    ab = b - a
    ap = p - a
    if ab.length_squared() == 0:
        return p.distance_to(a)
    
    t = ap.dot(ab) / ab.length_squared()
    t = max(0, min(1, t))
    
    closest_point = a + ab * t
    return p.distance_to(closest_point)

def is_tile_blocked(cx, cy, current_towers):
    """ 격자 중심점(cx, cy)이 포탑 중복이거나 '모든 경로 선분'과 가까운지 판정 """
    p = pygame.math.Vector2(cx, cy)
    
    for t in current_towers:
        if t.pos.distance_to(p) < GRID_SIZE:
            return True
            
    for path in PATHS:
        for i in range(len(path) - 1):
            if dist_to_segment(p, path[i], path[i+1]) < 35:
                return True
    return False


# 3. 클래스 정의

class Enemy:
    def __init__(self, wave_num, assigned_path):
        self.path = assigned_path
        self.pos = pygame.math.Vector2(self.path[0]) 
        self.waypoint_index = 1                 
        self.speed = ENEMY_SPEED                
        self.radius = ENEMY_RADIUS              
        
        hp_multiplier = WAVE_HEALTH_MULTIPLIERS[wave_num - 1]
        self.health = int(ENEMY_HEALTH * hp_multiplier)
        self.max_health = self.health

    def move(self):
        if self.waypoint_index < len(self.path):
            target = self.path[self.waypoint_index]
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
        
        bar_width = 30
        bar_height = 5
        bar_x = self.pos.x - bar_width // 2
        bar_y = self.pos.y - self.radius - 10
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))


class Tower:
    def __init__(self, x, y, tower_type):
        self.pos = pygame.math.Vector2(x, y)
        self.type = tower_type
        
        stats = TOWER_TYPES[tower_type]
        self.range = stats["range"]
        self.cooldown = stats["cooldown"]
        self.radius = stats["radius"]
        self.color = stats["color"]
        self.bullet_color = stats["bullet_color"]
        self.damage = stats["damage"]
        
        self.cooldown_tracker = 0
        
        self.range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_surface, (self.color[0], self.color[1], self.color[2], 40), (self.range, self.range), self.range)

    def update(self, enemies, projectiles):
        if self.cooldown_tracker > 0:
            self.cooldown_tracker -= 1

        target_enemy = None
        farthest_dist = -1 

        for enemy in enemies:
            dist = self.pos.distance_to(enemy.pos)
            if dist < self.range + enemy.radius:
                if dist > farthest_dist:
                    farthest_dist = dist
                    target_enemy = enemy

        if target_enemy and self.cooldown_tracker == 0:
            projectiles.append(Projectile(self.pos.x, self.pos.y, target_enemy, self.damage, self.bullet_color))
            self.cooldown_tracker = self.cooldown

    def draw(self, surface):
        surface.blit(self.range_surface, (self.pos.x - self.range, self.pos.y - self.range))
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius // 2, 2) 


class Projectile:
    def __init__(self, x, y, target, damage, color):
        self.pos = pygame.math.Vector2(x, y)
        self.target = target 
        self.speed = PROJECTILE_SPEED          
        self.damage = damage        
        self.color = color
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
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class ShopMenu:
    def __init__(self):
        self.width = WIDTH
        self.height = 150              
        self.visible_in_hidden = 30    
        self.y_open = HEIGHT - self.height                  
        self.y_hidden = HEIGHT - self.visible_in_hidden     
        self.current_y = self.y_hidden 
        self.target_y = self.y_hidden
        self.lerp_speed = 0.15         
        self.font = pygame.font.SysFont(None, 24)

    def update(self, shop_phase_active):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[1] > HEIGHT - 50 or shop_phase_active:
            self.target_y = self.y_open
        else:
            self.target_y = self.y_hidden
        self.current_y += (self.target_y - self.current_y) * self.lerp_speed

    def check_click(self, mouse_pos):
        btn_y = self.current_y + 45
        if btn_y <= mouse_pos[1] <= btn_y + 70:
            if 50 <= mouse_pos[0] <= 170: return "Basic"
            if 200 <= mouse_pos[0] <= 320: return "Sniper"
            if 350 <= mouse_pos[0] <= 470: return "Rapid"
        return None

    def draw(self, surface):
        shop_rect = pygame.Rect(0, int(self.current_y), self.width, self.height)
        pygame.draw.rect(surface, DARK_GREY, shop_rect)
        pygame.draw.rect(surface, BLACK, shop_rect, 3) 
        
        text_str = "SHOP PHASE (Click Tower to Buy / Right-Click to Cancel)" if self.target_y == self.y_open else "SHOP (Hover Mouse)"
        text_surface = self.font.render(text_str, True, WHITE)
        surface.blit(text_surface, (20, int(self.current_y) + 10))

        btn_y = int(self.current_y) + 45
        for idx, (t_name, stats) in enumerate(TOWER_TYPES.items()):
            btn_x = 50 + (idx * 150)
            btn_rect = pygame.Rect(btn_x, btn_y, 120, 70)
            
            pygame.draw.rect(surface, stats["color"], btn_rect)
            pygame.draw.rect(surface, WHITE, btn_rect, 2)
            
            name_lbl = self.font.render(t_name, True, WHITE)
            cost_lbl = self.font.render(f"Cost: {stats['cost']}G", True, YELLOW)
            surface.blit(name_lbl, (btn_x + 10, btn_y + 12))
            surface.blit(cost_lbl, (btn_x + 10, btn_y + 38))


# 4. 씬 제어 및 인게임 변수 초기화 함수
def init_game():
    """ 스테이지에 진입할 때 게임 내부 데이터를 깨끗하게 초기화하는 함수 """
    global life, gold, shop_phase, current_wave, enemies_spawned, game_clear, spawn_timer, selected_tower_type, enemies, towers, projectiles
    life = START_LIFE
    gold = START_GOLD
    shop_phase = False 
    current_wave = 1
    enemies_spawned = 0
    game_clear = False  
    spawn_timer = 0
    selected_tower_type = None 
    enemies = []
    towers = [] 
    projectiles = []


# 5. 메인 게임 루프 설정
pygame.init()
pygame.font.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Tower Defense Assignment - Scene Architecture")
clock = pygame.time.Clock()

# 전역 폰트 로드
ui_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

# [추가] 글로벌 씬 상태 변수 ("TITLE", "STAGE_SELECT", "GAME")
scene = "TITLE"

# UI용 고정 버튼 리스트 (중앙 배치)
title_start_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 60)
stage1_select_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60)
game_return_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 50) # 승리/패배시 탈출 버튼

shop_menu = ShopMenu() 

running = True
while running:
    clock.tick(FPS) 
    mouse_pos = pygame.mouse.get_pos()

    # ==========================================
    # Ⅰ. 이벤트 처리 파트 (씬별 분기)
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 1. 타이틀 화면 이벤트
        if scene == "TITLE":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if title_start_btn.collidepoint(mouse_pos):
                    scene = "STAGE_SELECT"

        # 2. 스테이지 선택 화면 이벤트
        elif scene == "STAGE_SELECT":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if stage1_select_btn.collidepoint(mouse_pos):
                    init_game() # 인게임 데이터 초기화
                    scene = "GAME"

        # 3. 실제 인게임 화면 이벤트
        elif scene == "GAME":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: 
                    shop_phase = not shop_phase

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    # 승리 혹은 패배 상태일 때 반환 버튼 클릭 판정
                    if (life <= 0 or game_clear) and game_return_btn.collidepoint(mouse_pos):
                        scene = "STAGE_SELECT"
                    # 정상 게임 진행 중 클릭 판정
                    elif mouse_pos[1] > shop_menu.current_y:
                        clicked_type = shop_menu.check_click(mouse_pos)
                        if clicked_type: selected_tower_type = clicked_type
                    elif selected_tower_type and life > 0 and not game_clear:
                        snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                        snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                        
                        if not is_tile_blocked(snap_x, snap_y, towers):
                            towers.append(Tower(snap_x, snap_y, selected_tower_type))
                            selected_tower_type = None 
                            
                elif event.button == 3: 
                    selected_tower_type = None

    # ==========================================
    # Ⅱ. 데이터 실시간 업데이트 파트 (씬별 분기)
    # ==========================================
    if scene == "GAME":
        if life > 0 and not game_clear:
            max_enemies_in_wave = WAVE_ENEMY_COUNTS[current_wave - 1]

            if enemies_spawned < max_enemies_in_wave:
                spawn_timer += 1
                if spawn_timer >= SPAWN_DELAY: 
                    available_paths = PATHS[:current_wave]
                    chosen_path = random.choice(available_paths) 
                    
                    enemies.append(Enemy(current_wave, chosen_path)) 
                    enemies_spawned += 1
                    spawn_timer = 0
            else:
                if len(enemies) == 0:
                    if current_wave < MAX_WAVES:
                        current_wave += 1
                        enemies_spawned = 0
                        spawn_timer = -120 
                    else:
                        game_clear = True

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
            
            shop_menu.update(shop_phase)

    # ==========================================
    # Ⅲ. 화면 렌더링(Draw) 파트 (씬별 분기)
    # ==========================================
    
    # --- 1. TITLE SCENE ---
    if scene == "TITLE":
        screen.fill(DARK_GREY)
        title_text = game_over_font.render("ROGUELIKE DEFENSE", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 120))
        
        # 스타트 버튼
        pygame.draw.rect(screen, BLUE, title_start_btn)
        pygame.draw.rect(screen, WHITE, title_start_btn, 2)
        btn_text = ui_font.render("GAME START", True, WHITE)
        screen.blit(btn_text, (title_start_btn.centerx - btn_text.get_width() // 2, title_start_btn.centery - btn_text.get_height() // 2))

    # --- 2. STAGE SELECT SCENE ---
    elif scene == "STAGE_SELECT":
        screen.fill(DARK_GREY)
        select_text = game_over_font.render("SELECT A STAGE", True, WHITE)
        screen.blit(select_text, (WIDTH // 2 - select_text.get_width() // 2, HEIGHT // 2 - 150))
        
        # 스테이지 1 버튼
        pygame.draw.rect(screen, GREEN, stage1_select_btn)
        pygame.draw.rect(screen, WHITE, stage1_select_btn, 2)
        st_text = ui_font.render("STAGE 1 (S-Curve)", True, WHITE)
        screen.blit(st_text, (stage1_select_btn.centerx - st_text.get_width() // 2, stage1_select_btn.centery - st_text.get_height() // 2))

    # --- 3. IN-GAME SCENE ---
    elif scene == "GAME":
        screen.fill(WHITE)
        
        # 경로 렌더링
        for path in PATHS:
            pygame.draw.lines(screen, GREY, False, [ (p.x, p.y) for p in path ], 40) 

        for tower in towers:
            tower.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)

        # 포탑 배치 배치 프리뷰
        if selected_tower_type and life > 0 and not game_clear:
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (235, 235, 235), (0, y), (WIDTH, y), 1)
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (235, 235, 235), (x, 0), (x, HEIGHT), 1)
                
            if mouse_pos[1] < shop_menu.current_y:
                snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                
                blocked = is_tile_blocked(snap_x, snap_y, towers)
                preview_color = (255, 50, 50, 90) if blocked else (50, 255, 50, 90)
                
                t_stats = TOWER_TYPES[selected_tower_type]
                r = t_stats["range"]
                p_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                pygame.draw.circle(p_surf, (t_stats["color"][0], t_stats["color"][1], t_stats["color"][2], 40), (r, r), r)
                screen.blit(p_surf, (snap_x - r, snap_y - r))
                
                b_surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                b_surf.fill(preview_color)
                screen.blit(b_surf, (snap_x - GRID_SIZE // 2, snap_y - GRID_SIZE // 2))

        # UI 상단 스탯 출력
        life_text = ui_font.render(f"LIFE: {max(0, life)}", True, BLACK)
        gold_text = ui_font.render(f"GOLD: {gold}G", True, BLACK)
        wave_text = ui_font.render(f"WAVE: {current_wave} / {MAX_WAVES}", True, BLUE)
        screen.blit(life_text, (20, 20))
        screen.blit(gold_text, (20, 55))
        screen.blit(wave_text, (WIDTH - 180, 20)) 

        if life > 0 and not game_clear:
            shop_menu.draw(screen)

        # 게임오버 버튼 UI 연출
        if life <= 0:
            game_over_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            game_over_surface.fill((0, 0, 0, 100)) 
            screen.blit(game_over_surface, (0, 0))
            go_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))
            
            # 스테이지로 리턴하는 버튼 출력
            pygame.draw.rect(screen, RED, game_return_btn)
            pygame.draw.rect(screen, WHITE, game_return_btn, 2)
            ret_text = ui_font.render("Return to Stage Select", True, WHITE)
            screen.blit(ret_text, (game_return_btn.centerx - ret_text.get_width() // 2, game_return_btn.centery - ret_text.get_height() // 2))

        # 게임 승리 버튼 UI 연출
        if game_clear:
            victory_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            victory_surface.fill((0, 200, 0, 80)) 
            screen.blit(victory_surface, (0, 0))
            vic_text = game_over_font.render("VICTORY!", True, BLUE)
            screen.blit(vic_text, (WIDTH // 2 - vic_text.get_width() // 2, HEIGHT // 2 - vic_text.get_height() // 2))
            
            # 스테이지로 리턴하는 버튼 출력
            pygame.draw.rect(screen, BLUE, game_return_btn)
            pygame.draw.rect(screen, WHITE, game_return_btn, 2)
            ret_text = ui_font.render("Return to Stage Select", True, WHITE)
            screen.blit(ret_text, (game_return_btn.centerx - ret_text.get_width() // 2, game_return_btn.centery - ret_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()