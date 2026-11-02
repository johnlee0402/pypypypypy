import pygame
import sys
import math
import random
import os

# 顏色常數
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
RED = (230, 50, 50)
BLUE = (30, 144, 255)
DARK_BAR = (30, 30, 40)

WIN_SCORE = 2000                                  # 累積 2000 分就過關
SCORE_PER_KILL = {1: 60, 2: 40, 3: 100}           # 擊殺各種病毒的得分

class Bullet:
    """ 子彈類別 """
    def __init__(self, x, y, target, damage, speed=12, image=None):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.image = image
        self.alive = True

    def update(self):
        if not self.target or self.target.hp <= 0:
            self.alive = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.target.hp -= self.damage
            self.alive = False
        else:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, screen):
        if self.image:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            angle = math.degrees(math.atan2(-dy, dx))
            rotated_img = pygame.transform.rotate(self.image, angle)
            rect = rotated_img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_img, rect)
        else:
            pygame.draw.circle(screen, (255, 255, 100), (int(self.x), int(self.y)), 6)


class Enemy:
    """ 病毒怪物類別 """
    def __init__(self, path, enemy_type=1, images=None):
        self.path = path
        self.target_node_idx = 0
        self.x, self.y = path[0]
        self.type = enemy_type
        self.images = images if images else {}
        
        if enemy_type == 1:   # 皇冠病毒
            self.speed = 2.2      # 原本 1.6
            self.hp = self.max_hp = 120
            self.reward = 20
        elif enemy_type == 2: # 多眼病毒
            self.speed = 3.2      # 原本 2.4
            self.hp = self.max_hp = 70
            self.reward = 15
        elif enemy_type == 3: # 鎖鏈鐵球病毒
            self.speed = 1.4      # 原本 1.0
            self.hp = self.max_hp = 250
            self.reward = 35

    def update(self):
        if self.target_node_idx < len(self.path):
            tx, ty = self.path[self.target_node_idx]
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.x, self.y = tx, ty
                self.target_node_idx += 1
            else:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed

    def draw(self, screen):
        img = self.images.get(f"enemy{self.type}")
        if img:
            rect = img.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(img, rect)
        else:
            color = (255, 100, 100) if self.type == 1 else (100, 255, 100)
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 18)

        # 怪物上方血條
        bar_w = 30
        rate = max(0, self.hp / self.max_hp)
        pygame.draw.rect(screen, (40, 40, 40), (self.x - 15, self.y - 25, bar_w, 4))
        pygame.draw.rect(screen, (0, 230, 100), (self.x - 15, self.y - 25, bar_w * rate, 4))


class Tower:
    """ 防禦細胞塔類別 """
    def __init__(self, x, y, tower_type=1, images=None):
        self.x = x
        self.y = y
        self.type = tower_type
        self.images = images if images else {}
        self.cooldown = 0
        self.laser_target = None

        # 雷射計時器變數 (用於塔2：發射2秒、暫停1秒)
        self.laser_on = True
        self.laser_timer = pygame.time.get_ticks()
        self.fire_duration = 2000   # 2秒
        self.pause_duration = 1000  # 1秒

        if tower_type == 1:   # 塔1
            self.range = 150
            self.fire_rate = 30
            self.damage = 12      # 原本 25
            self.cost = 50
        elif tower_type == 2: # 塔2 (激光塔)
            self.range = 180
            self.fire_rate = 1
            self.damage = 1       # 原本 2（每幀傷害）
            self.cost = 80
        elif tower_type == 3: # 塔3
            self.range = 130
            self.fire_rate = 45
            self.damage = 24      # 原本 50
            self.cost = 100

    def update(self, enemies, bullets):
        self.laser_target = None
        now = pygame.time.get_ticks()

        if self.cooldown > 0:
            self.cooldown -= 1

        # 針對雷射塔（塔2）的 2秒射擊 / 1秒暫停 邏輯
        if self.type == 2:
            elapsed = now - self.laser_timer
            if self.laser_on:
                if elapsed > self.fire_duration:
                    self.laser_on = False
                    self.laser_timer = now
            else:
                if elapsed > self.pause_duration:
                    self.laser_on = True
                    self.laser_timer = now

        for enemy in enemies:
            dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if dist <= self.range:
                if self.type == 2:
                    if self.laser_on:
                        enemy.hp -= self.damage
                        self.laser_target = (enemy.x, enemy.y)
                    break
                else:
                    if self.cooldown <= 0:
                        bullets.append(Bullet(self.x, self.y, enemy, self.damage, image=self.images.get("bullet1")))
                        self.cooldown = self.fire_rate
                    break

    def draw(self, screen):
        if self.type == 2 and self.laser_target and self.laser_on:
            pygame.draw.line(screen, (100, 200, 255), (self.x, self.y), self.laser_target, 6)
            pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), self.laser_target, 2)

        img = self.images.get(f"tower{self.type}")
        if img:
            rect = img.get_rect(center=(self.x, self.y))
            screen.blit(img, rect)
        else:
            pygame.draw.circle(screen, CYAN, (self.x, self.y), 20)


def load_image_with_fallback(base_name, extensions=[".png", ".jpg", ".jpeg"]):
    for ext in extensions:
        full_path = os.path.join("img", base_name + ext)
        if os.path.exists(full_path):
            try:
                return pygame.image.load(full_path).convert_alpha()
            except Exception as e:
                print(f"無法載入圖片 {full_path}: {e}")
    return None


def game_over_screen(screen, clock, screen_width, screen_height, draw_custom_crosshair):
    """ 遊戲結束畫面選單 """
    font_large = pygame.font.SysFont('arial', 64)
    font_medium = pygame.font.SysFont('microsoftjhenghei', 28)
    
    restart_btn = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 20, 300, 50)
    select_btn = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 90, 300, 50)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "select"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn.collidepoint(mouse_pos):
                    return "restart"
                elif select_btn.collidepoint(mouse_pos):
                    return "select"

        # 半透明遮罩
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # Game Over 標題
        game_over_surf = font_large.render("GAME OVER", True, (255, 50, 50))
        screen.blit(game_over_surf, game_over_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 60)))

        # 再玩一次按鈕
        pygame.draw.rect(screen, (50, 50, 70), restart_btn, border_radius=8)
        pygame.draw.rect(screen, CYAN, restart_btn, 2, border_radius=8)
        restart_text = font_medium.render("再玩一次", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=restart_btn.center))

        # 回到關卡選擇按鈕
        pygame.draw.rect(screen, (50, 50, 70), select_btn, border_radius=8)
        pygame.draw.rect(screen, CYAN, select_btn, 2, border_radius=8)
        select_text = font_medium.render("回到關卡選擇", True, WHITE)
        screen.blit(select_text, select_text.get_rect(center=select_btn.center))

        # 繪製自訂準星
        draw_custom_crosshair(screen)
        pygame.display.update()


def victory_screen(screen, clock, screen_width, screen_height, draw_custom_crosshair, score):
    """ 過關畫面選單 """
    font_large = pygame.font.SysFont('microsoftjhenghei', 56)
    font_medium = pygame.font.SysFont('microsoftjhenghei', 28)
    snapshot = screen.copy()

    restart_btn = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 40, 300, 50)
    select_btn = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 110, 300, 50)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "select"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_btn.collidepoint(mouse_pos):
                    return "restart"
                elif select_btn.collidepoint(mouse_pos):
                    return "select"

        screen.blit(snapshot, (0, 0))
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font_large.render("腸道關卡 通關！", True, (255, 230, 60))
        screen.blit(title, title.get_rect(center=(screen_width // 2, screen_height // 2 - 70)))
        score_surf = font_medium.render(f"最終分數：{score}", True, WHITE)
        screen.blit(score_surf, score_surf.get_rect(center=(screen_width // 2, screen_height // 2 - 10)))

        pygame.draw.rect(screen, (50, 50, 70), restart_btn, border_radius=8)
        pygame.draw.rect(screen, CYAN, restart_btn, 2, border_radius=8)
        restart_text = font_medium.render("再玩一次", True, WHITE)
        screen.blit(restart_text, restart_text.get_rect(center=restart_btn.center))

        pygame.draw.rect(screen, (50, 50, 70), select_btn, border_radius=8)
        pygame.draw.rect(screen, CYAN, select_btn, 2, border_radius=8)
        select_text = font_medium.render("回到關卡選擇", True, WHITE)
        screen.blit(select_text, select_text.get_rect(center=select_btn.center))

        draw_custom_crosshair(screen)
        pygame.display.update()


def run_organ_td(screen, clock, font_cache, draw_custom_crosshair):
    """ 供主程式呼叫的腸部 TD 塔防遊戲函式 """
    pygame.mouse.set_visible(False)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_width(), screen.get_height()

    # 載入所有圖片
    images = {}
    keys = ["bg", "ui_panel", "ui_stats", "tower1", "tower2", "tower3", "bullet1", "enemy1", "enemy2", "enemy3"]

    for key in keys:
        img = load_image_with_fallback(key)
        if img:
            if key == "bg":
                img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            elif "tower" in key:
                img = pygame.transform.scale(img, (48, 48))
            elif "bullet" in key:
                img = pygame.transform.scale(img, (24, 24))
            elif "enemy" in key:
                img = pygame.transform.scale(img, (42, 42))
            images[key] = img
        else:
            images[key] = None

    path = [(84, 86), (108, 113), (125, 129), (148, 140), 
            (176, 146), (199, 136), (229, 135), (255, 146), 
            (268, 169), (271, 189), (270, 206), (256, 223), 
            (250, 237), (237, 245), (225, 253), (212, 270), 
            (205, 289), (196, 308), (202, 330), (201, 348), 
            (199, 361), (189, 379), (173, 392), (162, 405), 
            (145, 420), (132, 434), (121, 453), (116, 476), 
            (116, 505), (116, 528), (123, 548), (133, 566), 
            (141, 583), (156, 593), (179, 603), (194, 613), 
            (221, 615), (234, 608), (246, 602), (261, 597), 
            (276, 578), (289, 558), (294, 533), (301, 507), 
            (309, 480), (314, 457), (326, 433), (343, 418), 
            (359, 397), (383, 392), (405, 389), (433, 388), 
            (452, 388), (471, 398), (488, 417), (501, 433), 
            (515, 456), (527, 475), (533, 490), (538, 507), 
            (544, 525), (551, 547), (561, 558), (586, 574), 
            (610, 580), (635, 576), (648, 560), (660, 540), 
            (668, 512), (667, 483), (657, 460), (660, 430), 
            (668, 407), (684, 389), (699, 365), (702, 338), 
            (697, 313), (682, 294), (661, 282), (641, 277), 
            (615, 283), (591, 284), (563, 279), (546, 271), 
            (527, 258), (513, 244), (499, 215), (499, 183), 
            (507, 156), (527, 132), (559, 122), (582, 124), 
            (591, 136), (616, 153), (636, 162), (660, 159), 
            (678, 142), (693, 125), (714, 97), (717, 91)]

    spots = [(150, 224), (121, 284), (141, 343), (191, 536), 
             (220, 465), (267, 445), (346, 333), (609, 222), 
             (664, 229), (529, 340), (581, 343), (583, 457), 
             (606, 396)]
    panel_w, panel_h = 240, 260
    panel_x = 300
    panel_y = 500
    ui_panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

    tower_slots = [
        {"rect": pygame.Rect(313, 634, 55, 55), "type": 1},
        {"rect": pygame.Rect(391, 635, 57, 52), "type": 2},
        {"rect": pygame.Rect(469, 635, 57, 51), "type": 3},
    ]

    running_td = True
    while running_td:
        max_hp, current_hp = 100, 100
        max_energy, current_energy = 200, 120
        selected_tower_type = 1
        
        towers = []
        enemies = []
        bullets = []
        spawn_timer = 0
        score = 0
        game_active = True

        while game_active:
            clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # 按 ESC 返回地圖選單
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for slot in tower_slots:
                        if slot["rect"].collidepoint(mouse_pos):
                            selected_tower_type = slot["type"]

                    for sx, sy in spots:
                        if math.hypot(mouse_pos[0] - sx, mouse_pos[1] - sy) < 28:
                            already_has_tower = any(t.x == sx and t.y == sy for t in towers)
                            cost = 50 if selected_tower_type == 1 else (80 if selected_tower_type == 2 else 100)
                            if not already_has_tower and current_energy >= cost:
                                towers.append(Tower(sx, sy, tower_type=selected_tower_type, images=images))
                                current_energy -= cost

            spawn_timer += 1
            if spawn_timer >= 90:
                e_type = random.choice([1, 2, 3])
                enemies.append(Enemy(path, enemy_type=e_type, images=images))
                spawn_timer = 0

            for enemy in enemies[:]:
                enemy.update()
                if enemy.target_node_idx >= len(path):
                    current_hp -= 10
                    enemies.remove(enemy)
                elif enemy.hp <= 0:
                    current_energy = min(max_energy, current_energy + enemy.reward)
                    score += SCORE_PER_KILL.get(enemy.type, 50)
                    enemies.remove(enemy)

            for tower in towers:
                tower.update(enemies, bullets)

            for bullet in bullets[:]:
                bullet.update()
                if not bullet.alive:
                    bullets.remove(bullet)

            if current_energy < max_energy and pygame.time.get_ticks() % 30 == 0:
                current_energy += 1

            # 檢查血量歸零 (Game Over)
            if current_hp <= 0:
                game_active = False
                choice = game_over_screen(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, draw_custom_crosshair)
                if choice == "restart":
                    break # 重新執行遊戲迴圈（再玩一次）
                elif choice == "select":
                    return # 返回關卡選擇

            # --- 畫面繪製 ---
            if images.get("bg"):
                screen.blit(images["bg"], (0, 0))
            else:
                screen.fill((20, 20, 30))

            for sx, sy in spots:
                pygame.draw.circle(screen, CYAN, (sx, sy), 22, 2)

            for tower in towers:
                tower.draw(screen)
            for bullet in bullets:
                bullet.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

            if images.get("ui_panel"):
                panel_img = pygame.transform.scale(images["ui_panel"], (panel_w, panel_h))
                screen.blit(panel_img, (panel_x, panel_y))
            else:
                pygame.draw.rect(screen, (50, 40, 30), ui_panel_rect, border_radius=10)

            for slot in tower_slots:
                t_type = slot["type"]
                r = slot["rect"]
                if selected_tower_type == t_type:
                    pygame.draw.rect(screen, CYAN, r.inflate(6, 6), 3, border_radius=5)
                if images.get(f"tower{t_type}"):
                    icon = pygame.transform.scale(images[f"tower{t_type}"], (48, 48))
                    screen.blit(icon, icon.get_rect(center=r.center))

            stats_x, stats_y = 15, 15
            if images.get("ui_stats"):
                stats_img = pygame.transform.scale(images["ui_stats"], (85, 150))
                screen.blit(stats_img, (stats_x, stats_y))
            else:
                pygame.draw.rect(screen, (40, 40, 40), (stats_x, stats_y, 85, 150))

            bar_x = stats_x + 95
            bar_w = 170
            bar_h = 20

            hp_y = stats_y + 30
            hp_rate = max(0, current_hp / max_hp)
            pygame.draw.rect(screen, DARK_BAR, (bar_x, hp_y, bar_w, bar_h), border_radius=5)
            pygame.draw.rect(screen, RED, (bar_x, hp_y, bar_w * hp_rate, bar_h), border_radius=5)
            pygame.draw.rect(screen, WHITE, (bar_x, hp_y, bar_w, bar_h), 2, border_radius=5)

            energy_y = stats_y + 95
            energy_rate = max(0, current_energy / max_energy)
            pygame.draw.rect(screen, DARK_BAR, (bar_x, energy_y, bar_w, bar_h), border_radius=5)
            pygame.draw.rect(screen, BLUE, (bar_x, energy_y, bar_w * energy_rate, bar_h), border_radius=5)
            pygame.draw.rect(screen, WHITE, (bar_x, energy_y, bar_w, bar_h), 2, border_radius=5)

            # 分數顯示（上方置中）
            score_font = pygame.font.SysFont('microsoftjhenghei', 22)
            score_surf = score_font.render(f"SCORE: {min(score, WIN_SCORE)} / {WIN_SCORE}", True, WHITE)
            score_box = score_surf.get_rect(midtop=(SCREEN_WIDTH // 2, 10)).inflate(24, 10)
            pygame.draw.rect(screen, (20, 20, 30), score_box, border_radius=8)
            pygame.draw.rect(screen, CYAN, score_box, 2, border_radius=8)
            screen.blit(score_surf, score_surf.get_rect(center=score_box.center))

            # 繪製自訂準星
            draw_custom_crosshair(screen)
            pygame.display.update()

            # 達到過關分數 -> 過關畫面
            if score >= WIN_SCORE:
                choice = victory_screen(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, draw_custom_crosshair, score)
                if choice == "restart":
                    break  # 重新開始本關
                return  # 回到關卡選擇