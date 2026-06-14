# 2026-04-14 (7주차 실습 정리)

## 오늘 한 것
- 레이저 페이즈 추가 및 조정
- 개발자 모드 추가 (원활한 테스트를 위함)

## AI 활용 내용
# Question
- 개발자 모드로 특정 단계를 바로 테스트 가능하게 끔 만들어줘 항목을 검색함

# Answer
## 🛠️ 개발자 모드가 추가된 main.py 핵심 로직

> - 개발자 모드를 추가하면 게임을 처음부터 플레이할 필요 없이 특정 레벨의 기믹(레이저, 이동 제한 해제 등)을 즉시 테스트할 수 있어 개발 효율이 엄청나게 올라갑니다.

> - 가장 직관적인 방법인 **"숫자 키(1, 2, 3, 4)를 눌러 해당 레벨로 즉시 점프"**하는 기능을 추가했습니다. 또한, 테스트 중 죽지 않도록 무적 모드(F1) 토글 기능도 함께 넣었습니다.

    def main():
        # ... (기존 초기화 코드 동일) ...

        # 💡 개발자 모드 전용 변수
        dev_mode = False  # F1 키로 토글
        god_mode = False  # 무적 상태

        while True:
            clock.tick(FPS)
            # 현재 점수에 따른 레벨 계산 로직은 유지하되, 개발자 모드에서 점수를 강제로 조절함
            level_idx = min(score // 300, len(LEVELS) - 1)
            level_cfg = LEVELS[level_idx]
            mode = level_cfg.get("mode", "normal")

            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                
                # 💡 개발자 키 입력 처리 (KEYDOWN 이벤트)
                if e.type == pygame.KEYDOWN:
                    # F1: 개발자 정보 표시 및 무적 토글
                    if e.key == pygame.K_F1:
                        dev_mode = not dev_mode
                        god_mode = dev_mode # 개발자 모드 켜지면 무적도 같이 켜짐
                    
                    # 숫자 키 1~4: 해당 레벨로 즉시 점수 조정
                    if dev_mode:
                        if e.key == pygame.K_1: score = 0      # Lv.1
                        elif e.key == pygame.K_2: score = 300  # Lv.2
                        elif e.key == pygame.K_3: score = 600  # Lv.3 (레이저 모드 진입)
                        elif e.key == pygame.K_4: score = 900  # Lv.4
                        elif e.key == pygame.K_k: enemies.clear(); lasers.clear() # K: 화면 정리

            # 1. 플레이어 조작 (상하좌우 제한 해제 로직은 mode에 따라 자동 적용)
            keys = pygame.key.get_pressed()
            # ... (기존 조작 로직 동일) ...

            # 💡 무적 모드 적용 (god_mode가 켜져 있으면 invincible 시간을 계속 초기화)
            if god_mode:
                invincible = 2 

            # ... (적/레이저 생성 및 업데이트 로직 동일) ...

            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # 그리기 섹션 하단에 개발자 정보 표시
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # ... (기존 그리기 코드 동일) ...

            if dev_mode:
                dev_txt = f"DEV MODE: {'GOD ON' if god_mode else 'NORMAL'} | LV JUMP: 1~4"
                dev_surf = font.render(dev_txt, True, (0, 255, 0)) # 초록색 글씨
                screen.blit(dev_surf, (WIDTH // 2 - dev_surf.get_width() // 2, 10))

            pygame.display.flip()

# 🕹️ 개발자 모드 사용법
1. F1 키: 개발자 모드를 켜거나 끕니다. (켜지면 화면 상단에 초록색 텍스트가 뜹니다.)
2. 숫자 1, 2 키: 일반 모드(Lv.1~2)를 테스트합니다.
3. 숫자 3, 4 키: 레이저 모드와 상하좌우 이동을 즉시 테스트합니다. (점수가 600점/900점으로 강제 세팅됩니다.)
4. K 키 (선택 사항): 화면에 너무 많은 적이나 레이저가 있을 때 순식간에 지워버립니다.

# 🧐 왜 이렇게 만드나요?
1. 점수 조작 방식: 우리 게임은 score // 300으로 레벨을 결정하기 때문에, 레벨 변수를 직접 바꾸는 것보다 점수(score)를 바꾸는 것이 가장 안전합니다. (기존 시스템을 건드리지 않고 레벨을 바꿀 수 있기 때문입니다.)
2. 모드 자동 전환: 점수가 600점(Lv.3)이 되는 순간 mode = "laser"가 되면서, 우리가 짜둔 if mode == "laser": 조작 로직과 생성 로직이 자동으로 활성화됩니다.
3.  무적(God Mode): 레이저 패턴이 너무 어렵게 생성되었을 때 죽지 않고 배치를 끝까지 확인하기 위해 필수적입니다.

이제 이 코드를 적용하면 굳이 900점까지 버티지 않아도 **F1 -> 4**만 누르면 바로 레이저 지옥을 맛보며 상하좌우로 기체를 조종해볼 수 있습니다! 바로 적용해 보시겠어요? 🚀✨

