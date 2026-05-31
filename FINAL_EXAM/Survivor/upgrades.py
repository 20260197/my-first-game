import random

UPGRADE_POOL = [
    {"id": "hp_up",       "type": "stat", "target_weapon": None, "name": "Vitality Core", "desc": "Max HP +20 수치를 획득하고 체력을 전부 회복합니다."},
    {"id": "speed_up",    "type": "stat", "target_weapon": None, "name": "Adrenaline Drive", "desc": "플레이어 기본 기동 이동 속도가 10% 증가합니다."},
    {"id": "global_dmg",  "type": "stat", "target_weapon": None, "name": "Overwhelm", "desc": "플레이어 전역 공격력 스탯 계수가 15% 추가 상승합니다."},
    {"id": "screen_bomb", "type": "consumable", "target_weapon": None, "name": "Nuke: Annihilation", "desc": "[일회성] 맵 상의 모든 적을 즉시 처치합니다.\n(단, 폭사된 적의 경험치는 50%만 획득)"},
    
    {"id": "ranged_dmg",   "type": "upgrade", "target_weapon": "ranged", "name": "Magic: Overload", "desc": "원거리 마법 구체의 기본 공격력을 +6 추가합니다."},
    # [수정] 2개씩 추가되도록 설명 변경
    {"id": "ranged_count", "type": "upgrade", "target_weapon": "ranged", "name": "Magic: Multi-Shot", "desc": "마법 구체의 동시 발사 개수가 +2개 추가되어 양옆으로 퍼집니다."},
    {"id": "melee_dmg",    "type": "upgrade", "target_weapon": "melee", "name": "Sword: Sharpen", "desc": "스피릿 소드의 절단 베기 기본 공격력을 +15 추가합니다."},
    {"id": "melee_rear",   "type": "upgrade", "target_weapon": "melee", "name": "Sword: Backslash", "desc": "전방뿐만 아니라 뒤쪽으로도 검을 동시에 휘두릅니다."},
    {"id": "orbit_dmg",    "type": "upgrade", "target_weapon": "orbit", "name": "Shield: Dense Plasma", "desc": "위성 오라가 적과 충돌 시 가하는 틱 데미지가 +3 증가합니다."},
    {"id": "orbit_count",  "type": "upgrade", "target_weapon": "orbit", "name": "Shield: Replication", "desc": "플레이어 주변을 맴도는 위성의 개수가 +1 증가합니다."},
    {"id": "axe_dmg",      "type": "upgrade", "target_weapon": "axe", "name": "Axe: Brutal Weight", "desc": "도끼 투척의 데미지가 무식하게 +20 증가합니다."},
    {"id": "axe_haste",    "type": "upgrade", "target_weapon": "axe", "name": "Axe: Quick Throw", "desc": "도끼 투척 쿨타임이 20% 빨라집니다."},
    {"id": "lightning_dmg",   "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: High Voltage", "desc": "체인 라이트닝의 기본 데미지가 +10 증가합니다."},
    {"id": "lightning_chain", "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: Conductor", "desc": "번개가 전이되는 최대 적의 수가 +2명 늘어납니다."},
    {"id": "lightning_bolt",  "type": "upgrade", "target_weapon": "lightning", "name": "Lightning: Dual Strike", "desc": "한 번에 쏘아내는 시작 번개의 줄기 수가 +1개 증가합니다."},

    {"id": "beam_dmg",     "type": "upgrade", "target_weapon": "beam",     "name": "Beam: Overcharge", "desc": "궤도 레이저의 한 방 데미지가 +50 증가합니다."},
    {"id": "beam_width",   "type": "upgrade", "target_weapon": "beam",     "name": "Beam: Wide Lens",  "desc": "궤도 레이저의 폭(두께)이 더 굵어집니다."},
    {"id": "blizzard_rad", "type": "upgrade", "target_weapon": "blizzard", "name": "Blizzard: Deep Chill", "desc": "눈보라의 광역 범위가 크게 늘어납니다."},
    {"id": "chakram_burn", "type": "upgrade", "target_weapon": "chakram",  "name": "Chakram: Hellfire", "desc": "차크람에 맞은 적이 초당 입는 화상 데미지가 +5 증가합니다."},

    {"id": "unlock_melee",     "type": "unlock", "target_weapon": "melee",     "name": "NEW: Spirit Sword", "desc": "스피릿 소드를 장착합니다. 광역 베기로 근접 적을 섬멸합니다."},
    {"id": "unlock_orbit",     "type": "unlock", "target_weapon": "orbit",     "name": "NEW: Orbiting Shield", "desc": "오라 실드를 개방합니다. 주변을 회전하며 근접 접근을 저지합니다."},
    {"id": "unlock_axe",       "type": "unlock", "target_weapon": "axe",       "name": "NEW: Heavy Axe", "desc": "다수의 몬스터를 뚫고 지나가는 강력한 둔탁 도끼를 던집니다."},
    {"id": "unlock_boomerang", "type": "unlock", "target_weapon": "boomerang", "name": "NEW: Boomerang", "desc": "적들을 뚫고 공격한 뒤 다시 되돌아오는 부메랑을 던집니다."},
    {"id": "unlock_bounce",    "type": "unlock", "target_weapon": "bounce",    "name": "NEW: Magic Wand", "desc": "맵의 벽 구조물에 닿으면 각도를 꺾어 튕기는 구체를 쏩니다."},
    {"id": "unlock_trail",     "type": "unlock", "target_weapon": "trail",     "name": "NEW: Meteor Strike", "desc": "플레이어 주변 무작위 위치에 3개의 화염 장판을 동시에 투하합니다."},
    
    {"id": "unlock_lightning", "type": "unlock", "target_weapon": "lightning", "name": "NEW: Chain Lightning", "desc": "가장 가까운 적을 타격 후 주변 적에게 연쇄 전이되는 번개를 쏩니다."},
    {"id": "unlock_beam",     "type": "unlock", "target_weapon": "beam",     "name": "NEW: Orbital Beam", "desc": "조준 방향으로 맵 끝까지 닿는 빛의 궤도 레이저를 즉시 방출합니다."},
    {"id": "unlock_blizzard", "type": "unlock", "target_weapon": "blizzard", "name": "NEW: Blizzard", "desc": "광역 눈보라 고리를 일으켜 닿은 적들을 빙결시키고 이속을 절반으로 낮춥니다."},
    {"id": "unlock_chakram",  "type": "unlock", "target_weapon": "chakram",  "name": "NEW: Hellfire Chakram", "desc": "적을 뚫고 돌아오며, 닿은 적에게 화상을 입혀 지속 피해를 주는 차크람입니다."}
]

def get_filtered_standard_pool(player):
    pool = []
    for card in UPGRADE_POOL:
        if card["type"] in ["stat", "consumable"]:
            pool.append(card)
        elif card["type"] == "upgrade":
            if player.weapons[card["target_weapon"]]["active"]:
                # [수정] 2개씩 추가되므로 최대 제한을 9로 변경 (1 -> 3 -> 5 -> 7 -> 9)
                if card["id"] == "ranged_count" and player.weapons["ranged"]["count"] >= 9: continue
                if card["id"] == "melee_rear" and player.weapons["melee"]["rear"]: continue
                pool.append(card)
    return pool

def generate_cards(player):
    if player.level % 5 == 0:
        unlock_pool = [c for c in UPGRADE_POOL if c["type"] == "unlock" and not player.weapons[c["target_weapon"]]["active"]]
        standard_pool = get_filtered_standard_pool(player)
        
        if unlock_pool:
            guaranteed_weapon = random.choice(unlock_pool)
            other_choices = random.sample(standard_pool, min(2, len(standard_pool)))
            final_cards = [guaranteed_weapon] + other_choices
            random.shuffle(final_cards) 
            return final_cards
        else:
            return random.sample(standard_pool, min(3, len(standard_pool)))
    else:
        standard_pool = get_filtered_standard_pool(player)
        return random.sample(standard_pool, min(3, len(standard_pool)))

def apply_card_effect(player, card_id, enemies=None):
    if card_id == "screen_bomb":
        if enemies is not None:
            for e in enemies:
                player.kills += 1
                player.xp += (e.xp_reward * 0.5)
            enemies.clear()
            
    elif card_id == "hp_up": player.max_hp += 20; player.hp = player.max_hp
    elif card_id == "speed_up": player.speed *= 1.10
    elif card_id == "global_dmg": player.global_dmg_mult += 0.15
        
    elif card_id == "ranged_dmg": player.weapons["ranged"]["base_damage"] += 6
    # [수정] 효과 적용 시 +2 증가
    elif card_id == "ranged_count": player.weapons["ranged"]["count"] += 2
    elif card_id == "melee_dmg": player.weapons["melee"]["base_damage"] += 15
    elif card_id == "melee_rear": player.weapons["melee"]["rear"] = True
    elif card_id == "orbit_dmg": player.weapons["orbit"]["base_damage"] += 3
    elif card_id == "orbit_count": player.weapons["orbit"]["count"] += 1
    elif card_id == "axe_dmg": player.weapons["axe"]["base_damage"] += 20
    elif card_id == "axe_haste": player.weapons["axe"]["cooldown"] = max(20, int(player.weapons["axe"]["cooldown"] * 0.8))
    elif card_id == "lightning_dmg": player.weapons["lightning"]["base_damage"] += 10
    elif card_id == "lightning_chain": player.weapons["lightning"]["chain_count"] += 2
    elif card_id == "lightning_bolt": player.weapons["lightning"]["bolt_count"] += 1

    elif card_id == "beam_dmg": player.weapons["beam"]["base_damage"] += 50
    elif card_id == "beam_width": player.weapons["beam"]["width"] += 10
    elif card_id == "blizzard_rad": player.weapons["blizzard"]["radius"] += 30
    elif card_id == "chakram_burn": player.weapons["chakram"]["burn_dmg"] += 5
    
    elif card_id == "unlock_melee": player.weapons["melee"]["active"] = True
    elif card_id == "unlock_orbit": player.weapons["orbit"]["active"] = True
    elif card_id == "unlock_axe": player.weapons["axe"]["active"] = True
    elif card_id == "unlock_boomerang": player.weapons["boomerang"]["active"] = True
    elif card_id == "unlock_bounce": player.weapons["bounce"]["active"] = True
    elif card_id == "unlock_trail": player.weapons["trail"]["active"] = True
    elif card_id == "unlock_lightning": player.weapons["lightning"]["active"] = True
    elif card_id == "unlock_beam": player.weapons["beam"]["active"] = True
    elif card_id == "unlock_blizzard": player.weapons["blizzard"]["active"] = True
    elif card_id == "unlock_chakram": player.weapons["chakram"]["active"] = True