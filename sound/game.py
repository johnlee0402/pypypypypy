import pygame
import random
import os

# --- 基礎設定 ---
FPS = 60
WIDTH = 500
HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 150, 255)

# 遊戲初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("人體保衛戰：白血球的逆襲")
clock = pygame.time.Clock()

# --- 載入資源 ---
background_img = pygame.image.load(os.path.join("img", "background.png")).convert()
player_img = pygame.image.load(os.path.join("img", "player.png")).convert() # 白血球/奈米飛船
bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert() # 抗體子彈

coin_img = pygame.image.load(os.path.join("img", "coin.png")).convert_alpha() # 維他命/特效藥
coin_img.set_colorkey(WHITE) 
coin_mini_img = pygame.transform.scale(coin_img, (30, 30))

heart_img = pygame.image.load(os.path.join("img", "heart.png")).convert_alpha()
heart_img.set_colorkey(WHITE)
heart_mini_img = pygame.transform.scale(heart_img, (25, 25))

rock_imgs = [] # 病毒與細菌
for i in range(7):
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())

expl_anim = {'lg': [], 'sm': [], 'player': []}
for i in range(9):
    expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
    p_expl = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
    p_expl.set_colorkey(BLACK)
    expl_anim['player'].append(p_expl)

power_imgs = {
    'shield': pygame.image.load(os.path.join("img", "shield.png")).convert(), # 醫療護盾
    'gun': pygame.image.load(os.path.join("img", "gun.png")).convert() # 疫苗強化
}

# --- 音效 ---
shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
expl_sounds = [
    pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.4)

font_name = os.path.join("font.ttf")

# --- 輔助函式 ---
def draw_text(surf, text, size, x, y, color=WHITE):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def new_rock(level=1):
    r = Rock(level)
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y, max_hp=100, color=GREEN, length=100):
    if hp < 0: hp = 0
    fill = (hp / max_hp) * length
    outline_rect = pygame.Rect(x, y, length, 10)
    fill_rect = pygame.Rect(x, y, fill, 10)
    pygame.draw.rect(surf, color, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x - (30 * i) 
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init():
    screen.blit(background_img, (0,0))
    draw_text(screen, '人體保衛戰', 64, WIDTH/2, HEIGHT/4 - 30, BLUE)
    draw_text(screen, '化身白血球，消滅入侵病毒！', 22, WIDTH/2, HEIGHT/2 - 20)
    draw_text(screen, '收集 3 個維他命可按 Z 釋放【免疫風暴】', 18, WIDTH/2, HEIGHT/2 + 30, YELLOW)
    draw_text(screen, '按任意鍵進入人體...', 18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            if event.type == pygame.KEYDOWN:
                waiting = False
                return False

# --- 類別定義 ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0
        self.power_duration = 5000

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > self.power_duration:
            self.gun = 1
        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_d]: self.rect.x += self.speedx
        if key_pressed[pygame.K_a]: self.rect.x -= self.speedx
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        if not self.hidden:
            if self.gun == 1:
                b = Bullet(self.rect.centerx, self.rect.top, -10)
                all_sprites.add(b); bullets.add(b)
            else:
                b1 = Bullet(self.rect.left, self.rect.centery, -10)
                b2 = Bullet(self.rect.right, self.rect.centery, -10)
                all_sprites.add(b1, b2); bullets.add(b1, b2)
            shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

    def gunup(self):
        self.gun = 2
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image_ori.set_colorkey(BLACK)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-180, -100)
        
        bonus_speed = min(4, level - 1)
        self.speedy = random.randrange(2, 5) + bonus_speed
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree = (self.total_degree + self.rot_degree) % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)

class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (120, 90))
        self.image = pygame.transform.flip(self.image, False, True)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 50
        self.rect.centerx = WIDTH / 2
        self.rect.y = -100
        
        self.level = level
        self.speedx = 4 + min(level, 4) 
        self.max_health = 1000 + (level - 1) * 500
        self.health = self.max_health
        self.shoot_delay = max(200, 500 - (level - 1) * 70)
        self.last_shoot = pygame.time.get_ticks()

    def update(self):
        if self.rect.y < 50: self.rect.y += 2
        else:
            self.rect.x += self.speedx
            if self.rect.right > WIDTH or self.rect.left < 0: self.speedx *= -1
        now = pygame.time.get_ticks()
        if now - self.last_shoot > self.shoot_delay:
            self.last_shoot = now
            self.shoot()

    def shoot(self):
        b_speed = 13 + self.level
        
        # --- 魔王狂暴模式：血量低於 50% 時發射三向散彈 ---
        if self.health <= self.max_health / 2:
            b1 = Bullet(self.rect.centerx, self.rect.bottom, b_speed, speedx=0)
            b2 = Bullet(self.rect.centerx, self.rect.bottom, b_speed, speedx=-3) # 往左斜
            b3 = Bullet(self.rect.centerx, self.rect.bottom, b_speed, speedx=3)  # 往右斜
            all_sprites.add(b1, b2, b3); enemy_bullets.add(b1, b2, b3) 
        else:
            b = Bullet(self.rect.centerx, self.rect.bottom, b_speed, speedx=0)
            all_sprites.add(b); enemy_bullets.add(b) 

class Bullet(pygame.sprite.Sprite):
    # 新增 speedx 讓子彈可以斜向飛行
    def __init__(self, x, y, speedy, speedx=0):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = speedy
        self.speedx = speedx

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH: 
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
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
            if self.frame == len(expl_anim[self.size]): self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT: self.kill()

# --- 主迴圈 ---
pygame.mixer.music.play(-1)
show_init = True
running = True
paused = False
coin = 0 
score = 0 
game_level = 1 

while running:
    if show_init:
        close = draw_init()
        if close: break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        enemy_bullets = pygame.sprite.Group() 
        powers = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8): new_rock(game_level)
        last_coin_score = 0
        game_state = 0 
        boss = None
        paused = False
        target_score = 5000 
        game_level = 1 

    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
                if paused: pygame.mixer.music.pause()
                else: pygame.mixer.music.unpause()
            
            if not paused:
                if event.key == pygame.K_SPACE: player.shoot()
                
                # --- 大招：免疫風暴 (消耗3金幣) ---
                if event.key == pygame.K_z and coin >= 3:
                    coin -= 3
                    die_sound.play() # 播放震撼音效
                    
                    # 清除畫面上所有的小病毒
                    for r in rocks:
                        all_sprites.add(Explosion(r.rect.center, 'lg'))
                        score += r.radius
                        r.kill()
                        new_rock(game_level) # 補回新的病毒在畫面上方
                    
                    # 如果魔王在場，給予大爆血傷害
                    if game_state == 1 and boss:
                        boss.health -= 500
                        all_sprites.add(Explosion(boss.rect.center, 'lg'))
                        all_sprites.add(Explosion((boss.rect.centerx+20, boss.rect.centery), 'lg'))
                        all_sprites.add(Explosion((boss.rect.centerx-20, boss.rect.centery), 'lg'))

    if not paused:
        all_sprites.update()

        if score - last_coin_score >= 2000:
            coin += 1
            last_coin_score += 2000

        if score >= target_score and game_state == 0:
            game_state = 1
            for r in rocks: r.kill()
            boss = Boss(game_level)
            all_sprites.add(boss)

        if game_state == 0 and len(rocks) < 8: new_rock(game_level)

        hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
        for hit in hits:
            random.choice(expl_sounds).play()
            score += hit.radius
            all_sprites.add(Explosion(hit.rect.center, 'lg'))
            if random.random() > 0.9:
                p = Power(hit.rect.center); all_sprites.add(p); powers.add(p)

        # 魔王死亡判定 (移出子彈碰撞迴圈外，這樣大招炸死魔王也能正常結算)
        if game_state == 1 and boss:
            boss_hits = pygame.sprite.spritecollide(boss, bullets, True)
            for hit in boss_hits:
                boss.health -= 25
                all_sprites.add(Explosion(hit.rect.center, 'sm'))
            
            # 若魔王血量歸零 (被子彈打死或被大招炸死)
            if boss.health <= 0:
                all_sprites.add(Explosion(boss.rect.center, 'lg'))
                score += 800 
                coin += 1 
                boss.kill()
                boss = None
                
                game_level += 1 
                draw_text(screen, f"SUPER VIRUS ELIMINATED! LV {game_level}", 40, WIDTH/2, HEIGHT/2, GREEN)
                pygame.display.update()
                pygame.time.delay(1500)
                
                target_score = score + 5000 
                game_state = 0 
                for eb in enemy_bullets: eb.kill() 
                for i in range(8): new_rock(game_level) 

        hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
        for hit in hits:
            player.health -= hit.radius * 2
            all_sprites.add(Explosion(hit.rect.center, 'sm'))
            if player.health <= 0:
                all_sprites.add(Explosion(player.rect.center, 'player'))
                die_sound.play(); player.lives -= 1; player.health = 100; player.hide()
            if game_state == 0: new_rock(game_level)

        enemy_hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_circle)
        for hit in enemy_hits:
            player.health -= 30 
            all_sprites.add(Explosion(hit.rect.center, 'sm'))
            if player.health <= 0:
                all_sprites.add(Explosion(player.rect.center, 'player'))
                die_sound.play(); player.lives -= 1; player.health = 100; player.hide()

        hits = pygame.sprite.spritecollide(player, powers, True)
        for hit in hits:
            if hit.type == 'shield': 
                player.health = min(100, player.health + 20); shield_sound.play()
            elif hit.type == 'gun': 
                player.gunup(); gun_sound.play()

        if player.lives <= 0:
            screen.fill(BLACK)
            draw_text(screen, "SYSTEM FAILURE (GAME OVER)", 48, WIDTH/2, HEIGHT/3, RED)
            draw_text(screen, f"淨化病毒數: {score}", 32, WIDTH/2, HEIGHT/2)
            draw_text(screen, f"存活至病毒變異: LEVEL {game_level}", 22, WIDTH/2, HEIGHT/2 + 50, YELLOW)
            draw_text(screen, "按任意鍵重啟免疫系統", 22, WIDTH/2, HEIGHT*2/3)
            pygame.display.update()
            waiting = True
            while waiting:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); running = False; waiting = False
                    if event.type == pygame.KEYDOWN: waiting = False
            score = 0 
            show_init = True

    # --- 繪製畫面 ---
    screen.fill(BLACK)
    screen.blit(background_img, (0,0))
    all_sprites.draw(screen)
    draw_text(screen, f"淨化指數: {score}", 18, WIDTH/2, 10)
    draw_text(screen, f"變異 LV: {game_level}", 18, 60, 10, YELLOW) 
    
    screen.blit(coin_mini_img, (10, 40))
    draw_text(screen, f"x {coin}", 22, 65, 42)
    
    # --- 大招提示 UI ---
    if coin >= 3:
        draw_text(screen, "【 Z 】釋放免疫風暴！", 20, WIDTH/2, 60, YELLOW)
        
    draw_health(screen, player.health, 5, 15)
    draw_lives(screen, player.lives, heart_mini_img, WIDTH - 40, 15)

    if game_state == 1 and boss:
        draw_health(screen, boss.health, WIDTH/2 - 100, 35, boss.max_health, RED, 200)

    if paused:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        draw_text(screen, "PAUSED", 64, WIDTH/2, HEIGHT/2 - 40, YELLOW)
        draw_text(screen, "按下 P 鍵繼續遊戲", 22, WIDTH/2, HEIGHT/2 + 30, WHITE)
        
    pygame.display.update()

pygame.quit()