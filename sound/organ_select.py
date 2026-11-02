# 檔案名稱：organ_select.py
import pygame
import sys
from organ_survival import run_organ_survival  # 1. 匯入你的白血球吞噬生存遊戲

def run_organ_select(screen, clock, font_cache, draw_custom_crosshair):
    # 隱藏預設滑鼠游標
    pygame.mouse.set_visible(False)
    
    # 載入背景圖
    bg_img = None
    try:
        loaded_img = pygame.image.load("img/map_bg.png").convert()
        bg_img = pygame.transform.scale(loaded_img, (screen.get_width(), screen.get_height()))
    except FileNotFoundError:
        print("警告：找不到 img/map_bg.png！已使用預設單色背景替代。")
        bg_img = pygame.Surface((screen.get_width(), screen.get_height()))
        bg_img.fill((20, 30, 50))

    # 器官資料定義
    organs = {
        "brain": {
            "select_rect": pygame.Rect(40, 30, 130, 120),       # 左邊大腦
            "highlight_rect": pygame.Rect(370, 120, 60, 60),    # 中間大腦
            "name": "大腦 (Brain)",
            "desc": "掌控全身思考與神經！\n病毒入侵會引發腦炎與高燒。",
            "enabled": True
        },
        "liver": {
            "select_rect": pygame.Rect(40, 190, 130, 80),      # 左邊肝臟
            "highlight_rect": pygame.Rect(330, 350, 65, 50),    # 中間肝臟
            "name": "肝臟 (Liver)",
            "desc": "幫助代謝與解毒！\n肝炎病毒會造成疲倦與發炎。",
            "enabled": False
        },
        "stomach": {
            "select_rect": pygame.Rect(40, 320, 130, 80),      # 左邊胃部
            "highlight_rect": pygame.Rect(410, 360, 60, 50),    # 中間胃部
            "name": "胃部 (Stomach - 吞噬生存戰)",
            "desc": "消化食物吸收營養！\n控制白血球在胃部吞噬病毒進化！",
            "enabled": True  # 2. 將胃部設為解鎖狀態 (True)
        },
        "lungs": {
            "select_rect": pygame.Rect(40, 460, 130, 80),      # 左邊肺臟
            "highlight_rect": pygame.Rect(325, 370, 150, 80),   # 中間肺臟
            "name": "肺臟 (Lungs)",
            "desc": "負責呼吸氧氣！\n流感病毒會侵襲肺部，導致咳嗽。",
            "enabled": True
        },
        "intestines": {
            "select_rect": pygame.Rect(40, 560, 130, 100),     # 左邊腸部
            "highlight_rect": pygame.Rect(330, 405, 140, 70),   # 中間腸部
            "name": "腸部 (Intestines)",
            "desc": "消化最後防線！\n腸病毒會破壞腸道引發腹瀉。",
            "enabled": True
        }
    }

    def draw_text_left(surf, text, size, x, y, color=(255, 255, 255)):
        if size not in font_cache:
            try:
                font_cache[size] = pygame.font.Font("font.ttf", size)
            except FileNotFoundError:
                font_cache[size] = pygame.font.SysFont("microsoftjhenghei", size)
        font = font_cache[size]
        text_surf = font.render(text, True, color)
        surf.blit(text_surf, (x, y))

    def draw_text_center(surf, text, size, x, y, color=(255, 255, 255)):
        if size not in font_cache:
            try:
                font_cache[size] = pygame.font.Font("font.ttf", size)
            except FileNotFoundError:
                font_cache[size] = pygame.font.SysFont("microsoftjhenghei", size)
        font = font_cache[size]
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(x, y))
        surf.blit(text_surf, text_rect)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        hovered_key = None

        # 判定是否移到左側選取區
        for key, data in organs.items():
            if data["select_rect"].collidepoint(mouse_pos):
                hovered_key = key
                break

        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered_key:
                    if organs[hovered_key]["enabled"]:
                        # 3. 判斷如果點擊的是胃部，直接啟動白血球生存遊戲！
                        if hovered_key == "stomach":
                            run_organ_survival(screen, clock, font_cache, draw_custom_crosshair)
                        else:
                            return hovered_key  # 其他器官維持原樣（回傳給主程式）
                    else:
                        print(f"{organs[hovered_key]['name']} 暫未開放解鎖！")

        # 1. 繪製背景底圖
        screen.blit(bg_img, (0, 0))

        # 2. 左邊選取時，中間對應器官亮起來 + 左邊圖示加框
        if hovered_key:
            info = organs[hovered_key]
            
            s_left = pygame.Surface((info["select_rect"].width, info["select_rect"].height), pygame.SRCALPHA)
            pygame.draw.rect(s_left, (0, 255, 200, 60), s_left.get_rect(), border_radius=10)
            screen.blit(s_left, info["select_rect"].topleft)
            pygame.draw.rect(screen, (0, 255, 200), info["select_rect"], 2, border_radius=10)

            hl_rect = info["highlight_rect"]
            s_mid = pygame.Surface((hl_rect.width + 10, hl_rect.height + 10), pygame.SRCALPHA)
            glow_color = (0, 255, 200, 120) if info["enabled"] else (200, 200, 200, 80)
            pygame.draw.rect(s_mid, glow_color, s_mid.get_rect(), border_radius=12)
            screen.blit(s_mid, (hl_rect.x - 5, hl_rect.y - 5))
            pygame.draw.rect(screen, (255, 255, 255), hl_rect, 2, border_radius=8)

        # 3. 右邊藍色小框內顯示器官介紹詞
        if hovered_key:
            info = organs[hovered_key]
            status_str = "【點擊進入遊戲】" if info["enabled"] else "【未解鎖】"
            color_status = (0, 255, 200) if info["enabled"] else (180, 180, 180)
            
            draw_text_left(screen, f"{info['name']}", 16, 810, 285, (255, 255, 255))
            draw_text_left(screen, status_str, 14, 810, 310, color_status)
            
            lines = info["desc"].split("\n")
            for idx, line in enumerate(lines):
                draw_text_left(screen, line, 13, 810, 335 + (idx * 18), (220, 240, 255))

        # 4. 右下角最大藍色框固定顯示提示文字
        draw_text_center(screen, "請移動滑鼠到想防禦的器官 (按 ESC 返回)", 18, 630, 485, (180, 220, 255))

        # 5. 繪製自訂準星
        draw_custom_crosshair(screen)

        pygame.display.update()