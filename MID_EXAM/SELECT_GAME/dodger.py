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
    sheet_bytes = base64.b64decode(SHEET_B64)
    player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()
    player_frames = [pygame.transform.scale(player_sheet.subsurface(pygame.Rect(i*8,0,8,8)), (PLAYER_W, PLAYER_H)) for i in range(3)]

    # 2. 적 미사일 스프라이트 시트 로드 및 슬라이싱
    enemy_sheet_bytes = base64.b64decode(ENEMY_MISSILE_B64)
    enemy_sheet_img = pygame.image.load(io.BytesIO(enemy_sheet_bytes)).convert_alpha()
    
    enemy_frames = []
    frame_width = 85  
    frame_height = 100 
    
    # 시트의 전체 너비를 프레임 너비로 나누어 프레임 개수 자동 계산
    num_frames = enemy_sheet_img.get_width() // frame_width
    for i in range(num_frames):
        # subsurface로 각 프레임을 잘라낸 후 settings의 ENEMY_W, ENEMY_H 크기로 조절
        frame = enemy_sheet_img.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
        enemy_frames.append(pygame.transform.scale(frame, (ENEMY_W, ENEMY_H)))
    
    # 튕겨나간 적 효과용 서피스 (이미지가 없을 경우를 대비한 백업)
    enemy_surface = pygame.Surface((ENEMY_W, ENEMY_H), pygame.SRCALPHA)
    pygame.draw.rect(enemy_surface, RED, (0, 0, ENEMY_W, ENEMY_H))

    # 초기 상태 변수
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 100, PLAYER_W, PLAYER_H)
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    
    current_frame_idx, current_angle, target_angle = 1, 0.0, 0.0
    my_shield = Shield(radius=75)
    enemies, particles, lasers = [], [], []
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

        # 2. 생성 로직
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            if mode == "normal":
                enemies.append(spawn_enemy(level_cfg))
            elif mode in ["laser", "laser_hell"]:
                spawn_count = 2 if mode == "laser_hell" else 1
                for _ in range(spawn_count):
                    px, py = player_rect.center
                    offset = 500
                    side = random.randint(0, 3)
                    if side == 0: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), -50]
                    elif side == 1: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), HEIGHT + 50]
                    elif side == 2: origin = [-50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    else: origin = [WIDTH + 50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    
                    lasers.append({
                        "origin": origin, 
                        "target": list(player_rect.center), 
                        "timer": 45, "timer_start": 45, "state": 1
                    })

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
        # 4. 미사일/파티클 업데이트 (통합 및 최적화)
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
                # 생존 시간 관리 (여기서만 깎음)
                en_data[7] -= 1
                if en_data[7] <= 0:
                    for _ in range(5): particles.append(Particle(rect.centerx, rect.centery, (100, 200, 255), size=2))
                    continue # 소멸

                # 확률 체크를 없애고 반복문을 넣습니다.
                for _ in range(3): # 숫자를 키울수록 꼬리가 길고 진해집니다.
                    p = Particle(rect.centerx, rect.centery, (100, 200, 255), size=random.randint(2, 4), lifetime=20)
                    # 꼬리가 퍼지도록 살짝의 랜덤 속도를 줍니다.
                    p.dx += random.uniform(-1, 1)
                    p.dy += random.uniform(-1, 1)
                    particles.append(p)

                en_data[4] += rot_speed # 회전 애니메이션

                if en_data[6] > 0: # 튕김 지연 (대기 시간)
                    en_data[6] -= 1
                    en_data[2] += 0.3 # 중력
                    en_data[1] *= 0.96 # 공기 저항
                else:
                    # 🎯 유도(Homing) 타겟 탐색
                    curr_pos = pygame.math.Vector2(rect.center)
                    target = None
                    min_dist = 9999
                    
                    for j, other in enumerate(enemies):
                        if i != j and not other[3] and j not in hit_enemies:
                            d = curr_pos.distance_to(other[0].center)
                            if d < min_dist:
                                min_dist, target = d, other
                    
                    if target:
                        # 조향(Steering) 물리 적용
                        target_pos = pygame.math.Vector2(target[0].center)
                        current_vel = pygame.math.Vector2(en_data[1], en_data[2])
                        desired = (target_pos - curr_pos).normalize() * 24.0 # 목표 속도
                        steering = (desired - current_vel) * 0.2 # 회전 민감도 (0.1~0.2 권장)
                        new_vel = current_vel + steering
                        
                        # 가속 및 속도 제한
                        if new_vel.length() > 0:
                            new_vel.scale_to_length(min(27, current_vel.length() + 0.4))
                        en_data[1], en_data[2] = new_vel.x, new_vel.y

                # 💥 적끼리의 충돌 체크
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies:
                        if rect.colliderect(other[0]):
                            hit_enemies.add(i); hit_enemies.add(j)
                            score += 50
                            for _ in range(50): # 50개 정도로 늘리면 훨씬 화려합니다.
                                p = Particle(rect.centerx, rect.centery, random.choice([WHITE, YELLOW, CYAN]))
                                # 파편이 더 멀리 퍼지도록 dx, dy 범위를 넓혀주면 더 좋습니다.
                                p.dx, p.dy = random.uniform(-8, 8), random.uniform(-8, 8) 
                                particles.append(p)
                            break

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

        # 5. 그리기 섹션
        screen.fill((20, 20, 40))
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

        # 💡 적 미사일 그리기 (애니메이션 적용)
        for en_data in enemies:
            rect, _, _, is_def, angle, _, _, _ = en_data[:8]
            
            # 현재 시간에 따른 프레임 인덱스 계산 (100ms마다 프레임 전환)
            current_idx = (pygame.time.get_ticks() // 100) % len(enemy_frames)
            current_frame = enemy_frames[current_idx]

            if is_def:
                # 튕겨나간 상태일 때는 현재 애니메이션 프레임을 회전시켜 출력
                rot_en = pygame.transform.rotate(current_frame, angle)
                screen.blit(rot_en, rot_en.get_rect(center=rect.center).topleft)
            else:
                # 정상적으로 떨어지는 적 애니메이션 출력
                screen.blit(current_frame, rect)

        if dev_mode:
            dev_surf = font.render(f"DEV | GOD: {god_mode}", True, (0, 255, 0))
            screen.blit(dev_surf, (WIDTH // 2 - dev_surf.get_width() // 2, 10))

        draw_hud(screen, font, score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()