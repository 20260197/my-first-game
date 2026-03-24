import pygame
import sys
import random
import math
from sprites import load_sprite

# 1. 초기화 및 설정
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Circle & SAT Debugger | R: Mode")

# 색상 정의
BLACK, WHITE = (20, 20, 20), (255, 255, 255)
AABB_RED, CIRCLE_BLUE = (255, 50, 50), (50, 50, 255)
GUIDE_GREEN, BG_HIT = (0, 255, 0), (150, 0, 0)
BOTH_YELLOW = (255, 255, 0)

# 2. 스프라이트 관리
sprite_names = ["adventurer", "stone", "rocket", "sword"]
SPRITE_SIZES = {
    "adventurer": (80, 110),
    "stone": (100, 100),
    "rocket": (60, 160),
    "sword": (50, 150)
}

player_idx, obs_idx = 0, 2 

def get_current_sprites():
    p_name = sprite_names[player_idx]
    o_name = sprite_names[obs_idx]
    p_img = load_sprite(p_name, SPRITE_SIZES[p_name])
    o_img = load_sprite(o_name, SPRITE_SIZES[o_name])
    return p_img, o_img

player_img, obstacle_img_orig = get_current_sprites()

# 3. 상태 변수
show_guides = True 
modes = ["AABB", "CIRCLE", "OBB", "ALL"]
mode_idx = 3 
collision_mode = modes[mode_idx]

player_pos = pygame.math.Vector2(100, 100)
player_speed = 5
obs_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
angle = 0
base_rot_speed = 2

font = pygame.font.SysFont("malgungothic", 22, bold=True)
clock = pygame.time.Clock()

# --- SAT 충돌 및 수학 함수 ---
def get_obb_points(center, size, angle):
    w, h = size[0] / 2, size[1] / 2
    pts = [pygame.math.Vector2(-w, -h), pygame.math.Vector2(w, -h), 
           pygame.math.Vector2(w, h), pygame.math.Vector2(-w, h)]
    return [center + p.rotate(-angle) for p in pts]

def get_axes(points):
    axes = []
    for i in range(len(points)):
        p1, p2 = points[i], points[(i + 1) % len(points)]
        edge = p2 - p1
        axes.append(pygame.math.Vector2(-edge.y, edge.x).normalize())
    return axes

def project(points, axis):
    dots = [p.dot(axis) for p in points]
    return min(dots), max(dots)

def sat_collision(pts1, pts2):
    axes = get_axes(pts1) + get_axes(pts2)
    for axis in axes:
        min1, max1 = project(pts1, axis)
        min2, max2 = project(pts2, axis)
        if max1 < min2 or max2 < min1: return False
    return True

# -----------------------

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB: show_guides = not show_guides
            if event.key == pygame.K_r: 
                mode_idx = (mode_idx + 1) % len(modes)
                collision_mode = modes[mode_idx]
            if event.key == pygame.K_c:
                player_idx = (player_idx + 1) % len(sprite_names)
                player_img, obstacle_img_orig = get_current_sprites()
            if event.key == pygame.K_x:
                obs_idx = (obs_idx + 1) % len(sprite_names)
                player_img, obstacle_img_orig = get_current_sprites()

    # 5. 업데이트
    keys = pygame.key.get_pressed()
    rot_speed = base_rot_speed * 4 if keys[pygame.K_z] else base_rot_speed
    angle += rot_speed
    
    move_vec = pygame.math.Vector2(0, 0)
    if keys[pygame.K_w] or keys[pygame.K_UP]: move_vec.y -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_vec.y += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_vec.x -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_vec.x += 1
    if move_vec.length() > 0: player_pos += move_vec.normalize() * player_speed

    # 회전 및 영역 설정
    rotated_obs = pygame.transform.rotate(obstacle_img_orig, angle)
    obs_rect = rotated_obs.get_rect(center=obs_pos)
    player_rect = player_img.get_rect(topleft=player_pos)

    # 6. 실시간 유동적 반지름 계산 (핵심 수정 부분)
    # 현재 스프라이트의 가로/세로 중 더 긴 쪽을 기준으로 반지름 설정
    p_radius = max(player_rect.width, player_rect.height) / 2 * 0.8 # 캐릭터 몸체에 맞게 0.8 보정
    o_radius = max(obs_rect.width, obs_rect.height) / 2 * 0.9      # 장애물에 맞게 0.9 보정

    # 7. 세 가지 충돌 계산
    p_obb = get_obb_points(pygame.math.Vector2(player_rect.center), player_img.get_size(), 0)
    o_obb = get_obb_points(obs_pos, obstacle_img_orig.get_size(), angle)

    # AABB
    aabb_hit = player_rect.colliderect(obs_rect)
    # CIRCLE (계산된 유동적 반지름 사용)
    p_center, o_center = pygame.math.Vector2(player_rect.center), obs_pos
    distance = p_center.distance_to(o_center)
    circle_hit = distance <= (p_radius + o_radius)
    # OBB (SAT)
    obb_hit = sat_collision(p_obb, o_obb)

    if collision_mode == "ALL":
        active_hit = obb_hit 
    else:
        active_hit = aabb_hit if collision_mode == "AABB" else circle_hit if collision_mode == "CIRCLE" else obb_hit

    # 8. 그리기
    screen.fill(BG_HIT if active_hit else BLACK)
    screen.blit(rotated_obs, obs_rect.topleft)
    screen.blit(player_img, player_pos)

    if show_guides:
        if collision_mode in ["AABB", "ALL"]:
            pygame.draw.rect(screen, AABB_RED, player_rect, 1)
            pygame.draw.rect(screen, AABB_RED, obs_rect, 1)
        if collision_mode in ["CIRCLE", "ALL"]:
            # 실시간으로 변하는 p_radius와 o_radius를 그림
            pygame.draw.circle(screen, CIRCLE_BLUE, p_center, int(p_radius), 2)
            pygame.draw.circle(screen, CIRCLE_BLUE, o_center, int(o_radius), 2)
        if collision_mode in ["OBB", "ALL"]:
            pygame.draw.polygon(screen, GUIDE_GREEN, p_obb, 2)
            pygame.draw.polygon(screen, GUIDE_GREEN, o_obb, 2)

    # 9. UI 출력
    status_y = 20
    def draw_t(t, c):
        global status_y
        screen.blit(font.render(t, True, c), (20, status_y)); status_y += 30

    draw_t(f"[R] MODE: {collision_mode}", BOTH_YELLOW)
    draw_t(f"[C/X] SWAP SPRITES | [Z] FAST ROT", WHITE)
    draw_t(f"AABB Status: {'[ HIT! ]' if aabb_hit else 'OFF'}", AABB_RED if aabb_hit else WHITE)
    draw_t(f"CIRCLE Status: {'[ HIT! ]' if circle_hit else 'OFF'}", CIRCLE_BLUE if circle_hit else WHITE)
    draw_t(f"OBB Status: {'[ HIT! ]' if obb_hit else 'OFF'}", GUIDE_GREEN if obb_hit else WHITE)
    
    if aabb_hit and not obb_hit:
        draw_t("-> AABB Phantom Collision!", AABB_RED)
    
    pygame.display.flip()
    clock.tick(60)