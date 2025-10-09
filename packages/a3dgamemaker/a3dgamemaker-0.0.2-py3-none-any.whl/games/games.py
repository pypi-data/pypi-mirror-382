import pygame
import math
import random
import time
import os

# ====== إعداد العدو ======
class Enemy:
    def __init__(self, x, y, sprite=None, speed=1.0, health=2, radius=16):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.speed = speed
        self.health = health
        self.radius = radius
        self.alive = True

# ====== محرك RAYCASTING ======
class RAYCASTING:
    def __init__(self):
        pygame.init()
        # إعدادات افتراضية
        self.TILESIZE = 64
        self.ROWS = 10
        self.COLS = 10
        self.FOV = math.radians(60)
        self.RES = 120
        self.HALF_FOV = self.FOV / 2
        self.MAX_DEPTH = 800
        self.show_minimap = True

        # زومبي ورصاص
        self.enemies = []
        self.zombie_enabled = False
        self.zombie_sprite = None
        self.bullets = []

        # المسدس
        self.gun_enabled = False
        self.gun_sound = None
        self.hit_sound = None

        # لاعب
        self.player_x = 150
        self.player_y = 150
        self.player_angle = 0.0
        self.player_radius = 8
        self.player_movespeed = 2.5
        self.player_rotationspeed = math.radians(2)

        # حياة اللاعب وعدّاد الضرر
        self.player_max_health = 10
        self.player_health = self.player_max_health
        self.player_damage_cooldown_ms = 3000  # 0.5 ثانية كولداون بين إصابات
        self._last_damage_time = 0  # وقت آخر ضربة للاعب (ms)

        # إعدادات النافذة وخرائط
        self.update_window_size()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.map_data = []

        # خط للعرض
        self.font = pygame.font.SysFont(None, 28)

    # ======== دوال الإعداد ========
    def caption(self, text):
        pygame.display.set_caption(text)

    def set_tilesize(self, tilesize):
        self.TILESIZE = tilesize
        self.update_window_size()

    def set_rows(self, rows):
        self.ROWS = rows
        self.update_window_size()

    def set_cols(self, cols):
        self.COLS = cols
        self.update_window_size()

    def set_fov(self, fov_degrees):
        self.FOV = math.radians(fov_degrees)
        self.HALF_FOV = self.FOV / 2

    def set_resolution(self, res):
        self.RES = res
        self.NUM_RAYS = res

    def update_window_size(self):
        self.WINDOW_WIDTH = max(200, self.COLS * self.TILESIZE)
        self.WINDOW_HEIGHT = max(200, self.ROWS * self.TILESIZE)
        self.NUM_RAYS = self.RES

    def set_map(self, map_layout):
        self.map_data = map_layout
        self.ROWS = len(map_layout)
        self.COLS = len(map_layout[0]) if len(map_layout) > 0 else 0
        self.update_window_size()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

    # ======== أصوات المسدس (اختياري) ========
    def enable_gun(self, enable=True, sound_path=None, hit_sound_path=None):
        self.gun_enabled = enable
        if sound_path and os.path.exists(sound_path):
            try:
                pygame.mixer.init()
                self.gun_sound = pygame.mixer.Sound(sound_path)
            except Exception as e:
                print("خطأ بتحميل صوت المسدس:", e)
                self.gun_sound = None
        if hit_sound_path and os.path.exists(hit_sound_path):
            try:
                pygame.mixer.init()
                self.hit_sound = pygame.mixer.Sound(hit_sound_path)
            except Exception as e:
                print("خطأ بتحميل صوت الإصابة:", e)
                self.hit_sound = None

    # ======== إعداد اللاعب (يمكن للمستخدم استدعاؤها) ========
    def setup_player(self, x=150, y=150, movespeed=2.5, rotation_speed_deg=2, radius=8, max_health=10):
        self.player_x = x
        self.player_y = y
        self.player_movespeed = movespeed
        self.player_rotationspeed = math.radians(rotation_speed_deg)
        self.player_radius = radius
        self.player_max_health = max_health
        self.player_health = max_health

    # ======== اللاعب (تحريك/دوران) ========
    def update_player(self):
        keys = pygame.key.get_pressed()
        turndirection = 0
        walkdirection = 0
        if keys[pygame.K_d]: turndirection = 1
        if keys[pygame.K_a]: turndirection = -1
        if keys[pygame.K_w]: walkdirection = 1
        if keys[pygame.K_s]: walkdirection = -1

        self.player_angle += turndirection * self.player_rotationspeed
        movestep = walkdirection * self.player_movespeed
        new_x = self.player_x + math.cos(self.player_angle) * movestep
        new_y = self.player_y + math.sin(self.player_angle) * movestep
        if not self.has_wall_at(new_x, new_y):
            self.player_x = new_x
            self.player_y = new_y

    # ======== جدران / ريندر اشعة ========
    def normalizeangle(self, angle):
        angle %= 2 * math.pi
        if angle < 0: angle += 2 * math.pi
        return angle

    def cast_ray_distance(self, angle):
        ray_angle = self.normalizeangle(angle)
        depth = 0
        rx, ry = self.player_x, self.player_y
        while depth < self.MAX_DEPTH:
            rx += math.cos(ray_angle)
            ry += math.sin(ray_angle)
            depth += 1
            if self.has_wall_at(rx, ry):
                return math.hypot(rx - self.player_x, ry - self.player_y)
        return self.MAX_DEPTH

    def cast_all_rays(self):
        start_angle = self.player_angle - (self.FOV / 2)
        rays = []
        for r in range(self.NUM_RAYS):
            ray_angle = self.normalizeangle(start_angle + r * (self.FOV / self.NUM_RAYS))
            dist = self.cast_ray_distance(ray_angle)
            rays.append((ray_angle, dist))
        return rays

    def has_wall_at(self, x, y):
        if x < 0 or y < 0: return True
        map_x = int(x // self.TILESIZE)
        map_y = int(y // self.TILESIZE)
        if map_y >= len(self.map_data) or map_x >= len(self.map_data[0]): return True
        return self.map_data[map_y][map_x] == 1

    # ======== ميني ماب ========
    def draw_minimap(self):
        if not self.show_minimap:
            return
        tile = self.TILESIZE // 4
        for ry, row in enumerate(self.map_data):
            for cx, val in enumerate(row):
                color = (50,50,50) if val==1 else (200,200,200)
                pygame.draw.rect(self.screen, color, (cx*tile, ry*tile, tile, tile))
        # لاعب على الميني ماب
        pygame.draw.circle(self.screen, (0,255,0), (int(self.player_x/4), int(self.player_y/4)), 4)

    # ======== رسم 3D للجدران والـ sprites ========
    def draw_3d_view(self):
        w, h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        half_h = h // 2
        rays = self.cast_all_rays()
        slice_w = int(w / self.NUM_RAYS) + 1
        for i, (ray_angle, dist) in enumerate(rays):
            corrected = dist * math.cos(self.player_angle - ray_angle)
            wall_h = (self.TILESIZE * 400) / (corrected + 0.0001)
            wall_h = min(wall_h, h)
            shade = max(0, 255 - int(corrected * 0.7))
            color = (shade, shade, shade)
            x = int(i * (w / self.NUM_RAYS))
            y1 = int(half_h - wall_h / 2)
            pygame.draw.rect(self.screen, color, (x, y1, slice_w, int(wall_h)))

        # رسم الزومبي كـ sprites (إذا مرئي)
        if self.zombie_enabled and self.zombie_sprite:
            for enemy in self.enemies:
                if not enemy.alive: continue
                dx = enemy.x - self.player_x
                dy = enemy.y - self.player_y
                distance = math.hypot(dx, dy)
                angle_to_enemy = math.atan2(dy, dx)
                ang_diff = self.normalizeangle(angle_to_enemy - self.player_angle)
                if ang_diff > math.pi: ang_diff -= 2*math.pi
                if abs(ang_diff) < (self.FOV/2):
                    # فحص وجود جدار بين اللاعب والعدو
                    visible = True
                    steps = int(distance)
                    for step in range(0, steps, 6):
                        cx = self.player_x + math.cos(angle_to_enemy) * step
                        cy = self.player_y + math.sin(angle_to_enemy) * step
                        if self.has_wall_at(cx, cy):
                            visible = False
                            break
                    if not visible: continue
                    # حساب الحجم وموضع الرسم
                    corrected = distance * math.cos(ang_diff)
                    sprite_h = (self.TILESIZE * 400) / (corrected + 0.0001)
                    sprite_h = min(sprite_h, h)
                    rel = (ang_diff + (self.FOV/2)) / self.FOV
                    screen_x = int(rel * w)
                    screen_y = int(half_h - sprite_h / 2)
                    sprite_scaled = pygame.transform.scale(enemy.sprite, (int(sprite_h), int(sprite_h)))
                    self.screen.blit(sprite_scaled, (screen_x - sprite_h//2, screen_y))

    # ======== تحديث حركة الزومبي ========
    def update_zombies(self):
        if not self.zombie_enabled: return
        for enemy in self.enemies:
            if not enemy.alive: continue
            dx = self.player_x - enemy.x
            dy = self.player_y - enemy.y
            dist = math.hypot(dx, dy)
            if dist > 1:
                step = enemy.speed
                nx = enemy.x + (dx / dist) * step
                ny = enemy.y + (dy / dist) * step
                if not self.has_wall_at(nx, ny):
                    enemy.x = nx
                    enemy.y = ny

    # ======== الاصطدام بين اللاعب والزومبي (يقلل صحة اللاعب) ========
    def check_player_damage_by_enemies(self):
        now_ms = pygame.time.get_ticks()
        if now_ms - self._last_damage_time < self.player_damage_cooldown_ms:
            return  # داخل الكولداون، لا نخصم الآن
        for enemy in self.enemies:
            if not enemy.alive: continue
            # إذا تقاربوا كثيراً => لمس
            dist = math.hypot(enemy.x - self.player_x, enemy.y - self.player_y)
            touch_threshold = enemy.radius + self.player_radius
            if dist <= touch_threshold:
                # أصيب اللاعب
                self.player_health -= 1
                self._last_damage_time = now_ms
                # صوت الإصابة على اللاعب (اختياري)
                if self.hit_sound:
                    try:
                        self.hit_sound.play()
                    except Exception:
                        pass
                # تحقق الموت
                if self.player_health <= 0:
                    self.player_health = 0
                # نكسر بعد أول إصابة في هذه الحلقة لتفادي نقصان متعدد من عدة أعداء بنفس اللحظة
                break

    # ======== إطلاق النار (طلقة متحركة) ========
    def fire_bullet(self):
        if not self.gun_enabled: return
        bullet_speed = 12
        dx = math.cos(self.player_angle) * bullet_speed
        dy = math.sin(self.player_angle) * bullet_speed
        # نبدأ من أمام اللاعب قليلاً لكي لا تصطدم في نفسه
        start_x = self.player_x + math.cos(self.player_angle) * (self.player_radius + 4)
        start_y = self.player_y + math.sin(self.player_angle) * (self.player_radius + 4)
        self.bullets.append({'x': start_x, 'y': start_y, 'dx': dx, 'dy': dy})
        if self.gun_sound:
            try:
                self.gun_sound.play()
            except Exception:
                pass

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            if self.has_wall_at(bullet['x'], bullet['y']):
                try:
                    self.bullets.remove(bullet)
                except ValueError:
                    pass
                continue
            for enemy in self.enemies:
                if not enemy.alive: continue
                distance = math.hypot(enemy.x - bullet['x'], enemy.y - bullet['y'])
                if distance < 100:
                    enemy.health -= 1
                    if self.hit_sound:
                        try:
                            self.hit_sound.play()
                        except Exception:
                            pass
                    if enemy.health <= 0:
                        enemy.alive = False
                    try:
                        self.bullets.remove(bullet)
                    except ValueError:
                        pass
                    break

    # ======== توليد الزومبي ========
    def spawn_zombies(self, num=5, positions=None, sprite_path=None):
        if not self.zombie_enabled:
            print("⚠️ الزومبي معطل. فعلهم أولاً بـ enable_zombies(True, sprite_path).")
            return
        # تحميل الصورة إن أعطيت
        if sprite_path and os.path.exists(sprite_path):
            try:
                self.zombie_sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception as e:
                print("خطأ بتحميل صورة الزومبي:", e)
        # أنشئ الأعداء
        self.enemies = []
        for i in range(num):
            if positions and i < len(positions):
                x, y = positions[i]
            else:
                while True:
                    xr = random.randint(1, max(1, self.COLS-2))
                    yr = random.randint(1, max(1, self.ROWS-2))
                    x = xr * self.TILESIZE + self.TILESIZE / 2
                    y = yr * self.TILESIZE + self.TILESIZE / 2
                    if not self.has_wall_at(x, y):
                        break
            sprite = self.zombie_sprite if self.zombie_sprite else self._default_zombie_surface()
            self.enemies.append(Enemy(x, y, sprite))

    def _default_zombie_surface(self):
        surf = pygame.Surface((40,40), pygame.SRCALPHA)
        surf.fill((120,200,120))
        return surf

    # ======== تفعيل الزومبي ========
    def enable_zombies(self, enable=True, sprite_path=None):
        self.zombie_enabled = enable
        if sprite_path and os.path.exists(sprite_path):
            try:
                self.zombie_sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception as e:
                print("خطأ بتحميل صورة الزومبي:", e)

    # ======== رسم HUD (حياة اللاعب) ========
    def draw_hud(self):
        txt = f"HP: {self.player_health}/{self.player_max_health}"
        surf = self.font.render(txt, True, (255,255,255))
        self.screen.blit(surf, (10, 10))

        # لو مات اللاعب: رسالة
        if self.player_health <= 0:
            over_surf = self.font.render("YOU DIED", True, (255, 30, 30))
            # مربع وسط الشاشة
            rect = over_surf.get_rect(center=(self.WINDOW_WIDTH//2, self.WINDOW_HEIGHT//2))
            self.screen.blit(over_surf, rect)

    # ======== حلقة اللعبة ========
    def loop(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.show_minimap = not self.show_minimap
                    elif event.key == pygame.K_z:
                        self.spawn_zombies(5)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.gun_enabled:
                        self.fire_bullet()

            # تحديثات اللعبة
            self.update_player()
            self.update_zombies()
            # تحقق هل لامس الزومبي اللاعب -> نقص حياة (مع كولداون)
            self.check_player_damage_by_enemies()
            # طلقات
            self.update_bullets()

            # رسم
            self.screen.fill((100,100,100))
            self.draw_3d_view()
            self.draw_minimap()
            self.draw_hud()
            pygame.display.update()

            # تحقق من موت اللاعب: نوقف اللعبة (أو اعادة تشغيل حسب ما تريد)
            if self.player_health <= 0:
                pygame.time.delay(1000)
                running = False

            clock.tick(60)
        pygame.quit()

# ========== تجربة السكربت ==========
if __name__ == "__main__":
    r = RAYCASTING()
    # إعدادات بسيطة
    r.caption("3D Zombies - Player Touch Damage")
    r.set_tilesize(64)
    r.set_rows(10)
    r.set_cols(10)
    r.set_fov(60)
    r.set_resolution(120)

    r.set_map([
        [1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,0,0,1,1,1,0,1,0,1],
        [1,0,0,0,0,0,0,1,0,1],
        [1,0,1,0,0,0,0,1,0,1],
        [1,0,1,0,1,1,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1,0,0],
        [1,1,1,1,0,0,0,0,0,0],
        [1,1,1,1,0,0,0,0,0,0]
    ])

    # إعداد اللاعب (هنا تعطيه 10 حياة)
    r.setup_player(x=150, y=150, movespeed=2.5, rotation_speed_deg=2, radius=8, max_health=10)

    # تفعيل المسدس (اختياري) — ضع مسار الصوت إذا عندك WAV/OGG
    # r.enable_gun(True, sound_path="gunshot.wav", hit_sound_path="hit.wav")
    r.enable_gun(True,"gun.wav")  # افتراضي معطل

    # تفعيل الزومبي وصورتهم (أعط مسار صحيح إن عندك)
    r.enable_zombies(True, sprite_path="a.png")  # بالصورة الافتراضية
    r.spawn_zombies(6)  # يولّد 6 زومبي

    r.loop()
