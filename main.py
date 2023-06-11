import math
import sys

import pygame as pg
import random as r

PLANTS_TEXTURES = {
    80: pg.image.load('sprites/grass.png'),
    7: pg.image.load('sprites/kolos.png'),
    6: pg.image.load('sprites/clever.png'),
    4: pg.image.load('sprites/flower_1.png'),
    3: pg.image.load('sprites/flower_2.png'),
    1: pg.image.load('sprites/clever_lucky.png'),
}

FOOD_TEXTURES = {
    40: pg.image.load('sprites/apple_red.png'),
    30: pg.image.load('sprites/apple_green.png'),
    20: pg.image.load('sprites/musgroom.png'),
    10: pg.image.load('sprites/blueberry.png'),
}

EZH_TEXTURE = pg.image.load('sprites/ezhik.png')
ATTENTION_TEXTURE = pg.image.load('sprites/attention.png')

TEXTURE_SIZE = 64
SCALE = [16, 9]
INDEXES = [(x, y) for x in range(SCALE[0]) for y in range(SCALE[1])]

_WIDTH = SCALE[0] * TEXTURE_SIZE
_HEIGHT = SCALE[1] * TEXTURE_SIZE

ezh_count = None
food_count = None


class Plant:
    def __init__(self, pos):
        self.texture = r.choices(list(PLANTS_TEXTURES.values()), weights=list(PLANTS_TEXTURES.keys()))[0]
        self.pos = pos
        self.pos_xy = (pos[0] * TEXTURE_SIZE, pos[1] * TEXTURE_SIZE)

    def draw(self, screen):
        screen.blit(self.texture, self.pos_xy)


class Food:
    def __init__(self, pos):
        self.texture = r.choices(list(FOOD_TEXTURES.values()), weights=list(FOOD_TEXTURES.keys()))[0]
        self.pos = pos
        self.pos_xy = (pos[0] * TEXTURE_SIZE, pos[1] * TEXTURE_SIZE)

    def draw(self, screen):
        # Отрисовка объекта на экране в позиции self.pos
        screen.blit(self.texture, self.pos_xy)


class Ezh:
    def __init__(self, pos):
        self.pos = pos
        self.pos_xy = None
        self.texture = EZH_TEXTURE

        self.extra_pos = None
        self.extra_pos_xy = None
        self.extra_texture = None

        self.target = None
        self.skip = False
        self.left = True
        self.update()

    def update(self):
        self.pos_xy = (self.pos[0] * TEXTURE_SIZE, self.pos[1] * TEXTURE_SIZE)
        self.extra_pos = (self.pos[0], self.pos[1] - 1)
        self.extra_pos_xy = (self.extra_pos[0] * TEXTURE_SIZE, self.extra_pos[1] * TEXTURE_SIZE)

    def draw(self, screen):
        screen.blit(self.texture, self.pos_xy)
        if self.extra_texture is not None:
            screen.blit(self.extra_texture, self.extra_pos_xy)

    def check_pos(self):
        return [(x, y) for x in range(self.pos[0] - 1, self.pos[0] + 2, 1) for y in
                range(self.pos[1] - 1, self.pos[1] + 2, 1)
                if (x, y) in INDEXES and self.pos != (x, y)]

    def texture_modify(self, next_step):
        if next_step[0] > self.pos[0] and self.left:
            self.texture = pg.transform.flip(self.texture, True, False)
            self.left = False
        if next_step[0] < self.pos[0] and not self.left:
            self.texture = pg.transform.flip(self.texture, True, False)
            self.left = True

    def random_step(self, targets):
        next_step = r.choice(targets)
        self.texture_modify(next_step)
        self.pos = next_step
        self.update()

    def go_to_target(self):
        min_distance = None
        nearest_coord = None

        for c in self.check_pos():
            distance = math.sqrt((c[0] - self.target[0]) ** 2 + (c[1] - self.target[1]) ** 2)
            if min_distance is None or distance < min_distance:
                min_distance = distance
                nearest_coord = c
        self.texture_modify(nearest_coord)
        self.pos = nearest_coord
        self.update()


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((_WIDTH, _HEIGHT))
        self.clock = pg.time.Clock()

        self.plants = []
        for ind in INDEXES:
            self.plants.append(Plant(ind))

        plant_indices_to_replace = r.sample(INDEXES, food_count)  # Выбор 4 уникальных индексов для замены
        for i in plant_indices_to_replace:
            self.plants[INDEXES.index(i)] = Food(self.plants[INDEXES.index(i)].pos)

        self.ezhs = []
        for _ in range(ezh_count):
            ezh = Ezh((0, 0))
            self.ezhs.append(ezh)

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            # Очистка экрана
            self.screen.fill((255, 255, 255))

            for ezh in self.ezhs:
                if ezh.skip:
                    ezh.skip = False
                elif ezh.target is not None:
                    if ezh.target != (0, 0):
                        ezh.go_to_target()
                        ezh.extra_texture = self.plants[INDEXES.index(ezh.target)].texture
                        self.plants[INDEXES.index(ezh.target)] = Plant(ezh.target)
                        ezh.target = (0, 0)
                    else:
                        if ezh.pos != ezh.target:
                            ezh.go_to_target()
                        else:
                            ezh.extra_texture = None
                            ezh.target = None
                            potencial_food_place = r.sample(INDEXES, food_count)
                            for fp in potencial_food_place:
                                if type(self.plants[INDEXES.index(fp)]) != Food:
                                    self.plants[INDEXES.index(fp)] = Food(self.plants[INDEXES.index(fp)].pos)
                                    break
                else:
                    targets = ezh.check_pos()
                    for target in targets:
                        if type(self.plants[INDEXES.index(target)]) == Food:
                            ezh.extra_texture = ATTENTION_TEXTURE
                            ezh.skip = True
                            ezh.target = target
                    if not ezh.skip:
                        ezh.random_step(targets)
                ezh.draw(self.screen)

            for plant in self.plants:
                draw = True
                for ezh in self.ezhs:
                    if plant.pos == ezh.pos:
                        draw = False
                    elif ezh.extra_pos == plant.pos and ezh.extra_texture is not None:
                        draw = False

                if draw:
                    plant.draw(self.screen)

            pg.display.flip()
            self.clock.tick(1)


if __name__ == "__main__":
    while ezh_count is None:
        ezh_count = int(input('Количество ежей? (от 1 до 10)\n'))
        if ezh_count > 10 or ezh_count < 1:
            print(f'{ezh_count} Вне диапазона!')
            ezh_count = None
    while food_count is None:
        food_count = int(input('Количество еды? (от 2 до 20)\n'))
        if food_count > 20 or food_count < 2:
            print(f'{food_count} Вне диапазона!')
            food_count = None
    pg.init()
    game = Game()
    game.run()
