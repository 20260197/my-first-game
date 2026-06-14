## 2026-03-17 (3주차 강의)
- hello_pygame.py 파일 추가
- 배경에 원형 도형이 떠있는 형태.

> 실시간으로 프레임이 변환하는것을 보이게 수정 (왼쪽 위 표시)
>> Q. 이 코드에 현재 틱이 몇인지 표시해주는 기능을 넣어줄래? 실시간으로 추적가능하게끔. 해당 표시는 왼쪽 위에 표시하게 만들어줘. 
>>> A.
    fps_val = int(clock.get_fps()) 
    => fps_val 이라는 변수에 프레임함수를 이용해 프레임을 구해서 int 형으로 변환 후 집어 넣는다.

> 원형 도형이 이동이 가능하게끔 (WASD 사용) 수정.
>> 이 코드에서 다양한 색깔을 추가해주고, (RGB 형식으로 / 0,0,0) 뱡향키(WASD)로 움직일 수 있게 코드를 추가해줘.
>>> A.
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: # 위로 이동 (Y축 감소)
        circle_y -= circle_speed
    if keys[pygame.K_s]: # 아래로 이동 (Y축 증가)
        circle_y += circle_speed
    if keys[pygame.K_a]: # 왼쪽으로 이동 (X축 감소)
        circle_x -= circle_speed
    if keys[pygame.K_d]: # 오른쪽으로 이동 (X축 증가)
        circle_x += circle_speed  

> 탭(TAB)키를 누를떄마다 도형의 색깔이 변경되도록 수정.
>> Q. 탭 키를 누를때 마다 색깔이 변경되게 해줘.
>>> A.
    
    import pygame
    import sys

    pygame.init()

    # 화면 설정
    WIDTH, HEIGHT = 400, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tab to Change Color!")

    # --- [수정] 색상들을 리스트로 묶기 ---
    COLORS = [
        (255, 0, 0),    # RED
        (0, 255, 0),    # GREEN
        (0, 0, 255),    # BLUE
        (255, 255, 0),  # YELLOW
        (0, 255, 255),  # CYAN
        (255, 0, 255),  # MAGENTA
        (255, 255, 255) # WHITE
    ]
    color_index = 0  # 현재 어떤 색상인지 가리키는 번호 (0부터 시작)

    # 원의 상태
    circle_x, circle_y = WIDTH // 2, HEIGHT // 2
    circle_radius = 25
    circle_speed = 5

    font = pygame.font.SysFont("arial", 20)
    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # --- [핵심] Tab 키를 눌렀을 때 색상 인덱스 변경 ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # 다음 번호로 넘어가되, 리스트 길이를 넘으면 다시 0이 됨
                    color_index = (color_index + 1) % len(COLORS)

        # 2. WASD 이동 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: circle_y -= circle_speed
        if keys[pygame.K_s]: circle_y += circle_speed
        if keys[pygame.K_a]: circle_x -= circle_speed
        if keys[pygame.K_d]: circle_x += circle_speed

        # 3. 그리기
        screen.fill((0, 0, 0)) # 배경은 검정
        
        # 리스트에서 현재 인덱스에 맞는 색상을 꺼내서 그립니다.
        pygame.draw.circle(screen, COLORS[color_index], (int(circle_x), int(circle_y)), circle_radius)

        # 4. 안내 텍스트
        guide = font.render(f"Press TAB to Change Color (Current: {color_index + 1})", True, (255, 255, 255))
        screen.blit(guide, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# 💡 핵심 원리 설명
> 1. 나머지 연산자($%$)의 마법
>> - 리스트의 길이가 7일 때, color_index가 6(마지막 색상)에서 1이 더해지면 7이 됩니다. 
>> - 이때 7 % 7을 계산하면 결과는 0이 됩니다. 덕분에 리스트 범위를 벗어나 에러가 나지 않고 자연스럽게 첫 번째 색상으로 되돌아갑니다.
>> - 게임 개발에서 인벤토리 슬롯이나 슬라이드 메뉴를 만들 때 정말 자주 쓰이는 기법이에요!

> 2. 왜 pygame.KEYDOWN에서 처리하나요?
>> - get_pressed()는 키를 누르고 있는 동안 계속 실행되지만, KEYDOWN 이벤트는 키를 처음 누르는 그 순간 한 번만 발생합니다.
>> - 만약 이동 로직처럼 get_pressed()에 Tab 기능을 넣었다면, 탭을 아주 살짝만 눌러도 색깔이 수십 번씩 순식간에 바뀌어서 제어하기 힘들었을 거예요.


    