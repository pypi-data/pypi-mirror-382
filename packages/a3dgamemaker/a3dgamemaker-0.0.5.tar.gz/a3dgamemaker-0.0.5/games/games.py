import pygame, math, random, os, time

# ====== إعداد العدو ======
class Enemy:
    def __init__(self, x, y, sprite=None, dead_sprite=None, speed=1.0, health=2, radius=16):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.dead_sprite = dead_sprite
        self.speed = speed
        self.health = health
        self.radius = radius
        self.alive = True
        self.last_hit_time = 0.0  # كولداون للضرب

# ====== محرك RAYCASTING ======
class RAYCASTING:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)

        self.TILESIZE = 64
        self.FOV = math.radians(60)
        self.RES = 120
        self.HALF_FOV = self.FOV / 2
        self.MAX_DEPTH = 800
        self.show_minimap = True

        self.enemies = []
        self.zombie_enabled_flag = False
        self.bullets = []

        # السلاح
        self.gun_enabled = False
        self.gun_idle = None
        self.gun_fire = None
        self.gun_sound = None
        self.current_gun_sprite = None
        self.fire_time = 0.0
        self.fire_duration = 0.12
        self.t = self.TILESIZE // 4

        # اللاعب
        self.player_x = 150
        self.player_y = 150
        self.player_angle = 0.0
        self.player_radius = 8
        self.player_movespeed = 2.5
        self.player_rotationspeed = math.radians(2)
        self.player_max_health = 10
        self.player_health = self.player_max_health
        self.on_stairs = False

        self.font = pygame.font.SysFont(None, 28)
        self.update_window_size()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.map_data = []

    # ===== إعدادات =====
    def caption(self, text): pygame.display.set_caption(text)
    def set_tilesize(self, t): self.TILESIZE=t; self.update_window_size()
    def set_rows(self, r): self.ROWS=r; self.update_window_size()
    def set_cols(self, c): self.COLS=c; self.update_window_size()
    def set_fov(self, deg): self.FOV=math.radians(deg); self.HALF_FOV=self.FOV/2
    def set_resolution(self, res): self.RES=res; self.NUM_RAYS=res
    def update_window_size(self):
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 650
        self.NUM_RAYS = self.RES

    def set_map(self, layout):
        self.map_data = layout
        self.ROWS = len(layout)
        self.COLS = len(layout[0]) if layout else 0
        self.update_window_size()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

    # ===== تفعيل السلاح =====
    def enable_gun(self, enable=True, idle_path=None, fire_path=None, sound_path=None, fire_duration=0.12):
        self.gun_enabled = enable
        self.fire_duration = float(fire_duration)
        if idle_path and os.path.exists(idle_path): self.gun_idle = pygame.image.load(idle_path).convert_alpha()
        if fire_path and os.path.exists(fire_path): self.gun_fire = pygame.image.load(fire_path).convert_alpha()
        if sound_path and os.path.exists(sound_path):
            try: pygame.mixer.init(); self.gun_sound = pygame.mixer.Sound(sound_path)
            except: self.gun_sound = None
        self.current_gun_sprite = self.gun_idle or self.gun_fire

    # ===== الزومبي =====
    def zombie_enabled(self, enable=True): self.zombie_enabled_flag = enable
    def spawn_zombies(self, count=5, sprite_path=None, dead_sprite_path=None):
        self.enemies.clear()
        sprite = dead_sprite = None
        if sprite_path and os.path.exists(sprite_path): sprite = pygame.image.load(sprite_path).convert_alpha()
        if dead_sprite_path and os.path.exists(dead_sprite_path): dead_sprite = pygame.image.load(dead_sprite_path).convert_alpha()
        empty_tiles = [(x, y) for y,row in enumerate(self.map_data) for x,val in enumerate(row) if val==0]
        for _ in range(count):
            if not empty_tiles: break
            x,y = random.choice(empty_tiles); empty_tiles.remove((x,y))
            zx = x*self.TILESIZE + self.TILESIZE//2
            zy = y*self.TILESIZE + self.TILESIZE//2
            self.enemies.append(Enemy(zx, zy, sprite, dead_sprite))

    # ===== حركة اللاعب مع الدرج والماء والمرتفع =====
    def update_player(self):
        keys = pygame.key.get_pressed()
        turn = walk = 0
        if keys[pygame.K_d]: turn = 1
        if keys[pygame.K_a]: turn = -1
        if keys[pygame.K_w]: walk = 1
        if keys[pygame.K_s]: walk = -1
        self.player_angle += turn * self.player_rotationspeed
        step = walk * self.player_movespeed
        nx = self.player_x + math.cos(self.player_angle) * step
        ny = self.player_y + math.sin(self.player_angle) * step

        mx,my = int(nx//self.TILESIZE), int(ny//self.TILESIZE)
        if my>=len(self.map_data) or mx>=len(self.map_data[0]): return
        tile = self.map_data[my][mx]

        # تحريك اللاعب حسب نوع البلاطة
        if tile in [0,2,4] or (tile==3 and self.on_stairs):
            self.player_x, self.player_y = nx, ny

        self.on_stairs = (tile==2)

    # ===== الريندر =====
    def normalizeangle(self,a): a%=2*math.pi; return a+2*math.pi if a<0 else a
    def has_wall_at(self,x,y):
        if x<0 or y<0: return True
        mx,my=int(x//self.TILESIZE),int(y//self.TILESIZE)
        if my>=len(self.map_data) or mx>=len(self.map_data[0]): return True
        tile = self.map_data[my][mx]
        return tile==1 or tile==3

    def cast_ray_distance(self,ang):
        ang=self.normalizeangle(ang)
        rx,ry=self.player_x,self.player_y
        for d in range(self.MAX_DEPTH):
            rx+=math.cos(ang); ry+=math.sin(ang)
            if self.has_wall_at(rx,ry): return math.hypot(rx-self.player_x,ry-self.player_y)
        return self.MAX_DEPTH

    def cast_all_rays(self):
        rays=[]
        start=self.player_angle-(self.FOV/2)
        for r in range(self.NUM_RAYS):
            ang=self.normalizeangle(start+r*(self.FOV/self.NUM_RAYS))
            dist=self.cast_ray_distance(ang)
            rays.append((ang,dist))
        return rays

    def has_line_of_sight(self, x1, y1, x2, y2):
        dx = x2 - x1; dy = y2 - y1
        dist = math.hypot(dx, dy)
        if dist == 0: return True
        steps = int(dist)
        for i in range(steps):
            xi = x1 + dx * i / steps
            yi = y1 + dy * i / steps
            if self.has_wall_at(xi, yi): return False
        return True

    # ===== رسم 3D محسّن =====
    def draw_simple_3d(self):
     w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
     half_h = h//2
     rays = self.cast_all_rays()
     slice_w = int(w/self.NUM_RAYS)+1

     for i,(ang,dist) in enumerate(rays):
        corrected = dist*math.cos(self.player_angle-ang)
        wall_h = min((self.TILESIZE*500)/(corrected+0.0001), h)  # ارتفاع أكبر للسقف
        shade = max(0, 255 - int(corrected*0.7))
        pygame.draw.rect(self.screen, (shade,shade,shade),
                         (int(i*(w/self.NUM_RAYS)), int(half_h - wall_h/2), slice_w, int(wall_h)))

    # رسم البلاطات 3D مع اختلاف الارتفاع
     


    # ===== السلاح =====
    def draw_gun(self):
        if not self.gun_enabled or not self.current_gun_sprite: return
        w,h=self.WINDOW_WIDTH,self.WINDOW_HEIGHT
        sprite = self.current_gun_sprite; sw, sh = sprite.get_size()
        desired_w = int(w*0.5); scale = desired_w / sw
        sprite_scaled = pygame.transform.scale(sprite,(int(sw*scale),int(sh*scale)))
        rect = sprite_scaled.get_rect(bottomright=(w-200,h+30))
        self.screen.blit(sprite_scaled, rect)

    # ===== إطلاق الطلقات =====
    def fire_bullet(self):
        if not self.gun_enabled: return
        if self.gun_sound:
            try: self.gun_sound.play()
            except: pass
        if self.gun_fire:
            self.current_gun_sprite = self.gun_fire
            self.fire_time = time.time()
        speed = 16
        dx = math.cos(self.player_angle)*speed
        dy = math.sin(self.player_angle)*speed
        start_x = self.player_x + math.cos(self.player_angle)*(self.player_radius+6)
        start_y = self.player_y + math.sin(self.player_angle)*(self.player_radius+6)
        self.bullets.append({'x':start_x,'y':start_y,'dx':dx,'dy':dy})

    def update_gun_animation(self):
        if self.current_gun_sprite == self.gun_fire:
            if (time.time()-self.fire_time) >= self.fire_duration:
                self.current_gun_sprite = self.gun_idle or self.gun_fire

    def update_bullets(self):
        for b in self.bullets[:]:
            b['x'] += b['dx']; b['y'] += b['dy']
            if self.has_wall_at(b['x'],b['y']):
                try: self.bullets.remove(b)
                except: pass; continue
            if self.zombie_enabled_flag:
                for e in self.enemies:
                    if not e.alive: continue
                    if math.hypot(e.x-b['x'], e.y-b['y']) < 40:
                        e.health -= 1
                        if e.health <= 0: e.alive = False
                        try: self.bullets.remove(b)
                        except: pass
                        break

    # ===== تحديث الأعداء مع كولداون 3 ثواني =====
    def update_enemies(self):
        if not self.zombie_enabled_flag: return
        for e in self.enemies:
            if not e.alive: continue
            dx = self.player_x - e.x
            dy = self.player_y - e.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                dx /= dist
                dy /= dist
            new_x = e.x + dx * e.speed
            new_y = e.y + dy * e.speed
            if not self.has_wall_at(new_x, e.y): e.x = new_x
            if not self.has_wall_at(e.x, new_y): e.y = new_y
            if dist < self.player_radius + e.radius:
                now = time.time()
                if now - e.last_hit_time >= 3:
                    self.player_health = max(0, self.player_health - 1)
                    e.last_hit_time = now

    # ===== رسم الزومبي مع Line of Sight =====
    def draw_enemies(self):
        if not self.zombie_enabled_flag: return
        w,h=self.WINDOW_WIDTH,self.WINDOW_HEIGHT; half_h=h//2
        for e in self.enemies:
            if not self.has_line_of_sight(self.player_x, self.player_y, e.x, e.y):
                continue
            sprite = e.sprite if e.alive else e.dead_sprite
            if not sprite: continue
            dx = e.x - self.player_x; dy = e.y - self.player_y
            angle_to_enemy = math.atan2(dy, dx) - self.player_angle
            angle_to_enemy = (angle_to_enemy + math.pi) % (2*math.pi) - math.pi
            if -self.HALF_FOV < angle_to_enemy < self.HALF_FOV:
                dist = math.hypot(dx, dy)
                corrected_dist = dist * math.cos(angle_to_enemy)
                size = min((self.TILESIZE*400)/(corrected_dist+0.0001), h)
                sprite_scaled = pygame.transform.scale(sprite, (int(size), int(size)))
                screen_x = int((0.5 + angle_to_enemy/self.FOV) * w - size/2)
                screen_y = int(half_h - size/2)
                self.screen.blit(sprite_scaled, (screen_x, screen_y))

    # ===== HUD =====
    def draw_hud(self):
        txt = f"HP: {int(self.player_health)}/{self.player_max_health}"
        self.screen.blit(self.font.render(txt,True,(255,255,255)),(10,10))

    def draw_bullets(self):
        for b in self.bullets:
            screen_x = int((b['x'] - self.player_x) + self.WINDOW_WIDTH / 2)
            screen_y = int((b['y'] - self.player_y) + self.WINDOW_HEIGHT / 2)
            pygame.draw.circle(self.screen, (255, 220, 100), (screen_x, screen_y), 4)

    # ===== الميني ماب محسّن =====
    def draw_minimap(self):
        if not self.show_minimap: return
        t = self.TILESIZE // 4
        for y,row in enumerate(self.map_data):
            for x,val in enumerate(row):
                if val==1: color = (60,60,60)
                elif val==2: color = (200,160,80)
                elif val==3: color = (120,120,120)
                elif val==4: color = (50,50,200)
                else: color = (200,200,200)
                pygame.draw.rect(self.screen, color, (x*t, y*t, t, t))
        pygame.draw.circle(self.screen,(0,255,0),(int(self.player_x/4), int(self.player_y/4)),4)

    # ===== Game Over =====
    def check_player_health(self):
        if self.player_health <= 0:
            self.show_game_over_menu()

    def show_game_over_menu(self):
        font = pygame.font.SysFont(None, 60)
        w,h = self.WINDOW_WIDTH, self.WINDOW_HEIGHT
        menu_surface = pygame.Surface((w,h))
        menu_surface.set_alpha(220)
        menu_surface.fill((0,0,0))
        self.screen.blit(menu_surface,(0,0))
        txt1 = font.render("Game Over", True,(255,0,0))
        txt2 = font.render("Press R to Restart or Q to Quit", True,(255,255,255))
        self.screen.blit(txt1,(w//2 - txt1.get_width()//2, h//2 - 50))
        self.screen.blit(txt2,(w//2 - txt2.get_width()//2, h//2 + 20))
        pygame.display.update()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        self.player_health = self.player_max_health
                        waiting = False
                    elif e.key == pygame.K_q:
                        pygame.quit(); exit()
            pygame.time.delay(100)

    # ===== الحلقة الرئيسية =====
    def loop(self):
        clock = pygame.time.Clock(); run=True
        while run:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: run=False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button==1: self.fire_bullet()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m: self.show_minimap = not self.show_minimap

            self.update_player()
            self.update_bullets()
            self.update_gun_animation()
            self.update_enemies()
            self.check_player_health()

            self.screen.fill((100,100,100))
            self.draw_simple_3d()
            self.draw_minimap()
            self.draw_bullets()
            self.draw_gun()
            self.draw_enemies()
            self.draw_hud()

            pygame.display.update()
            clock.tick(60)
        pygame.quit()

# ====== تشغيل تجربة ======
 #if __name__=="__main__":
  #  r = RAYCASTING()
   # r.caption("Gun + Zombies")
    #r.set_map([
     #   [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
      #  [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
       # [1,0,0,2,1,0,3,0,1,0,1,0,1,0,1,0,3,0,0,1],
        #[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    #])
    #r.enable_gun(True, idle_path="iddle.png", fire_path="shhot.png", sound_path="gun.wav", fire_duration=0.12)
    #r.zombie_enabled(True)
    #r.spawn_zombies(count=5, sprite_path="s.png", dead_sprite_path="axs.png")
    #r.loop()
