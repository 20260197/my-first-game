import pygame
import sys
from Sub_config import *
from utils import *
from entities import *
from upgrades import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Survivor - Weapon Inventory UI")
clock = pygame.time.Clock()

def reset_game():
    global player, enemies, projectiles, sword_waves, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams
    global gems, camera, frame_count, level_up_active
    player = Player()
    enemies = []
    gems = []
    projectiles = []
    sword_waves = []  
    dmg_texts = [] 
    boomerangs = []
    bouncing_orbs = []
    fire_zones = []
    lightnings = []
    beams = []
    blizzards = []
    chakrams = []
    camera = pygame.math.Vector2(0, 0)
    frame_count = 0
    level_up_active = False

reset_game()

card_rects = [
    pygame.Rect(300, 300, 280, 400),
    pygame.Rect(660, 300, 280, 400),
    pygame.Rect(1020, 300, 280, 400)
]

btn_start = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 300, 60)
btn_options = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 80, 300, 60)
btn_quit = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 160, 300, 60)

dev_mode = False
show_mechanics = False 
running = True
current_choices = []
state = "TITLE" 

while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if state == "TITLE":
                if btn_start.collidepoint(mouse_pos):
                    reset_game()
                    state = "PLAY"
                elif btn_options.collidepoint(mouse_pos):
                    state = "OPTIONS"
                elif btn_quit.collidepoint(mouse_pos):
                    running = False
                    
            elif state == "PLAY" and level_up_active:
                for idx, rect in enumerate(card_rects):
                    if idx < len(current_choices) and rect.collidepoint(mouse_pos):
                        apply_card_effect(player, current_choices[idx]["id"], enemies)
                        level_up_active = False
                        break

        if event.type == pygame.KEYDOWN:
            if state == "OPTIONS":
                if event.key == pygame.K_ESCAPE: state = "TITLE" 
            elif state == "GAMEOVER":
                if event.key == pygame.K_r: state = "TITLE" 
            elif state == "PAUSE":
                if event.key == pygame.K_ESCAPE: state = "PLAY" 
            elif state == "PLAY":
                if level_up_active:
                    selected_idx = -1
                    if event.key == pygame.K_1: selected_idx = 0
                    elif event.key == pygame.K_2: selected_idx = 1
                    elif event.key == pygame.K_3: selected_idx = 2
                    
                    if 0 <= selected_idx < len(current_choices):
                        apply_card_effect(player, current_choices[selected_idx]["id"], enemies)
                        level_up_active = False
                else:
                    if event.key == pygame.K_ESCAPE: state = "PAUSE"
                    
                    elif event.key == pygame.K_F1: 
                        dev_mode = not dev_mode
                        if not dev_mode: 
                            show_mechanics = False 
                            
                    elif dev_mode:
                        if event.key == pygame.K_F2: player.god_mode = not player.god_mode
                        elif event.key == pygame.K_F3: player.xp = player.max_xp
                        elif event.key == pygame.K_F4: 
                            player.kills += KILLS_PER_PHASE
                            player.phase = (player.kills // KILLS_PER_PHASE) + 1
                        elif event.key == pygame.K_F5: 
                            show_mechanics = not show_mechanics
                        
                        elif event.key == pygame.K_1: player.weapons["melee"]["active"] = not player.weapons["melee"]["active"]
                        elif event.key == pygame.K_2: player.weapons["orbit"]["active"] = not player.weapons["orbit"]["active"]
                        elif event.key == pygame.K_3: player.weapons["axe"]["active"] = not player.weapons["axe"]["active"]
                        elif event.key == pygame.K_4: player.weapons["lightning"]["active"] = not player.weapons["lightning"]["active"]
                        elif event.key == pygame.K_5: player.weapons["beam"]["active"] = not player.weapons["beam"]["active"]
                        elif event.key == pygame.K_6: player.weapons["blizzard"]["active"] = not player.weapons["blizzard"]["active"]
                        elif event.key == pygame.K_7: player.weapons["chakram"]["active"] = not player.weapons["chakram"]["active"]
                        elif event.key == pygame.K_8: player.weapons["boomerang"]["active"] = not player.weapons["boomerang"]["active"]
                        elif event.key == pygame.K_9: player.weapons["bounce"]["active"] = not player.weapons["bounce"]["active"]
                        elif event.key == pygame.K_0: player.weapons["trail"]["active"] = not player.weapons["trail"]["active"]

    if state == "PLAY":
        if not level_up_active:
            if player.xp >= player.max_xp:
                player.xp -= player.max_xp
                player.level += 1
                player.max_xp = int(player.max_xp * XP_MULTIPLIER)
                
                heal_amount = player.max_hp * 0.20
                player.hp = min(player.max_hp, player.hp + heal_amount)
                
                current_choices = generate_cards(player)
                level_up_active = True

        if not level_up_active:
            frame_count += 1
            player.handle_input()
            player.update_weapons(enemies, projectiles, sword_waves, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams)

            camera.x = player.pos.x - WIDTH / 2
            camera.y = player.pos.y - HEIGHT / 2

            spawn_rate = max(8, 35 - (player.phase * 4))
            if frame_count % spawn_rate == 0:
                enemies.append(Enemy(player.pos, player.phase))

            for p in projectiles[:]:
                p.update() 
                if p.pos.x < 0 or p.pos.x > WORLD_WIDTH or p.pos.y < 0 or p.pos.y > WORLD_HEIGHT: projectiles.remove(p)
            for bm in boomerangs[:]:
                if bm.update(player.pos): boomerangs.remove(bm)
            for ck in chakrams[:]:
                if ck.update(player.pos): chakrams.remove(ck)
            for bo in bouncing_orbs[:]:
                if bo.update(): bouncing_orbs.remove(bo)
            
            for sw in sword_waves[:]:
                if sw.update(): sword_waves.remove(sw)
                
            for fz in fire_zones[:]:
                if fz.update(): fire_zones.remove(fz)
            for lg in lightnings[:]:
                lg.life -= 1
                if lg.life <= 0: lightnings.remove(lg)
            for bm_eff in beams[:]:
                bm_eff.life -= 1
                if bm_eff.life <= 0: beams.remove(bm_eff)
            for bz_eff in blizzards[:]:
                bz_eff.life -= 1
                if bz_eff.life <= 0: blizzards.remove(bz_eff)
            for dt in dmg_texts[:]:
                dt.update()
                if dt.life <= 0: dmg_texts.remove(dt)

            for e in enemies[:]:
                e.update_timers(dmg_texts, player) 
                e.move_towards_player(player.pos, player) 
                
                for p in projectiles[:]:
                    if e.pos.distance_to(p.pos) < e.radius + p.radius and e not in p.hit_targets:
                        e.take_damage(p.damage, dmg_texts)
                        player.damage_stats[p.weapon_id] += p.damage
                        p.hit_targets.append(e)
                        p.pierce -= 1
                        if p.pierce <= 0 and p in projectiles: projectiles.remove(p)
                            
                for sw in sword_waves[:]:
                    if e.pos.distance_to(sw.pos) < e.radius + 50 and e not in sw.hit_targets:
                        e.take_damage(sw.damage, dmg_texts)
                        player.damage_stats[sw.weapon_id] += sw.damage
                        sw.hit_targets.append(e)
                        
                for bm in boomerangs[:]:
                    if e.pos.distance_to(bm.pos) < e.radius + bm.radius and e not in bm.hit_targets:
                        e.take_damage(bm.damage, dmg_texts)
                        player.damage_stats[bm.weapon_id] += bm.damage
                        bm.hit_targets.append(e)
                
                for ck in chakrams[:]:
                    if e.pos.distance_to(ck.pos) < e.radius + ck.radius and e not in ck.hit_targets:
                        e.take_damage(ck.damage, dmg_texts)
                        player.damage_stats[ck.weapon_id] += ck.damage
                        ck.hit_targets.append(e)
                        e.burn_timer = 180
                        e.burn_damage = int(player.weapons["chakram"]["burn_dmg"] * player.get_total_dmg_mult())
                        
                for bo in bouncing_orbs[:]:
                    if e.pos.distance_to(bo.pos) < e.radius + bo.radius and e not in bo.hit_targets:
                        e.take_damage(bo.damage, dmg_texts)
                        player.damage_stats[bo.weapon_id] += bo.damage
                        bo.hit_targets.append(e)
                        
                for fz in fire_zones[:]:
                    if fz.state == "burning": 
                        if e.pos.distance_to(fz.pos) < e.radius + fz.radius:
                            if e.can_receive_tick_damage("firezone", 20):
                                e.take_damage(fz.damage, dmg_texts)
                                player.damage_stats[fz.weapon_id] += fz.damage
                        
                if e.hp <= 0:
                    if e in enemies:
                        enemies.remove(e)
                        player.kills += 1
                        player.phase = (player.kills // KILLS_PER_PHASE) + 1
                        
                        from entities import ExpGem
                        gems.append(ExpGem(e.pos, e.xp_reward))
                        
                for gem in gems[:]:
                    if gem.update(player):
                        player.xp += gem.amount
                        gems.remove(gem)

            if player.hp <= 0:
                state = "GAMEOVER" 

    screen.fill(DARK_BG)
    
    if state in ["PLAY", "PAUSE", "GAMEOVER"]:
        start_x = int(camera.x // 100 * 100)
        start_y = int(camera.y // 100 * 100)
        for x in range(start_x, start_x + WIDTH + 100, 100):
            pygame.draw.line(screen, GRID_COLOR, (x - camera.x, 0), (x - camera.x, HEIGHT))
        for y in range(start_y, start_y + HEIGHT + 100, 100):
            pygame.draw.line(screen, GRID_COLOR, (0, y - camera.y), (WIDTH, y - camera.y))

        border_rect = pygame.Rect(-camera.x, -camera.y, WORLD_WIDTH, WORLD_HEIGHT)
        pygame.draw.rect(screen, WALL_COLOR, border_rect, 15)

        for fz in fire_zones: fz.draw(screen, camera)
        for bz in blizzards: bz.draw(screen, camera)
        for sw in sword_waves: sw.draw(screen, camera)
        for p in projectiles: p.draw(screen, camera)
        for bm in boomerangs: bm.draw(screen, camera)
        for ck in chakrams: ck.draw(screen, camera)
        for bo in bouncing_orbs: bo.draw(screen, camera)
        for lg in lightnings: lg.draw(screen, camera)
        for bm_eff in beams: bm_eff.draw(screen, camera)
        # ... (이전 이펙트 렌더링 코드들)
        for lg in lightnings: lg.draw(screen, camera)
        for bm_eff in beams: bm_eff.draw(screen, camera)
        
        # 👉 [이 줄이 있는지 반드시 확인하고 추가해 주세요!] 👈
        for gem in gems: gem.draw(screen, camera)
        
        for e in enemies: e.draw(screen, camera)
        player.draw(screen, camera)

        if dev_mode and show_mechanics:
            debug_font = pygame.font.SysFont("consolas", 16, bold=True)
            
            if player.weapons["orbit"]["active"]:
                pygame.draw.circle(screen, PURPLE, (int(player.pos.x - camera.x), int(player.pos.y - camera.y)), player.weapons["orbit"]["radius"], 1)
                
            for e in enemies:
                spos = (int(e.pos.x - camera.x), int(e.pos.y - camera.y))
                pygame.draw.circle(screen, (255, 100, 100), spos, e.radius, 1)

            for p in projectiles:
                spos = (int(p.pos.x - camera.x), int(p.pos.y - camera.y))
                epos = (int(p.pos.x + p.dir.x * 20 - camera.x), int(p.pos.y + p.dir.y * 20 - camera.y))
                pygame.draw.line(screen, GREEN, spos, epos, 2)
                
            for ck in chakrams:
                spos = (int(ck.pos.x - camera.x), int(ck.pos.y - camera.y))
                origin = (int(ck.spawn_pos.x - camera.x), int(ck.spawn_pos.y - camera.y))
                pygame.draw.line(screen, (255, 150, 150), spos, origin, 1) 
                txt = debug_font.render(f"[{ck.state.upper()}] T:{ck.timer if ck.state=='outward' else ck.hover_timer}", True, WHITE)
                screen.blit(txt, (spos[0] + 20, spos[1]))
                
            for fz in fire_zones:
                spos = (int(fz.pos.x - camera.x), int(fz.pos.y - camera.y))
                timer = fz.delay if fz.state == "warning" else fz.life
                txt = debug_font.render(f"[{fz.state.upper()}] {timer}F", True, YELLOW)
                screen.blit(txt, (spos[0] - 30, spos[1] + fz.radius + 5))
                
            for bm in boomerangs:
                spos = (int(bm.pos.x - camera.x), int(bm.pos.y - camera.y))
                txt = debug_font.render(f"[{bm.state.upper()}]", True, WHITE)
                screen.blit(txt, (spos[0] + 15, spos[1]))
                
        ui_font = get_korean_font(36)
        for dt in dmg_texts: dt.draw(screen, camera, ui_font)

        hp_text = ui_font.render(f"HP: {max(0, int(player.hp))} / {player.max_hp}", True, WHITE)
        kills_text = ui_font.render(f"KILLS: {player.kills}  (PHASE {player.phase})", True, WHITE)
        dmg_text = ui_font.render(f"DMG MULT: x{player.get_total_dmg_mult():.2f}", True, YELLOW)
        tab_hint = get_korean_font(24).render("[TAB] 키를 눌러 무기별 데미지 통계 확인", True, GREY)
        
        screen.blit(hp_text, (20, 20))
        screen.blit(kills_text, (20, 60))
        screen.blit(dmg_text, (20, 100))
        screen.blit(tab_hint, (20, 150))

        if dev_mode:
            dev_font = get_korean_font(24)
            god_str = "ON" if player.god_mode else "OFF"
            mech_str = "ON" if show_mechanics else "OFF"
            
            dev_msg1 = f"[DEV] F1:종료 | F2:무적({god_str}) | F3:레벨업 | F4:페이즈 점프 | F5:메커니즘 뷰어({mech_str})"
            dev_surf1 = dev_font.render(dev_msg1, True, CYAN)
            screen.blit(dev_surf1, (WIDTH - dev_surf1.get_width() - 20, 20))

            toggles = [
                ("1(검)", "melee"), ("2(오라)", "orbit"), ("3(도끼)", "axe"), 
                ("4(번개)", "lightning"), ("5(레이저)", "beam"), ("6(눈보라)", "blizzard"), 
                ("7(차크람)", "chakram"), ("8(부메랑)", "boomerang"), ("9(마법봉)", "bounce"), ("0(메테오)", "trail")
            ]
            
            title_surf = dev_font.render("무기 토글: ", True, YELLOW)
            rendered_pieces = []
            total_width = title_surf.get_width()
            
            for label, w_id in toggles:
                color = GREEN if player.weapons[w_id]["active"] else GREY
                piece_surf = dev_font.render(label + " ", True, color)
                rendered_pieces.append(piece_surf)
                total_width += piece_surf.get_width()
                
            start_x = WIDTH - total_width - 20
            screen.blit(title_surf, (start_x, 50))
            current_x = start_x + title_surf.get_width()
            
            for piece_surf in rendered_pieces:
                screen.blit(piece_surf, (current_x, 50))
                current_x += piece_surf.get_width()

        # ==========================================
        # [추가] 획득한 무기 인벤토리 UI (화면 하단 중앙)
        # ==========================================
        active_weapons = [(w_id, w_data) for w_id, w_data in player.weapons.items() if w_data["active"]]
        
        if active_weapons:
            slot_w = 56
            slot_h = 56
            gap = 8
            total_w = len(active_weapons) * slot_w + (len(active_weapons) - 1) * gap
            start_x = WIDTH // 2 - total_w // 2
            start_y = HEIGHT - 32 - slot_h - 15  # XP 바(32px) 바로 위에 위치
            
            # 슬롯에 들어갈 무기별 축약 이름
            short_names = {
                "ranged": "마법", "melee": "검기", "orbit": "오라", "axe": "도끼",
                "lightning": "번개", "beam": "레이저", "blizzard": "눈보라",
                "chakram": "차크람", "boomerang": "부메랑", "bounce": "마법봉", "trail": "메테오",
                "storm": "폭풍" 
            }
            
            name_font = get_korean_font(18)
            lv_font = get_korean_font(16)
            
            for i, (w_id, w_data) in enumerate(active_weapons):
                x = start_x + i * (slot_w + gap)
                y = start_y
                
                # 슬롯 배경 및 테두리 렌더링
                pygame.draw.rect(screen, (40, 44, 52), (x, y, slot_w, slot_h), border_radius=6)
                pygame.draw.rect(screen, (100, 105, 120), (x, y, slot_w, slot_h), 2, border_radius=6)
                
                # 무기 이름 렌더링 (가운데 정렬)
                n_str = short_names.get(w_id, "무기")
                n_surf = name_font.render(n_str, True, WHITE)
                screen.blit(n_surf, (x + slot_w // 2 - n_surf.get_width() // 2, y + 10))
                
                # 무기 레벨 렌더링 (MAX 달성 시 노란색으로 강조)
                is_max = w_data["level"] >= w_data["max_level"]
                lv_str = "MAX" if is_max else f"Lv.{w_data['level']}"
                lv_color = YELLOW if is_max else CYAN
                lv_surf = lv_font.render(lv_str, True, lv_color)
                screen.blit(lv_surf, (x + slot_w // 2 - lv_surf.get_width() // 2, y + 32))

        # XP 바 렌더링
        xp_bar_height = 32  
        xp_rect_y = HEIGHT - xp_bar_height
        pygame.draw.rect(screen, (30, 30, 40), (0, xp_rect_y, WIDTH, xp_bar_height))
        xp_ratio = max(0.0, min(1.0, player.xp / player.max_xp))
        pygame.draw.rect(screen, YELLOW, (0, xp_rect_y, int(WIDTH * xp_ratio), xp_bar_height))
        pygame.draw.line(screen, GREY, (0, xp_rect_y), (WIDTH, xp_rect_y), 2)
        
        xp_font = get_korean_font(20)
        xp_lbl = xp_font.render(f"Lv.{player.level}  [ {int(player.xp)} / {player.max_xp} XP ]", True, BLACK)
        text_x = WIDTH // 2 - xp_lbl.get_width() // 2
        text_y = xp_rect_y + (xp_bar_height // 2) - (xp_lbl.get_height() // 2)
        screen.blit(xp_lbl, (text_x, text_y))

    if state == "TITLE":
        title_font = get_korean_font(80)
        btn_font = get_korean_font(40)
        
        title_surf = title_font.render("PYTHON SURVIVOR", True, YELLOW)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3 - 80))

        buttons = [
            (btn_start, "게임 시작"),
            (btn_options, "옵션"),
            (btn_quit, "게임 종료")
        ]
        
        for rect, text in buttons:
            is_hover = rect.collidepoint(mouse_pos)
            color_bg = (70, 75, 90) if is_hover else (40, 44, 52)
            color_border = YELLOW if is_hover else WHITE
            
            pygame.draw.rect(screen, color_bg, rect, 0, 10)
            pygame.draw.rect(screen, color_border, rect, 3, 10)
            
            text_surf = btn_font.render(text, True, color_border)
            screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2, rect.centery - text_surf.get_height() // 2))

    elif state == "OPTIONS":
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 200))
        screen.blit(dim_mask, (0, 0))
        
        opt_font = get_korean_font(80)
        sub_font = get_korean_font(30)
        opt_surf = opt_font.render("OPTIONS", True, CYAN)
        sub_surf = sub_font.render("준비 중입니다. ESC 키를 눌러 뒤로 가기", True, WHITE)
        screen.blit(opt_surf, (WIDTH // 2 - opt_surf.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 2 + 50))

    elif state == "PAUSE":
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 180))
        screen.blit(dim_mask, (0, 0))
        
        pause_font = get_korean_font(100)
        sub_font = get_korean_font(30)
        pause_surf = pause_font.render("PAUSED", True, CYAN)
        sub_surf = sub_font.render("ESC 키를 눌러 계속하기", True, WHITE)
        screen.blit(pause_surf, (WIDTH // 2 - pause_surf.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, HEIGHT // 2 + 50))

    elif state == "PLAY" and level_up_active:
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 200))
        screen.blit(dim_mask, (0, 0))
        
        title_font = get_korean_font(64)
        sub_font = get_korean_font(26)
        title_surf = title_font.render("LEVEL UP STIMULUS", True, YELLOW)
        sub_surf = sub_font.render("숫자키(1, 2, 3) 또는 마우스로 카드를 선택하세요.", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 80))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 160))
        
        for idx, rect in enumerate(card_rects):
            if idx >= len(current_choices): break
            choice_data = current_choices[idx]
            
            card_color = (70, 75, 90) if rect.collidepoint(mouse_pos) else (40, 44, 52)
            pygame.draw.rect(screen, card_color, rect, 0, 14)
            pygame.draw.rect(screen, WHITE, rect, 3, 14)
            
            num_surf = get_korean_font(30).render(f"[{idx + 1}]", True, CYAN)
            screen.blit(num_surf, (rect.centerx - num_surf.get_width() // 2, rect.y - 45))
            
            # ==========================================
            # [신규] 카테고리 태그(뱃지) UI 렌더링
            # ==========================================
            tag_dict = {
                "unlock": ("신규 무기", GREEN),
                "upgrade": ("무기 강화", YELLOW),
                "stat": ("기본 스탯", BLUE),
                "consumable": ("일회성", RED),
                "union": ("합체 진화", PURPLE)
            }
            
            c_type = choice_data.get("type", "stat")
            tag_text, tag_color = tag_dict.get(c_type, ("강화", WHITE))
            
            tag_font = get_korean_font(18)
            tag_surf = tag_font.render(tag_text, True, tag_color)
            
            # 태그의 배경(뱃지 형태)을 그립니다.
            tag_rect = pygame.Rect(rect.centerx - tag_surf.get_width()//2 - 10, rect.y + 15, tag_surf.get_width() + 20, tag_surf.get_height() + 10)
            pygame.draw.rect(screen, (30, 30, 35), tag_rect, border_radius=5)
            pygame.draw.rect(screen, tag_color, tag_rect, 1, border_radius=5)
            screen.blit(tag_surf, (rect.centerx - tag_surf.get_width()//2, rect.y + 20))
            
            # ==========================================
            
            card_title_font = get_korean_font(24)
            name_surf = card_title_font.render(choice_data["name"], True, YELLOW)
            # 태그가 공간을 차지하므로 타이틀 Y축 위치를 +50에서 +65로 내림
            screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 65)) 
            
            desc_font = get_korean_font(20)
            max_width = rect.width - 30 
            lines = []
            
            for paragraph in choice_data["desc"].split('\n'):
                current_line = ""
                for char in paragraph:
                    test_line = current_line + char
                    if desc_font.size(test_line)[0] > max_width:
                        lines.append(current_line)
                        current_line = char
                    else:
                        current_line = test_line
                
                if current_line:
                    lines.append(current_line)
            
            # 설명란 Y축 위치도 +110에서 +115로 약간 내림
            # 설명란 Y축 위치 설정 및 출력
            y_offset = rect.y + 115 
            for i, line_text in enumerate(lines):
                # 첫 줄/나머지 줄 구분 없이 전부 WHITE(흰색)로 통일하여 출력합니다.
                desc_surf = desc_font.render(line_text.strip(), True, WHITE)
                screen.blit(desc_surf, (rect.centerx - desc_surf.get_width() // 2, y_offset))
                y_offset += 28

    elif state == "GAMEOVER":
        dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_mask.fill((0, 0, 0, 180))
        screen.blit(dim_mask, (0, 0))
        
        go_font = get_korean_font(100)
        go_text = go_font.render("GAME OVER", True, RED)
        stat_text = ui_font.render(f"도달한 페이즈: {player.phase} | 총 처치 수: {player.kills}", True, WHITE)
        restart_text = ui_font.render("R 키를 눌러 타이틀로 돌아가기", True, YELLOW)
        
        screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 100))
        screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, HEIGHT // 2 + 20))
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 80))

    if state in ["PLAY", "PAUSE", "GAMEOVER"]:
        if pygame.key.get_pressed()[pygame.K_TAB]:
            dim_mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim_mask.fill((0, 0, 0, 230)) 
            screen.blit(dim_mask, (0, 0))
            
            title_font = get_korean_font(60)
            dps_ui_font = get_korean_font(30)
            
            dps_title = title_font.render("DAMAGE STATISTICS", True, YELLOW)
            screen.blit(dps_title, (WIDTH // 2 - dps_title.get_width() // 2, 100))
            
            total_dmg = sum(player.damage_stats.values())
            total_dmg_safe = max(1, total_dmg) 
            
            sorted_stats = sorted(player.damage_stats.items(), key=lambda x: x[1], reverse=True)
            
            y_offset = 200
            for w_id, dmg in sorted_stats:
                if dmg == 0 and not player.weapons[w_id]["active"]: 
                    continue
                
                w_name = player.weapons[w_id]["name"]
                percent = (dmg / total_dmg_safe) * 100
                
                name_surf = dps_ui_font.render(w_name, True, WHITE)
                dmg_surf = dps_ui_font.render(f"{dmg:,} ({percent:.1f}%)", True, CYAN)
                
                screen.blit(name_surf, (WIDTH // 2 - 350, y_offset))
                screen.blit(dmg_surf, (WIDTH // 2 + 150, y_offset))
                
                bar_width = 460
                pygame.draw.rect(screen, (60, 60, 60), (WIDTH // 2 - 350, y_offset + 40, bar_width, 15), border_radius=5)
                pygame.draw.rect(screen, YELLOW, (WIDTH // 2 - 350, y_offset + 40, int(bar_width * (dmg / total_dmg_safe)), 15), border_radius=5)
                
                y_offset += 75

    pygame.display.flip()

pygame.quit()
sys.exit()