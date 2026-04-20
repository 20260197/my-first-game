import base64
import io
import pygame
import random
import sys
import math
from settings import *
from game_objects import *
from utils import *
from base import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shield Dodger: Tactical Laser (Hard Mode)")
    clock = pygame.time.Clock()

    font = get_korean_font(36)
    font_big = get_korean_font(72)

    # --- 이미지 로드 섹션 ---
    # 1. 플레이어 이미지 로드

    enemy_frames = []

    sheet_bytes = base64.b64decode(SHEET_B64)
    player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()
    player_frames = [pygame.transform.scale(player_sheet.subsurface(pygame.Rect(i*8,0,8,8)), (PLAYER_W, PLAYER_H)) for i in range(3)]

    # 2. 적 미사일 스프라이트 시트 로드 및 슬라이싱
    enemy_sheet_bytes = base64.b64decode(ENEMY_MISSILE_B64)
    enemy_sheet_img = pygame.image.load(io.BytesIO(enemy_sheet_bytes)).convert_alpha()
    
    frame_width = 85  
    frame_height = 100 

    # (이미지 로드 섹션 근처)
    display_surf = pygame.Surface((WIDTH, HEIGHT)) # 실제 게임이 그려질 도화지
    
    # 시트의 전체 너비를 프레임 너비로 나누어 프레임 개수 자동 계산
    num_frames = enemy_sheet_img.get_width() // frame_width
    for i in range(num_frames):
        frame = enemy_sheet_img.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        enemy_frames.append(pygame.transform.scale(frame, (ENEMY_W, ENEMY_H)))
    
    large_enemy_frames = [pygame.transform.scale(f, (ENEMY_W * 4, ENEMY_H * 4)) for f in enemy_frames]

    # 튕겨나간 적 효과용 서피스 (이미지가 없을 경우를 대비한 백업)
    enemy_surface = pygame.Surface((ENEMY_W, ENEMY_H), pygame.SRCALPHA)
    pygame.draw.rect(enemy_surface, RED, (0, 0, ENEMY_W, ENEMY_H))

    # 초기 상태 변수
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 100, PLAYER_W, PLAYER_H)
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)

    import os

    # 1. dodger.py 파일의 현재 위치를 구합니다.
    BASE_PATH = os.path.dirname(__file__)

    # 2. 하위 폴더 이름이 'assets'라면 중간에 넣어줍니다.
    # 만약 폴더 이름이 다르다면 "assets" 부분을 실제 이름으로 바꾸세요.
    bgm_dict = {
        0: os.path.join(BASE_PATH, "Assets", "Audio", "First_Second_Phase.mp3"),
        1: os.path.join(BASE_PATH, "Assets", "Audio", "First_Second_Phase.mp3"),
        2: os.path.join(BASE_PATH, "Assets", "Audio", "Third_Fourth_Phase.mp3"),
        3: os.path.join(BASE_PATH, "Assets", "Audio", "Third_Fourth_Phase.mp3"),
        4: os.path.join(BASE_PATH, "Assets", "Audio", "Fifth_Phase.mp3")
    }

    # --- 효과음 로드 섹션 ---
    # 레이저 발사 효과음 경로 (Assets/Audio/ 폴더 내에 파일이 있어야 함)
    laser_sfx_path = os.path.join(BASE_PATH, "Assets", "Audio", "laser_fire.mp3")
    
    try:
        laser_fire_sfx = pygame.mixer.Sound(laser_sfx_path)
        laser_fire_sfx.set_volume(0.4)  # 효과음 볼륨 조절 (0.0 ~ 1.0)
    except pygame.error:
        print("레이저 효과음 파일을 찾을 수 없습니다.")
        laser_fire_sfx = None
    
    current_bgm = None # 현재 재생 중인 음악 파일명 저장

    SCALE_FACTOR = 1.5  # 1.5배 키우기

    # 로드 부분
    new_w = int(frame_width * SCALE_FACTOR)
    new_h = int(frame_height * SCALE_FACTOR)

    current_frame_idx, current_angle, target_angle = 1, 0.0, 0.0
    my_shield = Shield(radius=75)
    enemies, particles, lasers = [], [], []

    # warnings 리스트를 하나 만듭니다.
    warnings = []
    
    score, lives, spawn_timer, invincible = 0, 3, 0, 0
    large_enemy_spawn_timer = 0
    
    dev_mode = False
    god_mode = False

    show_title_screen(screen, font, font_big)
    waiting_for_release = True
    while waiting_for_release:
        pygame.event.pump() # 내부 이벤트 상태 업데이트
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_SPACE]: # 스페이스 바에서 손을 떼면
            waiting_for_release = False
    
    # --- 상태 변수 추가 ---
    show_help = False  # 도움말 화면 표시 여부

    while True:
        clock.tick(FPS)

        level_idx = 0
        for i, t in enumerate(thresholds):
            if score >= t: level_idx = i
        level_idx = min(level_idx, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]
        mode = level_cfg.get("mode", "normal")

        # (기존 레벨 계산 코드 아래에 추가)
        # 현재 레벨에 맞는 음악 파일 가져오기
        target_bgm = bgm_dict.get(level_idx)

        # 현재 재생 중인 곡과 틀어야 할 곡이 다를 때만 실행
        if current_bgm != target_bgm:
            current_bgm = target_bgm
            if target_bgm:
                try:
                    pygame.mixer.music.load(target_bgm)
                    pygame.mixer.music.set_volume(0.5) # 볼륨 조절 (0.0 ~ 1.0)
                    pygame.mixer.music.play(-1)        # -1은 무한 반복
                except pygame.error as e:
                    # 파일이 없거나 형식이 틀려도 게임이 멈추지 않게 처리
                    print(f"음악 로드 실패: {target_bgm} / 에러: {e}")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F1:
                    dev_mode = not dev_mode
                    god_mode = dev_mode
                if dev_mode:
                    if e.key == pygame.K_1: score = 0
                    elif e.key == pygame.K_2: score = 200
                    elif e.key == pygame.K_3: score = 400
                    elif e.key == pygame.K_4: score = 2000
                    elif e.key == pygame.K_5: score = 6000 
                if e.key == pygame.K_h:
                    show_help = not show_help

        # 1. 플레이어 조작
        keys = pygame.key.get_pressed()
        current_frame_idx, target_angle = 1, 0
        move_speed = 8 
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
            player_rect.x -= move_speed
            current_frame_idx, target_angle = 0, 15
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < WIDTH:
            player_rect.x += move_speed
            current_frame_idx, target_angle = 2, -15
            
        if mode in ["laser", "laser_hell"]:
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_rect.top > 0:
                player_rect.y -= move_speed - 1
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_rect.bottom < HEIGHT:
                player_rect.y += move_speed - 1
        else:
            if player_rect.bottom < HEIGHT - 10: player_rect.y += 5

        current_angle += (target_angle - current_angle) * 0.3
        if god_mode: invincible = 2 
        my_shield.update(player_rect.center)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2. 생성 및 소환 로직 (Update)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        
        # (1) 고속 유성 전조 타이머 관리 및 소환
        for warn in warnings[:]:
            warn["timer"] -= 1
            if warn["timer"] <= 0:
                enemies.append(warn["data"]) # 실제 적 리스트로 추가
                warnings.remove(warn)

        # (2) 레이저 생성용 타이머 (기존 spawn_timer)
        should_wait = (mode in ["laser", "laser_hell"] and len(lasers) > 0)
        if not should_wait:
            spawn_timer += 1

        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            if mode == "normal":
                new_enemy = spawn_enemy(level_cfg)
                new_enemy.append(False) # 거대 유성 아님
                if new_enemy[2] >= 10:
                    warnings.append({"x": new_enemy[0].centerx, "timer": 50, "data": new_enemy})
                else:
                    enemies.append(new_enemy)
            
            elif mode == "laser":
                px, py = player_rect.center
                side = random.randint(0, 3)
                if side == 0: origin = [random.randint(0, WIDTH), -50]
                elif side == 1: origin = [random.randint(0, WIDTH), HEIGHT + 50]
                elif side == 2: origin = [-50, random.randint(0, HEIGHT)]
                else: origin = [WIDTH + 50, random.randint(0, HEIGHT)]
                lasers.append({"origin": origin, "target": [px, py], "timer": 45, "timer_start": 45, "state": 1})

            elif mode == "laser_hell":
                # 레이저만 생성 (5페이즈는 2개, 4페이즈는 1개)
                laser_count = 2 if level_idx == 4 else 1
                for _ in range(laser_count):
                    px, py = player_rect.center
                    origin = [random.randint(0, WIDTH), -50 if random.random() > 0.5 else HEIGHT + 50]
                    lasers.append({"origin": origin, "target": [px, py], "timer": 40, "timer_start": 40, "state": 1})

        # (3) 거대 유성 전용 생성 로직 (독립적 타이머)
        if mode == "laser_hell":
            large_enemy_spawn_timer += 1
            # 💡 주기를 60~80 정도로 잡으면 아주 많이 쏟아집니다.
            if large_enemy_spawn_timer >= 80: 
                large_enemy_spawn_timer = 0
                for _ in range(2): # 한 번에 2개씩 생성
                    large_enemy = spawn_enemy(level_cfg)
                    large_enemy[0].width, large_enemy[0].height = ENEMY_W * 4, ENEMY_H * 4
                    large_enemy[1] = random.uniform(-1.5, 1.5) 
                    large_enemy[2] = random.uniform(4, 8)
                    large_enemy.append(True) 
                    enemies.append(large_enemy)

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3. 레이저 로직 (그레이징 및 파티클)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        for laser in lasers[:]:
            start = laser["origin"]
            if laser["state"] == 1:
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    laser["state"] = 2
                    laser["timer"] = 60 

                    if laser_fire_sfx:
                        laser_fire_sfx.play()
                    
                    
            elif laser["state"] == 2:
                laser["timer"] -= 1
                dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
                dist = math.hypot(dx, dy)
                if dist != 0:
                    full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
                    graze_rect = player_rect.inflate(40, 40)
                    if graze_rect.clipline(start, full_end):
                        score += 5

                    clipped = screen_rect.clipline(start, full_end)
                    if clipped:
                        hit_point = clipped[1]
                        for _ in range(8):
                            p = Particle(hit_point[0], hit_point[1], random.choice([WHITE, YELLOW, (255, 100, 0)]), 
                                         size=random.randint(5, 12), lifetime=random.randint(20, 35))
                            p.dx, p.dy = random.uniform(-12, 12), random.uniform(-12, 12)
                            particles.append(p)

                    if invincible <= 0 and player_rect.clipline(start, full_end):
                        lives -= 1; invincible = 90; lasers.clear()
                        if lives <= 0:
                            if game_over_screen(screen, font, font_big, score): main()
                            return
                if laser["timer"] <= 0:
                    lasers.remove(laser); score += 100

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4. 미사일/파티클 업데이트 (화염 꼬리 및 유도 로직)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        alive_enemies, hit_enemies = [], set()
        CYAN = (0, 255, 255)

        # (1) 파티클 업데이트
        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)

        # (2) 미사일 로직 통합 루프
        for i, en_data in enumerate(enemies):
            # 0:rect, 1:dx, 2:dy, 3:is_def, 4:angle, 5:rot_speed, 6:bounce_delay, 7:life
            rect, dx, dy, is_def, angle, rot_speed, bounce_delay, life = en_data[:8]

            if is_def:
                # 🔵 [튕겨나간 상태] 푸른색 불꽃 꼬리
                en_data[7] -= 1
                if en_data[7] <= 0:
                    for _ in range(5): particles.append(Particle(rect.centerx, rect.centery, (100, 200, 255), size=2))
                    continue 

                for _ in range(6): 
                    p = Particle(rect.centerx, rect.centery, (100, 200, 255), size=random.randint(2, 4), lifetime=20)
                    p.dx += random.uniform(-1, 1)
                    p.dy += random.uniform(-1, 1)
                    particles.append(p)

                en_data[4] += rot_speed 

                if en_data[6] > 0: 
                    en_data[6] -= 1
                    en_data[2] += 0.3 
                    en_data[1] *= 0.96 
                else:
                    # 🎯 유도(Homing) 타겟 탐색
                    curr_pos = pygame.math.Vector2(rect.center)
                    target = None
                    min_dist = 9999
                    for j, other in enumerate(enemies):
                        if i != j and not other[3] and j not in hit_enemies:
                            d = curr_pos.distance_to(other[0].center)
                            if d < min_dist: min_dist, target = d, other
                    
                    if target:
                        target_pos = pygame.math.Vector2(target[0].center)
                        current_vel = pygame.math.Vector2(en_data[1], en_data[2])
                        desired = (target_pos - curr_pos).normalize() * 24.0 
                        steering = (desired - current_vel) * 0.2 
                        new_vel = current_vel + steering
                        if new_vel.length() > 0:
                            new_vel.scale_to_length(min(27, current_vel.length() + 0.4))
                        en_data[1], en_data[2] = new_vel.x, new_vel.y

                # 💥 적끼리의 충돌 체크
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies:
                        if rect.colliderect(other[0]):
                            hit_enemies.add(i); hit_enemies.add(j)
                            score += 50
                            for _ in range(50):
                                p = Particle(rect.centerx, rect.centery, random.choice([WHITE, YELLOW, CYAN]))
                                p.dx, p.dy = random.uniform(-8, 8), random.uniform(-8, 8) 
                                particles.append(p)
                            break
            
            else:
                # 🔥 [일반 상태] 화염 꼬리 로직
                is_large = en_data[8] if len(en_data) > 8 else False

                if is_large:
                    # ☄️ 4~6배 거대 유성 전용 웅장한 화염
                    # 유성이 커진 만큼 파티클을 더 많이 생성 (한 프레임당 6~10개)
                    if random.random() > 0.1: 
                        for _ in range(random.randint(6, 10)):
                            # 1. 꼬리 너비: 유성 너비의 80% 범위에서 랜덤하게 발생
                            # rect.width가 이미 4~6배 커진 상태이므로 이를 활용합니다.
                            half_w = rect.width // 2
                            px = rect.centerx + random.uniform(-half_w * 0.8, half_w * 0.8)
                            
                            # 2. 꼬리 높이: 유성 위쪽(꽁무니)에서 약간 안쪽으로 들어온 지점
                            # 유성이 커진 만큼 offset도 키워야 합니다 (예: 너비의 10% 지점)
                            py = rect.top + (rect.height * 0.1)
                            
                            fire_color = random.choice([(255, 180, 0), (255, 50, 0), (200, 20, 0)])
                            
                            # 3. 파티클 크기: 유성 크기에 맞춰 대폭 키움 (8~18 사이)
                            p_size = random.randint(8, 18)
                            
                            # 4. 생존 시간: 꼬리가 더 길게 남도록 30~50프레임 설정
                            p_lifetime = random.randint(30, 50)
                            
                            p = Particle(px, py, fire_color, size=p_size, lifetime=p_lifetime)
                            
                            # 5. 퍼지는 정도: 유성이 크므로 옆으로도 더 많이 퍼지게 설정
                            p.dx = random.uniform(-4, 4)
                            p.dy = -random.uniform(3, 7) # 더 빠르게 위로 솟구침
                            particles.append(p)
                else:
                    # 🎈 일반 유성 꼬리 (기존 로직)
                    if random.random() > 0.4:
                        for _ in range(2):
                            px = rect.centerx + random.uniform(-8, 8)
                            py = rect.top + 10
                            fire_color = random.choice([(255, 220, 0), (255, 100, 0), (255, 40, 0)])
                            p = Particle(px, py, fire_color, size=random.randint(2, 4), lifetime=15)
                            p.dx = random.uniform(-0.5, 0.5)
                            p.dy = -random.uniform(1, 3)
                            particles.append(p)

        # (3) 이동 적용 및 플레이어 충돌 판정
        if invincible > 0: invincible -= 1
        
        collision_event = False
        for i, en_data in enumerate(enemies):
            if i in hit_enemies: continue
            
            # 실제 좌표 이동
            en_data[0].x += en_data[1]
            en_data[0].y += en_data[2]
            
            # 쉴드 충돌 체크 (튕겨나가지 않은 적만)
            my_shield.check_collision(en_data)
            
            # 플레이어 충돌 (무적 아님 + 튕겨나가지 않은 적)
            if invincible <= 0 and not en_data[3]:
                if player_rect.colliderect(en_data[0]):
                    lives -= 1; invincible = 90; enemies.clear(); lasers.clear()
                    collision_event = True
                    if lives <= 0:
                        if game_over_screen(screen, font, font_big, score): main()
                        return
                    break
            
            # 화면 밖 처리
            r = en_data[0]
            if r.top > HEIGHT + 150 or r.bottom < -150 or r.left < -150 or r.right > WIDTH + 150:
                if not en_data[3] and r.top > HEIGHT: score += 5
                continue
            alive_enemies.append(en_data)

        if not collision_event:
            enemies = alive_enemies

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. 그리기 (Drawing)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1. 도화지 초기화
        display_surf.fill(BLACK)

        # 2. HUD 및 개발자 모드 표시
        draw_hud(display_surf, font, score, LEVELS[level_idx], lives)
        if dev_mode:
            dev_text = font.render("DEV MODE (GOD): ON", True, (0, 255, 0))
            display_surf.blit(dev_text, (WIDTH // 2 - dev_text.get_width() // 2, 10))

        # 3. 고속 유성 전조 표시 (출력만 담당)
        for warn in warnings:
            # 붉은색 세로 궤적
            warn_rect_surf = pygame.Surface((10, HEIGHT), pygame.SRCALPHA)
            alpha = 100 if (pygame.time.get_ticks() // 150) % 2 == 0 else 30
            pygame.draw.rect(warn_rect_surf, (255, 0, 0, alpha), (0, 0, 10, HEIGHT))
            display_surf.blit(warn_rect_surf, (warn["x"] - 5, 0))
            
            # 상단 경고 아이콘
            warn_icon = font.render("!", True, RED)
            display_surf.blit(warn_icon, (warn["x"] - warn_icon.get_width()//2, 5))

        # 4. 파티클 및 쉴드 그리기
        for p in particles:
            p.draw(display_surf)
        my_shield.draw(display_surf)

        # 5. 플레이어 프레임 (Left=0 / Idle=1 / Right=2)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            p_idx = 0  # 왼쪽 프레임
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            p_idx = 2  # 오른쪽 프레임
        else:
            p_idx = 1  # 중앙(Idle) 프레임

        rot_player = pygame.transform.rotate(player_frames[p_idx], current_angle)
        display_surf.blit(rot_player, rot_player.get_rect(center=player_rect.center))

        # 6. 레이저 그리기 (화면 끝까지 연장 및 각도 동기화)
        for laser in lasers:
            start, target = laser["origin"], laser["target"]
            dx, dy = target[0] - start[0], target[1] - start[1]
            dist = math.hypot(dx, dy)
            if dist == 0: continue
            
            # 실제 레이저가 발사될 최종 끝점 (3000px)
            full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]

            if laser["state"] == 1:
                # [전조] 점점 차오르는 보라색 가이드 빔
                laser_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                progress = 1.0 - (laser["timer"] / laser["timer_start"])
                
                # 💡 전조 끝점도 3000px 기준으로 채워야 각도/거리에 상관없이 정확히 발사 시점에 끝에 도달합니다.
                current_end = [
                    start[0] + (dx/dist) * 3000 * progress, 
                    start[1] + (dy/dist) * 3000 * progress
                ]
                
                warn_alpha = 120
                f_color = (255, 0, 255, warn_alpha) if (pygame.time.get_ticks() // 80) % 2 == 0 else (128, 0, 128, warn_alpha)
                pygame.draw.line(laser_surf, f_color, start, current_end, 15) # 두께 약간 조절
                pygame.draw.line(laser_surf, (200, 200, 255, warn_alpha), start, current_end, 3)
                display_surf.blit(laser_surf, (0, 0))

            elif laser["state"] == 2:
                # [발사] 붉은색 메인 광선
                for color, width in [((150, 0, 0), 26), ((255, 50, 50), 18), ((255, 150, 50), 10), ((255, 255, 255), 4)]:
                    pygame.draw.line(display_surf, color, start, full_end, width)

        # 7. 적(유성/거대유성) 그리기
        for en_data in enemies:
            rect, _, _, is_def, angle = en_data[0:5]
            # 인덱스 범위를 고려하여 마지막 값으로 대형 여부 판단
            is_large = en_data[-1] if len(en_data) > 8 else False
            
            curr_frames = large_enemy_frames if is_large else enemy_frames
            idx = (pygame.time.get_ticks() // 100) % len(curr_frames)
            img = curr_frames[idx]

            if is_def:
                rot_en = pygame.transform.rotate(img, angle)
                display_surf.blit(rot_en, rot_en.get_rect(center=rect.center))
            else:
                display_surf.blit(img, img.get_rect(center=rect.center))

        # 8. 스크린 쉐이크 및 최종 화면 출력
        shake_offset = [0, 0]
        is_firing = any(l["state"] == 2 for l in lasers)
        # 거대 유성 존재 여부 확인
        is_boss = any(en[-1] for en in enemies if len(en) > 8)

        if is_firing or is_boss:
            intensity = 4 if is_firing else 2
            shake_offset = [random.randint(-intensity, intensity), random.randint(-intensity, intensity)]
            
        if show_help:
            # 반투명 검은색 배경 상자
            help_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(help_surf, (0, 0, 0, 180), (50, 50, WIDTH-100, HEIGHT-100))
            display_surf.blit(help_surf, (0, 0))

            # 도움말 텍스트 내용
            help_title = font_big.render("HOW TO PLAY", True, (255, 255, 0))
            controls = [
                "이동: 방향키 (↑↓←→) 또는 WASD",
                "쉴드: 플레이어 주변에 자동 활성화 (유성 튕겨내기)",
                "",
                "★ 보너스 점수 ★",
                "레이저가 발사될 때 궤적 근처에 있으면",
                "근접 보너스(Grazing) 점수를 추가로 획득합니다!",
                "",
                "[ H 키를 눌러 게임으로 돌아가기 ]"
            ]

            # 텍스트 출력 위치 계산
            display_surf.blit(help_title, (WIDTH//2 - help_title.get_width()//2, 100))
            for i, line in enumerate(controls):
                text_surf = font.render(line, True, (255, 255, 255))
                display_surf.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, 220 + i * 45))
        
        screen.fill(BLACK)
        screen.blit(display_surf, (shake_offset[0], shake_offset[1]))
        pygame.display.flip()

if __name__ == "__main__":
    main()