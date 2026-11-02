import pygame
import random
import os
import math
import sys  
from organ_select import run_organ_select
# ==============================================================================
# --- 匯入你的塔防遊戲模組 (請確保檔名為 organ_td.py 或對應的名稱) ---
# ==============================================================================
try:
    from organ_td import run_organ_td
except ImportError:
    # 預防找不到模組時的防呆備用函式
    def run_organ_td(screen, clock, font_cache, draw_custom_crosshair):
        print("尚未找到 organ_td.py 模組或進入點函式！")

try:
    from organ_survival import run_organ_survival
except ImportError:
    def run_organ_survival(screen, clock, font_cache, draw_custom_crosshair):
        print("尚未找到 organ_survival.py 模組或進入點函式！")

# ==============================================================================
# --- 遊戲基礎配置與常數 ---
# ==============================================================================
class Config:
    FPS = 60
    WIDTH = 800    # 寬度拉大到 800，橫向空間極致寬敞，物件徹底分散
    HEIGHT = 700   # 高度拉高到 700，垂直戰線拉長，點擊反應時間更充裕
    
    LEVEL1_FALL_SPEED = 0.6    # 第一關掉落速度倍率（1.0=原速，越小越慢）
    TOOLBAR_SLOTS = 4          
    SLOT_SIZE = 42             
    SLOT_MARGIN = 10            
    TOOLBAR_X = 30             
    TOOLBAR_Y = 15             

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 165, 0)
    CYAN = (0, 200, 255)
    DARK_GRAY = (40, 40, 40)
    BLUE = (50, 100, 255)

# --- 全域遊戲與升級變數 ---
upgrade_max_hp = 100
upgrade_lives = 3
upgrade_click_dmg = 25
upgrade_click_radius = 0
game_level = 1
game_difficulty = 0 # 0: 簡單模式, 1: 困難模式
MAX_LEVEL = 2       # 目前實際有內容的最後一關
shield_msg_text = ''
shield_msg_timer = 0

passive_talents = set()
inventory = [None] * Config.TOOLBAR_SLOTS

# ==============================================================================
# --- 病毒百科資料 ---
# ==============================================================================
wiki_entries = [
    {
        "id": "flu", "page": 0, "name": "流感病毒", "sub": "季節性流感", "color": Colors.RED,
        "symptoms": "秋冬最盛行，會讓人突然高燒、頭痛、全身肌肉痠痛到想睡覺，繁殖快又愛變身。",
        "defense": "每年打流感疫苗（穿上防護罩）、勤洗手多漱口、戴口罩，教室多開窗通風。",
        "game": "遊戲中：【疫苗】道具可以回復基地 50 點生命值。",
        "hint": "通過第 1 關。",
    },
    {
        "id": "rhino", "page": 0, "name": "鼻病毒", "sub": "Rhinovirus", "color": Colors.ORANGE,
        "symptoms": "一年四季都在，是普通感冒的頭號大王，家族超多成員，會讓人狂打噴嚏、流鼻水、鼻塞。",
        "defense": "必須用肥皂和清水徹底洗手！因為鼻病毒不怕一般酒精，只有肥皂能拆掉它的防護。",
        "game": "遊戲中：【肥皂】可一次清除畫面上所有鼻病毒，【酒精】對它沒用！",
        "hint": "在戰鬥中對鼻病毒使用【肥皂】。",
    },
    {
        "id": "rsv", "page": 0, "name": "RSV", "sub": "呼吸道融合病毒", "color": Colors.CYAN,
        "symptoms": "冬春季最活躍，專挑 2 歲以下小寶寶麻煩，會讓人狂咳嗽（甚至咳到吐）、呼吸發出「咻咻」喘息聲。",
        "defense": "勤洗手、保持通風，大人絕對不能亂親小寶寶，避免把病毒傳給弟弟妹妹。",
        "game": "",
        "hint": "通過第 2 關。",
    },
    {
        "id": "tower1", "page": 1, "name": "漿細胞", "sub": "Plasma cell", "color": (100, 200, 255),
        "sym_label": "【 醫學小知識 】", "def_label": "【 怎麼幫它加油 】",
        "symptoms": "漿細胞是 B 細胞變身來的免疫細胞，專門大量製造抗體。抗體像一把把小鑰匙，會黏在病毒身上做記號、擋住它們，讓其他免疫細胞更容易抓到壞蛋。腸道裡還有一種分泌型 IgA 抗體，負責守住腸壁。",
        "defense": "均衡飲食、充足睡眠，免疫細胞才有力氣工作；接種疫苗就像提前教身體認識壞蛋，讓抗體提早準備好。",
        "game": "遊戲中：費用 50、射程 150，連射小子彈，每發傷害 12。便宜又好用，適合當作前期防線。",
        "hint": "進入並離開【腸道】關卡。",
    },
    {
        "id": "tower2", "page": 1, "name": "自然殺手細胞", "sub": "NK cell", "color": (255, 120, 200),
        "sym_label": "【 醫學小知識 】", "def_label": "【 怎麼幫它加油 】",
        "symptoms": "自然殺手細胞（NK 細胞）是身體天生的巡邏警察，不用事先認識壞蛋，一發現被病毒感染的細胞，就會釋放穿孔素和顆粒酶把它處理掉。",
        "defense": "規律運動、不熬夜、保持好心情，有助於讓 NK 細胞保持活力。",
        "game": "遊戲中：費用 80、射程 180（最遠），發射雷射 2 秒、休息 1 秒，適合壓制速度很快的多眼病毒。",
        "hint": "進入並離開【腸道】關卡。",
    },
    {
        "id": "tower3", "page": 1, "name": "巨噬細胞", "sub": "Macrophage", "color": (150, 255, 120),
        "sym_label": "【 醫學小知識 】", "def_label": "【 怎麼幫它加油 】",
        "symptoms": "巨噬細胞的名字意思是「大胃王」，會把入侵的細菌、病毒和壞掉的細胞一口吞下並消化，還會發出訊號，叫其他免疫細胞來幫忙。",
        "defense": "勤洗手、少讓病菌進入身體，就能減輕巨噬細胞的工作量；受傷了也要記得清潔傷口。",
        "game": "遊戲中：費用 100、射程 130（最短），射得慢但每發傷害 24，適合守在轉彎處對付鎖鏈鐵球病毒。",
        "hint": "進入並離開【腸道】關卡。",
    },
    {
        "id": "para", "page": 0, "name": "副流感病毒 & COVID-19", "sub": "穿外套的小魔鬼 / 新冠病毒", "color": Colors.GREEN,
        "symptoms": "副流感病毒像帶著「外套」的小魔鬼；COVID-19 則會讓人發燒、咳嗽、喉嚨痛或覺得很累。",
        "defense": "副流感病毒的外套可被酒精拆掉消毒；COVID-19 可透過接種疫苗來保護自己。兩者皆需落實勤洗手、少摸眼鼻口與戴口罩。",
        "game": "遊戲中：穿外套的副流感病毒只受 1/4 傷害，用【酒精】拆掉外套再打！",
        "hint": "在戰鬥中用【酒精】拆掉副流感病毒的外套。",
    },
    {
        "id": "virus1", "page": 2, "name": "腺病毒", "sub": "Adenovirus", "color": (50, 220, 100),
        "symptoms": "幼兒很常見，會喉嚨痛、發燒、咳嗽，有時眼睛紅紅的（紅眼症）。多數症狀輕微，休息幾天就會好。",
        "defense": "它不怕一般酒精，要用肥皂和清水好好洗手；玩具、門把常清潔，生病在家休息。",
        "game": "遊戲中（吞噬生存戰・病毒 1）：不會動，吃掉可得 50 分、20 經驗值，還能回復 10 點生命值。",
        "hint": "在【吞噬生存戰】中吞噬病毒 1。",
    },
    {
        "id": "virus2", "page": 2, "name": "諾羅病毒", "sub": "Norovirus", "color": (230, 50, 50),
        "symptoms": "傳染力超強，一點點就會中招！會讓人嘔吐、拉肚子、肚子痛，一下子就讓人沒力氣。",
        "defense": "用肥皂勤洗手，食物要煮熟、水果蔬菜洗乾淨；嘔吐物要戴手套，用稀釋漂白水消毒。",
        "game": "遊戲中（吞噬生存戰・病毒 2）：會追著你跑，最多 5 隻，碰到扣 25% 最大生命值！",
        "hint": "在【吞噬生存戰】中遇到病毒 2。",
    },
]

# --- 百科分頁（依關卡分開；條目的 "page" 對應這裡的索引） ---
wiki_pages = [
    {"title": "肺部防護戰", "color": Colors.CYAN},
    {"title": "腸道關卡", "color": Colors.YELLOW},
    {"title": "吞噬生存戰", "color": Colors.GREEN},
]

# --- 百科解鎖紀錄（目前所有條目一開始就全部解鎖） ---
wiki_unlocked = {e["id"] for e in wiki_entries}   # 全部預設解鎖，不需任何條件
unlock_msg_text = ''
unlock_msg_timer = 0

def unlock_wiki(entry_id):
    """解鎖一筆百科；第一次解鎖時顯示通知"""
    global unlock_msg_text, unlock_msg_timer
    if entry_id in wiki_unlocked:
        return
    wiki_unlocked.add(entry_id)
    name = next(e["name"] for e in wiki_entries if e["id"] == entry_id)
    unlock_msg_text = f"新解鎖百科：{name}（主選單按 W 查看）"
    unlock_msg_timer = pygame.time.get_ticks()

def draw_unlock_banner(surf, y):
    if unlock_msg_text and pygame.time.get_ticks() - unlock_msg_timer < 3500:
        w = get_font(20).size(unlock_msg_text)[0] + 40
        box = pygame.Surface((w, 40), pygame.SRCALPHA)
        box.fill((0, 40, 60, 210))
        pygame.draw.rect(box, Colors.CYAN, (0, 0, w, 40), 2, border_radius=8)
        surf.blit(box, (Config.WIDTH // 2 - w // 2, y))
        draw_text(surf, unlock_msg_text, 20, Config.WIDTH // 2, y + 8, Colors.CYAN)


# ==============================================================================
# --- 關卡任務系統（只存在記憶體，不存檔：關閉程式後自動重置） ---
# ==============================================================================
MISSION_DEFS = {
    1: [("soap",    "用肥皂洗掉鼻病毒", 1),
        ("alcohol", "用酒精拆掉病毒外套", 1),
        ("kill",    "消滅病毒", 15)],
    2: [("shield",  "使用疫苗回復防線", 1),
        ("alcohol", "用酒精拆掉病毒外套", 2),
        ("kill",    "消滅病毒", 25)],
}
current_missions = []
mission_msg_text = ''
mission_msg_timer = 0

def load_level_missions(level):
    """進入關卡時，載入該關任務並把進度歸零"""
    global current_missions
    defs = MISSION_DEFS.get(level, MISSION_DEFS[max(MISSION_DEFS)])
    current_missions = [{"kind": k, "text": t, "goal": g, "progress": 0, "done": False} for k, t, g in defs]

def mission_event(kind, amount=1):
    """回報一次任務事件；達標時顯示通知"""
    global mission_msg_text, mission_msg_timer
    for m in current_missions:
        if m["kind"] != kind or m["done"]:
            continue
        m["progress"] = min(m["goal"], m["progress"] + amount)
        if m["progress"] >= m["goal"]:
            m["done"] = True
            mission_msg_text = f"任務完成：{m['text']}"
            mission_msg_timer = pygame.time.get_ticks()

def draw_mission_panel(surf, x=30, y=88, w=250):
    if not current_missions:
        return
    line_h = 22
    h = 34 + line_h * len(current_missions)
    box = pygame.Surface((w, h), pygame.SRCALPHA)
    box.fill((10, 10, 20, 170))
    surf.blit(box, (x, y))
    pygame.draw.rect(surf, (120, 120, 140), (x, y, w, h), 1, border_radius=6)
    draw_text_left(surf, "【 關卡任務 】", 14, x + 8, y + 6, Colors.YELLOW)
    for i, m in enumerate(current_missions):
        color = Colors.GREEN if m["done"] else Colors.WHITE
        tag = "完成" if m["done"] else f"{m['progress']}/{m['goal']}"
        draw_text_left(surf, f"{m['text']}  {tag}", 13, x + 8, y + 32 + i * line_h, color)

def draw_mission_toast(surf, y):
    if mission_msg_text and pygame.time.get_ticks() - mission_msg_timer < 3000:
        w = get_font(20).size(mission_msg_text)[0] + 40
        box = pygame.Surface((w, 40), pygame.SRCALPHA)
        box.fill((20, 50, 20, 220))
        pygame.draw.rect(box, Colors.GREEN, (0, 0, w, 40), 2, border_radius=8)
        surf.blit(box, (Config.WIDTH // 2 - w // 2, y))
        draw_text(surf, mission_msg_text, 20, Config.WIDTH // 2, y + 8, Colors.GREEN)

# ==============================================================================
# --- 遊戲初始化與資源載入 ---
# ==============================================================================
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(16)
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("健康保衛戰 - 純點擊防守模式")
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)

raw_bg = pygame.image.load(os.path.join("img", "background.png")).convert()
background_img = pygame.transform.smoothscale(raw_bg, (Config.WIDTH, Config.HEIGHT))

boss_img = pygame.image.load(os.path.join("img", "demons.png")).convert_alpha()
boss_img2 = pygame.image.load(os.path.join("img", "demons2.png")).convert_alpha()

crosshair_available = False
try:
    crosshair_raw = pygame.image.load(os.path.join("img", "crosshair.png")).convert_alpha()
    crosshair_img = pygame.transform.smoothscale(crosshair_raw, (32, 32))
    crosshair_available = True
except FileNotFoundError:
    pass

soldier_img = pygame.image.load(os.path.join("img", "soldier.png")).convert_alpha()

heart_img = pygame.image.load(os.path.join("img", "heart.png")).convert_alpha()
heart_img.set_colorkey(Colors.WHITE)
heart_mini_img = pygame.transform.scale(heart_img, (25, 25))

rock_imgs = []
for i in range(7):
    path_png = os.path.join("img", f"rock{i}.png")
    path_jpg = os.path.join("img", f"rock{i}.jpg")
    if os.path.exists(path_png):
        img = pygame.image.load(path_png).convert_alpha()
    elif os.path.exists(path_jpg):
        img = pygame.image.load(path_jpg).convert_alpha()
    else:
        img = pygame.Surface((50, 50))
        img.fill(Colors.WHITE)
    img = pygame.transform.scale(img, (50, 50))
    rock_imgs.append(img)

expl_anim = {'lg': [], 'sm': []}
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(Colors.BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))

power_imgs = {
    'shield': pygame.image.load(os.path.join("img", "shield.png")).convert_alpha(),
    'damage_up': pygame.image.load(os.path.join("img", "gun.png")).convert_alpha()
}

ITEM_NAMES = {'shield': '疫苗', 'damage_up': '強效', 'soap': '肥皂', 'alcohol': '酒精'}

def make_soap_icon():
    icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(icon, (255, 170, 200), (8, 22, 48, 28), border_radius=8)
    pygame.draw.rect(icon, (255, 220, 235), (12, 26, 22, 8), border_radius=4)
    for cx, cy, r in ((16, 14, 6), (30, 8, 5), (46, 14, 7), (52, 6, 3)):
        pygame.draw.circle(icon, (200, 240, 255), (cx, cy), r, 2)
    return icon

def make_alcohol_icon():
    icon = pygame.Surface((64, 64), pygame.SRCALPHA)
    pygame.draw.rect(icon, (200, 60, 60), (24, 4, 16, 10), border_radius=3)
    pygame.draw.rect(icon, (170, 220, 255), (14, 14, 36, 46), border_radius=8)
    pygame.draw.rect(icon, Colors.WHITE, (20, 28, 24, 18), border_radius=3)
    pygame.draw.line(icon, (200, 60, 60), (32, 31), (32, 43), 3)
    pygame.draw.line(icon, (200, 60, 60), (26, 37), (38, 37), 3)
    return icon

power_imgs['soap'] = make_soap_icon()
power_imgs['alcohol'] = make_alcohol_icon()

shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
BGM_PATH = os.path.join("sound", "background.ogg")

music_volume = 0.4   # 音樂音量 0.0~1.0（設定畫面可調）
sfx_volume = 1.0     # 音效音量 0.0~1.0（設定畫面可調）

def apply_sfx_volume():
    for snd in (shoot_sound, gun_sound, shield_sound, die_sound, *expl_sounds):
        snd.set_volume(sfx_volume)

apply_sfx_volume()

def play_bgm():
    """所有關卡共用的背景音樂：每次進入關卡都重新載入並循環播放 background.ogg"""
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(BGM_PATH)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1)
    except pygame.error as e:
        print(f"無法播放背景音樂：{e}")

font_name = os.path.join("font.ttf")
font_cache = {}

choice_next_rect = pygame.Rect(Config.WIDTH // 2 - 130, Config.HEIGHT // 2 - 60, 260, 55)
choice_home_rect = pygame.Rect(Config.WIDTH // 2 - 130, Config.HEIGHT // 2 + 25, 260, 55)
game_back_rect = pygame.Rect(Config.WIDTH - 100, 75, 90, 32)   # 遊戲中的返回按鈕

# ==============================================================================
# --- 輔助功能與繪圖函式 ---
# ==============================================================================
def draw_text(surf, text, size, x, y, color=Colors.WHITE):
    if size not in font_cache:
        try:
            font_cache[size] = pygame.font.Font(font_name, size)
        except FileNotFoundError:
            font_cache[size] = pygame.font.SysFont('arial', size)
    font = font_cache[size]
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_mixed_color_text(surf, text, size, center_x, top_y, default_color=Colors.WHITE):
    if size not in font_cache:
        try:
            font_cache[size] = pygame.font.Font(font_name, size)
        except FileNotFoundError:
            font_cache[size] = pygame.font.SysFont('arial', size)
    font = font_cache[size]
    
    keyword = "流感病毒"
    parts = text.split(keyword)
    
    total_width = 0
    surfaces_and_colors = []
    
    for idx, part in enumerate(parts):
        if part: 
            p_surf = font.render(part, True, default_color)
            total_width += p_surf.get_width()
            surfaces_and_colors.append((p_surf, default_color))
        
        if idx < len(parts) - 1:
            k_surf = font.render(keyword, True, Colors.RED)
            total_width += k_surf.get_width()
            surfaces_and_colors.append((k_surf, Colors.RED))
            
    current_x = center_x - total_width / 2
    for p_surf, _ in surfaces_and_colors:
        surf.blit(p_surf, (current_x, top_y))
        current_x += p_surf.get_width()

virus_label_cache = {}

def draw_virus_label(surf, enemy):
    """在敵人頭上標示病毒種類，玩家才知道該用哪個道具"""
    key = (getattr(enemy, 'virus', None), getattr(enemy, 'coat', False))
    labels = {
        ('rhino', False): ("鼻病毒", Colors.CYAN),
        ('para', True): ("副流感·外套", Colors.ORANGE),
        ('para', False): ("副流感", Colors.GREEN),
    }
    if key not in labels:
        return
    if key not in virus_label_cache:
        text, color = labels[key]
        virus_label_cache[key] = get_font(12).render(text, True, color)
    lbl = virus_label_cache[key]
    surf.blit(lbl, (enemy.rect.centerx - lbl.get_width() // 2, enemy.rect.top - 14))

def new_enemy(level):
    e = Rock(level) if random.random() > 0.3 else Tracker(level)
    all_sprites.add(e)
    rocks.add(e)

def draw_health(surf, hp, x, y, max_hp=100, color=Colors.GREEN, length=100):
    if hp < 0: 
        hp = 0
    fill = (hp / max_hp) * length
    outline_rect = pygame.Rect(x, y, length, 10)
    fill_rect = pygame.Rect(x, y, fill, 10)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, Colors.WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - (30 * i)
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_custom_crosshair(surf):
    mx, my = pygame.mouse.get_pos()
    if crosshair_available:
        crect = crosshair_img.get_rect(center=(mx, my))
        surf.blit(crosshair_img, crect)
    else:
        pygame.draw.circle(surf, Colors.GREEN, (mx, my), 6, 2)
        pygame.draw.line(surf, Colors.GREEN, (mx - 12, my), (mx + 12, my), 2)
        pygame.draw.line(surf, Colors.GREEN, (mx, my - 12), (mx, my + 12), 2)

# ==============================================================================
# --- 背包與道具系統功能 ---
# ==============================================================================
def toolbar_slot_rect(i):
    return pygame.Rect(Config.TOOLBAR_X + i * (Config.SLOT_SIZE + Config.SLOT_MARGIN),
                       Config.TOOLBAR_Y, Config.SLOT_SIZE, Config.SLOT_SIZE)

def draw_toolbar(surf, inv):
    mouse_pos = pygame.mouse.get_pos()
    for i in range(Config.TOOLBAR_SLOTS):
        slot_rect = toolbar_slot_rect(i)
        slot_x, slot_y = slot_rect.x, slot_rect.y
        
        pygame.draw.rect(surf, (20, 20, 28), slot_rect)
        hover = inv[i] is not None and slot_rect.collidepoint(mouse_pos)
        pygame.draw.rect(surf, Colors.YELLOW if hover else (160, 160, 180), slot_rect, 2)
        
        if 10 not in font_cache:
            font_cache[10] = pygame.font.SysFont('arial', 10) if font_name == "" else pygame.font.Font(font_name, 10)
        try:
            num_surf = font_cache[10].render(str(i + 1), True, Colors.CYAN)
        except:
            font_cache[10] = pygame.font.SysFont('arial', 10)
            num_surf = font_cache[10].render(str(i + 1), True, Colors.CYAN)
        surf.blit(num_surf, (slot_x + 3, slot_y + 2))
        
        if inv[i] is not None:
            item_type = inv[i]["type"]
            item_count = inv[i]["count"]
            if item_type in power_imgs:
                item_img = pygame.transform.scale(power_imgs[item_type], (Config.SLOT_SIZE - 12, Config.SLOT_SIZE - 12))
                surf.blit(item_img, (slot_x + 6, slot_y + 7))
            if item_count > 0:
                if 12 not in font_cache:
                    font_cache[12] = pygame.font.SysFont('arial', 12) if font_name == "" else pygame.font.Font(font_name, 12)
                count_surf = font_cache[12].render(str(item_count), True, Colors.YELLOW)
                count_rect = count_surf.get_rect()
                count_rect.bottomright = (slot_x + Config.SLOT_SIZE - 3, slot_y + Config.SLOT_SIZE - 2)
                surf.blit(count_surf, count_rect)
            draw_text(surf, ITEM_NAMES.get(item_type, ''), 11, slot_x + Config.SLOT_SIZE // 2, slot_y + Config.SLOT_SIZE + 3, (180, 180, 190))

def add_to_inventory(item_type):
    for i in range(Config.TOOLBAR_SLOTS):
        if inventory[i] is not None and inventory[i]["type"] == item_type:
            inventory[i]["count"] += 1
            return True
    for i in range(Config.TOOLBAR_SLOTS):
        if inventory[i] is None:
            inventory[i] = {"type": item_type, "count": 1}
            return True
    return False 

def use_item_by_slot(slot_idx):
    global base_health, upgrade_click_dmg, shield_msg_text, shield_msg_timer
    if not (0 <= slot_idx < Config.TOOLBAR_SLOTS) or inventory[slot_idx] is None:
        return
    item_type = inventory[slot_idx]["type"]
    now = pygame.time.get_ticks()
    consumed = True

    if item_type == "shield":          # 疫苗：回復基地生命
        base_health = min(base_max_health, base_health + 50)
        shield_sound.play()
        mission_event('shield')
    elif item_type == "damage_up":
        upgrade_click_dmg += 3
        gun_sound.play()
    elif item_type == "soap":          # 肥皂：洗掉所有鼻病毒
        targets = [r for r in rocks if getattr(r, 'virus', None) == 'rhino']
        if targets:
            for r in targets:
                damage_rock(r, r.hp)
            shield_sound.play()
            shield_msg_text, shield_msg_timer = '肥皂洗掉了所有鼻病毒！', now
            unlock_wiki('rhino')
            mission_event('soap')
        else:
            consumed = False
            shield_msg_text, shield_msg_timer = '畫面上沒有鼻病毒，肥皂先留著！', now
    elif item_type == "alcohol":       # 酒精：拆掉副流感病毒的外套
        coated = [r for r in rocks if getattr(r, 'coat', False)]
        if coated:
            for r in coated:
                r.strip_coat()
                all_sprites.add(Explosion(r.rect.center, 'sm'))
            gun_sound.play()
            has_rhino = any(getattr(r, 'virus', None) == 'rhino' for r in rocks)
            shield_msg_text = '酒精拆掉了外套！鼻病毒不怕酒精' if has_rhino else '酒精拆掉了病毒的外套！'
            shield_msg_timer = now
            unlock_wiki('para')
            mission_event('alcohol')
        else:
            consumed = False
            shield_msg_text, shield_msg_timer = '沒有穿外套的病毒，酒精先留著！', now

    if consumed:
        inventory[slot_idx]["count"] -= 1
        if inventory[slot_idx]["count"] <= 0:
            inventory[slot_idx] = None

# ==============================================================================
# --- 獨立介面繪製 (天賦、關卡選擇、分歧選擇畫面) ---
# ==============================================================================
def draw_level_clear_box(surf, level):
    box_w, box_h = 460, 140
    box_x = (Config.WIDTH - box_w) // 2
    box_y = (Config.HEIGHT - box_h) // 2

    overlay_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay_box.fill((10, 25, 20, 240))
    pygame.draw.rect(overlay_box, Colors.GREEN, (0, 0, box_w, box_h), 3, border_radius=12)
    surf.blit(overlay_box, (box_x, box_y))

    draw_text(surf, f"【 第 {level} 關 通關成功 】", 28, Config.WIDTH / 2, box_y + 30, Colors.YELLOW)
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        draw_text(surf, "— 按 SPACE 或 點擊左鍵 繼續 —", 16, Config.WIDTH / 2, box_y + 85, Colors.CYAN)

def draw_level_transition_choice_screen(surf):
    mouse_pos = pygame.mouse.get_pos()
    
    overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 10, 15, 200))
    surf.blit(overlay, (0, 0))
    
    is_final = game_level >= MAX_LEVEL
    if is_final:
        draw_text(surf, "— 全部關卡通關 —", 24, Config.WIDTH / 2, Config.HEIGHT // 2 - 140, Colors.GREEN)
        draw_text(surf, "恭喜！免疫防線成功守住了人體！", 28, Config.WIDTH / 2, Config.HEIGHT // 2 - 100, Colors.WHITE)
    else:
        draw_text(surf, "— 階段戰役結束 —", 24, Config.WIDTH / 2, Config.HEIGHT // 2 - 140, Colors.GREEN)
        draw_text(surf, f"人體暫時脫離危險，是否繼續挺進第{game_level + 1}關？", 28, Config.WIDTH / 2, Config.HEIGHT // 2 - 100, Colors.WHITE)
        next_btn_color = Colors.YELLOW if choice_next_rect.collidepoint(mouse_pos) else Colors.GREEN
        pygame.draw.rect(surf, next_btn_color, choice_next_rect, 3, border_radius=10)
        draw_text(surf, f"挑戰第{game_level + 1}關", 22, choice_next_rect.centerx, choice_next_rect.y + 15, next_btn_color)
    
    home_btn_color = Colors.YELLOW if choice_home_rect.collidepoint(mouse_pos) else Colors.CYAN
    pygame.draw.rect(surf, home_btn_color, choice_home_rect, 3, border_radius=10)
    draw_text(surf, "返回主畫面", 22, choice_home_rect.centerx, choice_home_rect.y + 15, home_btn_color)

    done = sum(1 for m in current_missions if m["done"])
    draw_text(surf, f"本關任務完成 {done}/{len(current_missions)}", 18, Config.WIDTH / 2, Config.HEIGHT // 2 + 110, Colors.YELLOW)

def draw_talent_select():
    global passive_talents
    pygame.event.set_grab(True)
    ALL_TALENTS = {
        'splash': ('爆裂點擊', '點擊敵人時，對周圍小範圍敵人造成波及傷害'),
        'regen':  ('基地維修', '每 3 秒自動恢復基地 5 點生命值'),
        'chain':  ('連鎖點擊', '每次點擊會隨機自動額外打擊畫面上另一個敵人'),
    }
    available = [t for t in ALL_TALENTS if t not in passive_talents]
    if not available: 
        return

    choices = random.sample(available, min(2, len(available)))
    
    btn_w, btn_h = 240, 100
    btn_y = Config.HEIGHT // 2 - 40
    
    btn1_rect = pygame.Rect(Config.WIDTH // 4 - btn_w // 2, btn_y, btn_w, btn_h)
    btn2_rect = pygame.Rect(Config.WIDTH * 3 // 4 - btn_w // 2, btn_y, btn_w, btn_h)
    
    waiting = True
    while waiting:
        clock.tick(Config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        
        screen.fill(Colors.BLACK)
        screen.blit(background_img, (0, 0))
        draw_text(screen, '★ 請用滑鼠點擊選擇一個被動天賦 ★', 34, Config.WIDTH / 2, Config.HEIGHT / 5, Colors.YELLOW)
        
        name1, desc1 = ALL_TALENTS[choices[0]]
        color1 = Colors.YELLOW if btn1_rect.collidepoint(mouse_pos) else Colors.CYAN
        pygame.draw.rect(screen, color1, btn1_rect, 3, border_radius=12)
        draw_text(screen, name1, 26, btn1_rect.centerx, btn1_rect.y + 18, Colors.WHITE)
        draw_text(screen, desc1, 13, btn1_rect.centerx, btn1_rect.y + 60, (200, 200, 200))
        
        if len(choices) >= 2:
            name2, desc2 = ALL_TALENTS[choices[1]]
            color2 = Colors.YELLOW if btn2_rect.collidepoint(mouse_pos) else Colors.CYAN
            pygame.draw.rect(screen, color2, btn2_rect, 3, border_radius=12)
            draw_text(screen, name2, 26, btn2_rect.centerx, btn2_rect.y + 18, Colors.WHITE)
            draw_text(screen, desc2, 13, btn2_rect.centerx, btn2_rect.y + 60, (200, 200, 200))

        draw_text(screen, '按 ESC 可直接跳過', 16, Config.WIDTH / 2, Config.HEIGHT * 3 / 4 + 20, (140, 140, 140))
        draw_custom_crosshair(screen)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()  
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn1_rect.collidepoint(event.pos):
                    passive_talents.add(choices[0])
                    waiting = False
                elif len(choices) >= 2 and btn2_rect.collidepoint(event.pos):
                    passive_talents.add(choices[1])
                    waiting = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                waiting = False

def draw_level_select():
    global game_level, game_difficulty
    pygame.event.set_grab(True)
    
    lv1_btn = pygame.Rect(Config.WIDTH // 4 - 100, Config.HEIGHT // 2 - 50, 200, 50)
    lv2_btn = pygame.Rect(Config.WIDTH // 4 - 100, Config.HEIGHT // 2 + 20, 200, 50)
    
    easy_btn = pygame.Rect(Config.WIDTH * 3 // 4 - 100, Config.HEIGHT // 2 - 50, 200, 50)
    hard_btn = pygame.Rect(Config.WIDTH * 3 // 4 - 100, Config.HEIGHT // 2 + 20, 200, 50)
    
    back_btn = pygame.Rect(Config.WIDTH // 2 - 100, Config.HEIGHT * 3 // 4 + 20, 200, 45)
    
    while True:
        clock.tick(Config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))
        draw_text(screen, '--- 選擇戰鬥設定 ---', 38, Config.WIDTH / 2, Config.HEIGHT / 6, Colors.YELLOW)
        
        # --- 關卡選擇區 (左) ---
        draw_text(screen, '【 戰鬥關卡 】', 22, Config.WIDTH // 4, Config.HEIGHT // 2 - 100, Colors.WHITE)
        if lv1_btn.collidepoint(mouse_pos) or game_level == 1:
            pygame.draw.rect(screen, Colors.GREEN if game_level == 1 else Colors.CYAN, lv1_btn, border_radius=8)
            draw_text(screen, 'Level 1', 22, Config.WIDTH // 4, lv1_btn.y + 14, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, lv1_btn, border_radius=8)
            draw_text(screen, 'Level 1', 22, Config.WIDTH // 4, lv1_btn.y + 14, Colors.WHITE)
            
        if lv2_btn.collidepoint(mouse_pos) or game_level == 2:
            pygame.draw.rect(screen, Colors.RED if game_level == 2 else Colors.ORANGE, lv2_btn, border_radius=8)
            draw_text(screen, 'Level 2', 22, Config.WIDTH // 4, lv2_btn.y + 14, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, lv2_btn, border_radius=8)
            draw_text(screen, 'Level 2', 22, Config.WIDTH // 4, lv2_btn.y + 14, Colors.WHITE)
            
        # --- 難度模式選擇區 (右) ---
        draw_text(screen, '【 挑戰模式 】', 22, Config.WIDTH * 3 // 4, Config.HEIGHT // 2 - 100, Colors.WHITE)
        if easy_btn.collidepoint(mouse_pos) or game_difficulty == 0:
            pygame.draw.rect(screen, Colors.GREEN if game_difficulty == 0 else Colors.CYAN, easy_btn, border_radius=8)
            draw_text(screen, '簡單模式', 22, Config.WIDTH * 3 // 4, easy_btn.y + 14, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, easy_btn, border_radius=8)
            draw_text(screen, '簡單模式', 22, Config.WIDTH * 3 // 4, easy_btn.y + 14, Colors.WHITE)
            
        if hard_btn.collidepoint(mouse_pos) or game_difficulty == 1:
            pygame.draw.rect(screen, Colors.RED if game_difficulty == 1 else Colors.ORANGE, hard_btn, border_radius=8)
            draw_text(screen, '困難模式', 22, Config.WIDTH * 3 // 4, hard_btn.y + 14, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, hard_btn, border_radius=8)
            draw_text(screen, '困難模式', 22, Config.WIDTH * 3 // 4, hard_btn.y + 14, Colors.WHITE)

        # --- 返回按鈕 ---
        if back_btn.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.YELLOW, back_btn, border_radius=10)
            draw_text(screen, '確認返回', 20, Config.WIDTH // 2, back_btn.y + 12, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, back_btn, border_radius=10)
            draw_text(screen, '確認返回', 20, Config.WIDTH // 2, back_btn.y + 12, Colors.WHITE)
            
        draw_custom_crosshair(screen)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if lv1_btn.collidepoint(event.pos):
                    game_level = 1
                elif lv2_btn.collidepoint(event.pos):
                    game_level = 2
                elif easy_btn.collidepoint(event.pos):
                    game_difficulty = 0
                elif hard_btn.collidepoint(event.pos):
                    game_difficulty = 1
                elif back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return

def get_font(size):
    if size not in font_cache:
        try:
            font_cache[size] = pygame.font.Font(font_name, size)
        except FileNotFoundError:
            font_cache[size] = pygame.font.SysFont('arial', size)
    return font_cache[size]

def wrap_text(text, font, max_width):
    """中文逐字換行，回傳每一行的字串清單"""
    lines, cur = [], ""
    for ch in text:
        if font.size(cur + ch)[0] > max_width and cur and ch not in "，。、！？）」』：；,.!?)":
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines

def draw_text_left(surf, text, size, x, y, color=Colors.WHITE, max_width=None, line_gap=6):
    """靠左繪製文字（可自動換行），回傳繪製後的下一個 y 座標"""
    font = get_font(size)
    lines = wrap_text(text, font, max_width) if max_width else [text]
    for line in lines:
        surf.blit(font.render(line, True, color), (x, y))
        y += font.get_height() + line_gap
    return y

def draw_wiki():
    """病毒百科：依關卡分頁（←→ 換頁）；左側選病毒，右側顯示症狀、防護招式與遊戲用法"""
    pygame.event.set_grab(False)
    page = 0
    selected = 0

    list_x, list_w = 30, 230
    btn_h, gap, list_y = 62, 12, 120
    panel = pygame.Rect(280, 110, Config.WIDTH - 310, 502)
    btn_y = Config.HEIGHT - 80
    back_btn = pygame.Rect(Config.WIDTH // 2 - 100, btn_y, 200, 45)
    prev_btn = pygame.Rect(Config.WIDTH // 2 - 270, btn_y, 140, 45)
    next_btn = pygame.Rect(Config.WIDTH // 2 + 130, btn_y, 140, 45)

    def draw_btn(rect, label, mouse_pos):
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.YELLOW, rect, border_radius=10)
            draw_text(screen, label, 20, rect.centerx, rect.y + 11, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, rect, border_radius=10)
            draw_text(screen, label, 20, rect.centerx, rect.y + 11, Colors.WHITE)

    while True:
        clock.tick(Config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))

        veil = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        screen.blit(veil, (0, 0))

        # 目前這一頁的病毒
        entries = [en for en in wiki_entries if en.get("page", 0) == page]
        selected = max(0, min(selected, len(entries) - 1))
        entry_rects = [pygame.Rect(list_x, list_y + i * (btn_h + gap), list_w, btn_h) for i in range(len(entries))]
        page_info = wiki_pages[page]
        page_unlocked = sum(1 for en in entries if en["id"] in wiki_unlocked)

        draw_text(screen, '常見兒童病毒與防疫寶典', 36, Config.WIDTH / 2, 25, Colors.YELLOW)
        draw_text(screen, f'{page_info["title"]}　（第 {page + 1} / {len(wiki_pages)} 頁・已解鎖 {page_unlocked} / {len(entries)}）',
                  20, Config.WIDTH / 2, 72, page_info["color"])

        # --- 左側清單 ---
        for i, rect in enumerate(entry_rects):
            entry = entries[i]
            unlocked = entry["id"] in wiki_unlocked
            accent = entry["color"] if unlocked else (110, 110, 120)
            if i == selected:
                pygame.draw.rect(screen, (30, 40, 55), rect, border_radius=10)
                pygame.draw.rect(screen, accent, rect, 3, border_radius=10)
            else:
                border = Colors.YELLOW if rect.collidepoint(mouse_pos) else (110, 110, 120)
                pygame.draw.rect(screen, (20, 20, 28), rect, border_radius=10)
                pygame.draw.rect(screen, border, rect, 2, border_radius=10)
            name = entry["name"] if unlocked else "???"
            sub = entry["sub"] if unlocked else "尚未解鎖"
            name_size = 18 if len(name) > 8 else 22
            draw_text(screen, name, name_size, rect.centerx, rect.y + 10, Colors.WHITE if unlocked else (130, 130, 130))
            draw_text(screen, sub, 12, rect.centerx, rect.y + 40, (170, 170, 170))

        # --- 右側詳細內容 ---
        entry = entries[selected]
        unlocked = entry["id"] in wiki_unlocked
        accent = entry["color"] if unlocked else (110, 110, 120)
        box = pygame.Surface((panel.width, panel.height), pygame.SRCALPHA)
        box.fill((15, 15, 25, 235))
        screen.blit(box, panel.topleft)
        pygame.draw.rect(screen, accent, panel, 3, border_radius=12)

        tx, tw = panel.x + 25, panel.width - 50
        if unlocked:
            draw_text_left(screen, entry["name"], 32, tx, panel.y + 20, entry["color"], tw)
            draw_text_left(screen, entry["sub"], 16, tx, panel.y + 65, (170, 170, 170), tw)
            pygame.draw.line(screen, Colors.WHITE, (tx, panel.y + 95), (tx + tw, panel.y + 95), 1)

            y = draw_text_left(screen, entry.get("sym_label", "【 症狀與特色 】"), 22, tx, panel.y + 108, Colors.ORANGE, tw)
            y = draw_text_left(screen, entry["symptoms"], 18, tx, y + 4, Colors.WHITE, tw, 4)
            y = draw_text_left(screen, entry.get("def_label", "【 防護招式 】"), 22, tx, y + 16, Colors.GREEN, tw)
            y = draw_text_left(screen, entry["defense"], 18, tx, y + 4, Colors.WHITE, tw, 4)
            if entry["game"]:
                y = draw_text_left(screen, "【 遊戲中的用法 】", 22, tx, y + 16, Colors.CYAN, tw)
                draw_text_left(screen, entry["game"], 18, tx, y + 4, Colors.WHITE, tw, 4)
        else:
            draw_text_left(screen, "???", 32, tx, panel.y + 20, (130, 130, 130), tw)
            draw_text_left(screen, "尚未解鎖", 16, tx, panel.y + 65, (170, 170, 170), tw)
            pygame.draw.line(screen, Colors.WHITE, (tx, panel.y + 95), (tx + tw, panel.y + 95), 1)
            y = draw_text_left(screen, "【 解鎖條件 】", 22, tx, panel.y + 108, Colors.YELLOW, tw)
            y = draw_text_left(screen, entry["hint"], 18, tx, y + 4, Colors.WHITE, tw, 8)
            draw_text_left(screen, "去遊戲裡挑戰，解鎖後就能讀到這種病毒的防疫知識！", 16, tx, y + 16, (170, 170, 170), tw, 8)

        # --- 換頁與返回 ---
        draw_btn(prev_btn, '◀ 上一頁', mouse_pos)
        draw_btn(next_btn, '下一頁 ▶', mouse_pos)
        draw_btn(back_btn, '返回主畫面', mouse_pos)
        draw_text(screen, '↑↓ 切換病毒　|　←→ 切換頁面　|　ESC 返回', 14, Config.WIDTH / 2, Config.HEIGHT - 28, (170, 170, 170))

        draw_custom_crosshair(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(entries)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(entries)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    page = (page - 1) % len(wiki_pages)
                    selected = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    page = (page + 1) % len(wiki_pages)
                    selected = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    return
                if prev_btn.collidepoint(event.pos):
                    page = (page - 1) % len(wiki_pages)
                    selected = 0
                elif next_btn.collidepoint(event.pos):
                    page = (page + 1) % len(wiki_pages)
                    selected = 0
                else:
                    for i, rect in enumerate(entry_rects):
                        if rect.collidepoint(event.pos):
                            selected = i

def draw_settings():
    """設定：音樂音量、音效音量、遊戲難度"""
    global music_volume, sfx_volume, game_difficulty
    pygame.event.set_grab(False)

    cx = Config.WIDTH // 2
    music_track = pygame.Rect(cx - 180, 220, 360, 10)
    sfx_track = pygame.Rect(cx - 180, 320, 360, 10)
    easy_btn = pygame.Rect(cx - 200, 440, 180, 50)
    hard_btn = pygame.Rect(cx + 20, 440, 180, 50)
    back_btn = pygame.Rect(cx - 100, 600, 200, 45)
    dragging = None   # 'music' / 'sfx' / None

    def set_from_mouse(which, mx):
        global music_volume, sfx_volume
        track = music_track if which == 'music' else sfx_track
        v = max(0.0, min(1.0, (mx - track.x) / track.width))
        if which == 'music':
            music_volume = v
            pygame.mixer.music.set_volume(music_volume)
        else:
            sfx_volume = v
            apply_sfx_volume()

    def draw_slider(track, value, label):
        draw_text(screen, f"{label}：{int(round(value * 100))}%", 22, cx, track.y - 45, Colors.WHITE)
        pygame.draw.rect(screen, Colors.DARK_GRAY, track, border_radius=5)
        pygame.draw.rect(screen, Colors.CYAN, (track.x, track.y, int(track.width * value), track.height), border_radius=5)
        pygame.draw.rect(screen, Colors.WHITE, track, 2, border_radius=5)
        pygame.draw.circle(screen, Colors.YELLOW, (track.x + int(track.width * value), track.centery), 12)
        pygame.draw.circle(screen, Colors.WHITE, (track.x + int(track.width * value), track.centery), 12, 2)

    while True:
        clock.tick(Config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))
        veil = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        veil.fill((0, 0, 0, 150))
        screen.blit(veil, (0, 0))

        draw_text(screen, '--- 遊戲設定 ---', 42, cx, 60, Colors.YELLOW)
        draw_slider(music_track, music_volume, '音樂音量')
        draw_slider(sfx_track, sfx_volume, '音效音量')

        draw_text(screen, '遊戲難度', 22, cx, 395, Colors.WHITE)
        for btn, label, mode, on_color in ((easy_btn, '簡單模式', 0, Colors.GREEN), (hard_btn, '困難模式', 1, Colors.RED)):
            selected = game_difficulty == mode
            if selected:
                pygame.draw.rect(screen, on_color, btn, border_radius=8)
                draw_text(screen, label, 22, btn.centerx, btn.y + 13, Colors.BLACK)
            else:
                pygame.draw.rect(screen, Colors.YELLOW if btn.collidepoint(mouse_pos) else Colors.DARK_GRAY, btn, border_radius=8)
                draw_text(screen, label, 22, btn.centerx, btn.y + 13, Colors.BLACK if btn.collidepoint(mouse_pos) else Colors.WHITE)
        draw_text(screen, '困難模式：敵人血量 ×1.5、速度更快、魔王攻擊更頻繁', 15, cx, 510, (170, 170, 170))
        draw_text(screen, '（難度會在下次開始關卡時生效）', 14, cx, 535, (140, 140, 140))

        if back_btn.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.YELLOW, back_btn, border_radius=10)
            draw_text(screen, '返回主畫面', 20, back_btn.centerx, back_btn.y + 11, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, back_btn, border_radius=10)
            draw_text(screen, '返回主畫面', 20, back_btn.centerx, back_btn.y + 11, Colors.WHITE)

        draw_custom_crosshair(screen)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_track.inflate(30, 40).collidepoint(event.pos):
                    dragging = 'music'
                    set_from_mouse('music', event.pos[0])
                elif sfx_track.inflate(30, 40).collidepoint(event.pos):
                    dragging = 'sfx'
                    set_from_mouse('sfx', event.pos[0])
                elif easy_btn.collidepoint(event.pos):
                    game_difficulty = 0
                elif hard_btn.collidepoint(event.pos):
                    game_difficulty = 1
                elif back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.MOUSEMOTION and dragging:
                set_from_mouse(dragging, event.pos[0])
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging == 'sfx':
                    shoot_sound.play()   # 放開時播放試聽
                dragging = None

def draw_init():
    pygame.event.set_grab(False)
    
    start_btn_rect = pygame.Rect(Config.WIDTH // 2 - 100, Config.HEIGHT // 2 - 30, 200, 50)
    wiki_btn_rect = pygame.Rect(Config.WIDTH // 2 - 100, Config.HEIGHT // 2 + 35, 200, 45)
    settings_btn_rect = pygame.Rect(Config.WIDTH // 2 - 100, Config.HEIGHT // 2 + 95, 200, 45)
    while True:
        clock.tick(Config.FPS)
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))
        draw_text(screen, '健康防衛戰!', 68, Config.WIDTH / 2, Config.HEIGHT / 5)
        

        if start_btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.GREEN, start_btn_rect, border_radius=10)
        else:
            pygame.draw.rect(screen, Colors.CYAN, start_btn_rect, border_radius=10)
        draw_text(screen, '遊戲開始', 24, Config.WIDTH / 2, start_btn_rect.y + 12, Colors.BLACK)

        if wiki_btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.GREEN, wiki_btn_rect, border_radius=10)
            draw_text(screen, '病毒百科 [W]', 18, Config.WIDTH / 2, wiki_btn_rect.y + 12, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, wiki_btn_rect, border_radius=10)
            draw_text(screen, '病毒百科 [W]', 18, Config.WIDTH / 2, wiki_btn_rect.y + 12, Colors.WHITE)

        if settings_btn_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, Colors.ORANGE, settings_btn_rect, border_radius=10)
            draw_text(screen, '設定 [O]', 18, Config.WIDTH / 2, settings_btn_rect.y + 12, Colors.BLACK)
        else:
            pygame.draw.rect(screen, Colors.DARK_GRAY, settings_btn_rect, border_radius=10)
            draw_text(screen, '設定 [O]', 18, Config.WIDTH / 2, settings_btn_rect.y + 12, Colors.WHITE)

        draw_text(screen, '也可以按 SPACE 直接開始遊戲', 16, Config.WIDTH / 2, Config.HEIGHT * 3 / 4 + 60, (160, 160, 160))
        draw_unlock_banner(screen, Config.HEIGHT - 60)
        draw_custom_crosshair(screen)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: return "WIKI"
                elif event.key == pygame.K_o: return "SETTINGS"
                elif event.key == pygame.K_SPACE: return "PLAY"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn_rect.collidepoint(event.pos): return "PLAY"
                if wiki_btn_rect.collidepoint(event.pos): return "WIKI"
                if settings_btn_rect.collidepoint(event.pos): return "SETTINGS"

# ==============================================================================
# --- 遊戲精靈類別 (Sprites Class) ---
# ==============================================================================
class Barrier(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((80, 20), pygame.SRCALPHA) 
        pygame.draw.rect(self.image, (0, 255, 180, 180), (0, 0, 80, 20), border_radius=5)
        pygame.draw.rect(self.image, Colors.WHITE, (0, 0, 80, 20), 2, border_radius=5)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_hp = 300
        self.hp = self.max_hp
        self.dragging = False

    def update(self):
        if self.hp <= 0:
            self.kill()

    def draw_hp_bar(self, surf):
        if self.hp > 0:
            draw_health(surf, self.hp, self.rect.x, self.rect.y - 8, self.max_hp, Colors.CYAN, length=self.rect.width)

class Laser(pygame.sprite.Sprite):
    def __init__(self, boss_sprite):
        super().__init__()
        self.boss = boss_sprite
        self.width = 35
        self.image = pygame.Surface((self.width, Config.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 0, 50, 160), (0, 0, self.width, Config.HEIGHT))
        pygame.draw.rect(self.image, (255, 200, 200, 230), (10, 0, self.width - 20, Config.HEIGHT))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.boss.rect.centerx
        self.rect.y = self.boss.rect.bottom
        self.damage_timer = pygame.time.get_ticks()

    def update(self):
        if self.boss and self.boss.alive():
            self.rect.centerx = self.boss.rect.centerx
        else:
            self.kill()

class Rock(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.type_idx = random.randrange(len(rock_imgs)) 
        self.image_ori = rock_imgs[self.type_idx]
        self.image_ori.set_colorkey(Colors.BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, Config.WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        
        diff_hp_mult = 1.5 if game_difficulty == 1 else 1.0
        diff_spd_add = 1.5 if game_difficulty == 1 else 0.0

        if self.type_idx == 2:
            self.speedy = random.randrange(4, 6) + min(2, (level - 1) * 0.4) + diff_spd_add
            self.speedx = 0 
            self.rot_degree = 0 
        else:
            self.speedy = random.randrange(1, 3) + min(3, (level - 1) * 0.5) + diff_spd_add
            self.speedx = random.randrange(-2, 2)
            self.rot_degree = random.randrange(-3, 3)
        if level == 1:
            self.speedy *= Config.LEVEL1_FALL_SPEED
        self.y_acc = 0.0
        self.total_degree = 0
        self.hp = int((10 + (level * 5)) * diff_hp_mult)
        self.virus = 'rhino'   # 鼻病毒：怕肥皂，不怕酒精
        self.coat = False

    def rotate(self):
        if self.rot_degree != 0:
            self.total_degree = (self.total_degree + self.rot_degree) % 360
            self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center

    def update(self):
        self.rotate()
        self.y_acc += self.speedy          # 小數速度累積，避免被取整成 0
        step = int(self.y_acc)
        self.rect.y += step
        self.y_acc -= step
        self.rect.x += self.speedx
        if self.rect.left > Config.WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, Config.WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

class Tracker(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.image_plain = pygame.transform.scale(soldier_img, (80, 80))
        self.image_coat = self.image_plain.copy()
        pygame.draw.circle(self.image_coat, (255, 165, 0), (40, 40), 38, 4)   # 橘色外套圈
        self.virus = 'para'    # 副流感病毒：穿外套，要用酒精拆掉
        self.coat = True
        self.image = self.image_coat
        self.rect = self.image.get_rect()
        self.radius = 35
        self.rect.x = random.randrange(0, Config.WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        
        diff_hp_mult = 1.5 if game_difficulty == 1 else 1.0
        diff_spd_add = 1.2 if game_difficulty == 1 else 0.0

        self.speedy = random.randrange(2, 4) + min(level * 0.5, 2) + diff_spd_add
        if level == 1:
            self.speedy *= Config.LEVEL1_FALL_SPEED
        self.y_acc = 0.0
        self.hp = int((30 + (level * 10)) * diff_hp_mult)
        self.speedx = random.choice([-3, -2, 2, 3]) * (1 + min(level * 0.1, 0.5))

    def strip_coat(self):
        self.coat = False
        self.image = self.image_plain

    def update(self):
        self.y_acc += self.speedy          # 小數速度累積，避免被取整成 0
        step = int(self.y_acc)
        self.rect.y += step
        self.y_acc -= step
        self.rect.x += self.speedx
        if self.rect.right >= Config.WIDTH:
            self.rect.right = Config.WIDTH
            self.speedx *= -1
        elif self.rect.left <= 0:
            self.rect.left = 0
            self.speedx *= -1

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        current_boss_raw = boss_img2 if level >= 2 else boss_img
        orig_rect = current_boss_raw.get_rect()
        target_width = 160 
        target_height = int(target_width * (orig_rect.height / orig_rect.width))
        self.image = pygame.transform.smoothscale(current_boss_raw, (target_width, target_height))
        
        self.rect = self.image.get_rect()
        self.radius = 70
        self.rect.centerx = Config.WIDTH / 2
        self.rect.y = -target_height
        self.level = level
        self.speedx = 3 + min(level, 3)
        if game_difficulty == 1:
            self.speedx += 2 

        diff_hp_mult = 1.5 if game_difficulty == 1 else 1.0
        self.max_health = int((1000 + (level - 1) * 500) * diff_hp_mult)
        self.health = self.max_health

        self.shield_thresholds = [int(self.max_health * 0.66), int(self.max_health * 0.33)]
        self.shielded = False           
        self.shield_wave_count = 0      
        self.shield_wave_needed = 5     
        self.shield_flash_timer = 0     

        self.last_bullet_time = pygame.time.get_ticks()
        self.bullet_interval = 1800 if game_difficulty == 1 else 2500 
        
        self.laser_active = False
        self.laser_timer = pygame.time.get_ticks()
        self.laser_duration = 4000     
        self.laser_cooldown = 5000 if game_difficulty == 1 else 7000 

    def update(self):
        if self.rect.y < 50:
            self.rect.y += 2
        else:
            self.rect.x += self.speedx
            if self.rect.right > Config.WIDTH or self.rect.left < 0:
                self.speedx *= -1
        if self.shielded:
            self.shield_flash_timer += 1

    def check_shield_trigger(self):
        for threshold in self.shield_thresholds[:]:
            if self.health <= threshold:
                self.shield_thresholds.remove(threshold)
                self.shielded = True
                self.shield_wave_count = 0
                self.shield_flash_timer = 0
                return True
        return False

    def notify_minion_killed(self):
        if self.shielded:
            self.shield_wave_count += 1
            if self.shield_wave_count >= self.shield_wave_needed:
                self.shielded = False
                return True  
        return False

    def try_shoot_bullet(self, bullets_group, all_sprites_group):
        if self.rect.y < 50: 
            return  
        now = pygame.time.get_ticks()
        if now - self.last_bullet_time > self.bullet_interval:
            self.last_bullet_time = now
            b = BossBullet(self.rect.centerx, self.rect.bottom)
            bullets_group.add(b)
            all_sprites_group.add(b)

class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 80, 0), (9, 9), 9)
        pygame.draw.circle(self.image, (255, 200, 0), (9, 9), 5)
        self.rect = self.image.get_rect()
        self.rect.centerx = x + random.randint(-30, 30)
        self.rect.y = y
        self.speedy = 6 if game_difficulty == 1 else 4
        self.radius = 9
        self.hp = 1  

    def update(self):
        self.rect.y += self.speedy

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class ItemPopText(pygame.sprite.Sprite):
    def __init__(self, x, y, item_name):
        super().__init__()
        if 20 not in font_cache:
            try: font_cache[20] = pygame.font.Font(font_name, 20)
            except FileNotFoundError: font_cache[20] = pygame.font.SysFont('arial', 20)
        self.image = font_cache[20].render(f"+1 {item_name}", True, Colors.CYAN)
        self.rect = self.image.get_rect(center=(x, y - 25))
        self.speedy = -2.5
        self.alpha = 255
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        now = pygame.time.get_ticks()
        if now - self.last_update > 25:
            self.last_update = now
            self.alpha -= 12
            if self.alpha <= 0: 
                self.kill()
            else: 
                self.image.set_alpha(self.alpha)

class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage):
        super().__init__()
        if 20 not in font_cache:
            try: font_cache[20] = pygame.font.Font(font_name, 20)
            except FileNotFoundError: font_cache[20] = pygame.font.SysFont('arial', 20)
        self.image = font_cache[20].render(str(int(damage)), True, Colors.YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speedy = -2
        self.alpha = 255
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        now = pygame.time.get_ticks()
        if now - self.last_update > 30:
            self.last_update = now
            self.alpha -= 15
            if self.alpha <= 0: 
                self.kill()
            else: 
                self.image.set_alpha(self.alpha)

class ScoreText(pygame.sprite.Sprite):
    def __init__(self, x, y, score_val):
        super().__init__()
        if 22 not in font_cache:
            try: font_cache[22] = pygame.font.Font(font_name, 22)
            except FileNotFoundError: font_cache[22] = pygame.font.SysFont('arial', 22)
        self.image = font_cache[22].render(f"+{int(score_val)}", True, Colors.GREEN)
        self.rect = self.image.get_rect(center=(x + 25, y - 10))
        self.speedy = -1.5
        self.alpha = 255
        self.last_update = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speedy
        now = pygame.time.get_ticks()
        if now - self.last_update > 30:
            self.last_update = now
            self.alpha -= 12
            if self.alpha <= 0: 
                self.kill()
            else: 
                self.image.set_alpha(self.alpha)

# ==============================================================================
# --- 遊戲核心流程控制群組 ---
# ==============================================================================
def reset_run_progress():
    """遊戲結束或返回主畫面時，重置關卡進度與本輪天賦（商店升級保留）"""
    global game_level
    game_level = 1
    passive_talents.clear()

def damage_rock(hit, dmg):
    """對單一敵人造成傷害並處理死亡、掉落、護盾計數"""
    global score, shield_msg_text, shield_msg_timer
    if not hit.alive():
        return
    now = pygame.time.get_ticks()
    if getattr(hit, 'coat', False):    # 穿著外套：只受 1/4 傷害
        dmg = max(1, dmg // 4)
    hit.hp -= dmg
    all_sprites.add(DamageText(hit.rect.centerx, hit.rect.centery, dmg))
    if hit.hp > 0:
        all_sprites.add(Explosion(hit.rect.center, 'sm'))
        return

    hit.kill()
    mission_event('kill')
    random.choice(expl_sounds).play()
    add_score = 100 if isinstance(hit, Tracker) else (75 if (isinstance(hit, Rock) and hit.type_idx == 2) else hit.radius)
    score += add_score
    all_sprites.add(ScoreText(hit.rect.centerx, hit.rect.centery, add_score))
    all_sprites.add(Explosion(hit.rect.center, 'lg'))

    if random.random() > 0.9:
        gained_type = random.choice(['shield', 'damage_up', 'soap', 'alcohol'])
        add_to_inventory(gained_type)
        all_sprites.add(ItemPopText(hit.rect.centerx, hit.rect.centery, ITEM_NAMES[gained_type]))

    if game_state == 1 and boss and boss.shielded:
        if boss.notify_minion_killed():
            shield_msg_text = '護盾解除！繼續攻擊 Boss！'
            shield_msg_timer = now
    elif game_state == 0:
        new_enemy(game_level)

def proceed_to_next_level_setup():
    global target_score, game_state, game_level, max_enemies_on_screen
    for l in lasers: l.kill()
    for b in boss_bullets: b.kill()
    
    draw_talent_select()
    game_level += 1
    load_level_missions(game_level)
    
    screen.fill(Colors.BLACK)
    screen.blit(background_img, (0, 0))
    draw_text(screen, f"LEVEL {game_level} START!", 64, Config.WIDTH / 2, Config.HEIGHT / 2, Colors.YELLOW)
    pygame.display.update()
    pygame.time.delay(1000)
    
    # 關卡進階時，同樣依據難度模式增加目標分數
    if game_difficulty == 0:
        target_score = score + 500   # 簡單模式：下一關只需再拿 500 分就進魔王關
    else:
        target_score = score + 2500  # 困難模式：下一關需再拿 2500 分
        
    game_state = 0
    max_enemies_on_screen = 6 + game_level * 2  
    for i in range(max_enemies_on_screen): new_enemy(game_level)

def draw_game_ui(now):
    draw_text(screen, f"SCORE: {score}", 18, Config.WIDTH - 130, 15)
    diff_str = "簡單" if game_difficulty == 0 else "困難"
    draw_text(screen, f"LV: {game_level} ({diff_str})", 18, Config.WIDTH - 50, 45, Colors.YELLOW)
    draw_text(screen, f"DMG: {upgrade_click_dmg}", 18, Config.WIDTH - 130, 45, Colors.ORANGE)

    hover = game_back_rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, Colors.YELLOW if hover else Colors.DARK_GRAY, game_back_rect, border_radius=8)
    pygame.draw.rect(screen, Colors.WHITE, game_back_rect, 2, border_radius=8)
    draw_text(screen, "返回", 18, game_back_rect.centerx, game_back_rect.y + 5, Colors.BLACK if hover else Colors.WHITE)

    line_color = Colors.GREEN if base_health > base_max_health * 0.3 else Colors.RED
    if base_health <= base_max_health * 0.3 and (now // 150) % 2 == 0:
        pass  
    else:
        pygame.draw.line(screen, line_color, (0, Config.HEIGHT - 6), (Config.WIDTH, Config.HEIGHT - 6), 6)
        
    draw_text(screen, "🛡️ 免疫防線強度", 14, 100, Config.HEIGHT - 55, Colors.CYAN)
    draw_health(screen, base_health, 30, Config.HEIGHT - 35, base_max_health, color=line_color, length=150)
    
    draw_lives(screen, base_lives, heart_mini_img, Config.WIDTH - 120, Config.HEIGHT - 40)
    draw_text(screen, "核心細胞", 12, Config.WIDTH - 80, Config.HEIGHT - 36, Colors.WHITE)

    if game_state == 1 and boss:
        if game_level == 1:
            draw_text(screen, "【 病原體：流感病毒 】", 16, Config.WIDTH // 2, 2, Colors.RED)
        elif game_level == 2:
            draw_text(screen, "【 變異體：核心進化流感病毒 】", 16, Config.WIDTH // 2, 2, Colors.ORANGE)

        boss_bar_color = Colors.BLUE if boss.shielded else Colors.RED
        draw_health(screen, boss.health, Config.WIDTH // 2 - 150, 20, boss.max_health, boss_bar_color, 300) 

        if boss.shielded:
            if (boss.shield_flash_timer // 15) % 2 == 0:
                draw_text(screen, '🛡 護盾中 — 消滅小兵！', 20, Config.WIDTH / 2, 40, Colors.CYAN)
            remaining = boss.shield_wave_needed - boss.shield_wave_count
            draw_text(screen, f'演變小兵: {remaining}', 17, Config.WIDTH / 2, 65, Colors.YELLOW)
            
        if game_level >= 2 and not boss.laser_active:
            time_until_laser = boss.laser_cooldown - (now - boss.laser_timer)
            if time_until_laser < 2000 and (now // 200) % 2 == 0:
                draw_text(screen, '⚠️ 警告：偵測到高能粒子蓄力中！', 18, Config.WIDTH / 2, Config.HEIGHT // 2 - 80, Colors.RED)

# ==============================================================================
# --- 肺部防護戰 (原本遊戲的主流程) ---
# ==============================================================================
def start_lungs_game():
    global all_sprites, rocks, boss_bullets, barriers, lasers
    global inventory, base_health, base_max_health, base_lives
    global max_enemies_on_screen, game_state, boss
    global score, target_score, game_level
    global shield_msg_text, shield_msg_timer

    play_bgm()
    
    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    boss_bullets = pygame.sprite.Group()
    barriers = pygame.sprite.Group()
    lasers = pygame.sprite.Group()

    inventory = [None] * Config.TOOLBAR_SLOTS
    inventory[0] = {"type": "shield", "count": 1}       # 疫苗
    inventory[1] = {"type": "soap", "count": 1}         # 肥皂
    inventory[2] = {"type": "alcohol", "count": 1}      # 酒精
    inventory[3] = {"type": "damage_up", "count": 1}    # 強效

    base_health = upgrade_max_hp
    base_max_health = upgrade_max_hp
    base_lives = upgrade_lives
    max_enemies_on_screen = 6 + game_level * 2
    for i in range(max_enemies_on_screen): new_enemy(game_level)

    load_level_missions(game_level)
    game_state = 0 
    boss = None
    score = 0 
    
    # --- 依難度設定第一關的目標分數門檻 ---
    if game_difficulty == 0:
        target_score = 500   # 簡單模式：500 分就進魔王對話與關卡
    else:
        target_score = 2000  # 困難模式：第一關 2000 分就進魔王關
        
    regen_timer = pygame.time.get_ticks()
    shield_msg_timer = 0
    shield_msg_text = ''

    running = True
    paused = False
    pause_start = 0

    while running:
        clock.tick(Config.FPS)
        now = pygame.time.get_ticks()

        if game_state not in (2, 3, 4) and not paused:
            pygame.event.set_grab(True)
        else:
            pygame.event.set_grab(False)

        if 'regen' in passive_talents and now - regen_timer > 3000:
            regen_timer = now
            base_health = min(base_max_health, base_health + 5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:   # ESC：直接回到主畫面
                    for l in lasers: l.kill()
                    for b in boss_bullets: b.kill()
                    pygame.mixer.music.stop()
                    reset_run_progress()
                    return

                elif event.key == pygame.K_p:
                    paused = not paused
                    if paused:
                        pause_start = now
                        pygame.mixer.music.pause()
                    else:
                        # 把暫停期間的時間補回所有計時器，避免恢復後魔王/雷射瞬間連發
                        delta = now - pause_start
                        regen_timer += delta
                        shield_msg_timer += delta
                        if boss:
                            boss.last_bullet_time += delta
                            boss.laser_timer += delta
                        for l in lasers:
                            l.damage_timer += delta
                        pygame.mixer.music.unpause()
                
                elif game_state == 3 and event.key == pygame.K_SPACE:
                    if game_level == 1:   # 第一關通關後直接回主畫面
                        reset_run_progress()
                        return
                    game_state = 4

                elif not paused and game_state not in (2, 3, 4):
                    if event.key == pygame.K_1:   use_item_by_slot(0)
                    elif event.key == pygame.K_2: use_item_by_slot(1)
                    elif event.key == pygame.K_3: use_item_by_slot(2)
                    elif event.key == pygame.K_4: use_item_by_slot(3)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and game_back_rect.collidepoint(event.pos):   # 返回按鈕：回主畫面
                    for l in lasers: l.kill()
                    for b in boss_bullets: b.kill()
                    pygame.mixer.music.stop()
                    reset_run_progress()
                    return
                if not paused:
                    pos = pygame.mouse.get_pos()
                    
                    if game_state == 3:
                        if event.button == 1:
                            if game_level == 1:   # 第一關通關後直接回主畫面
                                reset_run_progress()
                                return
                            game_state = 4
                        continue

                    if game_state == 4:
                        if event.button == 1:
                            if game_level < MAX_LEVEL and choice_next_rect.collidepoint(pos):
                                proceed_to_next_level_setup()
                            elif choice_home_rect.collidepoint(pos):
                                for l in lasers: l.kill()
                                for b in boss_bullets: b.kill()
                                reset_run_progress()
                                return  # 返回選單區域
                        continue  # 選單點擊不要同時當成射擊

                    # 點擊工具列格子 = 使用該道具（與鍵盤 1~4 相同）
                    if event.button == 1:
                        slot_hit = next((i for i in range(Config.TOOLBAR_SLOTS) if toolbar_slot_rect(i).collidepoint(pos)), None)
                        if slot_hit is not None:
                            use_item_by_slot(slot_hit)
                            continue

                    if event.button == 1:
                        for b in barriers:
                            if b.rect.collidepoint(pos):
                                b.dragging = True
                                break
                        else:
                            shoot_sound.play()
                            current_click_dmg = upgrade_click_dmg

                            clicked_bullets = [b for b in boss_bullets if b.rect.inflate(upgrade_click_radius + 10, upgrade_click_radius + 10).collidepoint(pos)]
                            for b in clicked_bullets:
                                b.kill()
                                mission_event('bullet')
                                all_sprites.add(Explosion(b.rect.center, 'sm'))
                                score += 30
                                all_sprites.add(ScoreText(b.rect.centerx, b.rect.centery, 30))

                            clicked_rocks = [r for r in rocks if r.rect.inflate(upgrade_click_radius, upgrade_click_radius).collidepoint(pos)]
                            for hit in clicked_rocks:
                                damage_rock(hit, current_click_dmg)

                            # 天賦【爆裂點擊】：點中敵人時，點擊點周圍小範圍的其他敵人受到一半傷害
                            if 'splash' in passive_talents and clicked_rocks:
                                for r in list(rocks):
                                    if r in clicked_rocks:
                                        continue
                                    if math.hypot(r.rect.centerx - pos[0], r.rect.centery - pos[1]) <= 90:
                                        damage_rock(r, max(1, current_click_dmg // 2))

                            # 天賦【連鎖點擊】：每次點擊額外隨機打擊畫面上另一個敵人
                            if 'chain' in passive_talents:
                                others = [r for r in rocks if r not in clicked_rocks]
                                if others:
                                    damage_rock(random.choice(others), current_click_dmg)

                            if game_state == 1 and boss and not boss.shielded:
                                if boss.rect.inflate(upgrade_click_radius, upgrade_click_radius).collidepoint(pos):
                                    boss.health -= current_click_dmg
                                    all_sprites.add(DamageText(pos[0], pos[1], current_click_dmg))
                                    if boss.check_shield_trigger():
                                        shield_msg_text = f'護盾啟動！消滅 {boss.shield_wave_needed} 隻小兵！'
                                        shield_msg_timer = now
                                        for _ in range(boss.shield_wave_needed): new_enemy(game_level)
                                    
                                    if boss.health <= 0:
                                        all_sprites.add(Explosion(boss.rect.center, 'lg'))
                                        score += 800
                                        all_sprites.add(ScoreText(boss.rect.centerx, boss.rect.centery, 800))
                                        boss.kill()
                                        boss = None
                                        unlock_wiki('flu' if game_level == 1 else 'rsv')
                                        mission_event('boss')
                                        game_state = 3

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for b in barriers: b.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if not paused:
                    for b in barriers:
                        if b.dragging:
                            b.rect.centerx = event.pos[0]
                            b.rect.centery = max(Config.HEIGHT - 260, min(Config.HEIGHT - 80, event.pos[1])) 

        if not paused and game_state not in (2, 3, 4):
            all_sprites.update()
            
            if game_state == 1 and boss and game_level >= 2:
                if not boss.laser_active:
                    if now - boss.laser_timer > boss.laser_cooldown:
                        boss.laser_active = True
                        boss.laser_timer = now
                        laser_beam = Laser(boss)
                        all_sprites.add(laser_beam)
                        lasers.add(laser_beam)
                else:
                    if now - boss.laser_timer > boss.laser_duration:
                        boss.laser_active = False
                        boss.laser_timer = now
                        for l in lasers: l.kill()

            for l in lasers:
                blocked = False
                sorted_barriers = sorted(barriers.sprites(), key=lambda x: x.rect.y)
                for b in sorted_barriers:
                    if b.rect.left < l.rect.centerx < b.rect.right:
                        blocked = True
                        if now - l.damage_timer > 80: 
                            b.hp -= 8
                            l.damage_timer = now
                            all_sprites.add(Explosion((l.rect.centerx, b.rect.y + 10), 'sm'))
                        break 
                
                if not blocked and now - l.damage_timer > 100:
                    base_health -= 5 
                    l.damage_timer = now
                    all_sprites.add(Explosion((l.rect.centerx, Config.HEIGHT - 20), 'sm'))

            if score >= target_score and game_state == 0:
                # 已移除魔王：達到目標分數即直接通關
                for r in rocks: r.kill()
                unlock_wiki('flu' if game_level == 1 else 'rsv')
                game_state = 3

            if game_state == 0 and len(rocks) < max_enemies_on_screen: 
                new_enemy(game_level)

            if game_state == 1 and boss:
                boss.try_shoot_bullet(boss_bullets, all_sprites)
                if boss.shielded and len(rocks) < boss.shield_wave_needed: 
                    new_enemy(game_level)

            for r in rocks.copy():
                hit_barriers = pygame.sprite.spritecollide(r, barriers, False)
                for b in hit_barriers:
                    b.hp -= r.radius * 2
                    r.kill()
                    die_sound.play()
                    all_sprites.add(Explosion(r.rect.center, 'sm'))
                    if game_state == 0: new_enemy(game_level)

            for b in boss_bullets.copy():
                if b.rect.top > Config.HEIGHT:
                    b.kill()
                    base_health -= 15
                    die_sound.play()
                    all_sprites.add(Explosion((b.rect.centerx, Config.HEIGHT - 20), 'sm'))

            for r in rocks.copy():
                if r.rect.top > Config.HEIGHT:
                    base_health -= r.radius
                    r.kill()
                    die_sound.play()
                    all_sprites.add(Explosion((r.rect.centerx, Config.HEIGHT - 20), 'sm'))
                    if game_state == 0: new_enemy(game_level)

            if base_health <= 0:
                base_lives -= 1
                base_health = base_max_health
                if base_lives <= 0:
                    pygame.event.set_grab(False) 
                    screen.fill(Colors.BLACK)
                    draw_text(screen, "GAME OVER", 64, Config.WIDTH / 2, Config.HEIGHT / 3, Colors.RED)
                    draw_text(screen, f"FINAL SCORE: {score}", 32, Config.WIDTH / 2, Config.HEIGHT / 2)
                    draw_text(screen, "按任意鍵回到主選單", 22, Config.WIDTH / 2, Config.HEIGHT * 2 / 3)
                    pygame.display.update()
                    
                    waiting = True
                    while waiting:
                        clock.tick(Config.FPS)
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT: 
                                pygame.quit()
                                sys.exit()
                            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): 
                                waiting = False
                    reset_run_progress()
                    return

        # --------------------------------------------------------------------------
        # --- 畫面彩現與繪製 (Render & Drawing) ---
        # --------------------------------------------------------------------------
        screen.fill(Colors.BLACK)
        screen.blit(background_img, (0, 0))
        all_sprites.draw(screen)
        for r in rocks:
            draw_virus_label(screen, r)
        
        for b in barriers:
            b.draw_hp_bar(screen)
        
        draw_toolbar(screen, inventory)
        draw_mission_panel(screen)
        draw_game_ui(now)
        
        if game_state == 3:
            draw_level_clear_box(screen, game_level)

        if game_state == 4:
            draw_level_transition_choice_screen(screen)

        draw_unlock_banner(screen, Config.HEIGHT - 110)
        draw_mission_toast(screen, Config.HEIGHT - 160)

        if shield_msg_text and now - shield_msg_timer < 2000:
            msg_w = get_font(22).size(shield_msg_text)[0] + 40
            msg_surf = pygame.Surface((msg_w, 40), pygame.SRCALPHA)
            msg_surf.fill((0, 0, 0, 120))
            screen.blit(msg_surf, (Config.WIDTH // 2 - msg_w // 2, Config.HEIGHT // 2 - 20))
            draw_text(screen, shield_msg_text, 22, Config.WIDTH / 2, Config.HEIGHT // 2 - 15, Colors.YELLOW)

        if paused:
            overlay = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            draw_text(screen, "PAUSED", 64, Config.WIDTH / 2, Config.HEIGHT / 2 - 40, Colors.YELLOW)

        draw_custom_crosshair(screen)
        pygame.display.update()

# ==============================================================================
# --- 主程式進入點 ---
# ==============================================================================
def main():
    while True:
        pygame.event.set_grab(False)
        action = draw_init()
        
        if action == "QUIT": 
            break
        elif action == "WIKI":
            draw_wiki()
            continue
        elif action == "SETTINGS":
            draw_settings()
            continue
        elif action == "PLAY":   # 遊戲開始 → 進入關卡選擇
            # 呼叫器官地圖選擇選單
            selected_stage = run_organ_select(screen, clock, font_cache, draw_custom_crosshair)

            # 根據地圖選單點擊的結果進行分流
            if selected_stage == "lungs":
                # 執行現有的肺部流感防禦戰
                start_lungs_game()
            elif selected_stage == "intestines":
                # 執行你的 1333 行塔防遊戲關卡！
                play_bgm()
                run_organ_td(screen, clock, font_cache, draw_custom_crosshair)
            elif selected_stage == "stomach":
                # 吞噬生存戰
                play_bgm()
                run_organ_survival(screen, clock, font_cache, draw_custom_crosshair)
            elif selected_stage == "heart":
                # 未來可延伸心臟遊戲關卡
                play_bgm()
                pass
            continue

    pygame.quit()

if __name__ == "__main__":
    main()