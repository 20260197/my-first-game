import base64
import io
import pygame
import random
import sys
import math
from settings import *
from game_objects import Shield, Particle
from utils import get_korean_font, spawn_enemy, draw_hud, game_over_screen
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

    thresholds = [0, 500, 1000, 1500, 4500]
    dev_mode = False
    god_mode = False

    while True:
        clock.tick(FPS)

        level_idx = 0
        for i, t in enumerate(thresholds):
            if score >= t: level_idx = i
        level_idx = min(level_idx, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]
        mode = level_cfg.get("mode", "normal")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F1:
                    dev_mode = not dev_mode
                    god_mode = dev_mode
                if dev_mode:
                    if e.key == pygame.K_1: score = 0
                    elif e.key == pygame.K_2: score = 500
                    elif e.key == pygame.K_3: score = 1000
                    elif e.key == pygame.K_4: score = 1500
                    elif e.key == pygame.K_5: score = 4500 

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
        # 2. 생성 로직 (3: 레이저1 / 4: 레이저1+유성 / 5: 레이저2+유성)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        should_wait = False
        # 레이저가 화면에 하나라도 있으면 타이머 중지 (발사 간격 유지)
        if mode in ["laser", "laser_hell"] and len(lasers) > 0:
            should_wait = True

        if not should_wait:
            spawn_timer += 1

        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            
            # (1) 1, 2페이즈: 일반 및 고속 미사일
            if mode == "normal":
                new_enemy = spawn_enemy(level_cfg)
                new_enemy.append(False) # 거대 유성 아님
                if new_enemy[2] >= 10:
                    warnings.append({"x": new_enemy[0].centerx, "timer": 50, "data": new_enemy})
                else:
                    enemies.append(new_enemy)
            
            # (2) 3페이즈: 레이저 1개만 발사
            elif mode == "laser":
                px, py = player_rect.center
                offset = 500
                side = random.randint(0, 3)
                if side == 0: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), -50]
                elif side == 1: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), HEIGHT + 50]
                elif side == 2: origin = [-50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                else: origin = [WIDTH + 50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                
                lasers.append({
                    "origin": origin, "target": [px, py], 
                    "timer": 45, "timer_start": 45, "state": 1
                })

            # (3) 4, 5페이즈: 레이저 헬 (하이브리드)
            elif mode == "laser_hell":
                laser_count = 2 if level_idx == 4 else 1
                for _ in range(laser_count):
                    px, py = player_rect.center
                    offset = 500
                    side = random.randint(0, 3)
                
                # 1. 레이저 생성
                for _ in range(laser_count):
                    px, py = player_rect.center
                    offset = 500
                    side = random.randint(0, 3)
                    if side == 0: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), -50]
                    elif side == 1: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), HEIGHT + 50]
                    elif side == 2: origin = [-50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    else: origin = [WIDTH + 50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    
                    lasers.append({
                        "origin": origin, "target": [px, py], 
                        "timer": 40, "timer_start": 40, "state": 1
                    })
                
                # ☄️ 거대 유성 생성 및 설정
                large_enemy = spawn_enemy(level_cfg)
                
                # 1. 히트박스 크기를 이미지 배율(4배)에 맞춰 수정
                large_enemy[0].width = ENEMY_W * 4
                large_enemy[0].height = ENEMY_H * 4
                
                # 2. 비스듬하게 떨어지도록 dx 설정 (-2 ~ 2 사이의 랜덤값)
                large_enemy[1] = random.uniform(-1.5, 1.5) 
                
                # 3. 낙하 속도는 여전히 느리게 (2 ~ 4)
                large_enemy[2] = random.uniform(2, 4)
                
                large_enemy.append(True) # 거대 유성 플래그
                enemies.append(large_enemy)

        # 3. 레이저 로직 (그레이징 및 파티클)
        for laser in lasers[:]:
            start = laser["origin"]
            if laser["state"] == 1:
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    laser["state"] = 2
                    laser["timer"] = 60 
            elif laser["state"] == 2:
                laser["timer"] -= 1
                dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
                dist = math.hypot(dx, dy)
                if dist != 0:
                    full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
                    graze_rect = player_rect.inflate(40, 40)
                    if graze_rect.clipline(start, full_end):
                        score += 1 

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
                            p.dx = random.uniform(-2, 2)
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
                if not en_data[3] and r.top > HEIGHT: score += 1
                continue
            alive_enemies.append(en_data)

        if not collision_event:
            enemies = alive_enemies

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. 그리기 섹션
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        screen.fill((20, 20, 40))

        # 💡 [추가] 전조(Warning) 업데이트 및 궤적 그리기
        for w in warnings[:]:
            w["timer"] -= 1 # 타이머 감소
            
            # (1) 전조 궤적 그리기 (타이머가 15프레임 이상 남았을 때만)
            if w["timer"] > 15:
                # 얇은 2px 선, 깜빡이는 투명도 적용
                alpha = 100 if (pygame.time.get_ticks() // 100) % 2 == 0 else 40
                line_surf = pygame.Surface((2, HEIGHT), pygame.SRCALPHA)
                line_surf.fill((255, 50, 50, alpha))
                screen.blit(line_surf, (w["x"] - 1, 0))
            
            # (2) 시간이 다 되면 실제 적 리스트로 이동 (생성)
            if w["timer"] <= 0:
                enemies.append(w["data"])
                warnings.remove(w)
        
        my_shield.draw(screen)
        
        for p in particles: p.draw(screen)

        # 레이저 그리기
        for laser in lasers:
            start = laser["origin"]
            dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
            dist = math.hypot(dx, dy)
            if dist == 0: continue
            full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
            if laser["state"] == 1:
                progress = 1.0 - (laser["timer"] / laser["timer_start"])
                pygame.draw.line(screen, (50, 0, 50), start, full_end, 2)
                current_end = [start[0] + (full_end[0] - start[0]) * progress, start[1] + (full_end[1] - start[1]) * progress]
                flash_color = (255, 0, 255) if (pygame.time.get_ticks() // 80) % 2 == 0 else (128, 0, 128)
                pygame.draw.line(screen, flash_color, start, current_end, 22)
                pygame.draw.line(screen, (200, 200, 255), start, current_end, 4)
            elif laser["state"] == 2:
                for color, width in [((150, 0, 0), 26), ((255, 50, 50), 18), ((255, 150, 50), 10), ((255, 255, 255), 4)]:
                    pygame.draw.line(screen, color, start, full_end, width)

        # 플레이어 그리기
        if (invincible // 10) % 2 == 0:
            img = player_frames[current_frame_idx]
            rot_img = pygame.transform.rotate(img, int(current_angle / 5) * 5)
            screen.blit(rot_img, rot_img.get_rect(center=player_rect.center))

        # 💡 적 미사일 그리기 섹션
        for en_data in enemies:
            rect, _, _, is_def, angle = en_data[0:5]
            is_large = en_data[-1] if len(en_data) > 8 else False
            anim_base = pygame.time.get_ticks() // 100

            # 프레임 선택
            if is_large and large_enemy_frames:
                idx = anim_base % len(large_enemy_frames)
                curr_frame = large_enemy_frames[idx]
            else:
                idx = anim_base % len(enemy_frames)
                curr_frame = enemy_frames[idx]

            # 💡 위치 수정 포인트: 
            # 단순히 rect 위치에 그리는 대신, 이미지의 중심을 히트박스(rect)의 중심에 맞춤
            if is_def:
                rot_en = pygame.transform.rotate(curr_frame, angle)
                screen.blit(rot_en, rot_en.get_rect(center=rect.center))
            else:
                # 일반 낙하 상태에서도 중심을 맞춰야 이미지가 튀지 않습니다.
                screen.blit(curr_frame, curr_frame.get_rect(center=rect.center))

            if is_large:
                # 💡 리스트가 비어있지 않은지 확인 후, 자신의 길이에 맞춰 인덱스 계산
                if large_enemy_frames:
                    idx = anim_base % len(large_enemy_frames)
                    curr_frame = large_enemy_frames[idx]
                else:
                    # 혹시라도 리스트가 비어있다면 일반 프레임이라도 사용 (에러 방지)
                    idx = anim_base % len(enemy_frames)
                    curr_frame = enemy_frames[idx]
            else:
                idx = anim_base % len(enemy_frames)
                curr_frame = enemy_frames[idx]

            # 그리기 로직 (동일)
            if is_def:
                rot_en = pygame.transform.rotate(curr_frame, angle)
                screen.blit(rot_en, rot_en.get_rect(center=rect.center).topleft)
            else:
                screen.blit(curr_frame, rect)

        if dev_mode:
            dev_surf = font.render(f"DEV | GOD: {god_mode}", True, (0, 255, 0))
            screen.blit(dev_surf, (WIDTH // 2 - dev_surf.get_width() // 2, 10))

        draw_hud(screen, font, score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()