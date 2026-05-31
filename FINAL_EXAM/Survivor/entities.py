import pygame
import random
import math
from Sub_config import *
from weapons import Projectile, Boomerang, BouncingOrb, Chakram
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
            "ranged": {"active": True, "cooldown": 35, "timer": 0, "base_damage": 15, "count": 1, "name": "Ranged Magic", "desc": "[원거리] 마법 구체를 발사합니다."},
            "melee": {"active": False, "cooldown": 100, "timer": 0, "base_damage": 35, "rear": False, "name": "Spirit Sword", "desc": "[근접] 주변 적을 한 번에 베어버립니다."},
            "orbit": {"active": False, "angle": 0.0, "speed": 0.04, "base_damage": 8, "radius": 75, "count": 1, "name": "Orbiting Shield", "desc": "[오라] 주변을 공전하며 피해를 줍니다."},
            "axe": {"active": False, "cooldown": 120, "timer": 0, "base_damage": 50, "name": "Heavy Axe", "desc": "[투척] 적을 관통하는 둔탁한 도끼를 던집니다."},
            "boomerang": {"active": False, "cooldown": 90, "timer": 0, "base_damage": 25, "name": "Boomerang", "desc": "[특수] 궤도를 돌고 되돌아오는 부메랑입니다."},
            "bounce": {"active": False, "cooldown": 110, "timer": 0, "base_damage": 20, "name": "Magic Wand", "desc": "[마법] 맵의 벽에 튕기는 통통탄을 쏩니다."},
            "trail": {"active": False, "cooldown": 120, "timer": 0, "base_damage": 15, "name": "Meteor Strike", "desc": "[폭격] 주변 무작위 위치에 화염 장판을 폭격합니다."},
            "lightning": {"active": False, "cooldown": 80, "timer": 0, "base_damage": 25, "chain_count": 5, "bolt_count": 1, "name": "Chain Lightning", "desc": "[전기] 적을 관통하며 전이되는 번개를 방출합니다."},
            "beam": {"active": False, "cooldown": 180, "timer": 0, "base_damage": 100, "width": 20, "name": "Orbital Beam", "desc": "[관통] 조준 방향으로 화면을 뚫는 거대 레이저를 쏩니다."},
            "blizzard": {"active": False, "cooldown": 200, "timer": 0, "base_damage": 10, "radius": 180, "freeze_time": 180, "name": "Blizzard", "desc": "[결빙] 광역 눈보라를 일으켜 닿은 적을 3초간 얼려버립니다."},
            "chakram": {"active": False, "cooldown": 100, "timer": 0, "base_damage": 30, "burn_dmg": 5, "name": "Hellfire Chakram", "desc": "[화상] 적에게 지속 화상 피해를 입히는 차크람을 던집니다."}
        }

    # [신규] 카드 획득 증가분 + 페이즈(자동 증가분)을 합산한 최종 공격력 배율 반환
    def get_total_dmg_mult(self):
        # 페이즈가 1 오를 때마다 공격력이 10%씩(0.1) 자동으로 강해짐
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

    def update_weapons(self, enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams):
        target_dir = self.update_target(enemies)
        
        # [적용] 무기를 발사할 때 자동 상승분이 포함된 최종 배율을 가져옴
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
                    projectiles.append(Projectile(self.pos, fire_dir, dmg, pierce=2, color=YELLOW, radius=6))

        if self.weapons["melee"]["active"]:
            self.weapons["melee"]["timer"] += 1
            if self.weapons["melee"]["timer"] >= self.weapons["melee"]["cooldown"]:
                self.weapons["melee"]["timer"] = 0
                dmg = int(self.weapons["melee"]["base_damage"] * current_mult)
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
                orb_pos = pygame.math.Vector2(self.pos.x + math.cos(orbit["angle"] + angle_offset) * orbit["radius"], self.pos.y + math.sin(orbit["angle"] + angle_offset) * orbit["radius"])
                for e in enemies:
                    if orb_pos.distance_to(e.pos) < 10 + e.radius:
                        if e.can_receive_tick_damage("orbit", 15):
                            dmg = int(orbit["base_damage"] * current_mult)
                            e.take_damage(dmg, dmg_texts)

        if self.weapons["axe"]["active"]:
            self.weapons["axe"]["timer"] += 1
            if self.weapons["axe"]["timer"] >= self.weapons["axe"]["cooldown"]:
                self.weapons["axe"]["timer"] = 0
                dmg = int(self.weapons["axe"]["base_damage"] * current_mult)
                projectiles.append(Projectile(self.pos, target_dir, dmg, pierce=5, color=GREY, radius=12))

        if self.weapons["boomerang"]["active"]:
            self.weapons["boomerang"]["timer"] += 1
            if self.weapons["boomerang"]["timer"] >= self.weapons["boomerang"]["cooldown"]:
                self.weapons["boomerang"]["timer"] = 0
                dmg = int(self.weapons["boomerang"]["base_damage"] * current_mult)
                boomerangs.append(Boomerang(self.pos, target_dir, dmg))

        if self.weapons["bounce"]["active"]:
            self.weapons["bounce"]["timer"] += 1
            if self.weapons["bounce"]["timer"] >= self.weapons["bounce"]["cooldown"]:
                self.weapons["bounce"]["timer"] = 0
                dmg = int(self.weapons["bounce"]["base_damage"] * current_mult)
                bouncing_orbs.append(BouncingOrb(self.pos, target_dir, dmg))

        if self.weapons["trail"]["active"]:
            self.weapons["trail"]["timer"] += 1
            if self.weapons["trail"]["timer"] >= self.weapons["trail"]["cooldown"]:
                self.weapons["trail"]["timer"] = 0
                dmg = int(self.weapons["trail"]["base_damage"] * current_mult)
                drop_radius = 300 
                
                for _ in range(3): 
                    angle = random.uniform(0, math.pi * 2)
                    dist = random.uniform(0, drop_radius)
                    spawn_pos = pygame.math.Vector2(
                        self.pos.x + math.cos(angle) * dist,
                        self.pos.y + math.sin(angle) * dist
                    )
                    from weapons import FireZone
                    fire_zones.append(FireZone(spawn_pos, dmg))

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
                    for _ in range(max_chains - 1): 
                        next_enemy = None
                        min_dist = float('inf')
                        for e in enemies:
                            if e not in hit_list:
                                dist = current_enemy.pos.distance_squared_to(e.pos)
                                if dist < 62500: 
                                    if dist < min_dist:
                                        min_dist = dist
                                        next_enemy = e
                        if next_enemy:
                            hit_list.append(next_enemy)
                            points.append(next_enemy.pos)
                            next_enemy.take_damage(dmg, dmg_texts)
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
                        e.freeze_timer = freeze_time 

        if self.weapons["chakram"]["active"]:
            self.weapons["chakram"]["timer"] += 1
            if self.weapons["chakram"]["timer"] >= self.weapons["chakram"]["cooldown"]:
                self.weapons["chakram"]["timer"] = 0
                dmg = int(self.weapons["chakram"]["base_damage"] * current_mult)
                chakrams.append(Chakram(self.pos, target_dir, dmg))


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

    def update_timers(self, dmg_texts):
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