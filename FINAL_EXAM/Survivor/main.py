import pygame
import sys
from Sub_config import *
from utils import get_korean_font
from entities import Player, Enemy
from upgrades import generate_cards, apply_card_effect

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Survivor - Inherent Scaling")
clock = pygame.time.Clock()

def reset_game():
    global player, enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams
    global camera, frame_count, level_up_active
    player = Player()
    enemies = []
    projectiles = []
    slashes = []  
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

dev_mode = False
running = True
current_choices = []
state = "TITLE" 

while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if state == "TITLE":
                if event.key == pygame.K_SPACE:
                    reset_game()
                    state = "PLAY"
            elif state == "GAMEOVER":
                if event.key == pygame.K_r: state = "TITLE" 
            elif state == "PAUSE":
                if event.key == pygame.K_ESCAPE: state = "PLAY" 
            elif state == "PLAY":
                if not level_up_active:
                    if event.key == pygame.K_ESCAPE: state = "PAUSE"
                    elif event.key == pygame.K_F1: dev_mode = not dev_mode
                    elif event.key == pygame.K_F2: player.god_mode = not player.god_mode
                    elif event.key == pygame.K_F3: player.xp = player.max_xp
                    elif event.key == pygame.K_F4: 
                        player.kills += KILLS_PER_PHASE
                        player.phase = (player.kills // KILLS_PER_PHASE) + 1

        if state == "PLAY" and level_up_active:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, rect in enumerate(card_rects):
                    if idx < len(current_choices) and rect.collidepoint(mouse_pos):
                        apply_card_effect(player, current_choices[idx]["id"], enemies)
                        level_up_active = False
                        break

    if state == "PLAY":
        if not level_up_active:
            if player.xp >= player.max_xp:
                player.xp -= player.max_xp
                player.level += 1
                player.max_xp = int(player.max_xp * XP_MULTIPLIER)
                current_choices = generate_cards(player)
                level_up_active = True

        if not level_up_active:
            frame_count += 1
            player.handle_input()
            player.update_weapons(enemies, projectiles, slashes, dmg_texts, boomerangs, bouncing_orbs, fire_zones, lightnings, beams, blizzards, chakrams)

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
            
            for fz in fire_zones[:]:
                fz.life -= 1
                if fz.life <= 0: fire_zones.remove(fz)
            for slash in slashes[:]:
                slash.life -= 1
                if slash.life <= 0: slashes.remove(slash)
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
                e.update_timers(dmg_texts) 
                e.move_towards_player(player.pos, player) 
                
                for p in projectiles[:]:
                    if e.pos.distance_to(p.pos) < e.radius + p.radius and e not in p.hit_targets:
                        e.take_damage(p.damage, dmg_texts)
                        p.hit_targets.append(e)
                        p.pierce -= 1
                        if p.pierce <= 0 and p in projectiles: projectiles.remove(p)
                            
                for bm in boomerangs[:]:
                    if e.pos.distance_to(bm.pos) < e.radius + bm.radius and e not in bm.hit_targets:
                        e.take_damage(bm.damage, dmg_texts)
                        bm.hit_targets.append(e)
                
                for ck in chakrams[:]:
                    if e.pos.distance_to(ck.pos) < e.radius + ck.radius and e not in ck.hit_targets:
                        e.take_damage(ck.damage, dmg_texts)
                        ck.hit_targets.append(e)
                        e.burn_timer = 180
                        # [적용] 화상 데미지에도 페이즈 공격력 상승분을 똑같이 적용시켜줍니다.
                        e.burn_damage = int(player.weapons["chakram"]["burn_dmg"] * player.get_total_dmg_mult())
                        
                for bo in bouncing_orbs[:]:
                    if e.pos.distance_to(bo.pos) < e.radius + bo.radius and e not in bo.hit_targets:
                        e.take_damage(bo.damage, dmg_texts)
                        bo.hit_targets.append(e)
                        
                for fz in fire_zones[:]:
                    if e.pos.distance_to(fz.pos) < e.radius + fz.radius:
                        if e.can_receive_tick_damage("firezone", 20):
                            e.take_damage(fz.damage, dmg_texts)
                        
                if e.hp <= 0:
                    if e in enemies:
                        enemies.remove(e)
                        player.kills += 1
                        player.phase = (player.kills // KILLS_PER_PHASE) + 1
                        player.xp += e.xp_reward

            if player.hp <= 0:
                state = "GAMEOVER" 

    # ==========================================
    # 화면 렌더링 파트
    # ==========================================
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
        for slash in slashes: slash.draw(screen, camera)
        for p in projectiles: p.draw(screen, camera)
        for bm in boomerangs: bm.draw(screen, camera)
        for ck in chakrams: ck.draw(screen, camera)
        for bo in bouncing_orbs: bo.draw(screen, camera)
        for lg in lightnings: lg.draw(screen, camera)
        for bm_eff in beams: bm_eff.draw(screen, camera)
        
        for e in enemies: e.draw(screen, camera)
        player.draw(screen, camera)
        
        ui_font = get_korean_font(36)
        for dt in dmg_texts: dt.draw(screen, camera, ui_font)

        hp_text = ui_font.render(f"HP: {max(0, int(player.hp))} / {player.max_hp}", True, WHITE)
        kills_text = ui_font.render(f"KILLS: {player.kills}  (PHASE {player.phase})", True, WHITE)
        # [적용] UI에 보이는 데미지 계수도 자동 상승분을 적용하여 렌더링되게 변경
        dmg_text = ui_font.render(f"DMG MULT: x{player.get_total_dmg_mult():.2f}", True, YELLOW)
        
        screen.blit(hp_text, (20, 20))
        screen.blit(kills_text, (20, 60))
        screen.blit(dmg_text, (20, 100))

        if dev_mode:
            dev_font = get_korean_font(24)
            god_str = "ON" if player.god_mode else "OFF"
            dev_msg = f"[개발자 모드] F1:끄기 | F2:무적({god_str}) | F3:레벨업 | F4:페이즈 점프"
            dev_surf = dev_font.render(dev_msg, True, CYAN)
            screen.blit(dev_surf, (WIDTH - dev_surf.get_width() - 20, 20))

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
        sub_font = get_korean_font(30)
        title_surf = title_font.render("PYTHON SURVIVOR", True, YELLOW)
        sub_surf = sub_font.render("스페이스바를 눌러 게임 시작", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 3))
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
        sub_surf = sub_font.render("아래의 옵션 중 하나를 선택하여 캐릭터를 진화시키세요.", True, WHITE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 110))
        screen.blit(sub_surf, (WIDTH // 2 - sub_surf.get_width() // 2, 185))
        
        for idx, rect in enumerate(card_rects):
            if idx >= len(current_choices): break
            choice_data = current_choices[idx]
            
            card_color = (70, 75, 90) if rect.collidepoint(mouse_pos) else (40, 44, 52)
            pygame.draw.rect(screen, card_color, rect, 0, 14)
            pygame.draw.rect(screen, WHITE, rect, 3, 14)
            
            name_surf = ui_font.render(choice_data["name"], True, YELLOW)
            screen.blit(name_surf, (rect.centerx - name_surf.get_width() // 2, rect.y + 50))
            
            desc_font = get_korean_font(20)
            max_width = rect.width - 30 
            words = choice_data["desc"].replace('\n', ' ').split(' ')
            lines, current_line = [], ""
            
            for word in words:
                test_line = current_line + word + " "
                if desc_font.size(test_line)[0] < max_width: current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
            y_offset = rect.y + 140
            for i, line_text in enumerate(lines):
                color = WHITE if i == 0 else GREY
                desc_surf = desc_font.render(line_text.strip(), True, color)
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

    pygame.display.flip()

pygame.quit()
sys.exit()