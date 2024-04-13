import pygame as pg
from random import randint
import pyautogui as py
from numba import prange, njit


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
            self.fire.restart_animation(self)

    def draw(self):
        pg.draw.circle(self.surface.sc, self.color, self.pos, self.radius, self.width)


class MouseAnimation:
    def __init__(self, surface, pos, radius, add_for, width=0):
        self.pos = pos
        self.surface = surface
        self.radius = 0
        self.max_radius = radius
        self.add_for = add_for
        self.color = [randint(200, 255), randint(70, 140), 0]
        self.width = width

    def update(self):
        a1, a2 = 0.3, 10
        self.color[1] += a1 if self.color[1] + a1 <= 255 else 0
        self.color[2] += a2 if self.color[2] + a2 <= 255 else 0
        self.radius += self.add_for

        if self.radius >= self.max_radius:
            self.surface.animations.remove(self)

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
        self.smooth = 0.097
        self.air_resistance = 0.9975
        [self.add_obj() for _ in prange(350)]

    def update(self):
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

            if not self.surface.is_pressing:
                self.surface.animations.append(
                    MouseAnimation(self.surface, (x, y),
                                   40,
                                   1, width=1)
                )
                self.surface.is_pressing = not self.surface.is_pressing
        elif self.surface.is_pressing:
            self.surface.is_pressing = not self.surface.is_pressing

        self.pos[0] += self.x_adder * self.smooth
        self.pos[1] += self.y_adder * self.smooth

        # if self.pos[1] >= self.surface.size[1]: #bug
        #     self.pos[1] -= self.surface.size[1] - self.radius - 1

        if not 0 <= self.pos[0] <= self.surface.size[0]:
            self.x_adder *= -1

        if not 0 <= self.pos[1] <= self.surface.size[1]:
            self.y_adder *= -1

    def add_obj(self):
        self.objects.insert(
            0,
            Animation(self.surface, self, self.get_points(*self.pos, self.radius // 3),
                      self.get_radius(self.radius, self.radius // 3),
                      randint(1, 4), width=1)
        )

    def restart_animation(self, animation):
        self.objects.remove(animation)
        self.add_obj()

    def obj_update(self):
        for obj in self.objects:
            obj.update()
            obj.draw()

    @staticmethod
    @njit(fastmath=True)
    def get_radius(r1, r2):
        return r1 + randint(-r2, r2)

    @staticmethod
    @njit(fastmath=True)
    def get_points(x, y, radius):
        x += randint(-int(radius), int(radius))
        y += randint(-int(radius), int(radius))
        return x, y


class App:
    def __init__(self):
        self.size = py.size()#(800, 500)
        self.sc = pg.display.set_mode(self.size)
        self.clock = pg.time.Clock()
        self.fire_radius = 30
        self.fires = tuple(Fire(self, [randint(0, self.size[0]), randint(0, self.size[1])], self.fire_radius,
                           randint(-3, 3), randint(-3, 3), randint(300, 700) / 100)
                           for _ in range(1))
        self.FPS = 220
        self.alpha_surface = pg.Surface(self.size, flags=pg.SRCALPHA)
        self.alpha_surface.fill((0, 0, 0, 35))
        self.animations = []
        self.is_pressing = False

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

            for fire in self.fires:
                fire.update()

            for animation in self.animations:
                animation.update()
                animation.draw()

            pg.display.flip()
            self.clock.tick(self.FPS)
            pg.display.set_caption(str(self.clock.get_fps()))


if __name__ == '__main__':
    App().run()
