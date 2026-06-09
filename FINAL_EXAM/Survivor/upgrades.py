import random

UPGRADE_POOL = [
    # 1. 공통 스탯 및 소모품
    {"id": "hp_up",       "type": "stat", "target_weapon": None, "name": "Vitality Core", "desc": "플레이어의 최대 체력이 +20 증가합니다."},
    {"id": "speed_up",    "type": "stat", "target_weapon": None, "name": "Adrenaline Drive", "desc": "기본 이동 속도가 10% 증가합니다."},
    {"id": "global_dmg",  "type": "stat", "target_weapon": None, "name": "Overwhelm", "desc": "전역 공격력 스탯이 15% 상승합니다."},
    {"id": "screen_bomb", "type": "consumable", "target_weapon": None, "name": "Nuke: Annihilation", "desc": "[일회성] 맵 상의 모든 적을 즉시 처치합니다."},

    # 2. 신규 무기 해금 (Unlock)
    {"id": "unlock_melee", "type": "unlock",  "target_weapon": "melee", "name": "NEW: Spirit Sword", "desc": "스피릿 소드를 장착합니다. 전방으로 적을 관통하는 검기를 날립니다."},
    {"id": "unlock_orbit", "type": "unlock",  "target_weapon": "orbit", "name": "NEW: Orbiting Shield", "desc": "오라 실드를 개방합니다. 주변을 회전하며 피해를 줍니다."},
    {"id": "unlock_axe",   "type": "unlock",  "target_weapon": "axe", "name": "NEW: Heavy Axe", "desc": "관통하는 강력한 둔탁 도끼를 던집니다."},
    {"id": "unlock_lightning", "type": "unlock",  "target_weapon": "lightning", "name": "NEW: Chain Lightning", "desc": "가까운 적을 타격 후 연쇄 전이되는 번개를 쏩니다."},
    {"id": "unlock_beam", "type": "unlock",  "target_weapon": "beam", "name": "NEW: Orbital Beam", "desc": "조준 방향으로 화면을 뚫는 궤도 레이저를 방출합니다."},
    {"id": "unlock_blizzard", "type": "unlock",  "target_weapon": "blizzard", "name": "NEW: Blizzard", "desc": "광역 눈보라를 일으켜 닿은 적들을 빙결시킵니다."},
    {"id": "unlock_chakram", "type": "unlock",  "target_weapon": "chakram", "name": "NEW: Hellfire Chakram", "desc": "적을 관통 후 체공하다 최초 위치로 돌아오는 차크람 3개를 던집니다."},
    {"id": "unlock_boomerang", "type": "unlock", "target_weapon": "boomerang", "name": "NEW: Boomerang", "desc": "적들을 뚫고 되돌아오는 부메랑을 던집니다."},
    {"id": "unlock_bounce",    "type": "unlock", "target_weapon": "bounce",    "name": "NEW: Magic Wand", "desc": "벽에 닿으면 튕기는 마법 구체를 쏩니다."},
    {"id": "unlock_trail",     "type": "unlock", "target_weapon": "trail",     "name": "NEW: Meteor Strike", "desc": "적을 타겟팅하여 하늘에서 메테오를 떨어뜨립니다."},

    # 3. 통합 무기 강화 (Upgrade)
    {"id": "upgrade_ranged",   "type": "upgrade", "target_weapon": "ranged", "name": "Magic: Evolution", "desc": "마법 구체의 타격 데미지가 +2 증가하고, 동시 발사 개수가 +2개 늘어납니다."},
    {"id": "upgrade_melee",    "type": "upgrade", "target_weapon": "melee", "name": "Sword: Mastery", "desc": "검기 공격력이 +15 증가합니다. (Lv.3 도달 시 후방으로도 추가 발사)"},
    {"id": "upgrade_orbit",    "type": "upgrade", "target_weapon": "orbit", "name": "Shield: Overcharge", "desc": "위성 충돌 데미지가 +3, 주변을 도는 위성 개수가 +1 증가합니다."},
    {"id": "upgrade_axe",      "type": "upgrade", "target_weapon": "axe", "name": "Axe: Brutal", "desc": "도끼 데미지가 +20 폭증하고 투척 쿨타임이 15% 감소합니다."},
    {"id": "upgrade_lightning","type": "upgrade", "target_weapon": "lightning", "name": "Lightning: Storm", "desc": "번개 데미지가 +10, 최대 전이 +1, 시작 번개 줄기가 +1 증가합니다."},
    {"id": "upgrade_beam",     "type": "upgrade", "target_weapon": "beam", "name": "Beam: Annihilation", "desc": "레이저 데미지 +40, 두께가 +10 증가하고 쿨타임이 15% 감소합니다."},
    {"id": "upgrade_blizzard", "type": "upgrade", "target_weapon": "blizzard", "name": "Blizzard: Deep Chill", "desc": "눈보라 틱 데미지가 +5 증가하고, 광역 빙결 반경이 크게 늘어납니다."},
    {"id": "upgrade_chakram",  "type": "upgrade", "target_weapon": "chakram", "name": "Chakram: Hellfire", "desc": "차크람 관통 데미지가 +10, 화상 지속 데미지가 +5 증가합니다."},
    {"id": "upgrade_boomerang","type": "upgrade", "target_weapon": "boomerang", "name": "Boomerang: Swift", "desc": "부메랑의 왕복 타격 데미지가 +15 증가합니다."},
    {"id": "upgrade_bounce",   "type": "upgrade", "target_weapon": "bounce", "name": "Wand: Resonance", "desc": "마법봉(통통탄)의 타격 데미지가 +15 증가합니다."},
    {"id": "upgrade_trail",    "type": "upgrade", "target_weapon": "trail", "name": "Meteor: Cataclysm", "desc": "메테오의 직격 데미지 및 장판 틱 데미지가 +15 증가합니다."},
    {"id": "union_storm", "type": "union", "target_weapon": "storm", "name": "UNION: Elemental Storm", "desc": "[합체!] 눈보라와 차크람을 융합하여 얼음과 불의 거대 폭풍을 발생시킵니다."}
]

def get_filtered_standard_pool(player):
    pool = []
    for card in UPGRADE_POOL:
        if card["type"] in ["stat", "consumable"]:
            pool.append(card)
        elif card["type"] == "upgrade":
            w_id = card["target_weapon"]
            weapon = player.weapons[w_id]
            # 무기가 활성화되어 있고, 아직 만렙이 아닐 때만 풀에 추가
            if weapon["active"] and weapon["level"] < weapon["max_level"]:
                dynamic_card = card.copy()
                next_lv = weapon["level"] + 1
                # 카드 이름 뒤에 (Lv.2) 형식으로 목표 레벨 텍스트 동적 추가
                dynamic_card["name"] = f"{card['name']} (Lv.{next_lv})"
                pool.append(dynamic_card)
    return pool

def generate_cards(player):
    standard_pool = get_filtered_standard_pool(player)
    unlock_pool = [c for c in UPGRADE_POOL if c["type"] == "unlock" and not player.weapons[c["target_weapon"]]["active"]]
    
    # =======================================================
    # [1순위] 합체 무기(Union) 조건 검사
    # 두 무기가 모두 만렙(5)이고, 아직 합체 무기가 활성화되지 않았다면 무조건 등장
    # =======================================================
    union_pool = []
    if player.weapons["blizzard"]["level"] >= 5 and player.weapons["chakram"]["level"] >= 5 and not player.weapons["storm"]["active"]:
        union_card = next((c for c in UPGRADE_POOL if c["id"] == "union_storm"), None)
        if union_card: union_pool.append(union_card)
        
    if union_pool:
        guaranteed_card = union_pool[0]
        other_choices = random.sample(standard_pool, min(2, len(standard_pool)))
        final_cards = [guaranteed_card] + other_choices
        random.shuffle(final_cards) 
        return final_cards

    # =======================================================
    # [2순위] 기존 4레벨 주기 신규 무기 해금 검사
    # =======================================================
    needs_unlock = (player.level % 4 == 0)
    
    if needs_unlock and unlock_pool:
        guaranteed_weapon = random.choice(unlock_pool)
        
        if len(standard_pool) >= 2:
            other_choices = random.sample(standard_pool, 2)
        else:
            other_choices = standard_pool[:]
            remaining_unlocks = [c for c in unlock_pool if c["id"] != guaranteed_weapon["id"]]
            fill_amount = 2 - len(other_choices)
            if remaining_unlocks and fill_amount > 0:
                other_choices.extend(random.sample(remaining_unlocks, min(fill_amount, len(remaining_unlocks))))
        
        final_cards = [guaranteed_weapon] + other_choices
        random.shuffle(final_cards) 
        return final_cards
    else:
        return random.sample(standard_pool, min(3, len(standard_pool)))

def apply_card_effect(player, card_id, enemies=None):
    if card_id == "screen_bomb":
        if enemies is not None:
            for e in enemies:
                player.kills += 1
                player.xp += (e.xp_reward * 0.5)
            enemies.clear()
    elif card_id == "hp_up": player.max_hp += 20; player.hp += 20
    elif card_id == "speed_up": player.speed *= 1.10
    elif card_id == "global_dmg": player.global_dmg_mult += 0.15
    
    # 무기 해금 로직 (startswith를 사용하여 코드 10줄을 하나로 통합)
    elif card_id.startswith("unlock_"):
        w_id = card_id.replace("unlock_", "")
        if w_id in player.weapons:
            player.weapons[w_id]["active"] = True
            
    # 통합 무기 업그레이드 수치 적용 로직
    elif card_id == "upgrade_ranged":
        player.weapons["ranged"]["level"] += 1
        player.weapons["ranged"]["base_damage"] += 2  # 기존 +5에서 +2로 하향 (밸런스 조절)
        player.weapons["ranged"]["count"] += 2        # 기존 +1에서 +2로 상향 (샷건화)
        
    elif card_id == "upgrade_melee":
        player.weapons["melee"]["level"] += 1
        player.weapons["melee"]["base_damage"] += 15
        if player.weapons["melee"]["level"] >= 3:
            player.weapons["melee"]["rear"] = True
            
    elif card_id == "upgrade_orbit":
        player.weapons["orbit"]["level"] += 1
        player.weapons["orbit"]["base_damage"] += 3
        player.weapons["orbit"]["count"] += 1
        
    elif card_id == "upgrade_axe":
        player.weapons["axe"]["level"] += 1
        player.weapons["axe"]["base_damage"] += 20
        player.weapons["axe"]["cooldown"] = int(player.weapons["axe"]["cooldown"] * 0.85)
        
    elif card_id == "upgrade_lightning":
        player.weapons["lightning"]["level"] += 1
        player.weapons["lightning"]["base_damage"] += 10
        player.weapons["lightning"]["chain_count"] += 1
        player.weapons["lightning"]["bolt_count"] += 1

    elif card_id == "upgrade_beam":
        player.weapons["beam"]["level"] += 1
        player.weapons["beam"]["base_damage"] += 40
        player.weapons["beam"]["width"] += 10
        player.weapons["beam"]["cooldown"] = int(player.weapons["beam"]["cooldown"] * 0.85)
        
    elif card_id == "upgrade_blizzard":
        player.weapons["blizzard"]["level"] += 1
        player.weapons["blizzard"]["base_damage"] += 5
        player.weapons["blizzard"]["radius"] += 25
        
    elif card_id == "upgrade_chakram":
        player.weapons["chakram"]["level"] += 1
        player.weapons["chakram"]["base_damage"] += 10
        player.weapons["chakram"]["burn_dmg"] += 5
        
    elif card_id == "upgrade_boomerang":
        player.weapons["boomerang"]["level"] += 1
        player.weapons["boomerang"]["base_damage"] += 15
        
    elif card_id == "upgrade_bounce":
        player.weapons["bounce"]["level"] += 1
        player.weapons["bounce"]["base_damage"] += 15
        
    elif card_id == "upgrade_trail":
        player.weapons["trail"]["level"] += 1
        player.weapons["trail"]["base_damage"] += 15
        
    elif card_id == "union_storm":
        player.weapons["storm"]["active"] = True
        player.weapons["blizzard"]["active"] = False
        player.weapons["chakram"]["active"] = False