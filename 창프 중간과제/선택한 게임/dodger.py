import base64
import io
import pygame
import random
import sys
from settings import *
from game_objects import Shield, Particle
from utils import get_korean_font, spawn_enemy, draw_hud, game_over_screen
from base import SHEET_B64


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