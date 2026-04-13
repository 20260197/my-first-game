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
    pygame.display.set_caption("Shield Dodger: Tactical Laser")
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
    player_rect = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)
    current_frame_idx, current_angle, target_angle = 1, 0.0, 0.0
    my_shield = Shield(radius=75)
    enemies, particles, lasers = [], [], []
    score, lives, spawn_timer, invincible = 0, 3, 0, 0

    # 개발자 모드 변수
    dev_mode = False
    god_mode = False

    while True:
        clock.tick(FPS)
        level_idx = min(score // 300, len(LEVELS) - 1)
        level_cfg = LEVELS[level_idx]
        mode = level_cfg.get("mode", "normal")

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            
            # 💡 개발자 모드 입력 처리
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_F1:
                    dev_mode = not dev_mode
                    god_mode = dev_mode
                if dev_mode:
                    if e.key == pygame.K_1: score = 0
                    elif e.key == pygame.K_2: score = 300
                    elif e.key == pygame.K_3: score = 600
                    elif e.key == pygame.K_4: score = 900
                    elif e.key == pygame.K_k: enemies.clear(); lasers.clear()

        # 1. 플레이어 조작 (상하좌우 제한 해제)
        keys = pygame.key.get_pressed()
        current_frame_idx, target_angle = 1, 0
        
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
            player_rect.x -= 7
            current_frame_idx, target_angle = 0, 15
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < WIDTH:
            player_rect.x += 7
            current_frame_idx, target_angle = 2, -15
            
        if mode == "laser":
            if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_rect.top > 0:
                player_rect.y -= 6
            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_rect.bottom < HEIGHT:
                player_rect.y += 6
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
            elif mode == "laser":
                side = random.randint(0, 3)
                if side == 0: origin = [random.randint(0, WIDTH), -30]
                elif side == 1: origin = [random.randint(0, WIDTH), HEIGHT + 30]
                elif side == 2: origin = [-30, random.randint(0, HEIGHT)]
                else: origin = [WIDTH + 30, random.randint(0, HEIGHT)]
                lasers.append({"origin": origin, "target": list(player_rect.center), "timer": 40, "state": 0})

        # 3. 레이저 로직 (추적 -> 멈춤 -> 발사)
        for laser in lasers[:]:
            if laser["state"] == 0: 
                laser["target"] = list(player_rect.center)
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    laser["state"] = 1
                    laser["timer"] = 25 
            
            elif laser["state"] == 1: 
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    laser["state"] = 2
                    laser["timer"] = 12 
            
            elif laser["state"] == 2: 
                laser["timer"] -= 1
                if laser["timer"] <= 0:
                    lasers.remove(laser)
                    continue
                
                if invincible <= 0:
                    start = laser["origin"]
                    dx = laser["target"][0] - start[0]
                    dy = laser["target"][1] - start[1]
                    dist = math.hypot(dx, dy)
                    if dist != 0:
                        end = [start[0] + (dx/dist) * 1500, start[1] + (dy/dist) * 1500]
                        if player_rect.clipline(start, end):
                            lives -= 1
                            invincible = 90
                            lasers.clear()
                            if lives <= 0:
                                if game_over_screen(screen, font, font_big, score): main()
                                return

        # 4. 미사일 물리 로직 (가속 유도)
        alive_enemies, hit_enemies = [], set()
        for i, en_data in enumerate(enemies):
            if en_data[3]: 
                if en_data[6] > 0:
                    en_data[6] -= 1; en_data[2] += GRAVITY
                    en_data[1] *= 0.96; en_data[2] *= 0.96
                    if en_data[6] < 15 and random.random() > 0.5:
                        particles.append(Particle(en_data[0].centerx, en_data[0].centery, SMOKE_COLOR, 2, 12))
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
                        en_data[9] = min(en_data[9] + 0.5, 20.0)
                        desired = (pygame.math.Vector2(target[0].center) - curr_pos).normalize() * en_data[9]
                        new_vel = pygame.math.Vector2(en_data[1], en_data[2]).lerp(desired, 0.15)
                        if new_vel.length() > 0: new_vel.scale_to_length(en_data[9])
                        en_data[1], en_data[2] = new_vel.x, new_vel.y
                        if random.random() > 0.4:
                            particles.append(Particle(en_data[0].centerx, en_data[0].centery, BOOSTER_COLOR, 3, 15))

        # 이동 및 소멸 ([:8] 언패킹 보호 적용)
        for i, en_data in enumerate(enemies):
            if i in hit_enemies: continue
            rect, dx, dy, is_def, angle, rot_speed, _, missile_life = en_data[:8]
            rect.x += dx; rect.y += dy
            if is_def:
                en_data[7] -= 1
                if en_data[7] <= 0:
                    for _ in range(8): particles.append(Particle(rect.centerx, rect.centery, DARK_GRAY))
                    continue
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
        # 7. 그리기 섹션
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        screen.fill((20, 20, 40))
        my_shield.draw(screen)
        for p in particles: p.draw(screen)

        # 💡 [조절됨] 강화된 레이저 렌더링
        for laser in lasers:
            start = laser["origin"]
            dx, dy = laser["target"][0] - start[0], laser["target"][1] - start[1]
            dist = math.hypot(dx, dy)
            if dist == 0: continue
            end = [start[0] + (dx/dist) * 1500, start[1] + (dy/dist) * 1500]
            
            if laser["state"] == 0: 
                pygame.draw.line(screen, (150, 30, 30), start, end, 2)
            elif laser["state"] == 1: 
                flash_color = (255, 200, 0) if (pygame.time.get_ticks() // 100) % 2 == 0 else (255, 0, 0)
                pygame.draw.line(screen, flash_color, start, end, 5) # 두껍게
                pygame.draw.line(screen, (255, 255, 255), start, end, 2) # 내부 밝은 선
            elif laser["state"] == 2: 
                pygame.draw.line(screen, (255, 255, 255), start, end, 12) 
                pygame.draw.line(screen, (255, 50, 50), start, end, 6)

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