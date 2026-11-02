import pygame
import sys
import os

pygame.init()
# 配合主程式畫面大小 800 x 700
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("UI 按鈕框框標記工具 (先點左上角，再點右下角)")

# 載入背景與 UI 圖片
bg_path = None
for name in ["bg", "background"]:
    for ext in [".png", ".jpg", ".jpeg"]:
        target_path = os.path.join("img", name + ext)
        if os.path.exists(target_path):
            bg_path = target_path
            break
    if bg_path:
        break

ui_panel_img = None
for ext in [".png", ".jpg", ".jpeg"]:
    if os.path.exists(os.path.join("img", "ui_panel" + ext)):
        ui_panel_img = pygame.image.load(os.path.join("img", "ui_panel" + ext)).convert_alpha()
        break

if bg_path:
    bg = pygame.image.load(bg_path).convert()
    bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg.fill((30, 30, 30))

# -------------------------------------------------------------
# 💡 直接套用你在 organ_td_3.py 中改好的 panel 座標與尺寸
panel_w, panel_h = 440, 500
panel_x = (SCREEN_WIDTH - panel_w) // 2  # x = 180
panel_y = 120
# -------------------------------------------------------------

temp_point = None
rect_list = []
font = pygame.font.SysFont(None, 24)

running = True
while running:
    screen.blit(bg, (0, 0))
    
    # 畫出你的選單框架
    if ui_panel_img:
        scaled_ui = pygame.transform.smoothscale(ui_panel_img, (panel_w, panel_h))
        screen.blit(scaled_ui, (panel_x, panel_y))
    else:
        pygame.draw.rect(screen, (100, 80, 60), (panel_x, panel_y, panel_w, panel_h), 2)

    # 繪製已標記完成的矩形框
    for idx, r in enumerate(rect_list):
        pygame.draw.rect(screen, (0, 255, 255), r, 2)
        num_txt = font.render(f"Slot {idx + 1}", True, (0, 255, 255))
        screen.blit(num_txt, (r.x + 5, r.y + 5))

    # 如果點了第一點，畫即時拉框預覽
    if temp_point:
        m_x, m_y = pygame.mouse.get_pos()
        x = min(temp_point[0], m_x)
        y = min(temp_point[1], m_y)
        w = abs(temp_point[0] - m_x)
        h = abs(temp_point[1] - m_y)
        pygame.draw.rect(screen, (255, 255, 0), (x, y, w, h), 2)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if temp_point is None:
                temp_point = event.pos
            else:
                x = min(temp_point[0], event.pos[0])
                y = min(temp_point[1], event.pos[1])
                w = abs(temp_point[0] - event.pos[0])
                h = abs(temp_point[1] - event.pos[1])
                if w > 10 and h > 10:  # 避免誤點
                    rect_list.append(pygame.Rect(x, y, w, h))
                    print(f"新增 Slot {len(rect_list)}: pygame.Rect({x}, {y}, {w}, {h})")
                temp_point = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # R 鍵重置
                rect_list = []
                temp_point = None
                print("--- 已重置 ---")
            elif event.key == pygame.K_z and rect_list:  # Z 鍵撤銷
                rect_list.pop()
                print("--- 已撤銷上一個框框 ---")

    # 提示文字
    status_str = "請點擊格子的 [左上角]" if temp_point is None else "請點擊格子的 [右下角]"
    txt = font.render(f"Slots: {len(rect_list)}/3 | {status_str} (Press 'R' to clear, 'Z' to undo)", True, (255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 0), (10, 10, txt.get_width() + 10, 30))
    screen.blit(txt, (15, 15))

    pygame.display.update()

pygame.quit()

print("\n" + "="*50)
print("請複製下方代碼貼回 organ_td_3.py 中的 tower_slots：")
print("="*50)
print("tower_slots = [")
for idx, r in enumerate(rect_list):
    print(f'    {{"rect": pygame.Rect({r.x}, {r.y}, {r.width}, {r.height}), "type": {idx + 1}}},')
print("]")