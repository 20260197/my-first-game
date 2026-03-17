import pygame
import sys
import random

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Square vs Rotating Triangle Food")

# 색상 정의
BLACK, WHITE, GREEN, YELLOW = (0, 0, 0), (255, 255, 255), (0, 255, 0), (255, 255,0)
color_palette = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (255, 255, 255)]
color_index = 0
current_color = color_palette[color_index]

# 플레이어(사각형) 상태
rect_x, rect_y = WIDTH // 2, HEIGHT // 2
rect_size = 50
half_size = rect_size // 2
rect_speed = 5
angle = 0 

# --- [추가/수정] 먹이 및 게임 상태 변수 ---
score = 0
food_size = 20
food_angle = 0
food_spawn_time = pygame.time.get_ticks() # 생성된 시점의 시간 기록
FOOD_TIMEOUT = 3000 # 3000ms = 3초 후에 이동

def spawn_food():
    return pygame.Vector2(
        random.randint(food_size * 2, WIDTH - food_size * 2),
        random.randint(food_size * 2, HEIGHT - food_size * 2)
    )

food_pos = spawn_food()

font = pygame.font.SysFont("arial", 25)
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks() # 현재 시간 가져오기

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                color_index = (color_index + 1) % len(color_palette)
                current_color = color_palette[color_index]

    # 1. 키 입력 및 이동
    keys = pygame.key.get_pressed()
    is_moving = False
    if keys[pygame.K_w]: rect_y -= rect_speed; is_moving = True
    if keys[pygame.K_s]: rect_y += rect_speed; is_moving = True
    if keys[pygame.K_a]: rect_x -= rect_speed; is_moving = True
    if keys[pygame.K_d]: rect_x += rect_speed; is_moving = True

    # 회전 로직 (플레이어는 이동 시, 먹이는 항상)
    if is_moving: angle = (angle + 3) % 360
    food_angle = (food_angle + 1) % 360 # 먹이는 1도씩 회전
    
    # 2. 경계선 제한
    rect_x = max(half_size, min(WIDTH - half_size, rect_x))
    rect_y = max(half_size, min(HEIGHT - half_size, rect_y))

    # --- [핵심] 3. 충돌 감지 및 타임아웃 처리 ---
    player_rect = pygame.Rect(rect_x - half_size, rect_y - half_size, rect_size, rect_size)
    food_rect = pygame.Rect(food_pos.x - food_size, food_pos.y - food_size, food_size * 2, food_size * 2)

    # 먹이를 먹었을 때
    if player_rect.colliderect(food_rect):
        score += 1
        food_pos = spawn_food()
        food_spawn_time = current_time # 시간 초기화

    # 일정 시간이 지났을 때 (타임아웃)
    if current_time - food_spawn_time > FOOD_TIMEOUT:
        food_pos = spawn_food()
        food_spawn_time = current_time # 시간 초기화

    # 4. 그리기
    screen.fill(BLACK)

    # --- 회전하는 삼각형 먹이 그리기 ---
    # 삼각형을 그릴 별도의 Surface 생성
    food_surf_size = food_size * 3
    food_temp_surf = pygame.Surface((food_surf_size, food_surf_size), pygame.SRCALPHA)
    f_center = food_surf_size // 2
    f_points = [
        (f_center, f_center - food_size),
        (f_center - food_size, f_center + food_size),
        (f_center + food_size, f_center + food_size)
    ]
    pygame.draw.polygon(food_temp_surf, GREEN, f_points)
    
    # 삼각형 회전 적용
    rotated_food = pygame.transform.rotate(food_temp_surf, food_angle)
    food_rect_draw = rotated_food.get_rect(center=(food_pos.x, food_pos.y))
    screen.blit(rotated_food, food_rect_draw.topleft)

    # --- 회전하는 사각형 플레이어 그리기 ---
    surf_size = int(rect_size * 1.5)
    temp_surface = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
    pygame.draw.rect(temp_surface, current_color, (surf_size//2 - half_size, surf_size//2 - half_size, rect_size, rect_size))
    
    rotated_player = pygame.transform.rotate(temp_surface, angle)
    player_rect_draw = rotated_player.get_rect(center=(rect_x, rect_y))
    screen.blit(rotated_player, player_rect_draw.topleft)

    # 5. UI 출력
    score_surf = font.render(f"Score: {score}", True, WHITE)
    # 남은 시간을 시각적으로 보여주기 위한 텍스트 (선택 사항)
    time_left = max(0, (FOOD_TIMEOUT - (current_time - food_spawn_time)) // 1000 + 1)
    timer_surf = font.render(f"Food Teleport in: {time_left}s", True, YELLOW)
    
    screen.blit(score_surf, (10, 10))
    screen.blit(timer_surf, (10, 40))

    pygame.display.flip()
    clock.tick(120)

pygame.quit()
sys.exit()