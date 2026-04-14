import base64
import io
import pygame
import random
import sys
import math
from settings import *
from game_objects import Shield, Particle
from utils import get_korean_font, spawn_enemy, draw_hud, game_over_screen
from base import SHEET_B64

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shield Dodger: Tactical Laser (Hard Mode)")
    clock = pygame.time.Clock()
    
    font = get_korean_font(36)
    font_big = get_korean_font(72)

    # 이미지 로드
    sheet_bytes = base64.b64decode(SHEET_B64)
    player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()
    player_frames = [pygame.transform.scale(player_sheet.subsurface(pygame.Rect(i*8,0,8,8)), (PLAYER_W, PLAYER_H)) for i in range(3)]
    
    enemy_surface = pygame.Surface((ENEMY_W, ENEMY_H), pygame.SRCALPHA)
    pygame.draw.rect(enemy_surface, RED, (0, 0, ENEMY_W, ENEMY_H))

    # 초기 상태 변수
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 100, PLAYER_W, PLAYER_H)
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    
    current_frame_idx, current_angle, target_angle = 1, 0.0, 0.0
    my_shield = Shield(radius=75)
    enemies, particles, lasers = [], [], []
    score, lives, spawn_timer, invincible = 0, 3, 0, 0

    dev_mode = False
    god_mode = False

    while True:
        clock.tick(FPS)
        level_idx = min(score // 300, len(LEVELS) - 1)
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
                    elif e.key == pygame.K_5: score = 4500 # 💡 Lv.5 점프 추가

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
            
        if mode in["laser" , "laser_hell"] :
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_rect.top > 0:
                player_rect.y -= move_speed - 1
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_rect.bottom < HEIGHT:
                player_rect.y += move_speed - 1
        else:
            if player_rect.bottom < HEIGHT - 10: player_rect.y += 5

        current_angle += (target_angle - current_angle) * 0.3
        if god_mode: invincible = 2 
        my_shield.update(player_rect.center)

        # 2. 생성 로직 (페이즈 5: 멀티 레이저 대응)
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            
            if mode == "normal":
                enemies.append(spawn_enemy(level_cfg))
                
            elif mode in ["laser", "laser_hell"]:
                # 💡 페이즈 5일 경우 반복 횟수를 2로 설정
                spawn_count = 2 if mode == "laser_hell" else 1
                
                for _ in range(spawn_count):
                    px, py = player_rect.center
                    offset = 500 # 넓은 해상도를 고려해 오차 범위를 조금 늘림
                    
                    side = random.randint(0, 3)
                    if side == 0: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), -50]
                    elif side == 1: origin = [max(0, min(WIDTH, px + random.randint(-offset, offset))), HEIGHT + 50]
                    elif side == 2: origin = [-50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    else: origin = [WIDTH + 50, max(0, min(HEIGHT, py + random.randint(-offset, offset)))]
                    
                    # 💡 각 레이저가 서로 다른 타이밍에 발사되도록 타이머에 랜덤 변수 추가 가능
                    # 여기서는 동시에 조준을 시작하도록 설정했습니다.
                    lasers.append({
                        "origin": origin, 
                        "target": list(player_rect.center), 
                        "timer": 45,       # 조준 시간 (살짝 여유를 줌)
                        "timer_start": 45, 
                        "state": 1
                    })

        # 3. 레이저 로직
        for laser in lasers[:]:
            start = laser["origin"]
            if laser["state"] == 1: # 전조 단계
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    laser["state"] = 2
                    laser["timer"] = 60 
            
            elif laser["state"] == 2: # 실제 발사 단계
                laser["timer"] -= 1
                
                # 💡 [추가] 스치기 점수 (Grazing) 로직
                # 레이저의 시작점(start)과 끝점(full_end) 사이의 직선과 플레이어 사이의 거리를 체크
                start = laser["origin"]
                dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
                dist = math.hypot(dx, dy)
                if dist != 0:
                    full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
                    
                    # 플레이어(player_rect.center)가 레이저 선에 얼마나 가까운지 계산
                    # 복잡한 거리 공식 대신 clipline의 범위를 살짝 넓혀서 체크하는 꼼수를 쓸 수 있습니다.
                    # 플레이어 히트박스보다 조금 더 큰 가상의 범위를 설정
                    graze_rect = player_rect.inflate(40, 40) # 40픽셀 정도 여유 공간
                    if graze_rect.clipline(start, full_end):
                        score += 1 # 매 프레임 스치기 점수 추가 (빠르게 올라감)

                if laser["timer"] <= 0:
                    lasers.remove(laser)
                    # 💡 [추가] 생존 점수: 레이저가 무사히 사라졌을 때 보상
                    score += 100 
                    continue
                
                dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
                dist = math.hypot(dx, dy)
                if dist != 0:
                    full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
                    clipped = screen_rect.clipline(start, full_end)
                    if clipped:
                        hit_point = clipped[1]
                        for _ in range(8):
                            spark_color = random.choice([WHITE, YELLOW, (255, 200, 100), (255, 100, 0)])
                            p = Particle(hit_point[0], hit_point[1], spark_color, 
                                         size=random.randint(5, 12), 
                                         lifetime=random.randint(20, 35))
                            p.dx = random.uniform(-12, 12)
                            p.dy = random.uniform(-12, 12)
                            particles.append(p)

                    if invincible <= 0:
                        if player_rect.clipline(start, full_end):
                            lives -= 1
                            invincible = 90
                            lasers.clear()
                            if lives <= 0:
                                if game_over_screen(screen, font, font_big, score): main()
                                return

        # 4. 미사일/파티클 업데이트 (기존 유지)
        alive_enemies, hit_enemies = [], set()
        for i, en_data in enumerate(enemies):
            if en_data[3]: 
                if en_data[6] > 0:
                    en_data[6] -= 1; en_data[2] += GRAVITY
                    en_data[1] *= 0.96; en_data[2] *= 0.96
                else:
                    curr_pos = pygame.math.Vector2(en_data[0].center)
                    if len(en_data) < 9: en_data.append(None)
                    if len(en_data) < 10: en_data.append(0.0)
                    target = en_data[8]
                    if target is None or target not in enemies:
                        max_d, new_t = -1, None
                        for o in enemies:
                            if not o[3]:
                                d = curr_pos.distance_to(o[0].center)
                                if d > max_d: max_d, new_t = d, o
                        en_data[8] = target = new_t
                    if target:
                        en_data[9] = min(en_data[9] + 0.5, 22.0)
                        desired = (pygame.math.Vector2(target[0].center) - curr_pos).normalize() * en_data[9]
                        new_vel = pygame.math.Vector2(en_data[1], en_data[2]).lerp(desired, 0.15)
                        if new_vel.length() > 0: new_vel.scale_to_length(en_data[9])
                        en_data[1], en_data[2] = new_vel.x, new_vel.y
                        if random.random() > 0.4:
                            particles.append(Particle(en_data[0].centerx, en_data[0].centery, (255, 180, 50), 3, 15))

        for i, en_data in enumerate(enemies):
            if i in hit_enemies: continue
            rect, dx, dy, is_def, angle, rot_speed, _, missile_life = en_data[:8]
            rect.x += dx; rect.y += dy
            if is_def:
                en_data[7] -= 1
                if en_data[7] <= 0: continue
                en_data[4] += rot_speed
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies and rect.colliderect(other[0]):
                        hit_enemies.add(i); hit_enemies.add(j); score += 50
                        for _ in range(12): particles.append(Particle(rect.centerx, rect.centery, YELLOW))
            my_shield.check_collision(en_data)
            if rect.top > HEIGHT + 100 or rect.bottom < -100 or rect.left < -100 or rect.right > WIDTH + 100:
                if not is_def and rect.top > HEIGHT: score += 1
                continue
            if i not in hit_enemies: alive_enemies.append(en_data)
        enemies = alive_enemies

        for p in particles[:]:
            p.update()
            if p.lifetime <= 0: particles.remove(p)

        if invincible > 0: invincible -= 1
        else:
            for en_data in enemies:
                if not en_data[3] and player_rect.colliderect(en_data[0]):
                    lives -= 1; invincible = 90; enemies.clear(); lasers.clear()
                    if lives <= 0:
                        if game_over_screen(screen, font, font_big, score): main()
                        return
                    break

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 5. 그리기 섹션
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        screen.fill((20, 20, 40))
        my_shield.draw(screen)
        for p in particles: p.draw(screen)

        for laser in lasers:
            start = laser["origin"]
            dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
            dist = math.hypot(dx, dy)
            if dist == 0: continue
            
            # 레이저의 최종 도달 지점 계산
            full_end = [start[0] + (dx/dist) * 3000, start[1] + (dy/dist) * 3000]
            
            if laser["state"] == 1: # 💡 전조 단계: 게이지 충전 연출 적용
                # 진행률 계산 (0.0 ~ 1.0)
                progress = 1.0 - (laser["timer"] / laser["timer_start"])
                
                # 배경 가이드 라인 (어두운 보라색으로 미리 경로 표시)
                pygame.draw.line(screen, (50, 0, 50), start, full_end, 2)
                
                # 현재 게이지 끝점 계산
                current_end = [
                    start[0] + (full_end[0] - start[0]) * progress,
                    start[1] + (full_end[1] - start[1]) * progress
                ]
                
                # 게이지 그리기 (두껍게)
                flash_color = (255, 0, 255) if (pygame.time.get_ticks() // 80) % 2 == 0 else (128, 0, 128)
                pygame.draw.line(screen, flash_color, start, current_end, 22) 
                pygame.draw.line(screen, (200, 200, 255), start, current_end, 4)       
            
            elif laser["state"] == 2: # 발사 단계 (그라데이션 효과)
                gradient_colors = [
                    ((150, 0, 0), 26),   
                    ((255, 50, 50), 18),  
                    ((255, 150, 50), 10), 
                    ((255, 255, 255), 4)  
                ]
                for color, width in gradient_colors:
                    pygame.draw.line(screen, color, start, full_end, width)

        if (invincible // 10) % 2 == 0:
            img = player_frames[current_frame_idx]
            rot_img = pygame.transform.rotate(img, int(current_angle / 5) * 5)
            screen.blit(rot_img, rot_img.get_rect(center=player_rect.center))

        for en_data in enemies:
            rect, _, _, is_def, angle, _, _, missile_life = en_data[:8]
            if is_def:
                color_surf = enemy_surface.copy()
                if en_data[6] <= 0: pygame.draw.rect(color_surf, YELLOW, (0, 0, ENEMY_W, ENEMY_H), 1)
                rot_en = pygame.transform.rotate(color_surf, angle)
                screen.blit(rot_en, rot_en.get_rect(center=rect.center).topleft)
            else: pygame.draw.rect(screen, RED, rect)

        if dev_mode:
            dev_txt = f"DEV MODE | LV JUMP: 1~4 | GOD: {god_mode}"
            dev_surf = font.render(dev_txt, True, (0, 255, 0))
            screen.blit(dev_surf, (WIDTH // 2 - dev_surf.get_width() // 2, 10))

        draw_hud(screen, font, score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()