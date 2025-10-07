import pygame
import math

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = 600, 400
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.players = {}
        self.ground = {}
        self.registers = {}
        self.type = None
        self.step_delay = 500
        self.last_step_time = {}
        self.bullets = []

    def set_caption(self, caption):
        pygame.display.set_caption(caption)

    def set_size(self, hei, wid):
        self.WIDTH = wid
        self.HEIGHT = hei
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

    def screenfill(self, color):
        self.screen.fill(color)

    def create_player(self, name, wid, hei, x, y, color, speed):
        self.players[name] = {"x": x, "y": y, "width": wid, "height": hei,
                              "color": color, "speed": speed, "velocity_y": 0}

    def draw_player(self, name):
        if name in self.players:
            p = self.players[name]
            pygame.draw.rect(self.screen, p["color"], (p["x"], p["y"], p["width"], p["height"]))

    def create_ground(self, name, y, x, wid, hei, color, speed=0):
        self.ground[name] = {"x": x, "y": y, "width": wid, "height": hei,
                             "color": color, "speed": speed, "velocity_y": 0}

    def drawground(self, name):
        g = self.ground[name]
        pygame.draw.rect(self.screen, g["color"], (g["x"], g["y"], g["width"], g["height"]))

    def movement(self, name, type="2d"):
        if name not in self.players: return
        keys = pygame.key.get_pressed()
        p = self.players[name]
        now = pygame.time.get_ticks()
        last = self.last_step_time.get(name, 0)

        if type == "2d":
            if keys[pygame.K_d]: self.right(name)
            if keys[pygame.K_a]: self.left(name)
            if keys[pygame.K_SPACE]: self.jump(name)
            self.type = False

        if type == "fisheye":
            if now - last < self.step_delay: return
            if keys[pygame.K_w]: self.up(name)
            if keys[pygame.K_s]: self.down(name)
            if keys[pygame.K_a]: self.left(name)
            if keys[pygame.K_d]: self.right(name)
            self.last_step_time[name] = now
            self.type = True

    def up(self, name):
        p = self.players[name]
        p["y"] -= p["speed"]
        if p["y"] < 0: p["y"] = 0

    def down(self, name):
        p = self.players[name]
        p["y"] += p["speed"]
        if p["y"] + p["height"] > self.HEIGHT: p["y"] = self.HEIGHT - p["height"]

    def left(self, name):
        p = self.players[name]
        p["x"] -= p["speed"]
        if p["x"] < 0: p["x"] = 0

    def right(self, name):
        p = self.players[name]
        p["x"] += p["speed"]
        if p["x"] + p["width"] > self.WIDTH: p["x"] = self.WIDTH - p["width"]

    def jump(self, name):
        p = self.players[name]
        for g in self.ground.values():
            if p["y"] + p["height"] >= g["y"]:
                p["velocity_y"] = -15
                break

    def resolve_collision(self, p_rect, g_rect, p):
        """منع الدخول من كل الاتجاهات"""
        if p_rect.colliderect(g_rect):
            dx = (p_rect.centerx - g_rect.centerx)
            dy = (p_rect.centery - g_rect.centery)
            width = (p_rect.width + g_rect.width) / 2
            height = (p_rect.height + g_rect.height) / 2
            cross_width = width * dy
            cross_height = height * dx

            if abs(dx) <= width and abs(dy) <= height:
                if cross_width > cross_height:
                    if cross_width > -cross_height:
                        # collision from top
                        p_rect.top = g_rect.bottom
                        p["velocity_y"] = 0
                    else:
                        # collision from left
                        p_rect.left = g_rect.right
                else:
                    if cross_width > -cross_height:
                        # collision from right
                        p_rect.right = g_rect.left
                    else:
                        # collision from bottom
                        p_rect.bottom = g_rect.top
                        p["velocity_y"] = 0
        return p_rect

    def gravity(self, name):
     """جاذبية مستقرة + تجاهل التصادم الجانبي"""
     if name not in self.players or self.type:
        return

     p = self.players[name]
     p["y"] += p["velocity_y"]
     p["velocity_y"] += 1  # الجاذبية العادية

     player_rect = pygame.Rect(p["x"], p["y"], p["width"], p["height"])

     for g in self.ground.values():
        ground_rect = pygame.Rect(g["x"], g["y"], g["width"], g["height"])

        if player_rect.colliderect(ground_rect):
            # نسمح فقط بالتصادم الرأسي (من فوق أو تحت)
            if p["velocity_y"] > 0 and p["y"] + p["height"] > g["y"]:
                # من فوق الأرض
                p["y"] = g["y"] - p["height"]
                p["velocity_y"] = 0
            elif p["velocity_y"] < 0 and p["y"] < g["y"] + g["height"]:
                # من تحت الأرض
                p["y"] = g["y"] + g["height"]
                p["velocity_y"] = 1  # يدفعه للأسفل


    def whendie(self, player, x, y, death_condition=None):
        if player not in self.players:
            return
        p = self.players[player]
        if death_condition:
            died = death_condition(p)
        else:
            died = p["y"] > self.HEIGHT + 100
        if died:
            p["x"], p["y"], p["velocity_y"] = x, y, 0
            print(f"{player} died and respawned at ({x},{y})")

    def collider_rect(self, name):
        if name in self.players:
            p = self.players[name]
            return pygame.Rect(p["x"], p["y"], p["width"], p["height"])
        elif name in self.ground:
            g = self.ground[name]
            return pygame.Rect(g["x"], g["y"], g["width"], g["height"])
        else:
            return None

    def check_collision(self, name1, name2, register_name):
        rect1 = self.collider_rect(name1)
        rect2 = self.collider_rect(name2)
        if rect1 and rect2:
            self.registers[register_name] = rect1.colliderect(rect2)
        else:
            self.registers[register_name] = False

    def gun(self, playername):
        if playername not in self.players: return
        p = self.players[playername]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (p["x"] + p["width"] // 2)
        dy = mouse_y - (p["y"] + p["height"] // 2)
        distance = math.hypot(dx, dy)
        if distance == 0: return
        speed = 10
        vel_x = dx / distance * speed
        vel_y = dy / distance * speed
        bullet = {"rect": pygame.Rect(p["x"] + p["width"] // 2,
                                      p["y"] + p["height"] // 2, 5, 5),
                  "vel_x": vel_x, "vel_y": vel_y, "owner": playername}
        self.bullets.append(bullet)

    def update_bullets(self):
        for bullet in list(self.bullets):
            bullet["rect"].x += bullet["vel_x"]
            bullet["rect"].y += bullet["vel_y"]
            pygame.draw.rect(self.screen, (255, 215, 0), bullet["rect"])

            hit = False
            for key, player in list(self.players.items()):
                if key == bullet["owner"]: continue
                player_rect = pygame.Rect(player["x"], player["y"],
                                          player["width"], player["height"])
                if bullet["rect"].colliderect(player_rect):
                    del self.players[key]
                    hit = True
                    break

            for g in self.ground.values():
                ground_rect = pygame.Rect(g["x"], g["y"], g["width"], g["height"])
                if bullet["rect"].colliderect(ground_rect):
                    hit = True
                    break

            if hit or bullet["rect"].x < 0 or bullet["rect"].x > self.WIDTH or \
               bullet["rect"].y < 0 or bullet["rect"].y > self.HEIGHT:
                self.bullets.remove(bullet)

    def FPS(self, fps):
        pygame.display.flip()
        self.clock.tick(fps)

    def loop(self, playername, type="2d", bgcolor=(0,0,0), fps=60):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.gun(playername)

            self.screenfill(bgcolor)
            self.movement(playername, type)
            self.gravity(playername)

            for name in list(self.players.keys()):
                self.gravity(name)
                self.draw_player(name)
                self.whendie(name, x=100, y=300)

            for name in self.ground:
                self.drawground(name)

            self.update_bullets()
            self.FPS(fps)


# --- تشغيل ---
if __name__ == "__main__":
    game = Game()
    game.set_caption("Game with Shooting, Death, and Collision")
    game.create_player("player1", 40, 40, 100, 300, (0,200,0), 5)
    game.create_player("player2", 40, 40, 400, 300, (200,0,0), 5)
    game.create_ground("floor", 350, 0, 600, 50, (100,100,100))
    game.create_ground("block", 250, 200, 80, 30, (150,150,150))
    game.loop("player1")
