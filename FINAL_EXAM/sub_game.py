import pygame
import sys
import random
import math
from Sub_config import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Survivor - Chain Lightning")
clock = pygame.time.Clock()

def get_korean_font(size):
    fonts = ['malgungothic', 'applegothic', 'nanumgothic', 'dotum', 'gulim']
    for f in fonts:
        font_path = pygame.font.match_font(f)
        if font_path:
            return pygame.font.Font(font_path, size)
    return pygame.font.SysFont(None, size)

# =================================================================
# 엔티티 및 이펙트 클래스 선언 파트
# =================================================================

class DamageText:
    def __init__(self, pos, amount):
        self.pos = pygame.math.Vector2(pos)
        self.amount = amount
        self.life = 40
        self.vy = -1.5

    def update(self):
        self.pos.y += self.vy
        self.life -= 1

    def draw(self, surface, cam, font):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        color = YELLOW if self.amount > 20 else WHITE
        txt = font.render(str(self.amount), True, color)
        txt.set_alpha(max(0, int((self.life / 40) * 255)))
        surface.blit(txt, (screen_pos[0] - txt.get_width()//2, screen_pos[1]))


class SlashEffect:
    def __init__(self, pos, radius):
        self.pos = pygame.math.Vector2(pos)
        self.radius = radius
        self.life = 8

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, PURPLE, screen_pos, self.radius, 3)


# [신규 추가] 체인 라이트닝 시각 효과 클래스
class LightningEffect:
    def __init__(self, points):
        self.points = [pygame.math.Vector2(p) for p in points]
        self.life = 10  # 10프레임 동안 잔상 유지

    def draw(self, surface, cam):
        screen_points = [(int(p.x - cam.x), int(p.y - cam.y)) for p in self.points]
        if len(screen_points) >= 2:
            # 바깥쪽 푸른빛 글로우
            pygame.draw.lines(surface, CYAN, False, screen_points, 5)
            # 안쪽 하얀색 심지
            pygame.draw.lines(surface, WHITE, False, screen_points, 2)


class Boomerang:
    def __init__(self, spawn_pos, direction, damage):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 15
        self.damage = damage
        self.radius = 12
        self.state = "outward"
        self.timer = 30
        self.color = GREEN
        self.hit_targets = []

    def update(self, player_pos):
        if self.state == "outward":
            self.pos += self.dir * self.speed
            self.timer -= 1
            if self.timer <= 0:
                self.state = "returning"
                self.hit_targets = []
        else:
            target_dir = (player_pos - self.pos)
            if target_dir.length() < 30:
                return True
            self.dir = target_dir.normalize()
            self.pos += self.dir * self.speed
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius//2, 2)


class BouncingOrb:
    def __init__(self, pos, direction, damage):
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 10
        self.damage = damage
        self.radius = 10
        self.color = CYAN
        self.bounces = 3  
        self.hit_targets = []

    def update(self):
        self.pos += self.dir * self.speed
        
        bounced = False
        if self.pos.x <= self.radius:
            self.pos.x = self.radius
            self.dir.x *= -1
            bounced = True
        elif self.pos.x >= WORLD_WIDTH - self.radius:
            self.pos.x = WORLD_WIDTH - self.radius
            self.dir.x *= -1
            bounced = True
            
        if self.pos.y <= self.radius:
            self.pos.y = self.radius
            self.dir.y *= -1
            bounced = True
        elif self.pos.y >= WORLD_HEIGHT - self.radius:
            self.pos.y = WORLD_HEIGHT - self.radius
            self.dir.y *= -1
            bounced = True
            
        if bounced:
            self.bounces -= 1
            self.hit_targets = []
            
        return self.bounces < 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)


class FireZone:
    def __init__(self, pos, damage):
        self.pos = pygame.math.Vector2(pos)
        self.damage = damage
        self.radius = 35
        self.life = 120 

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (230, 126, 34, 100), (self.radius, self.radius), self.radius)
        surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))


class FireBomb:
    def __init__(self, pos, direction, damage):
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = 8
        self.damage = damage
        self.life = 45 
        self.tick_timer = 0
        self.color = ORANGE

    def update(self, fire_zones):
        self.pos += self.dir * self.speed
        self.life -= 1
        self.tick_timer += 1
        
        if self.tick_timer >= 5:
            self.tick_timer = 0
            fire_zones.append(FireZone(self.pos, self.damage * 0.5))
            
        return self.life <= 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, 8)


class Projectile:
    def __init__(self, spawn_pos, direction, damage, pierce=1, color=YELLOW, radius=PROJECTILE_RADIUS):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        self.speed = PROJECTILE_SPEED
        self.radius = radius
        self.damage = damage
        self.color = color
        self.pierce = pierce
        self.hit_targets = [] 

    def update(self):
        self.pos += self.dir * self.speed

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)


class Player:
    def __init__(self):
        self.pos = pygame.math.Vector2(WORLD_WIDTH / 2, WORLD_HEIGHT / 2)
        self.radius = 15
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.look_dir = pygame.math.Vector2(1, 0)
        self.aim_dir = pygame.math.Vector2(1, 0) 

        self.level = 1
        self.xp = 0
        self.max_xp = 100  
        self.kills = 0
        self.phase = 1
        self.global_dmg_mult = 1.0
        self.god_mode = False

        self.weapons = {
            "ranged": {
                "active": True, "cooldown": 35, "timer": 0, "base_damage": 15, "count": 1,
                "name": "Ranged Magic", "desc": "[원거리] 마법 구체를 발사합니다."
            },
            "melee": {
                "active": False, "cooldown": 100, "timer": 0, "base_damage": 35, "rear": False,
                "name": "Spirit Sword", "desc": "[근접] 주변 적을 한 번에 베어버립니다."
            },
            "orbit": {
                "active": False, "angle": 0.0, "speed": 0.04, "base_damage": 8, "radius": 75, "count": 1,
                "name": "Orbiting Shield", "desc": "[오라] 주변을 공전하며 피해를 줍니다."
            },
            "axe": {
                "active": False, "cooldown": 120, "timer": 0, "base_damage": 50,
                "name": "Heavy Axe", "desc": "[투척] 적을 관통하는 둔탁한 도끼를 던집니다."
            },
            "boomerang": {
                "active": False, "cooldown": 90, "timer": 0, "base_damage": 25,
                "name": "Boomerang", "desc": "[특수] 궤도를 돌고 되돌아오는 부메랑입니다."
            },
            "bounce": {
                "active": False, "cooldown": 110, "timer": 0, "base_damage": 20,
                "name": "Magic Wand", "desc": "[마법] 맵의 벽에 튕기는 통통탄을 쏩니다."
            },
            "trail": {
                "active": False, "cooldown": 150, "timer": 0, "base_damage": 15,
                "name": "Fire Bomb", "desc": "[폭탄] 궤적에 화염 장판을 남겨 불태웁니다."
            },
            # [신규 추가] 체인 라이트닝
            "lightning": {
                "active": False, "cooldown": 80, "timer": 0, "base_damage": 25, 
                "chain_count": 5, "bolt_count": 1,
                "name": "Chain Lightning", "desc": "[전기] 적을 관통하며 전이되는 번개를 방출합니다."
            }
        }

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move_dir = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:    move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1

        if move_dir.length_squared() > 0:
            move_dir.normalize_ip()
            self.pos += move_dir * self.speed
            self.look_dir = move_dir

        self.pos.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.pos.y))

    def get_nearest_enemy_dir(self, enemies):
        if not enemies: return self.look_dir 
        nearest_enemy = min(enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
        target_dir = nearest_enemy.pos - self.pos
        if target_dir.length_squared() == 0: return self.look_dir
        return target_dir.normalize()

    def update_weapons(self, enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_bombs, fire_zones, lightnings):
        self.aim_dir = self.get_nearest_enemy_dir(enemies)
        target_dir = self.aim_dir
        
        if self.weapons["ranged"]["active"]:
            self.weapons["ranged"]["timer"] += 1
            if self.weapons["ranged"]["timer"] >= self.weapons["ranged"]["cooldown"]:
                self.weapons["ranged"]["timer"] = 0
                dmg = int(self.weapons["ranged"]["base_damage"] * self.global_dmg_mult)
                
                count = self.weapons["ranged"]["count"]
                angle_step = 360.0 / count
                base_angle = math.degrees(math.atan2(target_dir.y, target_dir.x))
                
                for i in range(count):
                    offset_angle = i * angle_step
                    final_angle = math.radians(base_angle + offset_angle)
                    fire_dir = pygame.math.Vector2(math.cos(final_angle), math.sin(final_angle))
                    projectiles.append(Projectile(self.pos, fire_dir, dmg, pierce=2, color=YELLOW, radius=6))

        if self.weapons["melee"]["active"]:
            self.weapons["melee"]["timer"] += 1
            if self.weapons["melee"]["timer"] >= self.weapons["melee"]["cooldown"]:
                self.weapons["melee"]["timer"] = 0
                dmg = int(self.weapons["melee"]["base_damage"] * self.global_dmg_mult)
                slashes.append(SlashEffect(self.pos + target_dir * 30, 90))
                if self.weapons["melee"]["rear"]:
                    slashes.append(SlashEffect(self.pos - target_dir * 30, 90))
                    
                for e in enemies:
                    if self.pos.distance_to(e.pos) < 90 + e.radius:
                        e.take_damage(dmg, dmg_texts)

        if self.weapons["orbit"]["active"]:
            orbit = self.weapons["orbit"]
            orbit["angle"] += orbit["speed"]
            for i in range(orbit["count"]):
                angle_offset = (math.pi * 2 / orbit["count"]) * i
                orb_pos = pygame.math.Vector2(
                    self.pos.x + math.cos(orbit["angle"] + angle_offset) * orbit["radius"],
                    self.pos.y + math.sin(orbit["angle"] + angle_offset) * orbit["radius"]
                )
                for e in enemies:
                    if orb_pos.distance_to(e.pos) < 10 + e.radius:
                        if e.can_receive_tick_damage("orbit", 15):
                            dmg = int(orbit["base_damage"] * self.global_dmg_mult)
                            e.take_damage(dmg, dmg_texts)

        if self.weapons["axe"]["active"]:
            self.weapons["axe"]["timer"] += 1
            if self.weapons["axe"]["timer"] >= self.weapons["axe"]["cooldown"]:
                self.weapons["axe"]["timer"] = 0
                dmg = int(self.weapons["axe"]["base_damage"] * self.global_dmg_mult)
                projectiles.append(Projectile(self.pos, target_dir, dmg, pierce=5, color=GREY, radius=12))

        if self.weapons["boomerang"]["active"]:
            self.weapons["boomerang"]["timer"] += 1
            if self.weapons["boomerang"]["timer"] >= self.weapons["boomerang"]["cooldown"]:
                self.weapons["boomerang"]["timer"] = 0
                dmg = int(self.weapons["boomerang"]["base_damage"] * self.global_dmg_mult)
                boomerangs.append(Boomerang(self.pos, target_dir, dmg))

        if self.weapons["bounce"]["active"]:
            self.weapons["bounce"]["timer"] += 1
            if self.weapons["bounce"]["timer"] >= self.weapons["bounce"]["cooldown"]:
                self.weapons["bounce"]["timer"] = 0
                dmg = int(self.weapons["bounce"]["base_damage"] * self.global_dmg_mult)
                bouncing_orbs.append(BouncingOrb(self.pos, target_dir, dmg))

        if self.weapons["trail"]["active"]:
            self.weapons["trail"]["timer"] += 1
            if self.weapons["trail"]["timer"] >= self.weapons["trail"]["cooldown"]:
                self.weapons["trail"]["timer"] = 0
                dmg = int(self.weapons["trail"]["base_damage"] * self.global_dmg_mult)
                fire_bombs.append(FireBomb(self.pos, target_dir, dmg))

        # -----------------------------------------------------------
        # [신규 추가] 체인 라이트닝 연쇄 타격 알고리즘
        # -----------------------------------------------------------
        if self.weapons["lightning"]["active"]:
            self.weapons["lightning"]["timer"] += 1
            if self.weapons["lightning"]["timer"] >= self.weapons["lightning"]["cooldown"]:
                self.weapons["lightning"]["timer"] = 0
                dmg = int(self.weapons["lightning"]["base_damage"] * self.global_dmg_mult)
                
                bolt_count = self.weapons["lightning"]["bolt_count"]
                max_chains = self.weapons["lightning"]["chain_count"]

                # 가장 가까운 적을 시작 줄기(bolt_count) 개수만큼 필터링
                valid_enemies = sorted(enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
                initial_targets = valid_enemies[:bolt_count]

                for start_enemy in initial_targets:
                    # 이번 타격에 번개가 지나간 적을 저장하는 리스트 (왔다 갔다 반복 타격 방지)
                    hit_list = [start_enemy]
                    current_enemy = start_enemy
                    points = [self.pos, current_enemy.pos] # 번개를 그리기 위한 좌표 누적
                    current_enemy.take_damage(dmg, dmg_texts)

                    for _ in range(max_chains - 1): # 첫 적은 이미 타격했으므로 -1
                        next_enemy = None
                        min_dist = float('inf')
                        
                        # 현재 맞은 적을 기준으로 반경 250px 내에 있는 맞지 않은 다음 적 탐색
                        for e in enemies:
                            if e not in hit_list:
                                dist = current_enemy.pos.distance_squared_to(e.pos)
                                if dist < 62500: # 250^2 (탐색 한계 거리)
                                    if dist < min_dist:
                                        min_dist = dist
                                        next_enemy = e

                        if next_enemy:
                            hit_list.append(next_enemy)
                            points.append(next_enemy.pos)
                            next_enemy.take_damage(dmg, dmg_texts)
                            current_enemy = next_enemy
                        else:
                            # 주변에 더 이상 전이할 적이 없으면 조기 종료
                            break 

                    lightnings.append(LightningEffect(points))


    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, BLUE, screen_pos, self.radius)
        
        eye_pos = (int(screen_pos[0] + self.aim_dir.x * 10), int(screen_pos[1] + self.aim_dir.y * 10))
        pygame.draw.circle(surface, WHITE, eye_pos, 4)

        if self.weapons["orbit"]["active"]:
            orbit = self.weapons["orbit"]
            for i in range(orbit["count"]):
                angle_offset = (math.pi * 2 / orbit["count"]) * i
                orb_screen_x = int(self.pos.x + math.cos(orbit["angle"] + angle_offset) * orbit["radius"] - cam.x)
                orb_screen_y = int(self.pos.y + math.sin(orbit["angle"] + angle_offset) * orbit["radius"] - cam.y)
                pygame.draw.circle(surface, PURPLE, (orb_screen_x, orb_screen_y), 10)


class Enemy:
    def __init__(self, player_pos, phase):
        spawn_dist = max(WIDTH, HEIGHT) / 2 + 50
        angle = random.uniform(0, math.pi * 2)
        
        self.pos = pygame.math.Vector2(
            player_pos.x + math.cos(angle) * spawn_dist,
            player_pos.y + math.sin(angle) * spawn_dist
        )
        self.radius = ENEMY_RADIUS
        self.pos.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.pos.y))
        
        self.max_hp = ENEMY_BASE_HEALTH + (phase - 1) * 20
        self.hp = self.max_hp
        self.attack = ENEMY_BASE_ATTACK + (phase - 1) * 3
        self.xp_reward = ENEMY_BASE_XP + (phase - 1) * 6
        self.speed = ENEMY_BASE_SPEED + (phase - 1) * 0.08
        self.tick_timers = {}

    def can_receive_tick_damage(self, weapon_id, interval):
        if weapon_id not in self.tick_timers:
            self.tick_timers[weapon_id] = 0
            return True
        if self.tick_timers[weapon_id] >= interval:
            self.tick_timers[weapon_id] = 0
            return True
        return False

    def update_timers(self):
        for w_id in self.tick_timers:
            self.tick_timers[w_id] += 1

    def move_towards_player(self, player_pos, player_obj):
        dir_vector = player_pos - self.pos
        dist = dir_vector.length()
        if dist > 0:
            dir_vector.normalize_ip()
            self.pos += dir_vector * self.speed
            
        self.pos.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.pos.y))

        if dist < self.radius + player_obj.radius:
            if not player_obj.god_mode:
                player_obj.hp -= (self.attack * 0.016) 

    def take_damage(self, amount, dmg_texts):
        self.hp -= amount
        dmg_texts.append(DamageText((self.pos.x, self.pos.y - 15), amount))
        if self.hp <= 0:
            self.hp = 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.rect(surface, RED, (screen_pos[0] - self.radius, screen_pos[1] - self.radius, self.radius * 2, self.radius * 2))
        
        bar_width = self.radius * 2
        bar_height = 4
        bar_x = screen_pos[0] - self.radius
        bar_y = screen_pos[1] + self.radius + 5
        
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))


# =================================================================
# 강화 카드 데이터 풀 (체인 라이트닝 관련 옵션 추가)
# =================================================================
UPGRADE_POOL = [
    {"id": "hp_up",       "type": "stat", "target_weapon": None, "name": "Vitality Core", "desc": "Max HP +20 수치를 획득하고 체력을 전부 회복합니다."},
    {"id": "speed_up",    "type": "stat", "target_weapon": None, "name": "Adrenaline Drive", "desc": "플레이어 기본 기동 이동 속도가 10% 증가합니다."},
    {"id": "global_dmg",  "type": "stat", "target_weapon": None, "name": "Overwhelm", "desc": "플레이어 전역 공격력 스탯 계수가 15% 추가 상승합니다."},
    
    {"id": "screen_bomb", "type": "consumable", "target_weapon": None, "name": "Nuke: Annihilation", "desc": "[일회성] 맵 상의 모든 적을 즉시 처치합니다.\n(단, 폭사된 적의 경험치는 50%만 획득)"},
    
    {"id": "ranged_dmg",   "type": "upgrade", "target_weapon": "ranged", "name": "Magic: Overload", "desc": "원거리 마법 구체의 기본 공격력을 +6 추가합니다."},
    {"id": "ranged_count", "type": "upgrade", "target_weapon": "ranged", "name": "Magic: Multi-Shot", "desc": "마법 구체의 동시 발사 개수가 +1개 추가되어 사방으로 퍼집니다."},
    
    {"id": "melee_dmg",    "type": "upgrade", "target_weapon": "melee", "name": "Sword: Sharpen", "desc": "스피릿 소드의 절단 베기 기본 공격력을 +15 추가합니다."},
    {"id": "melee_rear",   "type": "upgrade", "target_weapon": "melee", "name": "Sword: Backslash", "desc": "전방뿐만 아니라 뒤쪽으로도 검을 동시에 휘두릅니다."},
    
    {"id": "orbit_dmg",    "type": "upgrade", "target_weapon": "orbit", "name": "Shield: Dense Plasma", "desc": "위성 오라가 적과 충돌 시 가하는 틱 데미지가 +3 증가합니다."},
    {"id": "orbit_count",  "type": "upgrade", "target_weapon": "orbit", "name": "Shield: Replication", "desc": "플레이어 주변을 맴도는 위성의 개수가 +1 증가합니다."},

    {"id": "axe_dmg",      "type": "upgrade", "target_weapon": "axe", "name": "Axe: Brutal Weight", "desc": "도끼 투척의 데미지가 무식하게 +20 증가합니다."},
    {"id": "axe_haste",    "type": "upgrade", "target_weapon": "axe", "name": "Axe: Quick Throw", "desc": "도끼 투척 쿨타임이 20% 빨라집니다."},

    # [신규 추가] 라이트닝 강화 옵션
    {"id": "lightning_dmg",   "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: High Voltage", "desc": "체인 라이트닝의 기본 데미지가 +10 증가합니다."},
    {"id": "lightning_chain", "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: Conductor", "desc": "번개가 전이되는 최대 적의 수가 +2명 늘어납니다."},
    {"id": "lightning_bolt",  "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: Dual Strike", "desc": "한 번에 쏘아내는 시작 번개의 줄기 수가 +1개 증가합니다."},

    {"id": "unlock_melee",     "type": "unlock", "target_weapon": "melee",     "name": "NEW: Spirit Sword", "desc": "스피릿 소드를 장착합니다. 광역 베기로 근접 적을 섬멸합니다."},
    {"id": "unlock_orbit",     "type": "unlock", "target_weapon": "orbit",     "name": "NEW: Orbiting Shield", "desc": "오라 실드를 개방합니다. 주변을 회전하며 근접 접근을 저지합니다."},
    {"id": "unlock_axe",       "type": "unlock", "target_weapon": "axe",       "name": "NEW: Heavy Axe", "desc": "다수의 몬스터를 뚫고 지나가는 강력한 둔탁 도끼를 던집니다."},
    {"id": "unlock_boomerang", "type": "unlock", "target_weapon": "boomerang", "name": "NEW: Boomerang", "desc": "적들을 뚫고 공격한 뒤 다시 되돌아오는 부메랑을 던집니다."},
    {"id": "unlock_bounce",    "type": "unlock", "target_weapon": "bounce",    "name": "NEW: Magic Wand", "desc": "맵의 벽 구조물에 닿으면 각도를 꺾어 튕기는 구체를 쏩니다."},
    {"id": "unlock_trail",     "type": "unlock", "target_weapon": "trail",     "name": "NEW: Fire Bomb", "desc": "날아가는 궤적 바닥에 뜨거운 화염 장판을 지속 생성합니다."},
    # [신규 추가] 라이트닝 해금
    {"id": "unlock_lightning", "type": "unlock", "target_weapon": "lightning", "name": "NEW: Chain Lightning", "desc": "가장 가까운 적을 타격 후 주변 적에게 연쇄 전이되는 번개를 쏩니다."}
]

def get_filtered_standard_pool(player):
    pool = []
    for card in UPGRADE_POOL:
        if card["type"] in ["stat", "consumable"]:
            pool.append(card)
        elif card["type"] == "upgrade":
            if player.weapons[card["target_weapon"]]["active"]:
                if card["id"] == "ranged_count" and player.weapons["ranged"]["count"] >= 8: continue
                if card["id"] == "melee_rear" and player.weapons["melee"]["rear"]: continue
                pool.append(card)
    return pool

def generate_cards(player):
    if player.level % 5 == 0:
        unlock_pool = [c for c in UPGRADE_POOL if c["type"] == "unlock" and not player.weapons[c["target_weapon"]]["active"]]
        standard_pool = get_filtered_standard_pool(player)
        
        if unlock_pool:
            guaranteed_weapon = random.choice(unlock_pool)
            other_choices = random.sample(standard_pool, min(2, len(standard_pool)))
            final_cards = [guaranteed_weapon] + other_choices
            random.shuffle(final_cards) 
            return final_cards
        else:
            return random.sample(standard_pool, min(3, len(standard_pool)))
    else:
        standard_pool = get_filtered_standard_pool(player)
        return random.sample(standard_pool, min(3, len(standard_pool)))

def apply_card_effect(player, card_id, enemies=None):
    if card_id == "screen_bomb":
        if enemies is not None:
            for e in enemies:
                player.kills += 1
                player.xp += (e.xp_reward * 0.5)
            enemies.clear()
            
    elif card_id == "hp_up":
        player.max_hp += 20
        player.hp = player.max_hp
    elif card_id == "speed_up":
        player.speed *= 1.10
    elif card_id == "global_dmg":
        player.global_dmg_mult += 0.15
        
    elif card_id == "ranged_dmg": player.weapons["ranged"]["base_damage"] += 6
    elif card_id == "ranged_count": player.weapons["ranged"]["count"] += 1
    
    elif card_id == "melee_dmg": player.weapons["melee"]["base_damage"] += 15
    elif card_id == "melee_rear": player.weapons["melee"]["rear"] = True
    
    elif card_id == "orbit_dmg": player.weapons["orbit"]["base_damage"] += 3
    elif card_id == "orbit_count": player.weapons["orbit"]["count"] += 1
    
    elif card_id == "axe_dmg": player.weapons["axe"]["base_damage"] += 20
    elif card_id == "axe_haste": player.weapons["axe"]["cooldown"] = max(20, int(player.weapons["axe"]["cooldown"] * 0.8))

    # [신규 추가] 라이트닝 강화
    elif card_id == "lightning_dmg": player.weapons["lightning"]["base_damage"] += 10
    elif card_id == "lightning_chain": player.weapons["lightning"]["chain_count"] += 2
    elif card_id == "lightning_bolt": player.weapons["lightning"]["bolt_count"] += 1
    
    elif card_id == "unlock_melee": player.weapons["melee"]["active"] = True
    elif card_id == "unlock_orbit": player.weapons["orbit"]["active"] = True
    elif card_id == "unlock_axe": player.weapons["axe"]["active"] = True
    elif card_id == "unlock_boomerang": player.weapons["boomerang"]["active"] = True
    elif card_id == "unlock_bounce": player.weapons["bounce"]["active"] = True
    elif card_id == "unlock_trail": player.weapons["trail"]["active"] = True
    elif card_id == "unlock_lightning": player.weapons["lightning"]["active"] = True


# =================================================================
# 메인 게임 루프
# =================================================================
def reset_game():
    global player, enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_bombs, fire_zones, lightnings
    global camera, frame_count, level_up_active, game_over
    player = Player()
    enemies = []
    projectiles = []
    slashes = []  
    dmg_texts = [] 
    boomerangs = []
    bouncing_orbs = []
    fire_bombs = []
    fire_zones = []
    lightnings = [] # 체인 라이트닝 이펙트 리스트
    camera = pygame.math.Vector2(0, 0)
    frame_count = 0
    level_up_active = False
    game_over = False

reset_game()

card_rects = [
    pygame.Rect(300, 300, 280, 400),
    pygame.Rect(660, 300, 280, 400),
    pygame.Rect(1020, 300, 280, 400)
]

dev_mode = False
running = True
current_choices = []

while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r: reset_game()
                
            if event.key == pygame.K_F1: dev_mode = not dev_mode
            elif event.key == pygame.K_F2: player.god_mode = not player.god_mode
            elif event.key == pygame.K_F3: 
                if not level_up_active and not game_over:
                    player.xp = player.max_xp
            elif event.key == pygame.K_F4: 
                if not level_up_active and not game_over:
                    player.kills += KILLS_PER_PHASE
                    player.phase = (player.kills // KILLS_PER_PHASE) + 1

        if level_up_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(card_rects):
                    if idx < len(current_choices) and rect.collidepoint(mouse_pos):
                        apply_card_effect(player, current_choices[idx]["id"], enemies)
                        level_up_active = False
                        break
            continue

    if not level_up_active and not game_over:
        if player.xp >= player.max_xp:
            player.xp -= player.max_xp
            player.level += 1
            player.max_xp = int(player.max_xp * XP_MULTIPLIER)
            current_choices = generate_cards(player)
            level_up_active = True

    if not level_up_active and not game_over:
        frame_count += 1
        
        player.handle_input()
        player.update_weapons(enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_bombs, fire_zones, lightnings)

        camera.x = player.pos.x - WIDTH / 2
        camera.y = player.pos.y - HEIGHT / 2

        spawn_rate = max(8, 35 - (player.phase * 4))
        if frame_count % spawn_rate == 0:
            enemies.append(Enemy(player.pos, player.phase))

        for p in projectiles[:]:
            p.update()
            if p.pos.x < 0 or p.pos.x > WORLD_WIDTH or p.pos.y < 0 or p.pos.y > WORLD_HEIGHT: projectiles.remove(p)
                
        for bm in boomerangs[:]:
            if bm.update(player.pos): boomerangs.remove(bm)
                
        for bo in bouncing_orbs[:]:
            if bo.update(): bouncing_orbs.remove(bo)
            
        for fb in fire_bombs[:]:
            if fb.update(fire_zones): fire_bombs.remove(fb)
            
        for fz in fire_zones[:]:
            fz.life -= 1
            if fz.life <= 0: fire_zones.remove(fz)

        for slash in slashes[:]:
            slash.life -= 1
            if slash.life <= 0: slashes.remove(slash)
                
        # [신규 추가] 라이트닝 이펙트 수명 관리
        for lg in lightnings[:]:
            lg.life -= 1
            if lg.life <= 0: lightnings.remove(lg)

        for dt in dmg_texts[:]:
            dt.update()
            if dt.life <= 0: dmg_texts.remove(dt)

        for e in enemies[:]:
            e.update_timers()
            e.move_towards_player(player.pos, player)
            
            for p in projectiles[:]:
                if e.pos.distance_to(p.pos) < e.radius + p.radius and e not in p.hit_targets:
                    e.take_damage(p.damage, dmg_texts)
                    p.hit_targets.append(e)
                    p.pierce -= 1
                    if p.pierce <= 0 and p in projectiles: projectiles.remove(p)
                        
            for bm in boomerangs[:]:
                if e.pos.distance_to(bm.pos) < e.radius + bm.radius and e not in bm.hit_targets:
                    e.take_damage(bm.damage, dmg_texts)
                    bm.hit_targets.append(e)
                    
            for bo in bouncing_orbs[:]:
                if e.pos.distance_to(bo.pos) < e.radius + bo.radius and e not in bo.hit_targets:
                    e.take_damage(bo.damage, dmg_texts)
                    bo.hit_targets.append(e)
                    
            for fz in fire_zones[:]:
                if e.pos.distance_to(fz.pos) < e.radius + fz.radius:
                    if e.can_receive_tick_damage("firezone", 20):
                        e.take_damage(fz.damage, dmg_texts)
                    
            if e.hp <= 0:
                if e in enemies:
                    enemies.remove(e)
                    player.kills += 1
                    player.phase = (player.kills // KILLS_PER_PHASE) + 1
                    player.xp += e.xp_reward

        if player.hp <= 0:
            game_over = True

    # ==========================================
    # 화면 렌더링 파트
    # ==========================================
    screen.fill(DARK_BG)

    start_x = int(camera.x // 100 * 100)
    start_y = int(camera.y // 100 * 100)
    for x in range(start_x, start_x + WIDTH + 100, 100):
        pygame.draw.line(screen, GRID_COLOR, (x - camera.x, 0), (x - camera.x, HEIGHT))
    for y in range(start_y, start_y + HEIGHT + 100, 100):
        pygame.draw.line(screen, GRID_COLOR, (0, y - camera.y), (WIDTH, y - camera.y))

    border_rect = pygame.Rect(-camera.x, -camera.y, WORLD_WIDTH, WORLD_HEIGHT)
    pygame.draw.rect(screen, WALL_COLOR, border_rect, 15)

    for fz in fire_zones: fz.draw(screen, camera)
    for slash in slashes: slash.draw(screen, camera)
    for p in projectiles: p.draw(screen, camera)
    for bm in boomerangs: bm.draw(screen, camera)
    for bo in bouncing_orbs: bo.draw(screen, camera)
    for fb in fire_bombs: fb.draw(screen, camera)
    for lg in lightnings: lg.draw(screen, camera) # 라이트닝 이펙트 렌더링
    
    for e in enemies:     e.draw(screen, camera)
    player.draw(screen, camera)
    
    ui_font = get_korean_font(36)
    
    for dt in dmg_texts: dt.draw(screen, camera, ui_font)

    hp_text = ui_font.render(f"HP: {max(0, int(player.hp))} / {player.max_hp}", True, WHITE)
    kills_text = ui_font.render(f"KILLS: {player.kills}  (PHASE {player.phase})", True, WHITE)
    dmg_text = ui_font.render(f"DMG MULT: x{player.global_dmg_mult:.2f}", True, YELLOW)
    screen.blit(hp_text, (20, 20))
    screen.blit(kills_text, (20, 60))
    screen.blit(dmg_text, (20, 100))

    if dev_mode:
        dev_font = get_korean_font(24)
        god_str = "ON" if player.god_mode else "OFF"
        dev_msg = f"[개발자 모드] F1:끄기 | F2:무적({god_str}) | F3:레벨업 | F4:페이즈 점프"
        dev_surf = dev_font.render(dev_msg, True, CYAN)
        screen.blit(dev_surf, (WIDTH - dev_surf.get_width() - 20, 20))

    if not game_over:
        xp_bar_height = 32  
        xp_rect_y = HEIGHT - xp_bar_height
        pygame.draw.rect(screen, (30, 30, 40), (0, xp_rect_y, WIDTH, xp_bar_height))
        xp_ratio = min(1.0, player.xp / player.max_xp)
        pygame.draw.rect(screen, YELLOW, (0, xp_rect_y, int(WIDTH * xp_ratio), xp_bar_height))
        pygame.draw.line(screen, GREY, (0, xp_rect_y), (WIDTH, xp_rect_y), 2)
        
        xp_font = get_korean_font(20)
        xp_lbl = xp_font.render(f"Lv.{player.level}  [ {player.xp} / {player.max_xp} XP ]", True, BLACK)
        
        text_x = WIDTH // 2 - xp_lbl.get_width() // 2
        text_y = xp_rect_y + (xp_bar_height // 2) - (xp_lbl.get_height() // 2)
        screen.blit(xp_lbl, (text_x, text_y))

    if level_up_active and not game_over:
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 200))
        screen.blit(dim_mask, (0, 0))
        
        title_font = get_korean_font(64)
        sub_font = get_korean_font(26)
        
        title_surf = title_font.render("LEVEL UP STIMULUS", True, YELLOW)
        sub_surf = sub_font.render("아래의 옵션 중 하나를 선택하여 캐릭터를 진화시키세요.", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 110))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 185))
        
        for idx, rect in enumerate(card_rects):
            if idx >= len(current_choices): break
            choice_data = current_choices[idx]
            
            card_color = (70, 75, 90) if rect.collidepoint(mouse_pos) else (40, 44, 52)
            pygame.draw.rect(screen, card_color, rect, 0, 14)
            pygame.draw.rect(screen, WHITE, rect, 3, 14)
            
            name_surf = ui_font.render(choice_data["name"], True, YELLOW)
            screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 50))
            
            desc_font = get_korean_font(20)
            max_width = rect.width - 30 
            
            words = choice_data["desc"].replace('\n', ' ').split(' ')
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if desc_font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            y_offset = rect.y + 140
            for i, line_text in enumerate(lines):
                color = WHITE if i == 0 else GREY
                desc_surf = desc_font.render(line_text.strip(), True, color)
                screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, y_offset))
                y_offset += 28

    if game_over:
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 150))
        screen.blit(dim_mask, (0, 0))
        
        go_font = get_korean_font(100)
        go_text = go_font.render("GAME OVER", True, RED)
        stat_text = ui_font.render(f"도달한 페이즈: {player.phase} | 총 처치 수: {player.kills}", True, WHITE)
        restart_text = ui_font.render("R 키를 눌러 다시 시작하세요", True, YELLOW)
        
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, HEIGHT // 2 + 20))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))

    pygame.display.flip()

pygame.quit()
sys.exit()