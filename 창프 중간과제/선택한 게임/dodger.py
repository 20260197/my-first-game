import base64
import io
import pygame
import random
import sys
from settings import *
from game_objects import Shield, Particle
from utils import get_korean_font, spawn_enemy, draw_hud, game_over_screen

# SHEET_B64 데이터는 여기에 위치
SHEET_B64 = "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"

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shield Dodger: Modular Version")
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
    enemies, particles = [], []
    score, lives, spawn_timer, invincible = 0, 3, 0, 0

    while True:
        clock.tick(FPS)
        level_cfg = LEVELS[min(score // 300, len(LEVELS) - 1)]

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()

        # 입력 및 기울기 로직
        keys = pygame.key.get_pressed()
        current_frame_idx, target_angle = 1, 0
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_rect.left > 0:
            player_rect.x -= 7
            current_frame_idx, target_angle = 0, 15
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_rect.right < WIDTH:
            player_rect.x += 7
            current_frame_idx, target_angle = 2, -15
        current_angle += (target_angle - current_angle) * 0.3
        
        my_shield.update(player_rect.center)

        # 적 생성
        spawn_timer += 1
        if spawn_timer >= level_cfg["spawn"]:
            spawn_timer = 0
            enemies.append(spawn_enemy(level_cfg))

        alive_enemies, hit_enemies = [], set()

        # 미사일 물리 로직 (관성 및 부스터)
        for i, en_data in enumerate(enemies):
            if en_data[3]:
                if en_data[6] > 0:
                    en_data[6] -= 1
                    en_data[2] += GRAVITY
                    en_data[1] *= 0.96; en_data[2] *= 0.96
                    if en_data[6] < 15 and random.random() > 0.5:
                        particles.append(Particle(en_data[0].centerx, en_data[0].centery, SMOKE_COLOR, 2, 12))
                else:
                    curr_pos = pygame.math.Vector2(en_data[0].center)
                    target = None
                    max_dist = -1
                    for other in enemies:
                        if not other[3]:
                            dist = curr_pos.distance_to(other[0].center)
                            if dist > max_dist: max_dist, target = dist, other
                    if target:
                        desired_vel = (pygame.math.Vector2(target[0].center) - curr_pos).normalize() * 17
                        en_data[1], en_data[2] = pygame.math.Vector2(en_data[1], en_data[2]).lerp(desired_vel, 0.1)
                        if random.random() > 0.4:
                            particles.append(Particle(en_data[0].centerx, en_data[0].centery, BOOSTER_COLOR, 3, 15))

        # 이동 및 충돌
        for i, en_data in enumerate(enemies):
            if i in hit_enemies: continue
            rect, dx, dy, is_def, angle, rot_speed, _, missile_life = en_data
            rect.x += dx; rect.y += dy
            if is_def:
                en_data[7] -= 1
                if en_data[7] <= 0:
                    for _ in range(8): particles.append(Particle(rect.centerx, rect.centery, DARK_GRAY))
                    continue
                en_data[4] += rot_speed
                for j, other in enumerate(enemies):
                    if i != j and not other[3] and j not in hit_enemies and rect.colliderect(other[0]):
                        hit_enemies.add(i); hit_enemies.add(j)
                        score += 50
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
                    lives -= 1; invincible = 90; enemies.clear()
                    if lives <= 0:
                        if game_over_screen(screen, font, font_big, score): main()
                        return
                    break

        # 그리기
        screen.fill((20, 20, 40))
        my_shield.draw(screen)
        for p in particles: p.draw(screen)

        if (invincible // 10) % 2 == 0:
            img = player_frames[current_frame_idx]
            rot_img = pygame.transform.rotate(img, int(current_angle / 5) * 5)
            screen.blit(rot_img, rot_img.get_rect(center=player_rect.center))

        for en_data in enemies:
            rect, _, _, is_def, angle, _, _, missile_life = en_data
            if is_def:
                if missile_life > 30 or (missile_life // 5) % 2 == 0:
                    color_surf = enemy_surface.copy()
                    if en_data[6] <= 0: pygame.draw.rect(color_surf, YELLOW, (0, 0, ENEMY_W, ENEMY_H), 1)
                    rot_en = pygame.transform.rotate(color_surf, angle)
                    screen.blit(rot_en, rot_en.get_rect(center=rect.center).topleft)
            else: pygame.draw.rect(screen, RED, rect)

        draw_hud(screen, font, score, level_cfg, lives)
        pygame.display.flip()

if __name__ == "__main__":
    main()