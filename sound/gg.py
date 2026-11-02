import pygame
import sys
import os

pygame.init()
# 配合目前主程式視窗尺寸 800 x 700
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("建塔點 (Spots) 標記工具 - 按 R 重來，按 Z 撤銷")

# 載入背景圖 (自動搜尋 bg 或 background 檔名)
bg_path = None
for name in ["bg", "background"]:
    for ext in [".png", ".jpg", ".jpeg"]:
        target_path = os.path.join("img", name + ext)
        if os.path.exists(target_path):
            bg_path = target_path
            break
    if bg_path:
        break

if bg_path:
    bg = pygame.image.load(bg_path).convert()
    bg = pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    print("⚠️ 提示：在 img/ 資料夾找不到背景圖片，改用預設底色。")
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg.fill((40, 40, 40))

spots_points = []
font = pygame.font.SysFont(None, 24)

running = True
while running:
    screen.blit(bg, (0, 0))

    # 繪製已點擊的建塔圈圈 (Cyan 青色)
    for idx, pt in enumerate(spots_points):
        pygame.draw.circle(screen, (0, 255, 255), pt, 22, 2)
        pygame.draw.circle(screen, (255, 255, 255), pt, 3)  # 中心點提示
        # 標示點的序號
        num_txt = font.render(str(idx + 1), True, (255, 255, 0))
        screen.blit(num_txt, (pt[0] + 12, pt[1] - 12))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # 左鍵點擊新增建塔點
            spots_points.append(event.pos)
            print(f"已標記建塔點 {len(spots_points)}: {event.pos}")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # 按 R 重來
                spots_points = []
                print("--- 建塔點已重置 ---")
            elif event.key == pygame.K_z and spots_points:  # 按 Z 撤銷上一步
                spots_points.pop()
                print("--- 已撤銷上一個點 ---")

    # 顯示提示文字
    txt = font.render(f"Spots: {len(spots_points)} | Left Click to Add | Press 'R' to clear, 'Z' to undo", True, (255, 255, 255))
    pygame.draw.rect(screen, (0, 0, 0), (10, 10, txt.get_width() + 10, 30))
    screen.blit(txt, (15, 15))

    pygame.display.update()

pygame.quit()

print("\n" + "="*50)
print("複製下方這行，貼回主程式的 spots = [...] 即可：")
print("="*50)
print(f"spots = {spots_points}")