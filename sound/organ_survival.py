# 檔案名稱：organ_survival.py
import pygame
import sys
import math
import random
import os

# 遊戲世界大小（支援 RPG 攝影機捲動）
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200

# 顏色常數
WHITE = (255, 255, 255)
GREEN = (50, 220, 100)
RED = (230, 50, 50)
BLUE = (30, 144, 255)
GOLD = (255, 215, 0)
PURPLE = (180, 50, 220)
CYAN = (0, 255, 255)
DARK_BG = (20, 25, 35)
DARK_BAR = (30, 30, 40)

def load_image_with_fallback(base_name, extensions=[".png", ".jpg", ".jpeg"]):
    """ 自動搜尋 img/ 資料夾下的圖片輔助函數 """
    for ext in extensions:
        full_path = os.path.join("img", base_name + ext)
        if os.path.exists(full_path):
            try:
                return pygame.image.load(full_path).convert_alpha()
            except Exception as e:
                print(f"無法載入圖片 {full_path}: {e}")
    return None


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 24  # 初始半徑
        self.speed = 3.5
        self.max_hp = 100
        self.hp = 100
        self.xp = 0
        self.max_xp = 100
        self.level = 1
        self.score = 0
        self.hit_cooldown = 0  # 受傷無敵幀防連續扣血

    def update(self):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:    dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.x += dx * self.speed
        self.y += dy * self.speed

        self.x = max(self.radius, min(WORLD_WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.y))

    def draw(self, screen, camera_x, camera_y, images):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # 三階段白血球圖片切換 (1-5, 6-10, 11-15)
        if self.level <= 5:
            img = images.get("player_1")
        elif self.level <= 10:
            img = images.get("player_2")
        else:
            img = images.get("player_3")

        if not img:
            img = images.get("player")

        if img:
            size = int(self.radius * 2)
            scaled_img = pygame.transform.smoothscale(img, (size, size))
            rect = scaled_img.get_rect(center=(screen_x, screen_y))
            screen.blit(scaled_img, rect)
        else:
            pygame.draw.circle(screen, WHITE, (screen_x, screen_y), int(self.radius))
            pygame.draw.circle(screen, BLUE, (screen_x, screen_y), int(self.radius), 3)


class Bullet:
    """ 病毒3（Boss）發射的彈藥 """
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 4.0
        
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.vx = (dx / dist) * self.speed
            self.vy = (dy / dist) * self.speed
        else:
            self.vx = 0
            self.vy = self.speed

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(screen, (255, 100, 0), (screen_x, screen_y), self.radius)
        pygame.draw.circle(screen, WHITE, (screen_x, screen_y), self.radius, 2)


class Laser:
    """ 病毒3 變異後發射的激光光束 """
    def __init__(self, x, y, target_x, target_y):
        self.start_x = x
        self.start_y = y
        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist > 0:
            nx, ny = dx / dist, dy / dist
        else:
            nx, ny = 1, 0
        # 光束延伸長度
        self.end_x = x + nx * 800
        self.end_y = y + ny * 800
        self.lifetime = 45  # 存在 45 幀 (約 0.75 秒)
        self.active = True

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False

    def check_collision(self, px, py, pradius):
        if not self.active:
            return False
        # 點到線段距離計算
        x1, y1 = self.start_x, self.start_y
        x2, y2 = self.end_x, self.end_y
        ab_x = x2 - x1
        ab_y = y2 - y1
        ap_x = px - x1
        ap_y = py - y1
        ab_len_sq = ab_x**2 + ab_y**2
        if ab_len_sq == 0:
            return math.hypot(px - x1, py - y1) <= pradius
        t = (ap_x * ab_x + ap_y * ab_y) / ab_len_sq
        t = max(0, min(1, t))
        closest_x = x1 + t * ab_x
        closest_y = y1 + t * ab_y
        return math.hypot(px - closest_x, py - closest_y) <= pradius

    def draw(self, screen, camera_x, camera_y):
        if not self.active:
            return
        sx1 = int(self.start_x - camera_x)
        sy1 = int(self.start_y - camera_y)
        sx2 = int(self.end_x - camera_x)
        sy2 = int(self.end_y - camera_y)
        # 繪製外發光激光與核心白光
        pygame.draw.line(screen, (255, 0, 150), (sx1, sy1), (sx2, sy2), 10)
        pygame.draw.line(screen, CYAN, (sx1, sy1), (sx2, sy2), 4)
        pygame.draw.line(screen, WHITE, (sx1, sy1), (sx2, sy2), 2)


class Virus1:
    """ 病毒1：靜止不動，吃到後加分並回血 """
    def __init__(self):
        self.x = random.randint(50, WORLD_WIDTH - 50)
        self.y = random.randint(50, WORLD_HEIGHT - 50)
        self.radius = 16

    def draw(self, screen, camera_x, camera_y, images):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        img = images.get("virus_1")
        if img:
            size = int(self.radius * 2)
            scaled_img = pygame.transform.smoothscale(img, (size, size))
            rect = scaled_img.get_rect(center=(screen_x, screen_y))
            screen.blit(scaled_img, rect)
        else:
            pygame.draw.circle(screen, GREEN, (screen_x, screen_y), self.radius)


class Virus2:
    """ 病毒2：隨機生成最多5隻，會追著玩家，碰到扣 1/4 血量 """
    def __init__(self, player_x, player_y, screen_w, screen_h):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(int(player_x - screen_w), int(player_x + screen_w))
            self.y = player_y - screen_h // 2 - random.randint(50, 100)
        elif side == 'bottom':
            self.x = random.randint(int(player_x - screen_w), int(player_x + screen_w))
            self.y = player_y + screen_h // 2 + random.randint(50, 100)
        elif side == 'left':
            self.x = player_x - screen_w // 2 - random.randint(50, 100)
            self.y = random.randint(int(player_y - screen_h), int(player_y + screen_h))
        else:
            self.x = player_x + screen_w // 2 + random.randint(50, 100)
            self.y = random.randint(int(player_y - screen_h), int(player_y + screen_h))

        self.x = max(20, min(WORLD_WIDTH - 20, self.x))
        self.y = max(20, min(WORLD_HEIGHT - 20, self.y))
        
        self.radius = 20
        self.speed = 2.0

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, screen, camera_x, camera_y, images):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        img = images.get("virus_2")
        if img:
            size = int(self.radius * 2)
            scaled_img = pygame.transform.smoothscale(img, (size, size))
            rect = scaled_img.get_rect(center=(screen_x, screen_y))
            screen.blit(scaled_img, rect)
        else:
            pygame.draw.circle(screen, RED, (screen_x, screen_y), self.radius)


class Virus3:
    """ 病毒3（Boss）：10等出現，14等變異後會發射激光光束與彈藥 """
    def __init__(self, player_x, player_y):
        self.x = player_x + 300
        self.y = player_y + 300
        self.x = max(50, min(WORLD_WIDTH - 50, self.x))
        self.y = max(50, min(WORLD_HEIGHT - 50, self.y))
        self.radius = 50
        self.speed = 1.2
        self.shoot_timer = 0
        self.laser_timer = 0

    def update(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 100:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

    def draw(self, screen, camera_x, camera_y, images):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        img = images.get("boss")
        if img:
            size = int(self.radius * 2)
            scaled_img = pygame.transform.smoothscale(img, (size, size))
            rect = scaled_img.get_rect(center=(screen_x, screen_y))
            screen.blit(scaled_img, rect)
        else:
            pygame.draw.circle(screen, PURPLE, (screen_x, screen_y), self.radius)
            pygame.draw.circle(screen, GOLD, (screen_x, screen_y), self.radius, 4)


def run_organ_survival(screen, clock, font_cache, draw_custom_crosshair):
    """ 供主程式呼叫的吞噬生存遊戲模組 """
    pygame.mouse.set_visible(False)
    screen_width, screen_height = screen.get_width(), screen.get_height()

    images = {}
    image_keys = [
        "player", "player_1", "player_2", "player_3", 
        "virus_1", "virus_2", "boss", "large_bg", 
        "ui_hp", "ui_exp"
    ]
    for key in image_keys:
        images[key] = load_image_with_fallback(key)

    if images.get("large_bg"):
        images["large_bg"] = pygame.transform.smoothscale(images["large_bg"], (WORLD_WIDTH, WORLD_HEIGHT))

    player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    
    virus_1_list = []
    virus_2_list = []
    bullets = []
    lasers = []
    boss = None

    spawn_timer = 0
    font = pygame.font.SysFont('microsoftjhenghei', 20)
    font_large = pygame.font.SysFont('microsoftjhenghei', 28, bold=True)

    # 變異警告標語計時器
    mutation_warned = False
    warning_timer = 0

    for _ in range(25):
        virus_1_list.append(Virus1())

    running = True
    while running:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # --- 遊戲邏輯更新 ---
        player.update()

        # 檢測 14 等變異觸發
        if player.level >= 14 and not mutation_warned:
            mutation_warned = True
            warning_timer = 180  # 警告標語顯示 3 秒 (180幀)
            print("⚠️ 警告：病毒 3 發生強烈變異，解鎖激光攻擊！")

        if warning_timer > 0:
            warning_timer -= 1

        # 1. 隨機生成病毒 1
        if len(virus_1_list) < 40 and random.random() < 0.3:
            virus_1_list.append(Virus1())

        # 2. 病毒 2 最多 5 隻
        spawn_timer += 1
        if spawn_timer >= 60 and len(virus_2_list) < 5:
            virus_2_list.append(Virus2(player.x, player.y, screen_width, screen_height))
            spawn_timer = 0

        # 3. 10 等生成 Boss
        if player.level >= 10 and boss is None:
            boss = Virus3(player.x, player.y)
            print("⚠️ 警告：病毒 3 (Boss) 已登場！")

        # Boss 行動與攻擊
        if boss:
            boss.update(player.x, player.y)
            boss.shoot_timer += 1
            if boss.shoot_timer >= 90:
                bullets.append(Bullet(boss.x, boss.y, player.x, player.y))
                boss.shoot_timer = 0

            # 14 等變異後，增加激光攻擊頻率
            if player.level >= 14:
                boss.laser_timer += 1
                if boss.laser_timer >= 150:  # 每 2.5 秒發射一次激光
                    lasers.append(Laser(boss.x, boss.y, player.x, player.y))
                    boss.laser_timer = 0

        # 更新彈藥判定
        for bullet in bullets[:]:
            bullet.update()
            if math.hypot(player.x - bullet.x, player.y - bullet.y) < player.radius + bullet.radius:
                bullets.remove(bullet)
                if player.hit_cooldown == 0:
                    damage = player.max_hp * 0.1
                    player.hp = max(0, player.hp - damage)
                    player.hit_cooldown = 30
                    if player.hp <= 0:
                        return

        # 更新激光判定
        for laser in lasers[:]:
            laser.update()
            if not laser.active:
                lasers.remove(laser)
            else:
                if laser.check_collision(player.x, player.y, player.radius):
                    if player.hit_cooldown == 0:
                        damage = player.max_hp * 0.2  # 激光扣 20% 血量
                        player.hp = max(0, player.hp - damage)
                        player.hit_cooldown = 30
                        print(f"遭到激光光束掃中！血量剩餘: {int(player.hp)}")
                        if player.hp <= 0:
                            return

        # 病毒 1 判定
        for v1 in virus_1_list[:]:
            if math.hypot(player.x - v1.x, player.y - v1.y) < player.radius + v1.radius:
                player.score += 50
                player.xp += 20
                if player.hp < player.max_hp:
                    player.hp = min(player.max_hp, player.hp + 10)
                
                virus_1_list.remove(v1)

                if player.level < 15 and player.xp >= player.max_xp:
                    player.xp = 0
                    player.level += 1
                    player.max_hp += 25
                    player.hp = player.max_hp
                    player.max_xp = int(player.max_xp * 1.2)

        # 病毒 2 判定
        for v2 in virus_2_list[:]:
            v2.update(player.x, player.y)
            if math.hypot(player.x - v2.x, player.y - v2.y) < player.radius + v2.radius:
                virus_2_list.remove(v2)
                if player.hit_cooldown == 0:
                    damage = player.max_hp * 0.25
                    player.hp = max(0, player.hp - damage)
                    player.hit_cooldown = 30
                    if player.hp <= 0:
                        return

        # 病毒 3 (Boss) 吞噬判定
        if boss:
            if math.hypot(player.x - boss.x, player.y - boss.y) < player.radius + boss.radius:
                if player.level >= 15:
                    player.score += 2000
                    print("🎉 恭喜達到 15 等並成功吞噬病毒 3！")
                    boss = None
                else:
                    if player.hit_cooldown == 0:
                        player.hp -= 20
                        player.hit_cooldown = 30
                        if player.hp <= 0:
                            return

        # 攝影機鎖定
        camera_x = player.x - screen_width // 2
        camera_y = player.y - screen_height // 2
        camera_x = max(0, min(WORLD_WIDTH - screen_width, camera_x))
        camera_y = max(0, min(WORLD_HEIGHT - screen_height, camera_y))

        # --- 畫面繪製 ---
        screen.fill(DARK_BG)

        if images.get("large_bg"):
            bg_img = images["large_bg"]
            screen.blit(bg_img, (-camera_x, -camera_y))
        else:
            grid_size = 100
            start_x = int(camera_x // grid_size) * grid_size
            start_y = int(camera_y // grid_size) * grid_size
            for x in range(start_x, start_x + screen_width + grid_size, grid_size):
                pygame.draw.line(screen, (30, 40, 55), (x - camera_x, 0), (x - camera_x, screen_height), 1)
            for y in range(start_y, start_y + screen_height + grid_size, grid_size):
                pygame.draw.line(screen, (30, 40, 55), (0, y - camera_y), (screen_width, y - camera_y), 1)

        for v1 in virus_1_list:
            v1.draw(screen, camera_x, camera_y, images)

        for v2 in virus_2_list:
            v2.draw(screen, camera_x, camera_y, images)

        for bullet in bullets:
            bullet.draw(screen, camera_x, camera_y)

        for laser in lasers:
            laser.draw(screen, camera_x, camera_y)

        if boss:
            boss.draw(screen, camera_x, camera_y, images)

        player.draw(screen, camera_x, camera_y, images)

        # ==================== 繪製 UI 與動態血條 ====================
        
        # 1. 左上角：血量 UI
        hp_panel_x, hp_panel_y = 15, 15
        if images.get("ui_hp"):
            hp_panel_img = pygame.transform.smoothscale(images["ui_hp"], (260, 95))
            screen.blit(hp_panel_img, (hp_panel_x, hp_panel_y))
        else:
            pygame.draw.rect(screen, (40, 40, 50), (hp_panel_x, hp_panel_y, 260, 95), border_radius=8)

        bar_x = hp_panel_x + 55
        bar_y = hp_panel_y + 38
        bar_w = 185
        bar_h = 20
        hp_rate = max(0, player.hp / player.max_hp)
        
        pygame.draw.rect(screen, DARK_BAR, (bar_x, bar_y, bar_w, bar_h), border_radius=4)
        pygame.draw.rect(screen, RED, (bar_x, bar_y, int(bar_w * hp_rate), bar_h), border_radius=4)
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)
        
        hp_txt = font.render(f"HP: {int(player.hp)} / {player.max_hp}", True, WHITE)
        screen.blit(hp_txt, (bar_x + 10, bar_y - 2))

        # 2. 右上角：等級與經驗值 UI
        exp_panel_w, exp_panel_h = 220, 110
        exp_panel_x, exp_panel_y = screen_width - exp_panel_w - 15, 15
        
        if images.get("ui_exp"):
            exp_panel_img = pygame.transform.smoothscale(images["ui_exp"], (exp_panel_w, exp_panel_h))
            screen.blit(exp_panel_img, (exp_panel_x, exp_panel_y))
        else:
            pygame.draw.rect(screen, (40, 40, 50), (exp_panel_x, exp_panel_y, exp_panel_w, exp_panel_h), border_radius=8)

        lv_str = f"MAX (15)" if player.level >= 15 else f"Lv. {player.level}"
        lv_txt = font.render(lv_str, True, GOLD)
        score_txt = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(lv_txt, (exp_panel_x + 60, exp_panel_y + 15))
        screen.blit(score_txt, (exp_panel_x + 60, exp_panel_y + 42))

        exp_bar_x = exp_panel_x + 20
        exp_bar_y = exp_panel_y + 75
        exp_bar_w = 180
        exp_bar_h = 14
        exp_rate = 1.0 if player.level >= 15 else max(0, player.xp / player.max_xp)

        pygame.draw.rect(screen, DARK_BAR, (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h), border_radius=4)
        pygame.draw.rect(screen, GREEN, (exp_bar_x, exp_bar_y, int(exp_bar_w * exp_rate), exp_bar_h), border_radius=4)
        pygame.draw.rect(screen, WHITE, (exp_bar_x, exp_bar_y, exp_bar_w, exp_bar_h), 2, border_radius=4)

        # 3. 14等變異警告標語顯示（置於畫面正上方閃爍）
        if warning_timer > 0:
            warn_surf = font_large.render("⚠️ 警告：病毒 3 發生強烈變異，解鎖激光攻擊！", True, (255, 50, 50))
            warn_rect = warn_surf.get_rect(center=(screen_width // 2, 70))
            # 加上黑色外框讓字更明顯
            outline_surf = font_large.render("⚠️ 警告：病毒 3 發生強烈變異，解鎖激光攻擊！", True, (0, 0, 0))
            screen.blit(outline_surf, (warn_rect.x + 2, warn_rect.y + 2))
            screen.blit(warn_surf, warn_rect)

        # =========================================================================

        draw_custom_crosshair(screen)
        pygame.display.update()


# 獨立測試模式
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("白血球吞噬生存戰 - 14等變異與激光測試")
    clock = pygame.time.Clock()
    
    def dummy_crosshair(s):
        pass
        
    run_organ_survival(screen, clock, None, dummy_crosshair)
    pygame.quit()
    sys.exit()