# raylib_demo.py
import pygame, math, random, os, time, sys

# =================== Enemy class ===================
class Enemy:
    def __init__(self, x, y, sprite=None, dead_sprite=None, speed=0.9, health=2, radius=16):
        self.x = float(x)
        self.y = float(y)
        self.sprite = sprite
        self.dead_sprite = dead_sprite
        self.speed = speed
        self.health = health
        self.radius = radius
        self.alive = True
        self.last_hit_time = 0.0  # ضرب اللاعب كولداون
    def __repr__(self):
        return f"<Enemy {self.x:.1f},{self.y:.1f} hp={self.health} alive={self.alive}>"

# =================== RAYCASTING engine (library) ===================
class RAYCASTING:
    def __init__(self):
        pygame.init()
        pygame.mixer.init() if not pygame.mixer.get_init() else None
        pygame.mouse.set_visible(False)

        # world / rendering
        self.TILESIZE = 64
        self.FOV = math.radians(60)
        self.RES = 200  # عدد الأشعة للـ3D
        self.HALF_FOV = self.FOV / 2
        self.MAX_DEPTH = 1000
        self.show_minimap = True
        self.minimap_scale = 0.18  # ثابت لحجم الميني ماب

        # runtime collections
        self.map_data = []
        self.enemies = []
        self.bullets = []

        # flags
        self.zombie_enabled_flag = False

        # gun + reload
        self.gun_enabled = False
        self.gun_idle = None
        self.gun_fire = None
        self.gun_sound = None
        self.current_gun_sprite = None
        self.fire_time = 0.0
        self.fire_duration = 0.12

        self.reload_sprite = None
        self.reload_sound = None
        self.reloading = False
        self.reload_start_time = 0.0
        self.reload_duration = 1.2
        self.max_ammo = 10
        self.ammo = self.max_ammo

        # player
        self.player_x = 150.0
        self.player_y = 150.0
        self.player_angle = 0.0
        self.player_radius = 8
        self.player_movespeed = 2.5
        self.player_rotationspeed = math.radians(3)
        self.player_max_health = 10
        self.player_health = float(self.player_max_health)
        self.on_stairs = False

        # screen
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 650
        self.NUM_RAYS = self.RES

        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.font = pygame.font.SysFont(None, 26)

    # ---------- configuration helpers ----------
    def caption(self, text): pygame.display.set_caption(text)
    def update_window_size(self, w=1000, h=650):
        self.WINDOW_WIDTH = w; self.WINDOW_HEIGHT = h
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
    def set_tilesize(self, t): self.TILESIZE = t
    def set_fov(self, deg): self.FOV = math.radians(deg); self.HALF_FOV = self.FOV/2
    def set_resolution(self, res): self.RES = res; self.NUM_RAYS = res

    def set_map(self, layout):
        self.map_data = layout
        # reposition player safely if outside
        rows = len(layout)
        cols = len(layout[0]) if rows else 0
        # ensure player's tile isn't a wall
        mx,my = int(self.player_x//self.TILESIZE), int(self.player_y//self.TILESIZE)
        if my>=rows or mx>=cols or layout[my][mx] != 0:
            # find first empty tile
            for y,row in enumerate(layout):
                for x,val in enumerate(row):
                    if val == 0:
                        self.player_x = x*self.TILESIZE + self.TILESIZE/2
                        self.player_y = y*self.TILESIZE + self.TILESIZE/2
                        return

    # ---------- gun + reload ----------
    def enable_gun(self, enable=True, idle_path=None, fire_path=None, sound_path=None, fire_duration=0.12):
        self.gun_enabled = bool(enable)
        self.fire_duration = float(fire_duration)
        self.gun_idle = self._safe_load_image(idle_path)
        self.gun_fire = self._safe_load_image(fire_path)
        self.gun_sound = self._safe_load_sound(sound_path)
        self.current_gun_sprite = self.gun_idle or self.gun_fire

    def enable_reload(self, reload_sprite_path=None, reload_sound_path=None, reload_duration=None, max_ammo=10):
        if max_ammo is not None:
            self.max_ammo = int(max_ammo)
            self.ammo = min(self.ammo, self.max_ammo)
        self.reload_sprite = self._safe_load_image(reload_sprite_path)
        rs = self._safe_load_sound(reload_sound_path)
        self.reload_sound = rs
        if rs and reload_duration is None:
            # use sound length
            try:
                self.reload_duration = max(self.reload_duration, rs.get_length())
            except:
                pass
        elif reload_duration is not None:
            self.reload_duration = float(reload_duration)

    def start_reload(self):
        if self.reloading: return
        if self.ammo >= self.max_ammo: return
        self.reloading = True
        self.reload_start_time = time.time()
        if self.reload_sound:
            try: self.reload_sound.play()
            except: pass
        if self.reload_sprite:
            self.current_gun_sprite = self.reload_sprite

    # ---------- zombies ----------
    def zombie_enabled(self, enable=True, spawn_on_enable=False, spawn_count=5, sprite_path=None, dead_sprite_path=None):
        self.zombie_enabled_flag = bool(enable)
        if enable and spawn_on_enable:
            self.spawn_zombies(count=spawn_count, sprite_path=sprite_path, dead_sprite_path=dead_sprite_path)

    def spawn_zombies(self, count=5, sprite_path=None, dead_sprite_path=None):
        sprite = self._safe_load_image(sprite_path)
        dead_sprite = self._safe_load_image(dead_sprite_path)
        empty_tiles = [(x,y) for y,row in enumerate(self.map_data) for x,val in enumerate(row) if val==0]
        random.shuffle(empty_tiles)
        for i in range(min(count, len(empty_tiles))):
            x,y = empty_tiles[i]
            zx = x*self.TILESIZE + self.TILESIZE/2
            zy = y*self.TILESIZE + self.TILESIZE/2
            self.enemies.append(Enemy(zx, zy, sprite=sprite, dead_sprite=dead_sprite))

    # ---------- util loaders ----------
    def _safe_load_image(self, path):
        if not path: return None
        try:
            if os.path.exists(path):
                return pygame.image.load(path).convert_alpha()
        except Exception as e:
            print("image load error:", e)
        return None
    def _safe_load_sound(self, path):
        if not path: return None
        try:
            if os.path.exists(path):
                if not pygame.mixer.get_init():
                    pygame.mixer.init()
                return pygame.mixer.Sound(path)
        except Exception as e:
            print("sound load error:", e)
        return None

    # ---------- player movement / map logic ----------
    def normalizeangle(self,a): a%=2*math.pi; return a+2*math.pi if a<0 else a
    def has_wall_at(self, x, y):
        if x < 0 or y < 0: return True
        if not self.map_data: return True
        mx = int(x // self.TILESIZE); my = int(y // self.TILESIZE)
        if my < 0 or my >= len(self.map_data) or mx < 0 or mx >= len(self.map_data[0]):
            return True
        tile = self.map_data[my][mx]
        # treat 1 as wall, 3 (high) also blocks movement; stairs (2) and water (4) are walkable depending logic
        return tile == 1 or tile == 3

    def update_player(self):
        keys = pygame.key.get_pressed()
        turn = walk = 0
        if keys[pygame.K_d]: turn = 1
        if keys[pygame.K_a]: turn = -1
        if keys[pygame.K_w]: walk = 1
        if keys[pygame.K_s]: walk = -1
        if keys[pygame.K_r]:
            # allow R to trigger reload (holds if pressed)
            self.start_reload()

        self.player_angle += turn * self.player_rotationspeed
        step = walk * self.player_movespeed
        nx = self.player_x + math.cos(self.player_angle) * step
        ny = self.player_y + math.sin(self.player_angle) * step

        # tile type checks
        if self.map_data:
            mx,my = int(nx//self.TILESIZE), int(ny//self.TILESIZE)
            if 0 <= my < len(self.map_data) and 0 <= mx < len(self.map_data[0]):
                tile = self.map_data[my][mx]
                # tile rules:
                # 0 = floor -> walk
                # 1 = wall -> blocked
                # 2 = stairs -> allow, set on_stairs
                # 3 = high -> block movement (can't enter)
                # 4 = water -> treat as floor but slower? for now allow
                if tile in (0,2,4) or (tile==3 and self.on_stairs):
                    self.player_x, self.player_y = nx, ny
                # else blocked by wall/high
                self.on_stairs = (tile==2)
            else:
                # out of map bounds block
                pass
        else:
            # no map: free roam
            self.player_x, self.player_y = nx, ny

    # ---------- raycasting (distance per ray) ----------
    def cast_ray_distance(self, ang):
        ang = self.normalizeangle(ang)
        rx, ry = self.player_x, self.player_y
        step = 0.0
        for d in range(int(self.MAX_DEPTH)):
            step += 1.0
            rx += math.cos(ang)
            ry += math.sin(ang)
            if self.has_wall_at(rx, ry):
                return math.hypot(rx - self.player_x, ry - self.player_y)
        return float(self.MAX_DEPTH)

    def cast_all_rays(self):
        rays = []
        start = self.player_angle - (self.FOV / 2)
        for r in range(self.NUM_RAYS):
            ang = self.normalizeangle(start + r * (self.FOV / self.NUM_RAYS))
            dist = self.cast_ray_distance(ang)
            rays.append((ang, dist))
        return rays

    # ---------- enemies behavior ----------
    def has_line_of_sight(self, x1,y1,x2,y2):
        dx = x2 - x1; dy = y2 - y1
        dist = math.hypot(dx,dy)
        if dist == 0: return True
        steps = int(dist)
        for i in range(0, steps, 2):  # step by 2 for performance
            xi = x1 + dx * i / steps
            yi = y1 + dy * i / steps
            if self.has_wall_at(xi, yi):
                return False
        return True

    # ===== تحديث الأعداء =====
    # ===== تحديث الأعداء مع فحص الجدار =====
    def update_enemies(self):
     if not self.zombie_enabled_flag:
        return
     for e in self.enemies:
        if e.health <= 0:
            e.alive = False
            if e.dead_sprite:
                e.sprite = e.dead_sprite
            continue

        # حركة الزومبي فقط إذا يوجد خط رؤية
        if self.has_line_of_sight(e.x, e.y, self.player_x, self.player_y):
            dx = self.player_x - e.x
            dy = self.player_y - e.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
            new_x = e.x + dx * e.speed
            new_y = e.y + dy * e.speed
            if not self.has_wall_at(new_x, e.y):
                e.x = new_x
            if not self.has_wall_at(e.x, new_y):
                e.y = new_y

            # هجوم اللاعب
            if dist < self.player_radius + e.radius:
                now = time.time()
                if now - e.last_hit_time >= 3:
                    self.player_health = max(0, self.player_health - 1)
                    e.last_hit_time = now


# ===== رسم الأعداء مع صورة الميت =====
    def draw_enemies(self):
     if not self.zombie_enabled_flag:
        return
     w, h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
     half_h = h // 2
     for e in self.enemies:
        # يظهر الزومبي فقط إذا يوجد خط رؤية
        if not self.has_line_of_sight(self.player_x, self.player_y, e.x, e.y):
            continue
        sprite = e.sprite or e.dead_sprite
        if not sprite:
            continue
        dx = e.x - self.player_x
        dy = e.y - self.player_y
        angle_to_enemy = math.atan2(dy, dx) - self.player_angle
        angle_to_enemy = (angle_to_enemy + math.pi) % (2 * math.pi) - math.pi
        if -self.HALF_FOV < angle_to_enemy < self.HALF_FOV:
            dist = math.hypot(dx, dy)
            corrected_dist = dist * math.cos(angle_to_enemy)
            size = min((self.TILESIZE * 400) / (corrected_dist + 0.0001), h)
            sprite_scaled = pygame.transform.scale(sprite, (int(size), int(size)))
            screen_x = int((0.5 + angle_to_enemy / self.FOV) * w - size / 2)
            screen_y = int(half_h - size / 2)
            self.screen.blit(sprite_scaled, (screen_x, screen_y))


    # ---------- bullets ----------
    def fire_bullet(self):
        if not self.gun_enabled: return
        if self.reloading: return
        if self.ammo <= 0:
            self.start_reload()
            return
        self.ammo -= 1
        # play sound
        if self.gun_sound:
            try: self.gun_sound.play()
            except: pass
        if self.gun_fire:
            self.current_gun_sprite = self.gun_fire
            self.fire_time = time.time()
        # create bullet
        speed = 14.0
        dx = math.cos(self.player_angle) * speed
        dy = math.sin(self.player_angle) * speed
        sx = self.player_x + math.cos(self.player_angle)*(self.player_radius+6)
        sy = self.player_y + math.sin(self.player_angle)*(self.player_radius+6)
        self.bullets.append({'x':sx, 'y':sy, 'dx':dx, 'dy':dy})

    def update_bullets(self):
        for b in self.bullets[:]:
            b['x'] += b['dx']
            b['y'] += b['dy']
            # wall collision
            if self.has_wall_at(b['x'], b['y']):
                try: self.bullets.remove(b)
                except: pass
                continue
            # enemy collision
            for e in self.enemies:
                if not e.alive: continue
                if math.hypot(e.x - b['x'], e.y - b['y']) < max(12, e.radius):
                    e.health -= 1
                    if e.health <= 0:
                        e.alive = False
                    try: self.bullets.remove(b)
                    except: pass
                    break

    # ---------- gun animation + reload finish ----------
    def update_gun_animation(self):
        if self.current_gun_sprite == self.gun_fire:
            if (time.time() - self.fire_time) >= self.fire_duration:
                if not self.reloading:
                    self.current_gun_sprite = self.gun_idle or self.gun_fire
        if self.reloading:
            elapsed = time.time() - self.reload_start_time
            if elapsed >= self.reload_duration:
                self.ammo = self.max_ammo
                self.reloading = False
                self.current_gun_sprite = self.gun_idle or self.gun_fire

    # ---------- draw 3D and HUD ----------
    def draw_3d_view(self):
        w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        half_h = h // 2
        rays = self.cast_all_rays()
        slice_w = max(1, int(w / self.NUM_RAYS) + 1)
        for i, (ang, dist) in enumerate(rays):
            corrected = dist * math.cos(self.player_angle - ang)
            wall_h = min((self.TILESIZE * 350) / (corrected + 0.0001), h)
            shade = max(20, 255 - int(corrected * 0.6))
            pygame.draw.rect(self.screen, (shade, shade, shade),
                             (int(i * (w / self.NUM_RAYS)), int(half_h - wall_h / 2), slice_w, int(wall_h)))

    def draw_minimap(self):
        if not self.show_minimap or not self.map_data: return
        # fixed minimap size (scale by minimap_scale)
        rows = len(self.map_data); cols = len(self.map_data[0])
        t = int(self.TILESIZE * self.minimap_scale)
        # left-top corner
        mx0 = 10; my0 = 10
        for y,row in enumerate(self.map_data):
            for x,val in enumerate(row):
                if val == 1: color = (60,60,60)
                else: color = (200,200,200)
                pygame.draw.rect(self.screen, color, (mx0 + x*t, my0 + y*t, t-1, t-1))
        # draw player on minimap
        px = mx0 + int(self.player_x * self.minimap_scale)
        py = my0 + int(self.player_y * self.minimap_scale)
        pygame.draw.circle(self.screen, (0,255,0), (px, py), max(2, int(self.player_radius * self.minimap_scale)))
        # enemies
        for e in self.enemies:
            if not e.alive: continue
            ex = mx0 + int(e.x * self.minimap_scale); ey = my0 + int(e.y * self.minimap_scale)
            # pygame.draw.circle(self.screen, (255,0,0), (ex, ey), max(2, int(e.radius * self.minimap_scale)))

    def draw_enemies_3d(self):
        # draw visible enemies as sprites in 3D view (billboards)
        if not self.enemies: return
        w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT; half_h = h//2
        for e in self.enemies:
            if not e.alive: continue
            # LOS check
            if not self.has_line_of_sight(self.player_x, self.player_y, e.x, e.y): continue
            dx = e.x - self.player_x; dy = e.y - self.player_y
            angle_to_enemy = math.atan2(dy, dx) - self.player_angle
            angle_to_enemy = (angle_to_enemy + math.pi) % (2*math.pi) - math.pi
            if -self.HALF_FOV < angle_to_enemy < self.HALF_FOV:
                dist = math.hypot(dx, dy)
                corrected_dist = dist * math.cos(angle_to_enemy)
                size = min((self.TILESIZE * 350) / (corrected_dist + 0.0001), h)
                # use sprite if exists else draw circle/rect
                if e.sprite:
                    try:
                        sprite_scaled = pygame.transform.scale(e.sprite, (int(size), int(size)))
                        screen_x = int((0.5 + angle_to_enemy / self.FOV) * w - size/2)
                        screen_y = int(half_h - size/2)
                        self.screen.blit(sprite_scaled, (screen_x, screen_y))
                    except:
                        pygame.draw.circle(self.screen, (255,0,0), (int(w/2 + math.tan(angle_to_enemy)*200), half_h), int(size/20))
                else:
                    screen_x = int((0.5 + angle_to_enemy / self.FOV) * w)
                    screen_y = half_h
                    pygame.draw.circle(self.screen, (255,0,0), (screen_x, screen_y), max(2, int(20* (400/(corrected_dist+1)))))

    def draw_gun(self):
        if not self.gun_enabled or not self.current_gun_sprite: return
        w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        sprite = self.current_gun_sprite
        sw,sh = sprite.get_size()
        desired_w = int(w * 0.65)
        scale = desired_w / sw
        sprite_scaled = pygame.transform.scale(sprite, (max(1,int(sw*scale)), max(1,int(sh*scale))))
        rect = sprite_scaled.get_rect(midbottom=(w - 125, h + 29))
        self.screen.blit(sprite_scaled, rect)

    def draw_hud(self):
        txt = f"HP: {int(self.player_health)}/{self.player_max_health}   Ammo: {self.ammo}/{self.max_ammo}"
        self.screen.blit(self.font.render(txt, True, (255,255,255)), (10, self.WINDOW_HEIGHT - 30))

    # ---------- Game Over ----------
    def show_game_over_menu(self):
        font = pygame.font.SysFont(None, 56)
        w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        overlay = pygame.Surface((w,h))
        overlay.set_alpha(220); overlay.fill((0,0,0))
        self.screen.blit(overlay, (0,0))
        t1 = font.render("Game Over", True, (255,50,50))
        t2 = self.font.render("Press R to Restart or Q to Quit", True, (255,255,255))
        self.screen.blit(t1, (w//2 - t1.get_width()//2, h//2 - 80))
        self.screen.blit(t2, (w//2 - t2.get_width()//2, h//2))
        pygame.display.update()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        # reset minimal state
                        self.player_health = float(self.player_max_health)
                        self.enemies.clear()
                        self.bullets.clear()
                        self.spawn_zombies(count=5)
                        waiting = False
                    elif e.key == pygame.K_q:
                        pygame.quit(); sys.exit()
            pygame.time.delay(100)

    # ---------- main loop (library provides loop) ----------
    def loop(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    run = False
                elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.fire_bullet()
                elif ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_m:
                        self.show_minimap = not self.show_minimap
                    elif ev.key == pygame.K_ESCAPE:
                        run = False
                    elif ev.key == pygame.K_r:
                        self.start_reload()

            # updates
            self.update_player()
            self.update_bullets()
            self.update_gun_animation()
            self.update_enemies()

            # draw
            self.screen.fill((100,100,100))
            self.draw_3d_view()
            self.draw_enemies_3d()
            self.draw_enemies()
            self.draw_minimap()
            self.draw_bullets_on_screen()
            self.draw_gun()
            self.draw_hud()

            # game over
            if self.player_health <= 0:
                self.show_game_over_menu()

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    # helper to draw bullets in screen coordinates (overlay)
    def draw_bullets_on_screen(self):
        # bullets drawn in world coords, map to screen for debug overlay
        for b in self.bullets:
            sx = int((b['x'] - self.player_x) + self.WINDOW_WIDTH/2)
            sy = int((b['y'] - self.player_y) + self.WINDOW_HEIGHT/2)
            # only draw if inside screen
            if 0 <= sx < self.WINDOW_WIDTH and 0 <= sy < self.WINDOW_HEIGHT:
                pygame.draw.circle(self.screen, (255,220,100), (sx, sy), 4)

# =================== Example usage (test script) ===================

