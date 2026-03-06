import config, models, sprites, utils
import pygame, os, random, sys
import asyncio

class Game:

    def reset_game(self):
        self.score = 0
        for s in list(self.obstacles) + list(self.coins) + list(self.portals):
            s.kill()
        self.player.rect.x = 80
        self.player.rect.y = config.GROUND_Y - self.player_sheet.frame_h
        self.player.vy = 0
        self.player.on_ground = True
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
        pygame.display.set_caption("Beneath the Surface")
        self.clock = pygame.time.Clock()
        self.dt = 0
        # load assets
        self.bg = utils.load_image(config.BG_IMG, (config.SCREEN_W, config.BG_H))
        self.tile = utils.load_image(config.TILE_IMG, (64, 32))
        self.tile_down = utils.load_image(config.TILE_IMG_DOWN, (64, 32))
        self.coin_img = utils.load_image(config.COIN_IMG, (16, 16))
        self.coin_down = utils.load_image(config.COIN_IMG_DOWN, (16, 16))
        self.ob_img = utils.load_image(config.OB_IMG, (32, 32))
        self.ob_down = utils.load_image(config.OB_IMG_DOWN, (32, 32))
        self.portal_img = utils.load_image(config.PORTAL_IMG, (48, 24))
        self.portal_down = utils.load_image(config.PORTAL_IMG_DOWN, (48, 24))

        #up player
        player_surf = utils.load_image(config.PLAYER_SHEET, (128, 32))
        self.player_sheet = sprites.SpriteSheet(player_surf, config.PLAYER_FRAMES)


        #down player
        player_down_surf = utils.load_image(config.PLAYER_SHEET_DOWN, (128, 32))
        self.player_sheet_down = sprites.SpriteSheet(player_down_surf, config.PLAYER_FRAMES)

        
        # state
        self.down = False
        self.scroll_x = 0
        self.frame_count = 0

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.portals = pygame.sprite.Group()

        # player
        start_x = 80
        # Place player on purple path (adjust y as needed)
        start_y = config.GROUND_Y - 100  # Example: 40 pixels above ground
        self.player = models.Player(self.player_sheet, start_x, start_y)
        self.all_sprites.add(self.player)

        # ground tile positions - ok we are using ts
        self.tiles = []
        self.tile_w = self.tile.get_width()
        for i in range((config.SCREEN_W // self.tile_w) + 3):
            self.tiles.append(i * self.tile_w)

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 18)
        self.game_over = False

    def toggle_down(self):
        self.down = not self.down #most stupid set up ever but I cant be bothered to change it
        if self.down is True:
            self.bg_down = utils.load_image(config.BG_IMG_DOWN, (config.SCREEN_W, config.BG_H))
            self.player.sheet = self.player_sheet_down
        else:
            self.bg_down = None
            self.player.sheet = self.player_sheet

    def spawn_obstacle(self):
        y = config.GROUND_Y - self.ob_img.get_height()
        x = config.SCREEN_W + 20
        img = self.ob_down if self.down and os.path.exists(config.OB_IMG_DOWN) else self.ob_img
        ob = models.ScrollingObject(img, x, y)
        self.obstacles.add(ob)
        self.all_sprites.add(ob)
    
    def spawn_coin(self):
        y = config.GROUND_Y - (self.coin_img.get_height() + 20)
        x = config.SCREEN_W + random.randint(20, 120)
        img = self.coin_down if self.down and os.path.exists(config.COIN_IMG_DOWN) else self.coin_img
        coin = models.ScrollingObject(img, x, y)
        self.coins.add(coin)
        self.all_sprites.add(coin)

    def spawn_portal(self):
        y = config.GROUND_Y - self.portal_img.get_height()
        x = config.SCREEN_W + 20
        img = self.portal_down if self.down and os.path.exists(config.PORTAL_IMG_DOWN) else self.portal_img
        portal = models.ScrollingObject(img, x, y)
        self.portals.add(portal)
        self.all_sprites.add(portal)

#fix ts
    def handle_collisions(self):
        # coins
        hit_coins = pygame.sprite.spritecollide(self.player, self.coins, True)
        self.score += len(hit_coins) * 10
        # obstacles
        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            self.game_over = True

        # portals
        hit_portal = pygame.sprite.spritecollide(self.player, self.portals, True)
        collided_portal = False
        if hit_portal and collided_portal is False:
            # flip world and remove portal
            self.portals.empty() #why does this not remove portal straight away? THERES NOTHING TO COLLIDE WITH SO IT NEVER GETS ADDED INTO THE OBJECT SPRITE GROUP
            collided_portal = True #now i need it to have no game over when you collide - it works now DONT TOUCH
            self.toggle_down()
        elif hit_portal:
            if self.dt > 20000:
                collided_portal = False

    def draw_ground(self):
        # draw repeating tiles ig
        tile_img = self.tile_down if (self.down and os.path.exists(config.TILE_IMG_DOWN)) else self.tile
        tile_w = tile_img.get_width()
        # compute offset for smooth scroll
        offset = self.frame_count * config.SCROLL_SPEED % tile_w
        if not self.down:
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
        if not self.down:
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

    async def run(self):
        running = True
        while running:
            self.dt = self.clock.tick(config.FPS)
            self.frame_count += 1
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        self.reset_game()
                        self.game_over = False
                        continue
                    if event.key == pygame.K_SPACE:
                        # jump direction depends on mode
                        if not self.down:
                            self.player.jump()
                        else:
                            # when upside down, jumping should push player upward toward ceiling
                            if self.player.on_ground:
                                self.player.vy = self.player.jump_strength # invert
                                self.player.on_ground = False
            

            # move scrolling objects manually
            for s in list(self.obstacles) + list(self.coins) + list(self.portals):
                s.rect.x -= config.SCROLL_SPEED
                if s.rect.right < 0:
                    s.kill()
            
            # update tiles offset
            # collisions
            self.handle_collisions()

            # draw how did you do ts twice
            if not self.down:
                self.screen.blit(self.bg, (0,0))
            else:
                #flipped background
                self.screen.blit(self.bg_down, (0,0))

            # ground tiles
            self.draw_ground()
            # draw sprites; order matters
            for group in (self.portals, self.coins, self.obstacles):
                for s in group:
                    self.render_sprite_mirrored(s)
            self.render_sprite_mirrored(self.player)

            # HUD
            score_surf = self.font.render(f"Score {self.score}", True, (255, 255, 255) if self.down else (0,0,0))
            self.screen.blit(score_surf, (10, 10))

            # Draw game over screen if needed
            if self.game_over:
                overlay = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))
                go_text = self.font.render("GAME OVER", True, (255, 0, 0))
                restart_text = self.font.render("Press any key to restart", True, (255, 255, 255))
                self.screen.blit(go_text, (config.SCREEN_W // 2 - go_text.get_width() // 2, config.SCREEN_H // 2 - 40))
                self.screen.blit(restart_text, (config.SCREEN_W // 2 - restart_text.get_width() // 2, config.SCREEN_H // 2))
            if not self.game_over:
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
                # collisions
                self.handle_collisions()
            pygame.display.flip()
            await asyncio.sleep(0)
            # Only update game logic if not game over
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    asyncio.run(Game().run())