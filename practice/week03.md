## 2026-03-17 (3주차 강의)
- hello_pygame.py 파일 추가
- 배경에 원형 도형이 떠있는 형태.

> 실시간으로 프레임이 변환하는것을 보이게 수정 (왼쪽 위 표시)
>> 이 코드에 현재 틱이 몇인지 표시해주는 기능을 넣어줄래?
>>> Q. 실시간으로 추적가능하게끔. 해당 표시는 왼쪽 위에 표시하게 만들어줘.
>>>> A. fps_val = int(clock.get_fps()) -> fps_val 이라는 변수에 프레임을 구해서 변수에 집어 넣는다.
        
      

- 2. 원형 도형이 이동이 가능하게끔 (WASD 사용) 수정.
 > 이 코드에서 다양한 색깔을 추가해주고, (RGB 형식으로 / 0,0,0)
   뱡향키(WASD)로 움직일 수 있게 코드를 추가해줘.
   > > # --- [추가] 2. 키보드 입력 실시간 처리 (WASD 이동) ---
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: # 위로 이동 (Y축 감소)
        circle_y -= circle_speed
    if keys[pygame.K_s]: # 아래로 이동 (Y축 증가)
        circle_y += circle_speed
    if keys[pygame.K_a]: # 왼쪽으로 이동 (X축 감소)
        circle_x -= circle_speed
    if keys[pygame.K_d]: # 오른쪽으로 이동 (X축 증가)
        circle_x += circle_speed
   
      

- 3. 탭(TAB)키를 누를떄마다 도형의 색깔이 변경되도록 수정.
    > 탭 키를 누를때 마다 색깔이 변경되게 해줘.
    > > 주요 코드
    ```
    COLORS = [
        (255, 0, 0),    # RED
        (0, 255, 0),    # GREEN
        (0, 0, 255),    # BLUE
        (255, 255, 0),  # YELLOW
        (0, 255, 255),  # CYAN
        (255, 0, 255),  # MAGENTA
        (255, 255, 255) # WHITE
    ]
    ```

    # --- [핵심] Tab 키를 눌렀을 때 색상 인덱스 변경 ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                # 다음 번호로 넘어가되, 리스트 길이를 넘으면 다시 0이 됨
                color_index = (color_index + 1) % len(COLORS)