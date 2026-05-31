import pygame
import sys
import random
from config import *

# 1. 원시 경로 데이터를 Pygame Vector2 리스트로 변환
PATHS = [[pygame.math.Vector2(pt) for pt in raw_p] for raw_p in RAW_PATHS]

# [버그 방지] 게임 최초 실행 시점의 원본 쿨타임 백업 데이터셋
ORIGINAL_COOLDOWNS = {t_name: stats["cooldown"] for t_name, stats in TOWER_TYPES.items()}

# 경로 픽셀 끊김 보완 전용 렌더링 함수
def draw_smooth_path(surface, color, path_points, width):
    if len(path_points) < 2:
        return
    int_points = [(int(p.x), int(p.y)) for p in path_points]
    radius = width // 2
    for p in int_points:
        pygame.draw.circle(surface, color, p, radius)
    for i in range(len(int_points) - 1):
        pygame.draw.line(surface, color, int_points[i], int_points[i+1], width)

# 고급 수학 연산 함수
def dist_to_segment(p, a, b):
    ab = b - a
    ap = p - a
    if ab.length_squared() == 0:
        return p.distance_to(a)
    t = ap.dot(ab) / ab.length_squared()
    t = max(0, min(1, t))
    closest_point = a + ab * t
    return p.distance_to(closest_point)

def is_tile_blocked(cx, cy, current_towers):
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
        self.radius = ENEMY_RADIUS              
        self.slow_timer = 0
        
        # [추가] 웨이브에 따라 무작위로 몬스터 타입 결정
        # 1웨이브는 일반형만, 2웨이브부터 신속형 섞임, 3웨이브는 광폭화형 등장
        types_available = ["Normal"]
        if wave_num >= 2: types_available.append("Fast")
        if wave_num >= 3: types_available.append("Berserker")
        self.type = random.choice(types_available)
        
        # 타입별 스탯 차별화 (시스템 확장 없이 값만 변조)
        if self.type == "Normal":
            self.base_speed = ENEMY_SPEED
            hp_mod = 1.0
            self.color = RED
        elif self.type == "Fast":
            self.base_speed = ENEMY_SPEED * 1.6  # 훨씬 빠름
            hp_mod = 0.6                        # 대신 체력이 낮음
            self.color = (255, 100, 255)         # 핑크색
        elif self.type == "Berserker":
            self.base_speed = ENEMY_SPEED * 0.8  # 처음엔 조금 느림
            hp_mod = 1.5                        # 대신 탱탱함
            self.color = (150, 0, 0)             # 검붉은색

        hp_multiplier = WAVE_HEALTH_MULTIPLIERS[wave_num - 1]
        self.health = int(ENEMY_HEALTH * hp_multiplier * hp_mod)
        self.max_health = self.health

    def move(self):
        # 1) 슬로우 상태이상 연산
        if self.slow_timer > 0:
            self.speed = self.base_speed * 0.5  
            self.slow_timer -= 1
        else:
            self.speed = self.base_speed

        # [추가 기믹] 광폭화(Berserker) 몹은 체력이 50% 이하로 떨어지면 속도가 2배 폭발
        if self.type == "Berserker" and self.health <= (self.max_health * 0.5):
            self.speed *= 2.0
            self.color = (255, 0, 0) # 분노 상태 표시 (밝은 빨간색 변조)

        # 2) 경로 이동 연산
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
        # 슬로우 상태일 때는 하늘색 오라, 평소에는 자신의 고유 타입 색상 출력
        body_color = (100, 200, 255) if self.slow_timer > 0 else self.color
        pygame.draw.circle(surface, body_color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # 체력바 렌더링
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
        self.level = 1
        self.upgrade_cost = 50
        self.equipment = None  
        
        self.total_invested = TOWER_COSTS[tower_type]
        self.sell_value = self.total_invested // 2
        
        self.update_range_surface()

    def update_range_surface(self):
        self.range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.range_surface, (self.color[0], self.color[1], self.color[2], 40), (self.range, self.range), self.range)

    def upgrade(self):
        if self.level >= 3:
            return
        self.level += 1
        self.damage = int(self.damage * 1.4)       
        self.range = int(self.range * 1.1)         
        self.upgrade_cost = int(self.upgrade_cost * 1.5) 
        self.update_range_surface()

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
            projectiles.append(Projectile(self.pos.x, self.pos.y, target_enemy, self.damage, self.bullet_color, self.equipment))
            self.cooldown_tracker = self.cooldown

    def draw(self, surface, font):
        surface.blit(self.range_surface, (self.pos.x - self.range, self.pos.y - self.range))
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.pos.x), int(self.pos.y)), self.radius // 2, 2) 
        
        lvl_color = (255, 120, 0) if self.level == 3 else BLACK
        lvl_str = "Lv.MAX" if self.level == 3 else f"Lv.{self.level}"
        lvl_lbl = font.render(lvl_str, True, lvl_color)
        surface.blit(lvl_lbl, (int(self.pos.x) - lvl_lbl.get_width() // 2, int(self.pos.y) - self.radius - 16))
        
        if self.equipment == "Ice Gem":
            pygame.draw.circle(surface, (0, 190, 255), (int(self.pos.x), int(self.pos.y)), 6)
        elif self.equipment == "Explosive Ammo":
            pygame.draw.circle(surface, (255, 120, 0), (int(self.pos.x), int(self.pos.y)), 6)


class Projectile:
    def __init__(self, x, y, target, damage, color, effect_type):
        self.pos = pygame.math.Vector2(x, y)
        self.target = target 
        self.speed = PROJECTILE_SPEED          
        self.damage = damage        
        self.color = color
        self.effect_type = effect_type  
        self.radius = PROJECTILE_RADIUS        

    def move(self):
        if self.target not in enemies:
            return True

        direction = self.target.pos - self.pos
        if direction.length() < self.speed:
            self.target.health -= self.damage
            if self.effect_type == "Ice Gem":
                self.target.slow_timer = 120  
            elif self.effect_type == "Explosive Ammo":
                for enemy in enemies:
                    if enemy != self.target and enemy.pos.distance_to(self.pos) < 80:
                        enemy.health -= int(self.damage * 0.5)
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
        self.target_y = self.y_open 
        self.lerp_speed = 0.15         
        self.font = pygame.font.SysFont(None, 22)

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
            if 50 <= mouse_pos[0] <= 170: return ("TOWER", "Basic")
            if 200 <= mouse_pos[0] <= 320: return ("TOWER", "Sniper")
            if 350 <= mouse_pos[0] <= 470: return ("TOWER", "Rapid")
            if 530 <= mouse_pos[0] <= 670: return ("EQUIP", "Ice Gem")
            if 700 <= mouse_pos[0] <= 840: return ("EQUIP", "Explosive Ammo")
        return None

    def draw(self, surface, gold):
        shop_rect = pygame.Rect(0, int(self.current_y), self.width, self.height)
        pygame.draw.rect(surface, DARK_GREY, shop_rect)
        pygame.draw.rect(surface, BLACK, shop_rect, 3) 
        
        text_str = "SHOP PHASE (Click Tower to Buy / Equip Card to Slot / Right-Click to Cancel)" if self.target_y == self.y_open else "SHOP (Hover Mouse)"
        text_surface = self.font.render(text_str, True, WHITE)
        surface.blit(text_surface, (20, int(self.current_y) + 10))

        btn_y = int(self.current_y) + 45
        
        for idx, (t_name, stats) in enumerate(TOWER_TYPES.items()):
            btn_x = 50 + (idx * 150)
            btn_rect = pygame.Rect(btn_x, btn_y, 130, 70)
            pygame.draw.rect(surface, stats["color"], btn_rect)
            pygame.draw.rect(surface, WHITE, btn_rect, 2)
            name_lbl = self.font.render(t_name, True, WHITE)
            
            cost_color = YELLOW if gold >= TOWER_COSTS[t_name] else RED
            cost_lbl = self.font.render(f"Cost: {TOWER_COSTS[t_name]}G", True, cost_color)
            surface.blit(name_lbl, (btn_x + 10, btn_y + 12))
            surface.blit(cost_lbl, (btn_x + 10, btn_y + 38))

        equip_idx = 0
        for eq_name, eq_cost in EQUIP_COSTS.items():
            btn_x = 530 + (equip_idx * 170)
            btn_rect = pygame.Rect(btn_x, btn_y, 150, 70)
            
            eq_color = (0, 140, 200) if eq_name == "Ice Gem" else (200, 80, 0)
            pygame.draw.rect(surface, eq_color, btn_rect)
            pygame.draw.rect(surface, WHITE, btn_rect, 2)
            
            name_lbl = self.font.render(eq_name, True, WHITE)
            
            cost_color = YELLOW if gold >= eq_cost else RED
            cost_lbl = self.font.render(f"Equip: {eq_cost}G", True, cost_color)
            surface.blit(name_lbl, (btn_x + 10, btn_y + 12))
            surface.blit(cost_lbl, (btn_x + 10, btn_y + 38))
            equip_idx += 1


AUGMENT_POOL = [
    {"id": "cooldown_down", "name": "Overcharge Battery", "desc": "All Basic Towers Cooldown -15%"},
    {"id": "gold_up",        "name": "Bounty Hunter",     "desc": "Kill Gold Reward +20G Global"},
    {"id": "life_up",        "name": "Emergency Repair",  "desc": "Instantly Restore 2 Lifes"}
]

def init_game():
    global life, gold, shop_phase, current_wave, enemies_spawned, game_clear, spawn_timer, enemies, towers, projectiles, wave_active
    global augment_active, current_choices, enemy_gold_bonus, selected_item, focused_tower
    life = START_LIFE
    gold = START_GOLD
    shop_phase = False 
    current_wave = 1
    enemies_spawned = 0
    game_clear = False  
    spawn_timer = 0
    enemies = []
    towers = [] 
    projectiles = []
    wave_active = False 
    
    augment_active = False
    current_choices = []
    enemy_gold_bonus = 0
    selected_item = None      
    focused_tower = None      

    for t_name, c_val in ORIGINAL_COOLDOWNS.items():
        TOWER_TYPES[t_name]["cooldown"] = c_val


def apply_augment(augment_id):
    global life, enemy_gold_bonus, towers
    if augment_id == "cooldown_down":
        for t_type in TOWER_TYPES:
            TOWER_TYPES[t_type]["cooldown"] = int(TOWER_TYPES[t_type]["cooldown"] * 0.85)
        for t in towers:
            t.cooldown = int(t.cooldown * 0.85)
    elif augment_id == "gold_up":
        enemy_gold_bonus += 20
    elif augment_id == "life_up":
        life += 2


# 5. 메인 게임 루프 설정
pygame.init()
pygame.font.init() 
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
pygame.display.set_caption("Tower Defense Assignment - Dynamic Scaling Master")
clock = pygame.time.Clock()

ui_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

scene = "TITLE"
wave_active = False 

title_start_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 60)
stage1_select_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 40, 300, 60)
game_return_btn = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 50) 
wave_start_btn = pygame.Rect(WIDTH - 220, 70, 200, 50)

choice_rects = [
    pygame.Rect(300, 250, 300, 400),
    pygame.Rect(650, 250, 300, 400),
    pygame.Rect(1000, 250, 300, 400)
]

shop_menu = ShopMenu() 

running = True
while running:
    clock.tick(FPS) 
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if scene == "TITLE":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if title_start_btn.collidepoint(mouse_pos):
                    scene = "STAGE_SELECT"

        elif scene == "STAGE_SELECT":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if stage1_select_btn.collidepoint(mouse_pos):
                    init_game() 
                    scene = "GAME"

        elif scene == "GAME":
            if augment_active:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for idx, rect in enumerate(choice_rects):
                        if rect.collidepoint(mouse_pos):
                            apply_augment(current_choices[idx]["id"])
                            current_wave += 1
                            enemies_spawned = 0
                            spawn_timer = 0
                            wave_active = False
                            augment_active = False
                            break
                continue 

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s: 
                    shop_phase = not shop_phase

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if (life <= 0 or game_clear) and game_return_btn.collidepoint(mouse_pos):
                        scene = "STAGE_SELECT"
                    
                    elif not wave_active and life > 0 and not game_clear and wave_start_btn.collidepoint(mouse_pos):
                        wave_active = True
                        selected_item = None 
                        focused_tower = None
                        
                    elif not wave_active and life > 0 and not game_clear:
                        if mouse_pos[1] > shop_menu.current_y:
                            clicked_res = shop_menu.check_click(mouse_pos)
                            if clicked_res:
                                cost = TOWER_COSTS[clicked_res[1]] if clicked_res[0] == "TOWER" else EQUIP_COSTS[clicked_res[1]]
                                if gold >= cost:
                                    selected_item = clicked_res
                                    focused_tower = None  
                                else:
                                    selected_item = None
                        
                        else:
                            if selected_item:
                                if selected_item[0] == "TOWER":
                                    snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                                    snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                                    if not is_tile_blocked(snap_x, snap_y, towers):
                                        towers.append(Tower(snap_x, snap_y, selected_item[1]))
                                        gold -= TOWER_COSTS[selected_item[1]]
                                        selected_item = None
                                        
                                elif selected_item[0] == "EQUIP":
                                    target_t = None
                                    for t in towers:
                                        if t.pos.distance_to(mouse_pos) < t.radius + 15:
                                            target_t = t
                                            break
                                    if target_t and target_t.equipment is None:
                                        target_t.equipment = selected_item[1]
                                        gold -= EQUIP_COSTS[selected_item[1]]
                                        selected_item = None
                            else:
                                upgrade_triggered = False
                                if focused_tower:
                                    up_btn_rect = pygame.Rect(focused_tower.pos.x - 70, focused_tower.pos.y - focused_tower.radius - 48, 65, 24)
                                    sell_btn_rect = pygame.Rect(focused_tower.pos.x + 5, focused_tower.pos.y - focused_tower.radius - 48, 65, 24)
                                    
                                    if up_btn_rect.collidepoint(mouse_pos):
                                        if focused_tower.level < 3 and gold >= focused_tower.upgrade_cost:
                                            gold -= focused_tower.upgrade_cost
                                            focused_tower.total_invested += focused_tower.upgrade_cost
                                            focused_tower.sell_value = focused_tower.total_invested // 2
                                            focused_tower.upgrade()
                                        upgrade_triggered = True
                                    
                                    elif sell_btn_rect.collidepoint(mouse_pos):
                                        gold += focused_tower.sell_value
                                        towers.remove(focused_tower)
                                        focused_tower = None
                                        upgrade_triggered = True
                                
                                if not upgrade_triggered:
                                    clicked_t = None
                                    for t in towers:
                                        if t.pos.distance_to(mouse_pos) < t.radius + 15:
                                            clicked_t = t
                                            break
                                    focused_tower = clicked_t
                            
                elif event.button == 3: 
                    selected_item = None
                    focused_tower = None

    if scene == "GAME":
        if life > 0 and not game_clear and not augment_active:
            # [변경] 웨이브가 리스트 범위를 초과할 경우 스폰 마리 수 자동 등차수열 계산
            if current_wave <= len(WAVE_ENEMY_COUNTS):
                max_enemies_in_wave = WAVE_ENEMY_COUNTS[current_wave - 1]
            else:
                max_enemies_in_wave = WAVE_ENEMY_COUNTS[-1] + (current_wave - len(WAVE_ENEMY_COUNTS)) * 6

            # [변경] 스폰 생성주기(딜레이 프레임) 조절: 후반부로 갈수록 스폰 주기가 6프레임씩 단축 (최소 15프레임 제한)
            current_spawn_delay = max(15, SPAWN_DELAY - (current_wave - 1) * 6)

            if wave_active:
                if enemies_spawned < max_enemies_in_wave:
                    spawn_timer += 1
                    if spawn_timer >= current_spawn_delay: 
                        # [변경] 경로 개수는 3개 이상 늘어나지 않도록 len(PATHS)로 가드 잠금
                        available_paths = PATHS[:min(current_wave, len(PATHS))]
                        chosen_path = random.choice(available_paths) 
                        enemies.append(Enemy(current_wave, chosen_path)) 
                        enemies_spawned += 1
                        spawn_timer = 0
                else:
                    if len(enemies) == 0:
                        if current_wave < MAX_WAVES:
                            augment_active = True
                            current_choices = random.sample(AUGMENT_POOL, 3)
                        else:
                            game_clear = True

            for enemy in enemies[:]:
                is_escaped = enemy.move()
                if is_escaped:
                    life -= 1
                    gold += (ENEMY_GOLD_REWARD + enemy_gold_bonus) // 2
                    enemies.remove(enemy)
                elif enemy.health <= 0:
                    gold += ENEMY_GOLD_REWARD + enemy_gold_bonus
                    enemies.remove(enemy)

            for tower in towers:
                tower.update(enemies, projectiles)

            for projectile in projectiles[:]:
                hit = projectile.move()
                if hit and projectile in projectiles:
                    projectiles.remove(projectile)
            
            shop_menu.update(shop_phase)

    # ==========================================
    # Ⅲ. 화면 렌더링(Draw) 파트
    # ==========================================
    if scene == "TITLE":
        screen.fill(DARK_GREY)
        title_text = game_over_font.render("ROGUELIKE DEFENSE", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 120))
        pygame.draw.rect(screen, BLUE, title_start_btn)
        pygame.draw.rect(screen, WHITE, title_start_btn, 2)
        btn_text = ui_font.render("GAME START", True, WHITE)
        screen.blit(btn_text, (title_start_btn.centerx - btn_text.get_width() // 2, title_start_btn.centery - btn_text.get_height() // 2))

    elif scene == "STAGE_SELECT":
        screen.fill(DARK_GREY)
        select_text = game_over_font.render("SELECT A STAGE", True, WHITE)
        screen.blit(select_text, (WIDTH // 2 - select_text.get_width() // 2, HEIGHT // 2 - 150))
        pygame.draw.rect(screen, GREEN, stage1_select_btn)
        pygame.draw.rect(screen, WHITE, stage1_select_btn, 2)
        st_text = ui_font.render("STAGE 1 (S-Curve)", True, WHITE)
        screen.blit(st_text, (stage1_select_btn.centerx - st_text.get_width() // 2, stage1_select_btn.centery - st_text.get_height() // 2))

    elif scene == "GAME":
        screen.fill(WHITE)
        
        for path in PATHS:
            draw_smooth_path(screen, GREY, path, 40) 

        if not wave_active:
            for idx, path in enumerate(PATHS):
                # [변경] 가이드라인 표시 상한선을 실제 경로 개수로 가드 처리
                if idx < min(current_wave, len(PATHS)):
                    draw_smooth_path(screen, (255, 200, 200), path, 12)

        for tower in towers:
            tower.draw(screen, shop_menu.font)
        for enemy in enemies:
            enemy.draw(screen)
        for projectile in projectiles:
            projectile.draw(screen)

        if not wave_active and focused_tower and life > 0 and not game_clear:
            up_box = pygame.Rect(focused_tower.pos.x - 70, focused_tower.pos.y - focused_tower.radius - 48, 65, 24)
            sell_box = pygame.Rect(focused_tower.pos.x + 5, focused_tower.pos.y - focused_tower.radius - 48, 65, 24)
            
            if focused_tower.level >= 3:
                pygame.draw.rect(screen, GREY, up_box, 0, 4)
                pygame.draw.rect(screen, BLACK, up_box, 1, 4)
                up_lbl = shop_menu.font.render("MAX", True, DARK_GREY)
            else:
                box_color = YELLOW if gold >= focused_tower.upgrade_cost else GREY
                pygame.draw.rect(screen, box_color, up_box, 0, 4)
                pygame.draw.rect(screen, BLACK, up_box, 1, 4)
                up_lbl = shop_menu.font.render(f"UP:{focused_tower.upgrade_cost}", True, BLACK)
            screen.blit(up_lbl, (up_box.centerx - up_lbl.get_width() // 2, up_box.centery - up_lbl.get_height() // 2))

            pygame.draw.rect(screen, (255, 200, 200), sell_box, 0, 4) 
            pygame.draw.rect(screen, BLACK, sell_box, 1, 4)
            sell_lbl = shop_menu.font.render(f"+$:{focused_tower.sell_value}", True, BLACK)
            screen.blit(sell_lbl, (sell_box.centerx - sell_lbl.get_width() // 2, sell_box.centery - sell_lbl.get_height() // 2))

        if not wave_active and selected_item and life > 0 and not game_clear:
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (235, 235, 235), (0, y), (WIDTH, y), 1)
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (235, 235, 235), (x, 0), (x, HEIGHT), 1)
                
            if mouse_pos[1] < shop_menu.current_y:
                if selected_item[0] == "TOWER":
                    snap_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                    snap_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
                    blocked = is_tile_blocked(snap_x, snap_y, towers)
                    preview_color = (255, 50, 50, 90) if blocked else (50, 255, 50, 90)
                    
                    t_stats = TOWER_TYPES[selected_item[1]]
                    r = t_stats["range"]
                    p_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
                    pygame.draw.circle(p_surf, (t_stats["color"][0], t_stats["color"][1], t_stats["color"][2], 40), (r, r), r)
                    screen.blit(p_surf, (snap_x - r, snap_y - r))
                    
                    b_surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                    b_surf.fill(preview_color)
                    screen.blit(b_surf, (snap_x - GRID_SIZE // 2, snap_y - GRID_SIZE // 2))
                    
                elif selected_item[0] == "EQUIP":
                    eq_lbl = ui_font.render(f"Equip -> [ {selected_item[1]} ]", True, BLACK)
                    screen.blit(eq_lbl, (mouse_pos[0] + 15, mouse_pos[1] - 15))

        if not wave_active and life > 0 and not game_clear:
            # [변경] 스폰 마커 드로우 범위 상한선을 실제 경로 개수로 안전하게 캡핑
            for idx in range(min(current_wave, len(PATHS))):
                spawn_pos = PATHS[idx][0]
                pygame.draw.circle(screen, RED, (int(spawn_pos.x), int(spawn_pos.y)), 24, 4)
                pygame.draw.circle(screen, YELLOW, (int(spawn_pos.x), int(spawn_pos.y)), 8)
                spawn_lbl = ui_font.render(f"SPAWN {idx+1}", True, RED)
                screen.blit(spawn_lbl, (int(spawn_pos.x) - spawn_lbl.get_width() // 2, int(spawn_pos.y) - 45))

        life_text = ui_font.render(f"LIFE: {max(0, life)}", True, BLACK)
        gold_text = ui_font.render(f"GOLD: {gold}G", True, BLACK)
        
        # UI 동적 표기 연동
        if current_wave <= len(WAVE_ENEMY_COUNTS):
            max_enemies_in_wave = WAVE_ENEMY_COUNTS[current_wave - 1]
        else:
            max_enemies_in_wave = WAVE_ENEMY_COUNTS[-1] + (current_wave - len(WAVE_ENEMY_COUNTS)) * 6
        remaining_enemies = (max_enemies_in_wave - enemies_spawned) + len(enemies)
        wave_text = ui_font.render(f"WAVE: {current_wave} / {MAX_WAVES}  ({remaining_enemies}/{max_enemies_in_wave})", True, BLUE)
        
        screen.blit(life_text, (20, 20))
        screen.blit(gold_text, (20, 55))
        screen.blit(wave_text, (WIDTH - 300, 20)) 

        if life > 0 and not game_clear:
            if not wave_active:
                pygame.draw.rect(screen, GREEN, wave_start_btn)
                pygame.draw.rect(screen, WHITE, wave_start_btn, 2)
                start_btn_text = ui_font.render("START WAVE", True, WHITE)
            else:
                pygame.draw.rect(screen, GREY, wave_start_btn)
                pygame.draw.rect(screen, DARK_GREY, wave_start_btn, 1)
                start_btn_text = ui_font.render("BATTLE...", True, DARK_GREY)
            screen.blit(start_btn_text, (wave_start_btn.centerx - start_btn_text.get_width() // 2, wave_start_btn.centery - start_btn_text.get_height() // 2))

        if life > 0 and not game_clear:
            shop_menu.draw(screen, gold)

        if augment_active and life > 0 and not game_clear:
            dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim_mask.fill((0, 0, 0, 160)) 
            screen.blit(dim_mask, (0, 0))
            
            aug_title = game_over_font.render("CHOOSE AN AUGMENT", True, YELLOW)
            screen.blit(aug_title, (WIDTH // 2 - aug_title.get_width() // 2, 100))
            
            for idx, rect in enumerate(choice_rects):
                aug_data = current_choices[idx]
                card_color = (80, 80, 80) if rect.collidepoint(mouse_pos) else (40, 40, 40)
                pygame.draw.rect(screen, card_color, rect, 0, 12)
                pygame.draw.rect(screen, WHITE, rect, 3, 12)
                
                name_surf = ui_font.render(aug_data["name"], True, YELLOW)
                desc_font = pygame.font.SysFont(None, 22)
                desc_surf = desc_font.render(aug_data["desc"], True, WHITE)
                
                screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 60))
                screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, rect.y + 200))

        if life <= 0:
            game_over_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            game_over_surface.fill((0, 0, 0, 100)) 
            screen.blit(game_over_surface, (0, 0))
            go_text = game_over_font.render("GAME OVER", True, RED)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - go_text.get_height() // 2))
            pygame.draw.rect(screen, RED, game_return_btn)
            pygame.draw.rect(screen, WHITE, game_return_btn, 2)
            ret_text = ui_font.render("Return to Stage Select", True, WHITE)
            screen.blit(ret_text, (game_return_btn.centerx - ret_text.get_width() // 2, game_return_btn.centery - ret_text.get_height() // 2))

        if game_clear:
            victory_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            victory_surface.fill((0, 200, 0, 80)) 
            screen.blit(victory_surface, (0, 0))
            vic_text = game_over_font.render("VICTORY!", True, BLUE)
            screen.blit(vic_text, (WIDTH // 2 - vic_text.get_width() // 2, HEIGHT // 2 - vic_text.get_height() // 2))
            pygame.draw.rect(screen, BLUE, game_return_btn)
            pygame.draw.rect(screen, WHITE, game_return_btn, 2)
            ret_text = ui_font.render("Return to Stage Select", True, WHITE)
            screen.blit(ret_text, (game_return_btn.centerx - ret_text.get_width() // 2, game_return_btn.centery - ret_text.get_height() // 2))

    pygame.display.flip()

pygame.quit()
sys.exit()