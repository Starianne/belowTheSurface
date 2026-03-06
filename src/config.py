# config

import os

SCREEN_W, SCREEN_H = 640, 360
BG_H = 360
GROUND_Y = BG_H
FPS = 60

ASSET_DIR = "assets"
PLAYER_SHEET = os.path.join(ASSET_DIR, "player.png")
PLAYER_SHEET_DOWN = os.path.join(ASSET_DIR, "player_down.png")
PLAYER_FRAMES = 4
PLAYER_FRAME_W = None # auto detect

TILE_IMG = os.path.join(ASSET_DIR, "tile.png")
TILE_IMG_DOWN = os.path.join(ASSET_DIR, "tile_down.png")

COIN_IMG = os.path.join(ASSET_DIR, "coin.png")
COIN_IMG_DOWN = os.path.join(ASSET_DIR, "coin_down.png")

OB_IMG = os.path.join(ASSET_DIR, "obstacle.png")
OB_IMG_DOWN = os.path.join(ASSET_DIR, "obstacle_down.png")

PORTAL_IMG = os.path.join(ASSET_DIR, "portal.png")
PORTAL_IMG_DOWN = os.path.join(ASSET_DIR, "portal_down.png")

BG_IMG = os.path.join(ASSET_DIR, "bg.png")
BG_IMG_DOWN = os.path.join(ASSET_DIR, "bg_down.png")

SCROLL_SPEED = 2
SPAWN_INTERVAL = 120 # frames
PORTAL_INTERVAL = 900 # frames