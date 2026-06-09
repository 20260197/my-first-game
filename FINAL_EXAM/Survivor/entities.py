import pygame
import random
import math
from Sub_config import *
from weapons import Projectile, Boomerang, BouncingOrb, Chakram, SwordWave
from effects import SlashEffect, LightningEffect, DamageText, BeamEffect, BlizzardEffect

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
            "ranged": {"active": True, "level": 1, "max_level": 5, "cooldown": 35, "timer": 0, "base_damage": 15, "count": 1, "name": "Ranged Magic", "desc": "[원거리] 마법 구체를 발사합니다."},
            "melee": {"active": False, "level": 1, "max_level": 5, "cooldown": 100, "timer": 0, "base_damage": 35, "rear": False, "name": "Spirit Sword", "desc": "[근접] 전방으로 적을 관통하는 검기를 날립니다."},
            "orbit": {"active": False, "level": 1, "max_level": 5, "angle": 0.0, "speed": 0.04, "base_damage": 8, "radius": 75, "count": 1, "name": "Orbiting Shield", "desc": "[오라] 주변을 공전하며 피해를 줍니다."},
            "axe": {"active": False, "level": 1, "max_level": 5, "cooldown": 120, "timer": 0, "base_damage": 50, "name": "Heavy Axe", "desc": "[투척] 적을 관통하는 둔탁한 도끼를 던집니다."},
            "boomerang": {"active": False, "level": 1, "max_level": 5, "cooldown": 90, "timer": 0, "base_damage": 25, "name": "Boomerang", "desc": "[특수] 궤도를 돌고 되돌아오는 부메랑입니다."},
            "bounce": {"active": False, "level": 1, "max_level": 5, "cooldown": 110, "timer": 0, "base_damage": 20, "name": "Magic Wand", "desc": "[마법] 맵의 벽에 튕기는 통통탄을 쏩니다."},
            "trail": {"active": False, "level": 1, "max_level": 5, "cooldown": 120, "timer": 0, "base_damage": 15, "name": "Meteor Strike", "desc": "[폭격] 주변 무작위 위치에 화염 장판을 폭격합니다."},
            "lightning": {"active": False, "level": 1, "max_level": 5, "cooldown": 80, "timer": 0, "base_damage": 25, "chain_count": 5, "bolt_count": 1, "name": "Chain Lightning", "desc": "[전기] 적을 관통하며 전이되는 번개를 방출합니다."},
            "beam": {"active": False, "level": 1, "max_level": 5, "cooldown": 180, "timer": 0, "base_damage": 100, "width": 20, "name": "Orbital Beam", "desc": "[관통] 조준 방향으로 화면을 뚫는 거대 레이저를 쏩니다."},
            "blizzard": {"active": False, "level": 1, "max_level": 5, "cooldown": 200, "timer": 0, "base_damage": 10, "radius": 180, "freeze_time": 180, "name": "Blizzard", "desc": "[결빙] 광역 눈보라를 일으켜 닿은 적을 3초간 얼려버립니다."},
            "chakram": {"active": False, "level": 1, "max_level": 5, "cooldown": 100, "timer": 0, "base_damage": 30, "burn_dmg": 5, "name": "Hellfire Chakram", "desc": "[화상] 적에게 지속 화상 피해를 입히는 차크람을 던집니다."},
            "storm": {"active": False, "level": 1, "max_level": 1, "cooldown": 30, "timer": 0, "base_damage": 25, "radius": 220, "burn_dmg": 15, "freeze_time": 90, "name": "Elemental Storm", "desc": "[합체] 빙염의 폭풍이 상시 전개되어 빙결과 화상을 줍니다."}
        }
        self.storm_angle = 0.0 # 폭풍 회전 애니메이션용 변수
        self.damage_stats = {key: 0 for key in self.weapons.keys()}

    def get_total_dmg_mult(self):
        phase_bonus = (self.phase - 1) * 0.10
        return self.global_dmg_mult + phase_bonus

    def handle_input(self):
        keys = pygame.key.get_pressed()
        move_dir = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1

        if move_dir.length_squared() > 0:
            move_dir.normalize_ip()
            self.pos += move_dir * self.speed
            self.look_dir = move_dir

        self.pos.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.pos.y))

    def update_target(self, enemies):
        if not enemies: return self.look_dir 
        nearest_enemy = min(enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
        target_dir = nearest_enemy.pos - self.pos
        if target_dir.length_squared() > 0:
            self.aim_dir = target_dir.normalize()
            return self.aim_dir
        return self.look_dir

    def point_line_distance(self, p, a, b):
        ap = p - a
        ab = b - a
        if ab.length_squared() == 0: return ap.length()
        t = max(0, min(1, ap.dot(ab) / ab.length_squared()))
        proj = a + ab * t
        return p.distance_to(proj)

    # [수정] slashes 파라미터를 삭제하고 sword_waves 리스트를 전달받습니다.
    def update_weapons(self, enemies, projectiles, sword_waves, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams):
        target_dir = self.update_target(enemies)
        current_mult = self.get_total_dmg_mult()
        
        if self.weapons["ranged"]["active"]:
            self.weapons["ranged"]["timer"] += 1
            if self.weapons["ranged"]["timer"] >= self.weapons["ranged"]["cooldown"]:
                self.weapons["ranged"]["timer"] = 0
                dmg = int(self.weapons["ranged"]["base_damage"] * current_mult)
                count = self.weapons["ranged"]["count"]
                base_angle = math.degrees(math.atan2(target_dir.y, target_dir.x))
                spread_gap = 7.0 
                start_angle = base_angle - ((count - 1) * spread_gap / 2.0)
                for i in range(count):
                    final_angle = math.radians(start_angle + (i * spread_gap))
                    fire_dir = pygame.math.Vector2(math.cos(final_angle), math.sin(final_angle))
                    projectiles.append(Projectile(self.pos, fire_dir, dmg, pierce=2, color=YELLOW, radius=6, weapon_id="ranged"))

        # [수정] 즉발 타격이 아닌 검기(SwordWave) 투사체 생성으로 변경
        if self.weapons["melee"]["active"]:
            self.weapons["melee"]["timer"] += 1
            if self.weapons["melee"]["timer"] >= self.weapons["melee"]["cooldown"]:
                self.weapons["melee"]["timer"] = 0
                dmg = int(self.weapons["melee"]["base_damage"] * current_mult)
                
                # 전방으로 검기 발사
                sword_waves.append(SwordWave(self.pos, target_dir, dmg))
                if self.weapons["melee"]["rear"]:
                    # 후방으로 검기 발사
                    sword_waves.append(SwordWave(self.pos, -target_dir, dmg))

        if self.weapons["orbit"]["active"]:
            orbit = self.weapons["orbit"]
            orbit["angle"] += orbit["speed"]
            for i in range(orbit["count"]):
                angle_offset = (math.pi * 2 / orbit["count"]) * i
                orb_pos = pygame.math.Vector2(self.pos.x + math.cos(orbit["angle"] + angle_offset) * orbit["radius"], self.pos.y + math.sin(orbit["angle"] + angle_offset) * orbit["radius"])
                for e in enemies:
                    if orb_pos.distance_to(e.pos) < 10 + e.radius:
                        if e.can_receive_tick_damage("orbit", 15):
                            dmg = int(orbit["base_damage"] * current_mult)
                            e.take_damage(dmg, dmg_texts)
                            self.damage_stats["orbit"] += dmg 

        if self.weapons["axe"]["active"]:
            self.weapons["axe"]["timer"] += 1
            if self.weapons["axe"]["timer"] >= self.weapons["axe"]["cooldown"]:
                self.weapons["axe"]["timer"] = 0
                dmg = int(self.weapons["axe"]["base_damage"] * current_mult)
                projectiles.append(Projectile(self.pos, target_dir, dmg, pierce=5, color=GREY, radius=12, weapon_id="axe"))

        if self.weapons["boomerang"]["active"]:
            self.weapons["boomerang"]["timer"] += 1
            if self.weapons["boomerang"]["timer"] >= self.weapons["boomerang"]["cooldown"]:
                self.weapons["boomerang"]["timer"] = 0
                dmg = int(self.weapons["boomerang"]["base_damage"] * current_mult)
                boomerangs.append(Boomerang(self.pos, target_dir, dmg, weapon_id="boomerang"))

        if self.weapons["bounce"]["active"]:
            self.weapons["bounce"]["timer"] += 1
            if self.weapons["bounce"]["timer"] >= self.weapons["bounce"]["cooldown"]:
                self.weapons["bounce"]["timer"] = 0
                dmg = int(self.weapons["bounce"]["base_damage"] * current_mult)
                bouncing_orbs.append(BouncingOrb(self.pos, target_dir, dmg, weapon_id="bounce"))

        if self.weapons["trail"]["active"]:
            self.weapons["trail"]["timer"] += 1
            if self.weapons["trail"]["timer"] >= self.weapons["trail"]["cooldown"]:
                self.weapons["trail"]["timer"] = 0
                dmg = int(self.weapons["trail"]["base_damage"] * current_mult)
                
                from weapons import MeteorDrop
                targets = []
                
                # 1. 화면에 적이 있으면 무작위로 3마리(또는 남은 수만큼) 조준
                if len(enemies) > 0:
                    sample_size = min(3, len(enemies))
                    targets = random.sample(enemies, sample_size)
                    
                for t in targets:
                    fire_zones.append(MeteorDrop(t.pos, dmg, weapon_id="trail"))
                    
                # 2. 만약 적이 없거나 3마리보다 적다면, 남은 개수만큼 플레이어 주변 무작위 투하
                if len(targets) < 3:
                    for _ in range(3 - len(targets)):
                        angle = random.uniform(0, math.pi * 2)
                        dist = random.uniform(50, 200)
                        spawn_pos = pygame.math.Vector2(self.pos.x + math.cos(angle) * dist, self.pos.y + math.sin(angle) * dist)
                        fire_zones.append(MeteorDrop(spawn_pos, dmg, weapon_id="trail"))

        if self.weapons["lightning"]["active"]:
            self.weapons["lightning"]["timer"] += 1
            if self.weapons["lightning"]["timer"] >= self.weapons["lightning"]["cooldown"]:
                self.weapons["lightning"]["timer"] = 0
                dmg = int(self.weapons["lightning"]["base_damage"] * current_mult)
                bolt_count = self.weapons["lightning"]["bolt_count"]
                max_chains = self.weapons["lightning"]["chain_count"]
                valid_enemies = sorted(enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
                initial_targets = valid_enemies[:bolt_count]
                for start_enemy in initial_targets:
                    hit_list = [start_enemy]
                    current_enemy = start_enemy
                    points = [self.pos, current_enemy.pos] 
                    current_enemy.take_damage(dmg, dmg_texts)
                    self.damage_stats["lightning"] += dmg 
                    for _ in range(max_chains - 1): 
                        next_enemy = None
                        min_dist = float('inf')
                        for e in enemies:
                            if e not in hit_list:
                                dist = current_enemy.pos.distance_squared_to(e.pos)
                                if dist < 14400: 
                                    if dist < min_dist:
                                        min_dist = dist
                                        next_enemy = e
                        if next_enemy:
                            hit_list.append(next_enemy)
                            points.append(next_enemy.pos)
                            next_enemy.take_damage(dmg, dmg_texts)
                            self.damage_stats["lightning"] += dmg 
                            current_enemy = next_enemy
                        else: break 
                    lightnings.append(LightningEffect(points))

        if self.weapons["beam"]["active"]:
            self.weapons["beam"]["timer"] += 1
            if self.weapons["beam"]["timer"] >= self.weapons["beam"]["cooldown"]:
                self.weapons["beam"]["timer"] = 0
                dmg = int(self.weapons["beam"]["base_damage"] * current_mult)
                width = self.weapons["beam"]["width"]
                end_pos = self.pos + target_dir * 2000 
                beams.append(BeamEffect(self.pos, end_pos, width))
                for e in enemies:
                    if self.point_line_distance(e.pos, self.pos, end_pos) < (width/2) + e.radius:
                        e.take_damage(dmg, dmg_texts)
                        self.damage_stats["beam"] += dmg 

        if self.weapons["blizzard"]["active"]:
            self.weapons["blizzard"]["timer"] += 1
            if self.weapons["blizzard"]["timer"] >= self.weapons["blizzard"]["cooldown"]:
                self.weapons["blizzard"]["timer"] = 0
                dmg = int(self.weapons["blizzard"]["base_damage"] * current_mult)
                radius = self.weapons["blizzard"]["radius"]
                freeze_time = self.weapons["blizzard"]["freeze_time"]
                blizzards.append(BlizzardEffect(self.pos, radius))
                for e in enemies:
                    if self.pos.distance_to(e.pos) < radius + e.radius:
                        e.take_damage(dmg, dmg_texts)
                        self.damage_stats["blizzard"] += dmg 
                        e.freeze_timer = freeze_time 

        if self.weapons["chakram"]["active"]:
            self.weapons["chakram"]["timer"] += 1
            if self.weapons["chakram"]["timer"] >= self.weapons["chakram"]["cooldown"]:
                self.weapons["chakram"]["timer"] = 0
                dmg = int(self.weapons["chakram"]["base_damage"] * current_mult)
                
                # [수정] 조준 방향을 기준으로 -15도, 0도, +15도 방향으로 3개 동시 생성
                base_angle = math.degrees(math.atan2(target_dir.y, target_dir.x))
                angles = [base_angle - 15, base_angle, base_angle + 15]
                
                for ang in angles:
                    rad_ang = math.radians(ang)
                    fire_dir = pygame.math.Vector2(math.cos(rad_ang), math.sin(rad_ang))
                    chakrams.append(Chakram(self.pos, fire_dir, dmg, weapon_id="chakram"))

                    # ... 기존 무기 로직들 아래에 추가
        if self.weapons["storm"]["active"]:
            self.weapons["storm"]["timer"] += 1
            if self.weapons["storm"]["timer"] >= self.weapons["storm"]["cooldown"]:
                self.weapons["storm"]["timer"] = 0
                dmg = int(self.weapons["storm"]["base_damage"] * current_mult)
                rad = self.weapons["storm"]["radius"]
                
                # 반경 안의 모든 적에게 즉발 데미지 + 빙결 + 강력한 화상 동시 부여
                for e in enemies:
                    if self.pos.distance_to(e.pos) < rad + e.radius:
                        e.take_damage(dmg, dmg_texts)
                        self.damage_stats["storm"] += dmg 
                        e.freeze_timer = self.weapons["storm"]["freeze_time"]
                        e.burn_timer = 180
                        e.burn_damage = int(self.weapons["storm"]["burn_dmg"] * current_mult)


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
                
                # draw 함수 맨 아래 orbit 렌더링 아래쪽에 추가
        if self.weapons["storm"]["active"]:
            self.storm_angle += 0.08
            rad = self.weapons["storm"]["radius"]
            
            # 반투명 캔버스 생성 (하늘색 베이스)
            s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 255, 40), (rad, rad), rad)
            
            # 주황색 십자선이 소용돌이치듯 회전하는 효과
            for i in range(4):
                angle = self.storm_angle + (math.pi / 2) * i
                p1 = (rad + math.cos(angle) * rad, rad + math.sin(angle) * rad)
                pygame.draw.line(s, (255, 100, 0, 150), (rad, rad), p1, 15)
                
            surface.blit(s, (screen_pos[0] - rad, screen_pos[1] - rad))
            pygame.draw.circle(surface, CYAN, screen_pos, rad, 3)
            pygame.draw.circle(surface, ORANGE, screen_pos, rad - 8, 3)


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
        self.speed = ENEMY_BASE_SPEED + (phase - 1) * 0.03
        self.tick_timers = {}

        self.freeze_timer = 0
        self.burn_timer = 0
        self.burn_damage = 0
        self.burn_tick = 0

    def can_receive_tick_damage(self, weapon_id, interval):
        if weapon_id not in self.tick_timers:
            self.tick_timers[weapon_id] = 0
            return True
        if self.tick_timers[weapon_id] >= interval:
            self.tick_timers[weapon_id] = 0
            return True
        return False

    def update_timers(self, dmg_texts, player):
        for w_id in self.tick_timers:
            self.tick_timers[w_id] += 1
            
        if self.freeze_timer > 0:
            self.freeze_timer -= 1
            
        if self.burn_timer > 0:
            self.burn_timer -= 1
            self.burn_tick += 1
            if self.burn_tick >= 60: 
                self.burn_tick = 0
                self.take_damage(self.burn_damage, dmg_texts)
                player.damage_stats["chakram"] += self.burn_damage 

    def move_towards_player(self, player_pos, player_obj):
        dir_vector = player_pos - self.pos
        dist = dir_vector.length()
        
        current_speed = self.speed * 0.5 if self.freeze_timer > 0 else self.speed
        
        if dist > 0:
            dir_vector.normalize_ip()
            self.pos += dir_vector * current_speed
            
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
        
        body_color = RED
        if self.freeze_timer > 0: body_color = CYAN
        elif self.burn_timer > 0: body_color = ORANGE
            
        pygame.draw.rect(surface, body_color, (screen_pos[0] - self.radius, screen_pos[1] - self.radius, self.radius * 2, self.radius * 2))
        
        bar_width = self.radius * 2
        bar_height = 4
        bar_x = screen_pos[0] - self.radius
        bar_y = screen_pos[1] + self.radius + 5
        
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y, bar_width, bar_height))
        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        pygame.draw.rect(surface, GREEN, (bar_x, bar_y, int(bar_width * hp_ratio), bar_height))