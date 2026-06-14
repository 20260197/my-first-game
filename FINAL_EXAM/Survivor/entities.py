import pygame
import random
import math
from Sub_config import *
from weapons import *
from effects import *
from resource_manager import *

# 게임 시작 전 로딩

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
        self.max_xp = 15
        self.kills = 0
        self.phase = 1
        self.global_dmg_mult = 1.0
        self.god_mode = False
        self.pickup_radius = 150  
        self.invincible_timer = 0
        self.frenzy_timer = 0   

        self.weapons = {
            "ranged": {"active": True, "level": 1, "max_level": 5, "cooldown": 35, "timer": 0, "base_damage": 15, "count": 1, "name": "Ranged Magic", "desc": "[원거리] 마법 구체를 발사합니다."},
            "melee": {"active": False, "level": 1, "max_level": 5, "cooldown": 100, "timer": 0, "base_damage": 35, "rear": False, "name": "Spirit Sword", "desc": "[근접] 전방으로 적을 관통하는 검기를 날립니다."},
            "orbit": {"active": False, "level": 1, "max_level": 5, "angle": 0.0, "speed": 0.04, "base_damage": 8, "radius": 75, "count": 1, "name": "Orbiting Shield", "desc": "[오라] 주변을 공전하며 피해를 줍니다."},
            "axe": {"active": False, "level": 1, "max_level": 5, "cooldown": 120, "timer": 0, "base_damage": 50, "name": "Heavy Axe", "desc": "[투척] 적을 관통하는 둔탁한 도끼를 던집니다."},
            "boomerang": {"active": False, "level": 1, "max_level": 5, "cooldown": 90, "timer": 0, "base_damage": 25, "name": "Boomerang", "desc": "[특수] 궤도를 돌고 되돌아오는 부메랑입니다."},
            "bounce": {"active": False, "level": 1, "max_level": 5, "cooldown": 110, "timer": 0, "base_damage": 20, "name": "Magic Wand", "desc": "[마법] 맵의 벽에 튕기는 통통탄을 쏩니다."},
            "trail": {"active": False, "level": 1, "max_level": 5, "cooldown": 120, "timer": 0, "base_damage": 15, "radius": 45, "name": "Meteor Strike", "desc": "[폭격] 주변 무작위 위치에 화염 장판을 폭격합니다."},
            "lightning": {"active": False, "level": 1, "max_level": 5, "cooldown": 80, "timer": 0, "base_damage": 25, "chain_count": 5, "bolt_count": 1, "name": "Chain Lightning", "desc": "[전기] 적을 관통하며 전이되는 번개를 방출합니다."},
            "beam": {"active": False, "level": 1, "max_level": 5, "cooldown": 180, "timer": 0, "base_damage": 100, "width": 20, "name": "Orbital Beam", "desc": "[관통] 조준 방향으로 화면을 뚫는 거대 레이저를 쏩니다."},
            "blizzard": {"active": False, "level": 1, "max_level": 3, "cooldown": 200, "timer": 0, "base_damage": 10, "radius": 180, "freeze_time": 180, "name": "Blizzard", "desc": "[결빙] 광역 눈보라를 일으켜 닿은 적을 3초간 얼려버립니다."},
            "chakram": {"active": False, "level": 1, "max_level": 3, "cooldown": 100, "timer": 0, "base_damage": 30, "burn_dmg": 5, "name": "Hellfire Chakram", "desc": "[화상] 적에게 지속 화상 피해를 입히는 차크람을 던집니다."},
            "storm": {"active": False, "level": 1, "max_level": 1, "cooldown": 30, "timer": 0, "base_damage": 25, "radius": 220, "burn_dmg": 15, "freeze_time": 90, "name": "Elemental Storm", "desc": "[합체] 빙염의 폭풍이 상시 전개되어 빙결과 화상을 줍니다."}
        }
        self.storm_angle = 0.0 # 폭풍 회전 애니메이션용 변수
        self.damage_stats = {key: 0 for key in self.weapons.keys()}

        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 5  
        self.is_moving = False
        self.facing_row = 0 
        
        # 실제 파일 경로에 맞게 "assets/player_sheet.png" 부분을 수정하세요
        self.animations = load_sprite_sheet("assets/Player/Player.png", 32, 32, 6, 16)

    def get_total_dmg_mult(self):
        phase_bonus = (self.phase - 1) * 0.10
        total = self.global_dmg_mult + phase_bonus    

        if getattr(self, 'frenzy_timer', 0) > 0:
            total *= 2.0 
            
        return total

    def handle_input(self):
        if getattr(self, 'invincible_timer', 0) > 0:
            self.invincible_timer -= 1

        if getattr(self, 'frenzy_timer', 0) > 0:
            self.frenzy_timer -= 1
            
        keys = pygame.key.get_pressed()
        move_dir = pygame.math.Vector2(0, 0)


        if keys[pygame.K_w] or keys[pygame.K_UP]: move_dir.y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_dir.y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_dir.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_dir.x += 1

        if move_dir.length_squared() > 0:
            self.is_moving = True
            move_dir.normalize_ip()
            self.pos += move_dir * self.speed
            self.look_dir = move_dir
            
            import math
            angle = math.degrees(math.atan2(move_dir.y, move_dir.x))
            if angle < 0: angle += 360
            
            dir_index = int((angle + 22.5) // 45) % 8 
            mapping = [2, 1, 0, 7, 6, 5, 4, 3] 
            self.facing_row = mapping[dir_index]
        else:
            self.is_moving = False

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

    def update_weapons(self, enemies, projectiles, sword_waves, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams):
        
        target_dir = self.look_dir
        if target_dir.length_squared() == 0:
            target_dir = pygame.math.Vector2(1, 0)
            
        current_mult = self.get_total_dmg_mult()

        timer_speed = 4 if getattr(self, 'frenzy_timer', 0) > 0 else 1

        if self.weapons["ranged"]["active"]:
            self.weapons["ranged"]["timer"] += timer_speed
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
                    projectiles.append(Projectile(self.pos, fire_dir, dmg, weapon_id="ranged"))

        if self.weapons["melee"]["active"]:
            self.weapons["melee"]["timer"] += timer_speed
            if self.weapons["melee"]["timer"] >= self.weapons["melee"]["cooldown"]:
                self.weapons["melee"]["timer"] = 0
                dmg = int(self.weapons["melee"]["base_damage"] * current_mult)
                sword_waves.append(SwordWave(self.pos, target_dir, dmg))
                if self.weapons["melee"]["rear"]:
                    sword_waves.append(SwordWave(self.pos, -target_dir, dmg))

        if self.weapons["orbit"]["active"]:
            orbit = self.weapons["orbit"]
            # 💡 오라 무기도 광란 시 4배 빠르게 회전합니다!
            orbit["angle"] += orbit["speed"] * timer_speed
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
            self.weapons["axe"]["timer"] += timer_speed
            if self.weapons["axe"]["timer"] >= self.weapons["axe"]["cooldown"]:
                self.weapons["axe"]["timer"] = 0
                dmg = int(self.weapons["axe"]["base_damage"] * current_mult)
                projectiles.append(ThrowingAxe(self.pos, target_dir, dmg, weapon_id="axe"))

        if self.weapons["boomerang"]["active"]:
            self.weapons["boomerang"]["timer"] += timer_speed
            if self.weapons["boomerang"]["timer"] >= self.weapons["boomerang"]["cooldown"]:
                self.weapons["boomerang"]["timer"] = 0
                dmg = int(self.weapons["boomerang"]["base_damage"] * current_mult)
                boomerangs.append(Boomerang(self.pos, target_dir, dmg, weapon_id="boomerang"))

        if self.weapons["bounce"]["active"]:
            self.weapons["bounce"]["timer"] += timer_speed
            if self.weapons["bounce"]["timer"] >= self.weapons["bounce"]["cooldown"]:
                self.weapons["bounce"]["timer"] = 0
                dmg = int(self.weapons["bounce"]["base_damage"] * current_mult)
                bouncing_orbs.append(BouncingOrb(self.pos, target_dir, dmg, weapon_id="bounce"))

        if self.weapons["trail"]["active"]:
            self.weapons["trail"]["timer"] += timer_speed
            if self.weapons["trail"]["timer"] >= self.weapons["trail"]["cooldown"]:
                self.weapons["trail"]["timer"] = 0
                dmg = int(self.weapons["trail"]["base_damage"] * current_mult)
                rad = self.weapons["trail"]["radius"]
                from weapons import MeteorDrop
                targets = []
                if len(enemies) > 0:
                    sample_size = min(3, len(enemies))
                    targets = random.sample(enemies, sample_size)
                for t in targets:
                    fire_zones.append(MeteorDrop(t.pos, dmg, radius=rad, weapon_id="trail"))
                if len(targets) < 3:
                    for _ in range(3 - len(targets)):
                        angle = random.uniform(0, math.pi * 2)
                        dist = random.uniform(50, 200)
                        spawn_pos = pygame.math.Vector2(self.pos.x + math.cos(angle) * dist, self.pos.y + math.sin(angle) * dist)
                        fire_zones.append(MeteorDrop(spawn_pos, dmg, radius=rad, weapon_id="trail"))

        if self.weapons["lightning"]["active"]:
            self.weapons["lightning"]["timer"] += timer_speed
            if self.weapons["lightning"]["timer"] >= self.weapons["lightning"]["cooldown"]:
                self.weapons["lightning"]["timer"] = 0
                dmg = int(self.weapons["lightning"]["base_damage"] * current_mult)
                bolt_count = self.weapons["lightning"]["bolt_count"]
                max_chains = self.weapons["lightning"]["chain_count"]
                
                # ==========================================
                # 💡 [핵심] 번개 사거리 설정 (픽셀 단위)
                # ==========================================
                max_range_sq = 400 ** 2   # 첫 타격 최대 사거리 (예: 반경 400픽셀 이내)
                jump_range_sq = 150 ** 2  # 적과 적 사이 점프 최대 거리 (예: 반경 150픽셀 이내)
                
                # 💡 [수정] 무조건 전체 적을 가져오지 않고, 최대 사거리 내에 있는 적들만 먼저 추려냅니다.
                valid_enemies = [e for e in enemies if self.pos.distance_squared_to(e.pos) <= max_range_sq]
                valid_enemies.sort(key=lambda e: self.pos.distance_squared_to(e.pos))
                
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
                                # 💡 [수정] 기존의 14400 하드코딩 대신 설정한 점프 사거리 변수를 사용
                                if dist < jump_range_sq: 
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
            self.weapons["beam"]["timer"] += timer_speed
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
            self.weapons["blizzard"]["timer"] += timer_speed
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
            self.weapons["chakram"]["timer"] += timer_speed
            if self.weapons["chakram"]["timer"] >= self.weapons["chakram"]["cooldown"]:
                self.weapons["chakram"]["timer"] = 0
                dmg = int(self.weapons["chakram"]["base_damage"] * current_mult)
                base_angle = math.degrees(math.atan2(target_dir.y, target_dir.x))
                angles = [base_angle - 15, base_angle, base_angle + 15]
                for ang in angles:
                    rad_ang = math.radians(ang)
                    fire_dir = pygame.math.Vector2(math.cos(rad_ang), math.sin(rad_ang))
                    chakrams.append(Chakram(self.pos, fire_dir, dmg, weapon_id="chakram"))

        if self.weapons["storm"]["active"]:
            self.weapons["storm"]["timer"] += timer_speed
            if self.weapons["storm"]["timer"] >= self.weapons["storm"]["cooldown"]:
                self.weapons["storm"]["timer"] = 0
                dmg = int(self.weapons["storm"]["base_damage"] * current_mult)
                rad = self.weapons["storm"]["radius"]
                for e in enemies:
                    if self.pos.distance_to(e.pos) < rad + e.radius:
                        e.take_damage(dmg, dmg_texts)
                        self.damage_stats["storm"] += dmg 
                        e.freeze_timer = self.weapons["storm"]["freeze_time"]
                        e.burn_timer = 180
                        e.burn_damage = int(self.weapons["storm"]["burn_dmg"] * current_mult)

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))

        if getattr(self, 'frenzy_timer', 0) > 0:
            import random
            aura_rad = self.radius + random.randint(4, 12)
            pygame.draw.circle(surface, RED, screen_pos, aura_rad, 2)
            pygame.draw.circle(surface, ORANGE, screen_pos, aura_rad + 4, 1)
        
        # 👇 [순서 변경] 폭풍과 오라 이펙트를 '플레이어 렌더링'보다 먼저 그립니다. (바닥에 깔리게 됨)
        if self.weapons["storm"]["active"]:
            self.storm_angle += 0.08
            rad = self.weapons["storm"]["radius"]
            
            s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (0, 255, 255, 40), (rad, rad), rad)
            
            for i in range(4):
                angle = self.storm_angle + (math.pi / 2) * i
                p1 = (rad + math.cos(angle) * rad, rad + math.sin(angle) * rad)
                pygame.draw.line(s, (255, 100, 0, 150), (rad, rad), p1, 15)
                
            surface.blit(s, (screen_pos[0] - rad, screen_pos[1] - rad))
            pygame.draw.circle(surface, CYAN, screen_pos, rad, 3)
            pygame.draw.circle(surface, ORANGE, screen_pos, rad - 8, 3)

        if self.weapons["orbit"]["active"]:
            orbit = self.weapons["orbit"]
            for i in range(orbit["count"]):
                angle_offset = (math.pi * 2 / orbit["count"]) * i
                orb_screen_x = int(self.pos.x + math.cos(orbit["angle"] + angle_offset) * orbit["radius"] - cam.x)
                orb_screen_y = int(self.pos.y + math.sin(orbit["angle"] + angle_offset) * orbit["radius"] - cam.y)
                pygame.draw.circle(surface, PURPLE, (orb_screen_x, orb_screen_y), 10)

        # 👇 [순서 변경] 플레이어 도트 이미지를 가장 마지막에 그립니다. (항상 최상단에 노출됨)
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % 6 

        current_row = self.facing_row
        if self.is_moving:
            current_row += 8 

        if getattr(self, 'invincible_timer', 0) > 0 and (self.invincible_timer // 5) % 2 == 0:
            pass 
        else:
            current_image = self.animations[current_row][self.frame_index]
            surface.blit(current_image, (screen_pos[0] - 16, screen_pos[1] - 16))

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
            if not player_obj.god_mode and player_obj.invincible_timer <= 0:
                player_obj.hp -= self.attack        # 틱 데미지가 아닌 1회 온전한 공격력 적용
                player_obj.invincible_timer = 60    # 타격받은 직후 30프레임(0.5초) 동안 무적

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
        
class ExpGem:
    def __init__(self, pos, amount):
        self.pos = pygame.math.Vector2(pos)
        self.amount = amount
        self.radius = max(6, min(amount // 3, 12)) 
        
        if amount < 25: self.color = GREEN
        elif amount < 50: self.color = CYAN
        else: self.color = YELLOW
            
        # 초기 속도를 없애서 스폰된 그 자리에 가만히 멈춰있게 합니다.
        self.velocity = pygame.math.Vector2(0, 0)
        self.pull_force = 0.0 
        self.is_moving = False

    def update(self, player):
        dist = self.pos.distance_to(player.pos)
        
        # 플레이어 자석 반경에 닿았을 때만 끌려가는 로직 작동
        if dist < player.pickup_radius:
            self.is_moving = True

        # 한 번 자석에 반응하면 그때부터 속도가 붙으며 끌려옵니다.
        if self.is_moving:
            if dist > 0:
                dir_vector = (player.pos - self.pos).normalize()
                self.pull_force += 0.15 
                self.velocity += dir_vector * self.pull_force
                self.velocity *= 0.88 
            
            # 끌려올 때만 좌표 이동 연산을 수행합니다.
            self.pos += self.velocity
                
        return dist < player.radius + self.radius

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius, 2) 
        
        line_len = self.radius - 2
        pygame.draw.line(surface, WHITE, (screen_pos[0] - line_len, screen_pos[1]), (screen_pos[0] + line_len, screen_pos[1]), 2)
        pygame.draw.line(surface, WHITE, (screen_pos[0], screen_pos[1] - line_len), (screen_pos[0], screen_pos[1] + line_len), 2)

class BossProjectile:
    def __init__(self, pos, direction, speed, damage):
        self.pos = pygame.math.Vector2(pos)
        self.direction = direction.normalize() if direction.length() > 0 else pygame.math.Vector2(1, 0)
        self.speed = speed
        self.damage = damage
        self.radius = 10
        self.color = (255, 50, 255) # 눈에 띄는 자홍색(Magenta) 탄막
        self.life = 180 # 3초 동안 날아감

    def update(self):
        self.pos += self.direction * self.speed
        self.life -= 1
        return self.life <= 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius, 2)

class Boss:
    def __init__(self, pos, hp):
        self.pos = pygame.math.Vector2(pos)
        self.radius = 50 
        self.max_hp = hp
        self.hp = hp
        self.speed = 1.2
        self.color = RED
        self.attack = 30
        self.xp_reward = 5
        self.tick_timers = {}
        
        # [신규] 보스 패턴(상태) 관리 변수
        self.state = "CHASE"
        self.state_timer = 0
        self.attack_timer = 0
        self.enraged = False
        self.spiral_angle = 0.0
        self.dash_dir = pygame.math.Vector2(0, 0)
        
        # ⚠️ 주의: 이미지 파일 경로와 프레임 사이즈(w, h)를 실제 이미지에 맞게 수정하세요!
        # 예: 3x3 그리드라면 전체 이미지 가로/3, 세로/3 값을 입력합니다.
        sheet_path = r"assets\Enemy\Boss\Boss_Sheet.png"
        self.frames = load_sprite_sheet(sheet_path, 341, 256, 3, 3) 

        if not self.frames:
            print("❌ 에러: 이미지를 불러오지 못했습니다. 경로를 확인하세요:", sheet_path)
        else:
            self.all_frames = [frame for row in self.frames for frame in row if frame is not None]
            print(f"✅ 성공: 총 {len(self.all_frames)}개의 프레임을 불러왔습니다.")

        self.all_frames = [frame for row in self.frames for frame in row if frame is not None]
        self.frame_index = 0
        self.anim_timer = 0

    def take_damage(self, damage, dmg_texts):
        self.hp -= damage
        try:
            from entities import DamageText
            dmg_texts.append(DamageText(self.pos, damage))
        except Exception:
            pass

    def can_receive_tick_damage(self, source_id, cooldown):
        import pygame 
        current_time = pygame.time.get_ticks()
        ms_cooldown = cooldown * 17 
        if source_id not in self.tick_timers or current_time - self.tick_timers[source_id] >= ms_cooldown:
            self.tick_timers[source_id] = current_time
            return True
        return False

    def update(self, player_obj, boss_projectiles):
        import math
        dist = self.pos.distance_to(player_obj.pos)
        
        # 1. 광폭화 체크
        if not self.enraged and self.hp <= self.max_hp * 0.5:
            self.enraged = True
            self.speed = 1.8 

        self.state_timer += 1

        # 2. 보스 패턴 상태 머신
        if self.state == "CHASE":
            if dist > 0:
                dir_vector = (player_obj.pos - self.pos).normalize()
                self.pos += dir_vector * self.speed
            self.attack_timer += 1
            cooldown = 80 if self.enraged else 120
            if self.attack_timer >= cooldown:
                self.attack_timer = 0
                for i in range(8):
                    angle = i * (math.pi / 4) 
                    proj_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    boss_projectiles.append(BossProjectile(self.pos, proj_dir, speed=4.5, damage=15))
            if self.state_timer >= 200:
                self.state_timer = 0
                import random
                self.state = random.choice(["DASH_PREP", "SPIRAL"])

        elif self.state == "SPIRAL":
            if self.state_timer % 4 == 0:
                proj_dir = pygame.math.Vector2(math.cos(self.spiral_angle), math.sin(self.spiral_angle))
                boss_projectiles.append(BossProjectile(self.pos, proj_dir, speed=5.0, damage=15))
                self.spiral_angle += 0.35
            if self.state_timer >= 120:
                self.state = "CHASE"
                self.state_timer = 0
                self.attack_timer = 0

        elif self.state == "DASH_PREP":
            if self.state_timer == 1:
                self.dash_dir = (player_obj.pos - self.pos).normalize() if dist > 0 else pygame.math.Vector2(1, 0)
            if self.state_timer >= 60:
                self.state = "DASH"
                self.state_timer = 0

        elif self.state == "DASH":
            self.pos += self.dash_dir * (12.0 if self.enraged else 8.0)
            if self.state_timer >= 30:
                self.state = "CHASE"
                self.state_timer = 0
                self.attack_timer = 0

        # 3. 몸통 박치기 판정
        if dist < self.radius + player_obj.radius:
            if not player_obj.god_mode and getattr(player_obj, 'invincible_timer', 0) <= 0:
                player_obj.hp -= self.attack
                player_obj.invincible_timer = 60

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 💡 애니메이션 업데이트
        self.anim_timer += 1
        if self.anim_timer >= 6:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.all_frames)
        
        # 이미지 그리기
        img = self.all_frames[self.frame_index]
        rect = img.get_rect(center=screen_pos)
        surface.blit(img, rect.topleft)

        # 돌진 경고선
        if self.state == "DASH_PREP":
            end_pos = (int(screen_pos[0] + self.dash_dir.x * 1000), int(screen_pos[1] + self.dash_dir.y * 1000))
            if (self.state_timer // 5) % 2 == 0:
                pygame.draw.line(surface, (255, 50, 50), screen_pos, end_pos, 3)

        # 체력바 (시각적 일관성 유지)
        bar_width = self.radius * 2
        bar_height = 6
        pygame.draw.rect(surface, BLACK, (screen_pos[0]-self.radius, screen_pos[1]+self.radius+10, bar_width, bar_height))
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, RED, (screen_pos[0]-self.radius, screen_pos[1]+self.radius+10, int(bar_width * hp_ratio), bar_height))

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # [연출] 돌진 준비 중일 때 붉은색 경고 레이저 선 표시
        if self.state == "DASH_PREP":
            end_pos = (int(screen_pos[0] + self.dash_dir.x * 1000), int(screen_pos[1] + self.dash_dir.y * 1000))
            # 깜빡이는 경고선 연출
            if (self.state_timer // 5) % 2 == 0:
                pygame.draw.line(surface, (255, 50, 50), screen_pos, end_pos, 3)

        pygame.draw.circle(surface, self.color, screen_pos, self.radius)
        pygame.draw.circle(surface, (100, 0, 0) if not self.enraged else BLACK, screen_pos, self.radius, 5)
        pygame.draw.circle(surface, WHITE, screen_pos, self.radius + 5, 2)