import config, models, sprites, utils
import pygame, os, random, sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
        pygame.display.set_caption("Beneath the Surface")
        self.clock = pygame.time.Clock()
        self.dt = 0

        # load assets
        self.bg = utils.load_image(config.BG_IMG, (config.SCREEN_W, config.BG_H))
        self.tile = utils.load_image(config.TILE_IMG, (64, 32))
        self.tile_up = utils.load_image(config.TILE_IMG_UP, (64, 32))
        self.coin_img = utils.load_image(config.COIN_IMG, (16, 16))
        self.coin_up = utils.load_image(config.COIN_IMG_UP, (16, 16))
        self.ob_img = utils.load_image(config.OB_IMG, (32, 32))
        self.ob_up = utils.load_image(config.OB_IMG_UP, (32, 32))
        self.portal_img = utils.load_image(config.PORTAL_IMG, (48, 24))
        self.portal_up = utils.load_image(config.PORTAL_IMG_UP, (48, 24))

        # player spritesheets
        player_surf = utils.load_image(config.PLAYER_SHEET, (128, 32))
        if config.PLAYER_FRAME_W is None:
            frame_w = player_surf.get_width() // config.PLAYER_FRAMES
        else:
            frame_w = config.PLAYER_FRAME_W
        self.player_sheet = sprites.SpriteSheet(player_surf, config.PLAYER_FRAMES)

        # upside down spritesheet fallback
        if os.path.exists(config.PLAYER_SHEET_UP):
            player_up_surf = utils.load_image(config.PLAYER_SHEET_UP)
            self.player_sheet_up = sprites.SpriteSheet(player_up_surf, config.PLAYER_FRAMES)
        else:
            # auto-generate darker/inverted variant
            self.player_sheet_up = sprites.SpriteSheet(utils.darken_surface(player_surf, 0.35), config.PLAYER_FRAMES)
        
        # state
        self.upside = False
        self.scroll_x = 0
        self.frame_count = 0

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()

        # player
        start_x = 80
        start_y = config.GROUND_Y - self.player_sheet.frame_h
        self.player = models.Player(self.player_sheet, start_x, start_y)
        self.all_sprites.add(self.player)

        # ground tile positions
        self.tiles = []
        self.tile_w = self.tile.get_width()
        for i in range((config.SCREEN_W // self.tile_w) + 3):
            self.tiles.append(i * self.tile_w)
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 18)
    
    def spawn_obstacle(self):
        y = config.GROUND_Y - self.ob_img.get_height()
        x = config.SCREEN_W + 20
        img = self.ob_up if self.upside and os.path.exists(config.OB_IMG_UP) else self.ob_img
        ob = models.ScrollingObject(img, x, y)
        self.obstacles.add(ob)
        self.all_sprites.add(ob)
    
    def spawn_coin(self):
        y = config.GROUND_Y - 60
        x = config.SCREEN_W + random.randint(20, 120)
        img = self.coin_up if self.upside and os.path.exists(config.COIN_IMG_UP) else self.coin_img
        coin = models.ScrollingObject(img, x, y)
        self.coins.add(coin)
        self.all_sprites.add(coin)

    def spawn_portal(self):
        self.upside = not self.upside
        # swap player sheet
        self.player_sheet = self.player_sheet_up if self.upside else self.player_sheet
        # darken background or flip
        if self.upside:
            self.bg_up = pygame.transform.flip(utils.darken_surface(self.bg, 0.45), False, True)
        else:
            self.bg_up = None

    def handle_collisions(self):
        # coins
        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        self.score += len(hit_coins) * 10
        # obstacles
        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            # simple death: reset score and objects
            self.score = 0
            for s in list(self.obstacles) + list(self.coins) + list(self.portals):
                s.kill()
        # portals
        hit_portal = pygame.sprite.spritecollideany(self.player, self.portals)
        if hit_portal:
            # flip world and remove portal
            hit_portal.kill()
            self.toggle_upside()

    def draw_ground(self):
        # draw repeating tiles; if upside and tile_up exists use it
        tile_img = self.tile_up if (self.upside and os.path.exists(config.TILE_IMG_UP)) else self.tile
        tile_w = tile_img.get_width()
        # compute offset for smooth scroll
        offset = self.frame_count * config.SCROLL_SPEED % tile_w
        if not self.upside:
            y = config.GROUND_Y
            for i in range(-1, config.SCREEN_W // tile_w + 3):
                self.screen.blit(tile_img, (i*tile_w - offset, y))
        else:
            # render tiles on ceiling (mirrored)
            y = 0 # top
            for i in range(-1, config.SCREEN_W // tile_w + 3):
                self.screen.blit(tile_img, (i*tile_w - offset, y))
    
    def render_sprite_mirrored(self, sprite):
        # if upside, render sprite attached to ceiling: mirror vertically
        if not self.upside:
            self.screen.blit(sprite.image, sprite.rect)
        else:
            img = sprite.image
            # compute mirrored y: distance from bottom becomes distance from top
            h = img.get_height()
            # original y relative to bottom
            rel_y = config.SCREEN_H - sprite.rect.bottom
            draw_y = rel_y
            draw_rect = pygame.Rect(sprite.rect.x, draw_y, img.get_width(), h)
            self.screen.blit(img, draw_rect)

    def run(self):
        running = True
        while running:
            self.dt = self.clock.tick(config.FPS)
            self.frame_count += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # jump direction depends on mode
                        if not self.upside:
                            self.player.jump()
                        else:
                            # when upside down, jumping should push player upward toward ceiling
                            if self.player.on_ground:
                                self.player.vy = -self.player.jump_strength # invert
                                self.player.on_ground = False
            
            # spawn logic
            if self.frame_count % config.SPAWN_INTERVAL == 0:
                self.spawn_coin()
            if self.frame_count % (config.SPAWN_INTERVAL * 2) == 0:
                self.spawn_obstacle()
            if self.frame_count % config.PORTAL_INTERVAL == 0:
                self.spawn_portal()
            
            # update groups
            self.all_sprites.update(self.dt)

            # move scrolling objects manually
            for s in list(self.obstacles) + list(self.coins) + list(self.portals):
                s.rect.x -= config.SCROLL_SPEED
                if s.rect.right < 0:
                    s.kill()
            
            # update tiles offset
            # collisions
            self.handle_collisions()

            # draw
            if not self.upside:
                self.screen.fill((135, 206, 235)) # sky
                self.screen.blit(self.bg, (0,0))
            else:
                # dark mode: flipped background
                self.screen.fill((18, 18, 28))
                if hasattr(self, "bg_up") and self.bg_up:
                    self.screen.blit(self.bg_up, (0,0))
                else:
                    self.screen.blit(utils.darken_surface(pygame.transform.flip(self.bg, False, True), 0.4), (0,0))

            # ground tiles
            self.draw_ground()

            # draw sprites; order matters
            # draw portals, coins, obstacles, player
            for group in (self.portals, self.coins, self.obstacles):
                for s in group:
                    self.render_sprite_mirrored(s)
            self.render_sprite_mirrored(self.player)

            # HUD
            score_surf = self.font.render(f"Score {self.score}", True, (255, 255, 255) if self.upside else (0,0,0))
            self.screen.blit(score_surf, (10, 10))

            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()