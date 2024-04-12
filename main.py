import pygame as pg
from random import randint
import pyautogui as py


class Animation:
    def __init__(self, surface, fire, pos, radius, minus_for, width=0):
        self.pos = pos
        self.fire = fire
        self.surface = surface
        self.radius = radius
        self.minus_for = minus_for
        self.color = [randint(200, 255), randint(70, 140), 0]
        self.width = width

    def update(self):
        a1, a2 = 0.51, 5
        self.color[1] += a1 if self.color[1] + a1 <= 255 else 0
        self.color[2] += a2 if self.color[2] + a2 <= 255 else 0
        self.radius -= self.minus_for

        if self.radius <= 0:
            self.fire.objects.remove(self)
    
    def draw(self):
        pg.draw.circle(self.surface.sc, self.color, self.pos, self.radius, self.width)


class Fire:
    def __init__(self, surface, pos, radius, x_adder, y_adder, g):
        self.surface = surface
        self.pos = pos
        self.radius = radius
        self.objects = []
        self.speed = randint(1, 5)
        self.x_adder = x_adder
        self.y_adder = y_adder
        self.g = g
        self.smooth = 0.1
        self.air_resistance = 0.997

    def update(self):
        self.add_objs()
        self.obj_update()
        self.move()

    def move(self):
        self.y_adder *= self.air_resistance
        self.y_adder += self.g * self.smooth
        self.x_adder *= self.air_resistance

        if any(pg.mouse.get_pressed()):
            x, y = pg.mouse.get_pos()
            x1, y1 = self.pos
            self.x_adder = x - x1
            self.y_adder = y - y1

        self.pos[0] += self.x_adder * self.smooth
        self.pos[1] += self.y_adder * self.smooth

        if not 0 <= self.pos[0] <= self.surface.size[0]:
            self.x_adder *= -1

        if not 0 <= self.pos[1] <= self.surface.size[1]:
            self.y_adder *= -1

    def add_objs(self):
        for i in range(35):
            self.objects.append(
                Animation(self.surface, self, self.get_points(self.radius // 3), self.get_radius(self.radius // 3),
                          randint(1, 4), width=1)
            )

    def obj_update(self):
        i = 0
        while i < len(self.objects):
            self.objects[i].update()
            self.objects[i].draw()
            i += 1

    def draw(self):
        # pg.draw.circle(self.surface.sc, (255, 90, 0), self.pos, self.radius, 1)
        i = len(self.objects) - 1
        while i >= 0:
            self.objects[i].draw()
            i -= 1

    def get_radius(self, radius):
        return self.radius + randint(-int(radius), int(radius))

    def get_points(self, radius):
        x = self.pos[0] + randint(-int(radius), int(radius))
        y = self.pos[1] + randint(-int(radius), int(radius))

        return x, y


class App:
    def __init__(self):
        self.size = py.size()#(800, 500)
        self.sc = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.bg = (0, 0, 0)
        self.fire_radius = 30
        self.fires = tuple(Fire(self, [randint(0, self.size[0]), randint(0, self.size[1])], self.fire_radius,
                           randint(-3, 3), randint(-3, 3), randint(3, 7))
                           for _ in range(1))
        self.fire_length = len(self.fires)
        self.FPS = 220
        self.alpha_surface = pg.Surface(self.size, flags=pg.SRCALPHA)
        self.alpha_surface.fill((0, 0, 0, 35))

    def run(self):
        pg.init()

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_q:
                        exit()

            self.sc.blit(self.alpha_surface, (0, 0))
            i = 0
            while i < self.fire_length:
                self.fires[i].update()
                self.fires[i].draw()

                i += 1

            pg.display.flip()
            self.clock.tick(self.FPS)
            pg.display.set_caption(str(self.clock.get_fps()))


if __name__ == '__main__':
    App().run()
