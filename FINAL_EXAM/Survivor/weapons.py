import pygame
import math
from Sub_config import *
from resource_manager import *

class MeteorDrop:
    # [수정] radius 매개변수를 추가하고 기본값을 45로 설정합니다.
    def __init__(self, target_pos, damage, radius=45, weapon_id="trail"):
        self.pos = pygame.math.Vector2(target_pos)
        self.damage = damage
        self.radius = radius # [수정] 고정값 45 대신 동적 변수로 받습니다.
        self.weapon_id = weapon_id
        
        # 상태 관리 (경고/추락 -> 화염 장판)
        self.state = "warning"
        self.delay = 45 
        self.life = 120 
        
        self.fall_y = self.pos.y - 800

    def update(self):
        if self.state == "warning":
            self.delay -= 1
            # 목표 지점을 향해 점점 빠르게 떨어지는 애니메이션 연산
            self.fall_y += (self.pos.y - self.fall_y) * 0.15 
            if self.delay <= 0:
                self.state = "burning"
        elif self.state == "burning":
            self.life -= 1
            
        # 수명이 다하면 True를 반환하여 소멸시킴
        return self.state == "burning" and self.life <= 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        if self.state == "warning":
            # 바닥 경고 표시 (테두리와 옅은 붉은색 채우기)
            pygame.draw.circle(surface, RED, screen_pos, self.radius, 2)
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 0, 0, 40), (self.radius, self.radius), self.radius)
            surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))
            
            # 하늘에서 떨어지는 메테오 본체 렌더링
            meteor_screen_y = int(self.fall_y - cam.y)
            pygame.draw.circle(surface, ORANGE, (screen_pos[0], meteor_screen_y), 15)
            pygame.draw.line(surface, YELLOW, (screen_pos[0], meteor_screen_y), (screen_pos[0], meteor_screen_y - 60), 5)
            
        elif self.state == "burning":
            # 기존 화염 장판 렌더링
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (230, 126, 34, 100), (self.radius, self.radius), self.radius)
            surface.blit(s, (screen_pos[0]-self.radius, screen_pos[1]-self.radius))

import pygame
import math
from resource_manager import load_sprite_sheet, get_image

class Projectile:
    def __init__(self, spawn_pos, direction, damage, weapon_id="ranged"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)

        self.damage = damage
        self.weapon_id = weapon_id
        
        from resource_manager import load_sprite_sheet, get_image
        sheet_path = r"assets\Weapon\Muzzle\Muzzle_Sheet.png" # 에셋 폴더 경로 재확인!
        temp_img = get_image(sheet_path)
        total_w, total_h = temp_img.get_size()
        
        self.frame_w = total_w // 3
        self.frame_h = total_h
        self.frames = load_sprite_sheet(sheet_path, self.frame_w, self.frame_h, 3, 1)

        # 💡 상태 및 변수 초기화
        self.state = "flying"
        self.hit_targets = [] 
        self.radius = 15
        self.frame_index = 0
        self.anim_timer = 0
        self.angle = 0
        
        self.speed = 10
        self.life = 120
        self.velocity = self.dir.normalize() * self.speed
        
        # 유도 센서용 변수
        self.target = None
        self.detection_radius_sq = 300 ** 2 # 센서 반경 (이 안에 들어와야 유도 시작)

    # 💡 [핵심] update 함수가 enemies를 받도록 수정되었습니다.
    def update(self, enemies):
        if self.state == "exploding":
            self.anim_timer += 1
            if self.anim_timer >= 3: # 폭발 애니메이션 속도
                self.anim_timer = 0
                self.frame_index += 1
            if self.frame_index >= 3:
                return True # 삭제
            return False

        self.life -= 1
        if self.life <= 0:
            self.hit()
            return False

        # 💡 유도(Homing) 로직
        if enemies and (not self.target or self.target not in enemies):
            valid_enemies = [e for e in enemies if self.pos.distance_squared_to(e.pos) <= self.detection_radius_sq]
            if valid_enemies:
                self.target = min(valid_enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
            else:
                self.target = None

        if self.target:
            desired_dir = (self.target.pos - self.pos)
            if desired_dir.length_squared() > 0:
                desired_velocity = desired_dir.normalize() * self.speed
                self.velocity = self.velocity.lerp(desired_velocity, 0.15) # 0.15 = 꺾이는 속도

        self.pos += self.velocity
        return False

    def hit(self):
        if self.state == "flying":
            self.state = "exploding"
            self.frame_index = 1
            self.anim_timer = 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))

        if self.state == "flying":
            current_image = self.frames[0][0]
            self.angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
            rotated_image = pygame.transform.rotate(current_image, self.angle)
            new_rect = rotated_image.get_rect(center=screen_pos)
            surface.blit(rotated_image, new_rect.topleft)

        elif self.state == "exploding":
            idx = min(self.frame_index, 2)
            current_image = self.frames[0][idx]
            rotated_image = pygame.transform.rotate(current_image, self.angle)
            new_rect = rotated_image.get_rect(center=screen_pos)
            surface.blit(rotated_image, new_rect.topleft)

# 👇 [신규 추가] Projectile 클래스 밑에 이 클래스를 통째로 붙여넣으세요.
class HomingProjectile:
    def __init__(self, spawn_pos, direction, damage, pierce=1, color=YELLOW, radius=PROJECTILE_RADIUS, weapon_id="ranged"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        
        self.velocity = self.dir.normalize() * PROJECTILE_SPEED
        self.speed = PROJECTILE_SPEED
        self.radius = radius
        self.damage = damage
        self.color = color
        self.pierce = pierce
        self.hit_targets = []
        self.weapon_id = weapon_id
        
        self.life = 90  # 1초 수명
        self.target = None
        
        # 💡 [핵심] 근접 센서 반경 (픽셀). 이 거리 안으로 적이 들어와야 유도를 시작합니다.
        # 연산 최적화를 위해 미리 제곱값으로 저장해둡니다. (예: 250 픽셀)
        self.detection_radius_sq = 250 ** 2  

    def update(self, enemies=None):
        self.life -= 1
        if self.life <= 0:
            return True

        # ==========================================
        # 1. 타겟 감지 로직 (센서)
        # ==========================================
        # 아직 타겟이 없거나, 쫓던 타겟이 죽었을 때만 주변을 스캔합니다.
        if enemies and (not self.target or self.target not in enemies):
            # 💡 무조건 가장 가까운 적을 찾는 게 아니라, '센서 반경(250)' 안에 들어온 적만 추려냅니다.
            valid_enemies = [e for e in enemies if self.pos.distance_squared_to(e.pos) <= self.detection_radius_sq]
            
            if valid_enemies:
                # 반경 안에 적이 들어왔다면, 그중 가장 가까운 적을 타겟으로 '락온(Lock-on)' 합니다.
                self.target = min(valid_enemies, key=lambda e: self.pos.distance_squared_to(e.pos))
            else:
                self.target = None # 반경에 적이 없으면 타겟 없음 유지

        # ==========================================
        # 2. 이동 및 궤도 꺾기(포물선) 로직
        # ==========================================
        if self.target:
            # 센서에 적이 포착된 상태: 적을 향해 부드럽게 궤도를 꺾음 (Lerp)
            desired_dir = (self.target.pos - self.pos)
            if desired_dir.length_squared() > 0:
                desired_velocity = desired_dir.normalize() * self.speed
                # 0.08의 비율로 서서히 궤도를 틉니다. 수치를 0.04 정도로 낮추면 훨씬 더 크게 우회하는 포물선을 그립니다.
                self.velocity = self.velocity.lerp(desired_velocity, 0.08)

        # 센서에 포착된 적이 없다면? 기존 velocity가 변하지 않으므로 처음 발사된 방향으로 계속 '직진'합니다.
        self.pos += self.velocity
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, self.color, screen_pos, self.radius)

# 👇 [수정] 기존 Boomerang 클래스를 통째로 덮어씌우세요.
class Boomerang:
    def __init__(self, spawn_pos, direction, damage, weapon_id="boomerang"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)

        from resource_manager import get_image
        
        # 💡 [적용] 파일명을 'Boomerang_Sheet.png'로 영구 고정
        sheet_path = r"assets\Weapon\Boomerang\Boomerang_Sheet.png" 
        temp_img = get_image(sheet_path)
        total_w, total_h = temp_img.get_size()
        
        self.frame_w = total_w // 2  # 가로 2칸
        self.frame_h = total_h // 2  # 세로 2칸
        
        self.frames = load_sprite_sheet(sheet_path, self.frame_w, self.frame_h, 2, 2)
        
        self.frame_index = 0
        self.anim_timer = 0
        
        self.velocity = self.dir.normalize() * 15 
        self.speed = 15
        self.damage = damage
        self.radius = 12
        self.state = "outward"
        self.timer = 30
        self.color = GREEN
        self.hit_targets = []
        self.weapon_id = weapon_id
        self.life = 240

    def update(self, player_pos):
        self.life -= 1 
        if self.life <= 0: return True

        # 💡 4프레임 애니메이션을 순서대로 재생합니다.
        self.anim_timer += 1
        if self.anim_timer >= 2: # 회전(프레임 교체) 속도 조절
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % 4

        if self.state == "outward":
            self.pos += self.velocity
            self.timer -= 1
            if self.timer <= 0:
                self.state = "returning"
                self.hit_targets = []
        else:
            target_dir = (player_pos - self.pos)
            if target_dir.length() < 30: return True
                
            desired_velocity = target_dir.normalize() * (self.speed * 1.5)
            self.velocity = self.velocity.lerp(desired_velocity, 0.06)
            self.pos += self.velocity
            
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 1. 현재 프레임 이미지 가져오기
        row = self.frame_index // 2
        col = self.frame_index % 2
        current_image = self.frames[row][col]
        
        # 💡 [핵심] 2. 날아가는 방향(velocity)을 각도로 계산
        # pygame 화면은 y축이 아래로 갈수록 커지므로 -self.velocity.y 를 해줍니다.
        angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        
        # 💡 3. 이미지 회전시키기
        rotated_image = pygame.transform.rotate(current_image, angle)
        
        # 💡 4. 회전 후 틀어지는 중심점 잡아주기 (매우 중요!)
        # 이미지를 회전하면 사각형 크기가 변해서 덜덜 떨리게 됩니다.
        # get_rect(center=...)를 쓰면 이런 현상 없이 중심축을 완벽하게 고정해 줍니다.
        new_rect = rotated_image.get_rect(center=screen_pos)
        
        surface.blit(rotated_image, new_rect.topleft)

class BouncingOrb:
    def __init__(self, pos, direction, damage, weapon_id="bounce"):
        self.pos = pygame.math.Vector2(pos)
        self.dir = pygame.math.Vector2(direction).normalize()
        self.speed = 10
        self.damage = damage
        self.radius = 12
        self.weapon_id = weapon_id
        
        self.bounces = 3
        self.hit_targets = []
        
        # 💡 [핵심 1] 스프라이트 시트 로드 (4열 3행 = 12프레임)
        sheet_path = r"assets\Weapon\Bounce\BouncingOrb_Sheet.png"
        raw_surf = get_image(sheet_path)
        
        scaled_surf = pygame.transform.scale(raw_surf, (256, 192))
        
        self.frames = self.split_sheet(scaled_surf, 64, 64, 4, 3)
        
        self.all_frames = []
        for r in range(3):
            for c in range(4):
                self.all_frames.append(self.frames[r][c])
        
        self.frame_index = 0
        self.anim_timer = 0
        self.angle = 0 # 회전용 각도
        self.flash_timer = 0 # 튕길 때 반짝이는 타이머

    def update(self):
        # 애니메이션 재생
        self.anim_timer += 1
        if self.anim_timer >= 2: # 2프레임마다 이미지 교체
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % 12
            
        # 이동 및 튕기기
        self.pos += self.dir * self.speed
        self.angle += 15 # 이동하면서 빙글빙글 회전
        
        bounced = False
        if self.pos.x <= self.radius or self.pos.x >= WORLD_WIDTH - self.radius:
            self.dir.x *= -1
            bounced = True
        if self.pos.y <= self.radius or self.pos.y >= WORLD_HEIGHT - self.radius:
            self.dir.y *= -1
            bounced = True
            
        if bounced:
            self.bounces -= 1
            self.flash_timer = 4 # 튕기면 4프레임 동안 번쩍!
            self.hit_targets = [] # 관통 판정 초기화
            
        if self.flash_timer > 0:
            self.flash_timer -= 1
            
        return self.bounces < 0

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 이미지 회전
        img = self.all_frames[self.frame_index]
        rotated_img = pygame.transform.rotate(img, self.angle)
        
        # 💡 [핵심 3] 튕길 때 번쩍이는 효과 (색상 덮어씌우기)
        if self.flash_timer > 0:
            # 밝게 보이기 위해 흰색을 덧씌우는 연출
            white_surf = rotated_img.copy()
            white_surf.fill((255, 255, 255, 128), special_flags=pygame.BLEND_RGBA_ADD)
            surface.blit(white_surf, rotated_img.get_rect(center=screen_pos).topleft)
        else:
            surface.blit(rotated_img, rotated_img.get_rect(center=screen_pos).topleft)

    def split_sheet(self, surface, w, h, cols, rows):
        frames = []
        for r in range(rows):
            row_frames = []
            for c in range(cols):
                frame = surface.subsurface(pygame.Rect(c * w, r * h, w, h))
                row_frames.append(frame)
            frames.append(row_frames)
        return frames

class Chakram:
    def __init__(self, spawn_pos, direction, damage, weapon_id="chakram"):
        self.spawn_pos = pygame.math.Vector2(spawn_pos)
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        
        self.speed = 12
        self.damage = damage
        self.radius = 18 # 적과 부딪히는 충돌 판정 크기
        
        self.state = "outward"
        self.timer = 25       
        self.hover_timer = 45 
        
        self.hit_targets = []
        self.weapon_id = weapon_id

        # 💡 [핵심 1] 50x50 사이즈 8x8 그리드 로드
        from resource_manager import load_sprite_sheet, get_image
        sheet_path = r"assets\Weapon\Chakram\Charkram_Sheet.png"
        temp_frames = load_sprite_sheet(sheet_path, 50, 50, 8, 8)
        
        # 💡 [핵심 2] 2차원 배열에서 정확히 60개의 이미지만 1차원 리스트로 쭉 뽑아냅니다.
        self.frames = []
        for r in range(8):
            for c in range(8):
                if len(self.frames) < 60: # 60장이 다 차면 그만 가져옵니다.
                    self.frames.append(temp_frames[r][c])
                    
        self.frame_index = 0
        self.anim_timer = 0

    def update(self, player_pos):
        # 💡 [핵심 3] 프레임이 60개나 되므로, 엄청 부드럽게 돌아가도록 매 프레임(또는 2프레임마다) 이미지를 교체합니다.
        self.anim_timer += 1
        if self.anim_timer >= 1: # 1이면 가장 빠르고 부드러움. 조금 느리게 하려면 2로 변경.
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % 60
            
        # 이동 로직
        if self.state == "outward":
            self.pos += self.dir * self.speed
            self.timer -= 1
            if self.timer <= 0:
                self.state = "hover"
                self.hit_targets = [] 
                
        elif self.state == "hover":
            self.hover_timer -= 1
            if self.hover_timer <= 0:
                self.state = "returning"
                self.hit_targets = [] 
                
        elif self.state == "returning":
            target_dir = (self.spawn_pos - self.pos)
            if target_dir.length() < self.speed: 
                return True 
            self.dir = target_dir.normalize()
            self.pos += self.dir * self.speed
            
        return False

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 1차원 리스트로 펴두었기 때문에 [row][col] 계산 없이 바로 인덱스로 가져올 수 있습니다.
        current_image = self.frames[self.frame_index]
        
        # 이미지 크기가 50x50이므로 정확한 중앙(25, 25)을 빼서 위치를 보정합니다.
        surface.blit(current_image, (screen_pos[0] - 25, screen_pos[1] - 25))

# [신규] 스피릿 소드용 날아가는 검기
class SwordWave:
    def __init__(self, spawn_pos, direction, damage, weapon_id="melee"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        
        self.speed = 14
        self.damage = damage
        self.hit_targets = []
        self.life = 35 # 프레임 수명 (사거리)
        self.weapon_id = weapon_id

        # 💡 [핵심 1] 단일 이미지를 불러옵니다. (파일명 규칙 적용)
        from resource_manager import get_image
        sheet_path = r"assets\Weapon\Melee\Melee_Sheet.png"
        self.base_image = get_image(sheet_path)

        self.timer = 0
        self.history = [] # 잔상 위치를 기억할 리스트

    def update(self):
        # 💡 [핵심 2] 매 프레임마다 현재 위치를 잔상 기록에 남깁니다.
        self.history.append((self.pos.x, self.pos.y))
        if len(self.history) > 4: # 잔상의 길이 (숫자가 클수록 꼬리가 길어짐)
            self.history.pop(0)

        self.pos += self.dir * self.speed
        self.life -= 1
        self.timer += 1
        return self.life <= 0

    def draw(self, surface, cam):
        import math
        
        # 날아가는 방향 각도 계산
        angle = math.degrees(math.atan2(-self.dir.y, self.dir.x))
        
        for i, (hx, hy) in enumerate(self.history):
            screen_pos = (int(hx - cam.x), int(hy - cam.y))
            
            # 과거의 궤적일수록 크기를 점점 작게 만듭니다.
            scale_factor = 0.5 + (i / len(self.history)) * 0.4
            new_w = int(self.base_image.get_width() * scale_factor)
            new_h = int(self.base_image.get_height() * scale_factor)
            
            trail_img = pygame.transform.scale(self.base_image, (new_w, new_h))
            
            # 투명도를 낮춰서 흐릿하게 만듭니다.
            alpha = int(255 * (i / len(self.history)))
            trail_img.set_alpha(alpha // 2)
            
            rotated_trail = pygame.transform.rotate(trail_img, angle)
            rect = rotated_trail.get_rect(center=screen_pos)
            surface.blit(rotated_trail, rect.topleft)

        # ==========================================
        # 2. 본체(Main) 일렁임 그리기
        # ==========================================
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        
        # 💡 [핵심 3] 사인(sin) 함수를 써서 크기를 85% ~ 115% 사이로 엄청 빠르게 요동치게 합니다. 
        # 눈으로 보면 반짝거리며 에너지가 뿜어지는 것처럼 보입니다!
        pulse = 1.0 + math.sin(self.timer * 1.5) * 0.15 
        new_w = int(self.base_image.get_width() * pulse)
        new_h = int(self.base_image.get_height() * pulse)
        
        pulsing_img = pygame.transform.scale(self.base_image, (new_w, new_h))
        rotated_main = pygame.transform.rotate(pulsing_img, angle)
        
        rect_main = rotated_main.get_rect(center=screen_pos)
        surface.blit(rotated_main, rect_main.topleft)

# 👇 weapons.py 맨 아래에 추가
class ThrowingAxe:
    def __init__(self, spawn_pos, direction, damage, weapon_id="axe"):
        self.pos = pygame.math.Vector2(spawn_pos)
        self.dir = pygame.math.Vector2(direction)
        if self.dir.length_squared() == 0: self.dir = pygame.math.Vector2(1, 0)
        
        self.speed = 10
        self.velocity = self.dir.normalize() * self.speed
        self.damage = damage
        self.pierce = 5 # 도끼 특유의 5회 관통력
        self.radius = 12
        self.weapon_id = weapon_id
        
        self.life = 120
        self.hit_targets = []
        self.state = "flying" # 시스템 에러 방지용 상태
        
    def update(self, enemies=None):
        self.pos += self.velocity
        self.life -= 1
        return self.life <= 0

    def hit(self):
        # 도끼는 타격 시 폭발하지 않고 관통력을 소모하며 적을 뚫고 지나갑니다.
        self.pierce -= 1
        if self.pierce <= 0:
            self.life = 0 # 관통력을 다 쓰면 삭제

    def draw(self, surface, cam):
        screen_pos = (int(self.pos.x - cam.x), int(self.pos.y - cam.y))
        pygame.draw.circle(surface, (150, 150, 150), screen_pos, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), screen_pos, self.radius, 2)