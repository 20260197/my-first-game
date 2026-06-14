# 2026-03-24 (4주차 실습 정리)

> 오늘 한 것
- 원형 / AABB / OBB Bounding Box 시각화
- 세 방식의 충돌 판정 차이 관찰

> 관찰 내용
- 오브젝트의 충돌 가이드라인 생성 지점과, 가이드라인 충돌 시 생기는 변화를 관찰함
- 오브젝트의 외형이 복잡해질 경우, 가이드라인이 어떻게 변하는지와 회전시에 가이드라인의 변화를 관찰함.

> 구현 순서 
>> Q1 -  이 코드에서 AABB를 화면에 그리는 부분만 설명해줘. 그리고 pygame.draw.rect 의 인자가 각각 뭘 의미하는지 포함해줘.
>>> A1. 코드의 하단 그리기(draw) 섹션에 위치한 이 두 줄이 AABB를 화면에 표시하는 역할을 합니다.
>>> 1. 원형 플레이어를 감싸는 AABB 테두리 그리기

pygame.draw.rect(screen, AABB_RED, player_aabb, 2)

>>> 2. 고정 사각형의 AABB 테두리 그리기

pygame.draw.rect(screen, AABB_RED, fixed_rect_aabb, 2)

## 🛠️ pygame.draw.rect 인자 상세 설명
### pygame.draw.rect(surface, color, rect, width)의 각 인자는 다음과 같은 의미를 가집니다.
> 1. surface (대상): 사각형을 어디에 그릴지 지정합니다.
>> 우리 코드에서는 screen(우리가 만든 800x600 창)이 들어갑니다.
> 2. color (색상): 사각형의 색상을 지정합니다.
>> (R, G, B) 형태의 튜플을 받습니다. 코드에서는 미리 정의한 AABB_RED인 (255, 0, 0)이 사용되었습니다.
> 3. rect (사각형 정보): 사각형의 위치와 크기를 담고 있는 정보입니다.
>> pygame.Rect 객체나 (x, y, width, height) 형태의 튜플을 전달합니다.
>> 중요: 여기서 x, y는 사각형의 중심이 아니라 왼쪽 상단(Top-Left) 꼭짓점의 좌표입니다.
> 4. width (선 두께): 사각형을 어떻게 채울지 결정하는 가장 중요한 인자입니다.
>> 0 (기본값): 사각형 내부를 색상으로 가득 채웁니다.
>> 0보다 큰 정수: 내부를 채우지 않고, 설정한 숫자만큼의 테두리 두께를 가진 사각형을 그립니다.
>> 시각화 팁: 우리는 충돌 영역 '테두리'만 확인해야 하므로 2를 넣어 선으로 표현했습니다.

## 🔍 왜 player_aabb를 따로 계산해서 넣었나요?
### 원형 오브젝트는 중심점(player_pos)을 기준으로 움직이지만, pygame.draw.rect는 왼쪽 상단을 기준으로 그리기 때문입니다.
> 코드 내부 계산: Rect(int(player_pos.x - player_radius), int(player_pos.y - player_radius), ...)
> 이렇게 원의 중심에서 반지름만큼 빼준 좌표를 rect 인자로 넘겨주어야, 원을 정확히 감싸는 사각형 테두리가 그려지게 됩니다.

>> Q2 -  1.현재 코드에 원형 bounding box 를 추가해줘. 2. 각 오브젝트의 중심에서 파란 원을 그려줘. 3. 반지름은 오브젝트 너비의 절반으롤 설정해줘. 4. 원형 충돌 감지도 구현하고, 충돌 시 화면 배경을 노란색으로 바꿔줘.
>>> A2. 

    import pygame
    import sys

    # 1. 초기화 및 화면 설정
    pygame.init()

    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("AABB vs Circular Collision Visualization")

    # 색상 정의
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)      
    AABB_RED = (255, 0, 0)      
    BLUE = (0, 0, 255)          # 원형 바운딩 박스 색상
    YELLOW = (255, 255, 0)      # 충돌 시 배경색
    GREEN = (50, 255, 50)       

    # 폰트 설정
    font = pygame.font.SysFont("arial", 20)

    # --- 오브젝트 설정 ---

    # 1. 고정 사각형
    fixed_rect = pygame.Rect(0, 0, 150, 150)
    fixed_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    fixed_radius = fixed_rect.width // 2  # 반지름은 너비의 절반

    # 2. 이동 사각형 (플레이어)
    player_size = 80
    player_rect = pygame.Rect(100, 100, player_size, player_size)
    player_radius = player_size // 2      # 반지름은 너비의 절반
    player_speed = 5

    clock = pygame.time.Clock()
    running = True

    while running:
        # 2. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 3. 업데이트 (방향키 + WASD 이동)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            player_rect.x += player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:    
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:  
            player_rect.y += player_speed

        # 화면 경계선 제한
        player_rect.left = max(0, min(SCREEN_WIDTH - player_size, player_rect.left))
        player_rect.top = max(0, min(SCREEN_HEIGHT - player_size, player_rect.top))

        # --- 충돌 감지 로직 ---

        # A. AABB 충돌 (사각형 기반)
        aabb_colliding = player_rect.colliderect(fixed_rect)

        # B. 원형 충돌 (중심 거리 기반)
        # 1. 두 오브젝트의 중심점 좌표 구하기
        p1 = pygame.math.Vector2(player_rect.center)
        p2 = pygame.math.Vector2(fixed_rect.center)
        
        # 2. 두 중심점 사이의 거리 계산
        distance = p1.distance_to(p2)
        
        # 3. 거리가 두 반지름의 합보다 작으면 충돌
        circle_colliding = distance <= (player_radius + fixed_radius)


        # 5. 그리기
        # 원형 충돌 시 배경을 노란색으로, 아니면 검은색으로 설정
        bg_color = YELLOW if circle_colliding else BLACK
        screen.fill(bg_color)

        # 오브젝트 채우기 (AABB 충돌 시 빨간색 계열로 변경)
        object_color = (255, 100, 100) if aabb_colliding else GRAY
        pygame.draw.rect(screen, object_color, fixed_rect)
        pygame.draw.rect(screen, object_color, player_rect)

        # --- 시각화: AABB (빨간 사각형 테두리) ---
        pygame.draw.rect(screen, AABB_RED, player_rect, 2)
        pygame.draw.rect(screen, AABB_RED, fixed_rect, 2)

        # --- 시각화: 원형 Bounding Box (파란 원 테두리) ---
        pygame.draw.circle(screen, BLUE, player_rect.center, player_radius, 2)
        pygame.draw.circle(screen, BLUE, fixed_rect.center, fixed_radius, 2)

        # UI 텍스트 출력
        instr_surf = font.render("Move: WASD or Arrow Keys", True, WHITE if not circle_colliding else BLACK)
        aabb_status = "AABB Colliding: YES" if aabb_colliding else "AABB Colliding: NO"
        circle_status = "Circle Colliding: YES" if circle_colliding else "Circle Colliding: NO"
        
        screen.blit(instr_surf, (10, 10))
        screen.blit(font.render(aabb_status, True, AABB_RED), (10, 40))
        screen.blit(font.render(circle_status, True, BLUE), (10, 70))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

## 💡 주요 핵심 내용 설명
> 원형 충돌의 수학적 원리
>> 사각형 충돌(AABB)은 단순히 면적이 겹치는지를 보지만, 원형 충돌은 두 점 사이의 거리를 이용합니다.

>> $$Distance(P_1, P_2) \le Radius_1 + Radius_2$$

>> 두 오브젝트의 중심 사이의 거리가 각 반지름을 더한 값보다 작으면 "겹쳤다"고 판단합니다. 코드에서는 pygame.math.Vector2의 distance_to 함수를 사용하여 피타고라스 정리를 한 줄로 처리했습니다.

> 시각적 차이점 관찰하기
>> 이 코드를 실행해보면 재미있는 점을 발견할 수 있습니다.
>>> AABB(빨간색): 사각형의 모서리 부분이 닿았을 때 먼저 충돌이 발생합니다.
>>> 원형(파란색): 모서리 부분에서는 충돌이 일어나지 않다가, 사각형의 몸체 쪽으로 더 깊숙이 들어가야 배경이 노란색으로 변합니다.

> 왜 반지름을 너비의 절반으로 하나요?
>> 사각형을 완전히 감싸는 원(외접원)을 만들 수도 있지만, 보통 게임에서는 캐릭터의 본체 부피에 가장 가깝게 맞추기 위해 너비의 절반을 반지름으로 사용합니다. 이를 통해 '히트박스'의 오차를 줄일 수 있습니다.

## ✅ 다음 단계 제안
> 두 가지 충돌 방식을 동시에 보니 차이가 명확하죠?
>> 이제 **"두 원형 박스가 충돌했을 때 튕겨 나가는 효과(물리 반작용)"**를 넣어볼까요? 아니면 **"원형 박스의 크기를 실시간으로 조절하는 기능"**을 추가해 볼까요? 궁금한 점이 있다면 무엇이든 물어보세요! Would you like me to help you implement a physics response for the circular collision?
