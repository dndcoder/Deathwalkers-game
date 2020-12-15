import pygame as pg
import random
vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)

# game settings
WIDTH = 920   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 620  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 120
TITLE = "Deathwalkers"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_START_HEALTH = 80
PLAYER_HEALTH = 100
PLAYER_GAME_HEALTH = PLAYER_HEALTH
PLAYER_SPEED = 280
PLAYER_ROT_SPEED = 200
PLAYER_IMG = 'soldier2_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

# Weapon settings
BULLET_IMG = 'bullet.png'
BULLET_RUST = 'bullet_rust.png'
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 600,
                     'bullet_lifetime': 1000,
                     'rate': 250,
                     'kickback': 200,
                     'spread': 5,
                     'damage': 10,
                     'bullet_size': 'lg',
                     'bullet_count': 1}
WEAPONS['shotgun'] = {'bullet_speed': 450,
                      'bullet_lifetime': 500,
                      'rate': 900,
                      'kickback': 300,
                      'spread': 20,
                      'damage': 5,
                      'bullet_size': 'sm',
                      'bullet_count': 12}
WEAPONS['rust_gun'] = {'bullet_speed': 350,
                      'bullet_lifetime': 300,
                      'rate': 1000,
                      'kickback': 150,
                      'spread': 20,
                      'damage': 20,
                      'bullet_size': 'rst',
                      'bullet_count': 1}

# Mob settings
MOB_IMG = 'zombie1_hold.png'
MOB_IMG2 = 'zombie2_hold.png'
MOB_SPEEDS = [150, 100, 75, 125]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = [75, 100, 125]
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 400

# Boss settings
BOSS_IMG = 'zombie1_hold.png'
BOSS_SPEEDS = [50, 75]
BOSS_HIT_RECT = pg.Rect(230, 230, 120, 120)
BOSS_HEALTH = 2000
BOSS_DAMAGE = 75
BOSS_KNOCKBACK = 50
AVOID_RADIUS = 50
BOSS_DETECT_RADIUS = 800

# Ghost settings
GHOST_IMG = 'ghost.png'
GHOST_SPEEDS = [200, 230]
GHOST_HIT_RECT = pg.Rect(230, 230, 120, 120)
GHOST_HEALTH = 1000
GHOST_DAMAGE = 50
GHOST_KNOCKBACK = 50
AVOID_RADIUS = 50
GHOST_DETECT_RADIUS = 800

# Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
SPLAT = 'splat red.png'
GHOST_SPLAT = 'splat green.png'
FLASH_DURATION = 50
DAMAGE_ALPHA = [i for i in range(0, 255, 55)]
NIGHT_COLOR = (10, 10, 10)
LIGHT_RADIUS = (750, 750)
LIGHT_MASK = "light_350_soft.png"

# Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

# Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'obj_shotgun.png',
               'armor': 'obj_armor.png',
               'hazard': 'death_hazard.png',
               'antidote': 'antidote_1.png'}
HEALTH_PACK_AMOUNT = 20
ANTIDOTE_AMOUNT = 45
SHOTGUN_AMMO = 2
BOB_RANGE = 15
BOB_SPEED = 0.3
QUICKEN = 75
TURN_QU = 50

# Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                 'shotgun': ['shotgun.wav']}
EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'gun_pickup.wav',
                  'level_Up': 'levelCleared.wav',
                  'armor_clink': 'Armor_on.wav',
                  'ouch': 'Ouch.wav',
                  'antidote': 'Powerup6.wav'}

# Menu
GUN1 = 'pistallx4.png'
GUN2 = 'pic_shotgun.png'
BOX1 = 'box1.png'
BOX2 = 'box2.png'
BOX3 = 'Box3.png'
TRANSPARENT = (0, 0, 0, 0)



































