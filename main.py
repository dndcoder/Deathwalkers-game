import wx
import pygame as pg
import sys
from random import choice
import random
from os import path
from settings import *
from sprites import *
from tilemap import *
import zstd
import copy
from itertools import repeat
import time

# HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('DEATHWALKERS')
        self.clock = pg.time.Clock()
        self.load_data()
        self.current_level = 0
        self.offset = repeat((0, 0))

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'tiley_img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'tiley_img/maps')
        self.title_font = path.join(img_folder, 'ZOMBIE.ttf')
        self.hud_font = path.join(img_folder, 'Impacted2.0.ttf')
        self.menu_text = path.join(img_folder, 'Menu.png')
        self.area_text = path.join(img_folder, 'Alineatypeface-eldx.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['rst'] = pg.image.load(path.join(img_folder, BULLET_RUST)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_image = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.boss_img = pg.transform.scale(self.mob_image, (200, 200))
        self.ghost_image = pg.image.load(path.join(img_folder, GHOST_IMG)).convert_alpha()
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.ghost_splat = pg.image.load(path.join(img_folder, GHOST_SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (64, 64))
        self.ghost_splat = pg.transform.scale(self.ghost_splat, (150, 150))
        self.big_splat = pg.transform.scale(self.splat, (200, 200))
        self.pistol_img = pg.image.load(path.join(img_folder, GUN1)).convert_alpha()
        self.shotgun_img = pg.image.load(path.join(img_folder, GUN2)).convert_alpha()
        self.choose_box = pg.image.load(path.join(img_folder, BOX3)).convert_alpha()
        self.choose_box = pg.transform.scale(self.choose_box, (200, 200)).convert_alpha()
        self.choose_box2 = pg.transform.scale(self.choose_box, (170, 170)).convert_alpha()
        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
        #lighting
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()
        # Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            self.effects_sounds[type] = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.2)
                self.weapon_sounds[weapon].append(s)
        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            self.player_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            self.zombie_hit_sounds.append(pg.mixer.Sound(path.join(snd_folder, snd)))

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'Starter.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False
        self.effects_sounds['level_start'].play()

    def new2(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'Orchard.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False

    def new3(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False

    def new4(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'Boss_level.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False

    def new5(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'Last_level.tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False

    def new6(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.boss = pg.sprite.Group()
        self.ghost = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'You_Win (2).tmx'))
        self.map_img = self.map.make_map()
        self.map.rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            if tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
            if tile_object.name == 'boss':
                Boss(self, obj_center.x, obj_center.y)
            if tile_object.name == 'ghost':
                Ghost(self, obj_center.x, obj_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in ['health', 'shotgun', 'armor', 'hazard', 'antidote']:
                Item(self, obj_center, tile_object.name)
        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.night = False
        self.menu = False
        
    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000.0  # fix for Python 2.x
            self.events()
            if self.menu:
                pass
            else:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # Game over?
        if len(self.mobs) == 0 and len(self.boss) == 0 and len(self.ghost) == 0 and self.current_level < 5:
            self.show_go_screen()
            self.current_level += 1
            # self.player.minus_speed(QUICKEN / 3, TURN_QU / 3)
            if self.current_level == 1:
                self.new2()
            elif self.current_level == 2:
                self.new3()
            elif self.current_level == 3:
                self.new4()
            elif self.current_level == 4:
                self.new5()
            else:
                self.new6()
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)
        # player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                hit.kill()
                self.effects_sounds['gun_pickup'].play()
                self.player.weapon = 'shotgun'
            if hit.type == 'armor':
                hit.kill()
                self.effects_sounds['armor_clink'].play()
                global MOB_DAMAGE
                global BOSS_DAMAGE
                MOB_DAMAGE -= 1
                BOSS_DAMAGE -= 10
            if hit.type == 'hazard':
                hit.kill()
                self.effects_sounds['ouch'].play()
                self.player.health -= 50
                if self.player.health <= 0:
                    self.playing = False
            if hit.type == 'antidote' and self.player.health < PLAYER_HEALTH:
                    hit.kill()
                    self.effects_sounds['antidote'].play()
                    self.player.add_health(ANTIDOTE_AMOUNT)
                    self.player.minus_speed(45, 10)
        # mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random.random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            self.offset = self.player.shake(amount=5, step=2, times=2)
        # boss hit player
        hits = pg.sprite.spritecollide(self.player, self.boss, False, collide_hit_rect)
        for hit in hits:
            if random.random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= BOSS_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(BOSS_KNOCKBACK, 0).rotate(-hits[0].rot)
        # ghost hit player
        hits = pg.sprite.spritecollide(self.player, self.ghost, False, collide_hit_rect)
        for hit in hits:
            if random.random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= GHOST_DAMAGE
            hit.vel = vec(0, 0)
            if self.player.health <= 0:
                self.playing = False
        if hits:
            self.player.hit()
            self.player.pos += vec(GHOST_KNOCKBACK, 0).rotate(-hits[0].rot)
        # bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)
        # bullets hit boss
        hits = pg.sprite.groupcollide(self.boss, self.bullets, False, True)
        for boss in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[boss]:
                boss.health -= bullet.damage
            boss.vel = vec(0, 0)
        # bullets hit ghost
        hits = pg.sprite.groupcollide(self.ghost, self.bullets, False, True)
        for ghost in hits:
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[ghost]:
                ghost.health -= bullet.damage
            ghost.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        #draw light mask
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self. camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption('DEATHWALKERS')
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply(self.map))
        # self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            if isinstance(sprite, Boss):
                sprite.draw_health()
            if isinstance(sprite, Ghost):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        if self.night:
            self.render_fog()
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        self.draw_text('ZOMBIES: {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, WIDTH - 10, 10, align="ne")
        if len(self.boss) >= 1:
            self.draw_text('BOSSES: {}'.format(len(self.boss)), self.hud_font, 30, WHITE, WIDTH - 175, 10, align="ne")
        if len(self.ghost) >= 1:
            self.draw_text('GHOSTS: {}'.format(len(self.ghost)), self.hud_font, 30, WHITE, WIDTH - 350, 10, align="ne")
        if self.menu:
            self.screen.blit(self.dim_screen, (0, 0))
            self.screen.blit(self.pistol_img, (250, 300))
            if self.player.weapon == 'shotgun':
                self.screen.blit(self.choose_box, (500, 260))
                self.screen.blit(self.shotgun_img, (550, 310))
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.quit()
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_LEFT:
                            self.choose_box.fill(TRANSPARENT)
                            self.player.weapon = 'pistol'
                            self.player.pistol_shotgun = True
                            self.screen.blit(self.choose_box, (200, 250))
                            self.screen.blit(self.shotgun_img, (550, 310))
            if self.player.weapon == 'pistol' and self.player.pistol_shotgun == False:
                self.screen.blit(self.choose_box, (200, 250))
                self.screen.blit(self.pistol_img, (250, 300))
            if self.player.weapon == 'pistol' and self.player.pistol_shotgun == True:
                self.screen.blit(self.choose_box, (200, 250))
                self.choose_box.fill(RED)
                self.screen.blit(self.pistol_img, (250, 300))
                self.screen.blit(self.shotgun_img, (550, 310))
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.quit()
                    if event.type == pg.K_DOWN:
                        if event.key == pg.K_RIGHT:
                            # if self.player.weapon == 'pistol' and self.player.pistol_shotgun == True:
                            self.choose_box.fill(TRANSPARENT)
                            self.player.weapon = 'shotgun'
                            self.player.pistol_shotgun = True
                            self.screen.blit(self.choose_box, (500, 260))
                            self.screen.blit(self.shotgun_img, (550, 310))
            if self.player.weapon == 'shotgun' and self.player.pistol_shotgun == True:
                self.screen.blit(self.choose_box, (500, 260))
                self.choose_box.fill(RED)
                self.screen.blit(self.pistol_img, (250, 300))
                self.screen.blit(self.shotgun_img, (550, 310))
            self.draw_text("Paused", self.title_font, 50, RED, WIDTH / 2, 50, align="center")
            self.draw_text("Art from kenney.nl", self.area_text, 50, RED, WIDTH / 2, HEIGHT - 50, align="center")
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
#                 if event.key == pg.K_p and self.credits == False:
#                     self.paused = not self.paused
#                 if event.key == pg.K_c and self.paused == False:
#                     self.credits = not self.credits
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_RETURN:
                    self.menu = not self.menu
            #if event.type == pg.MOUSEBUTTONDOWN:
                #self.player.shoot()
                

    def show_start_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("DEATHWALKERS", self.title_font, 120, RED, WIDTH / 2, HEIGHT / 4, align="center")
        self.draw_text("PRESS ANY KEY TO START", self.title_font, 60, WHITE, WIDTH / 2, HEIGHT / 2, align="center")
        self.draw_text("N FOR NIGHT MODE    ESC TO QUIT", self.title_font, 35, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
        self.draw_text("H FOR CODERS    RETURN FOR MENU", self.title_font, 35, WHITE, WIDTH / 2, HEIGHT * 3.5 / 4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        self.screen.fill(BLACK)
        if self.player.health <= 0:
            self.draw_text("YOU DIED", self.title_font, 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
            self.draw_text("PRESS ANY KEY TO RESTART", self.title_font, 60, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
            pg.display.flip()
            self.wait_for_key()
            self.current_level = 0
        if len(self.mobs) == 0 and len(self.boss) == 0 and len(self.ghost) == 0:
            self.draw_text("AREA COMPLETED", self.area_text, 80, RED, WIDTH / 2, HEIGHT / 4 + 50, align="center")
            self.draw_text("LEVEL UP!", self.title_font, 150, RED, WIDTH / 2, HEIGHT / 2, align="center")
            self.draw_text("PRESS ANY KEY TO START", self.title_font, 50, WHITE, WIDTH / 2, HEIGHT * 3 / 4, align="center")
            pg.display.flip()
            self.wait_for_key()
        if self.current_level == 6:
            self.draw_text("YOU WON!", self.area_text, 80, RED, WIDTH / 2, HEIGHT / 4 + 50, align="center")
            pg.display.flip()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()




















































    
