# 2026-04-07 (6주차 실습 정리)

## 게임 에셋 (스프라이트, 사운드) 적용 방법 실습
- 1. 이미지 파일을 별도로 준비하여 프로젝트 내부에서 이미지 파일을 찾는 방법을 알아보았다.
> 헷갈렸던 부분 - 절대경로와 상대경로 개념을 오랜만에 접해서 그런지 조금 버벅였다.
>> 질문 - pygame image 상대경로 절대경로
>>> 답변 - 절대경로란 컴퓨터 전체의 경로를 말하는거고, 상대경로란 '해당 파일이 들어가있는 폴더를 기준' 으로 한 경로를 말하는 것이다.

> 스프라이트 시트 관련
>> 나는 스프라이트 시트 도구를 AI로 만들라는 말인 줄 알았으나, 기존에 있는 도구를 이용하라는 말이었음.

> 시트 도구를 사용하여 이미지를 메인코드에 넣어보자
>> 질문 - 스프라이트 시트 도구를 이용해서, 특정 우주선을 하나 가지고 코드로 변환시킨 코드야. 이중에서 필요한 코드를 골라내서 복사가 가능하게 해주고, 메인 게임코드 어디부분에 넣어야 할지 알려줘.
>>> 답변 - 

    import base64
    import io
    import pygame

    (기존 import들...)

    💡 제공해주신 Base64 데이터를 그대로 복사해서 넣으세요.

    SHEET_B64 = 'BASE64 코드'

    💡 Base64 데이터로부터 이미지 로드
    sheet_bytes = base64.b64decode(SHEET_B64)
    player_sheet = pygame.image.load(io.BytesIO(sheet_bytes)).convert_alpha()

    💡 스프라이트 시트에서 프레임 추출 (8x8 크기, 10열 가정)
    player_frames = []
    for i in range(4):  # 사용할 프레임 개수 (예: 4개)
        # Ship_Pack.png에서 첫 번째 줄 4개를 가져오는 로직
        rect = pygame.Rect(i * 8, 0, 8, 8) 
        frame_img = player_sheet.subsurface(rect)
        # 캐릭터 크기에 맞춰 확대 (PLAYER_W, PLAYER_H)
        frame_img = pygame.transform.scale(frame_img, (PLAYER_W, PLAYER_H))
        player_frames.append(frame_img)

    💡 애니메이션 변수
    current_frame = 0
    last_update = pygame.time.get_ticks()
    animation_speed = 150 # 밀리초

    💡 플레이어 애니메이션 업데이트
        now = pygame.time.get_ticks()
        if now - last_update > animation_speed:
            last_update = now
            current_frame = (current_frame + 1) % len(player_frames)

    6. 그리기 섹션
        if (invincible // 10) % 2 == 0:
            # 💡 기존 네모 대신 현재 애니메이션 프레임을 그림
            screen.blit(player_frames[current_frame], player)

> BASE64 코드가 심각하게 길어서 AI가 그대로 돌려주는 답변으론 사용 X
>> 시트 도구에서 나오는 코드중 BASE64 내용만 그대로 복사해서 수정을 하니 정상적으로 작동된다.

> 기껏 적용했더니 잔상이 생기는 문제 발생
>> 질문 - 플레이어 이미지도 바뀌지 않았고, 게임 플레이를 해보면 이미지가 연속적으로 이어지는 형태로 나오고 있어, 즉, 계속해서 그려내기만 하고 지우는 느낌이 들지 않아
>>> 답변 - 잔상이 남고 이미지가 덮어씌워지는 이유는 딱 두 가지 실수가 겹쳤기 때문입니다. 전공자들도 코드를 합치다 보면 자주 하는 실수니 걱정 마세요! 가장 큰 문제는 도화지를 닦지 않고(fill) 그 위에 계속 그림을 그린 것과 이미지를 그린 직후에 다시 파란 네모를 그려서 덮어버린 것 입니다.

    6. 그리기 섹션
        # 💡 [필수] 매 프레임마다 배경을 먼저 칠해줘야 잔상이 남지 않습니다!
        screen.fill(GRAY) 

        # 방어막 그리기
        my_shield.draw(screen)

        # 파티클 그리기
        for p in particles:
            p.draw(screen)

        # 플레이어 그리기
        if (invincible // 10) % 2 == 0:
            # 💡 [수정] 이미지 블릿! (아래에 있던 draw.rect는 지워야 합니다)
            screen.blit(player_frames[current_frame], player)

        # 적 그리기
        for en_data in enemies:
            rect, _, _, is_deflected, angle, _, _, missile_lifetime = en_data
            if is_deflected:
                if missile_lifetime > 30 or (missile_lifetime // 5) % 2 == 0:
                    rotated_img = pygame.transform.rotate(enemy_surface, angle)
                    new_rect = rotated_img.get_rect(center=rect.center)
                    screen.blit(rotated_img, new_rect.topleft)
            else:
                pygame.draw.rect(screen, RED, rect)

        # HUD 그리기
        draw_hud(score, level_cfg, lives)
        
        # 화면 업데이트
        pygame.display.flip()

> 키보드 먹통 이슈. 자연스러운 애니메이션이 나오지 않는 이슈.
>> 질문 - 우주선은 잘 움직이네. 그런데 AD 키로 움직이는게 먹히지가 않아. 그리고 우주선 프레임 4개로 해줬는데 3개밖에 나오지가 않네 수정해줄래?
>>> 답변 - 우선 AD키 이슈부터 조정.

    # 💡 1. 입력 처리 (AD 키 및 화살표 키 동시 지원)
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player.left > 0:
        player.x -= 7
    if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player.right < WIDTH:
        player.x += 7
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and player.top > 0:
        player.y -= 7
    if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player.bottom < HEIGHT:
        player.y += 7

>>> 답변 - 이후 애니메이션 프레임 수정

    💡 1. 실제 이미지가 있는 3개만 추출 (0, 1, 2번 인덱스)
    player_frames = []
    for i in range(3): 
        rect = pygame.Rect(i * 8, 0, 8, 8) 
        frame_img = player_sheet.subsurface(rect)
        frame_img = pygame.transform.scale(frame_img, (PLAYER_W, PLAYER_H))
        player_frames.append(frame_img)

    💡 2. 애니메이션 재생 순서 정의 (1-2-3-2 순서)
    # 인덱스 기준으로는 [0, 1, 2, 1] 입니다.
    anim_sequence = [0, 1, 2, 1]
    current_anim_idx = 0  # 시퀀스 리스트의 몇 번째인지를 가리킴
    
    last_update = pygame.time.get_ticks()
    animation_speed = 120

    💡 애니메이션 시퀀스 업데이트
        now = pygame.time.get_ticks()
        if now - last_update > animation_speed:
            last_update = now
            # 시퀀스 리스트(0, 1, 2, 1) 내에서 다음 순서로 이동
            current_anim_idx = (current_anim_idx + 1) % len(anim_sequence)

    💡 플레이어 그리기
        if (invincible // 10) % 2 == 0:
            # anim_sequence[current_anim_idx]는 0, 1, 2, 1 중 하나가 됩니다.
            actual_frame_to_draw = player_frames[anim_sequence[current_anim_idx]]
            screen.blit(actual_frame_to_draw, player)