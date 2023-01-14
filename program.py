import pygame.font
from pygame import *
import random
import math

vec2, vec3 = pygame.math.Vector2, pygame.math.Vector3
pygame.font.init()
FONT = pygame.font.SysFont('calibry', 50)
RES = WIDTH, HEIGHT = 1600, 900
NUM_STARS = 101
CENTER = vec2(WIDTH // 2, HEIGHT // 2)
COLORS = "red green blue orrange purple cyan".split
Z_DISTANCE = 40


class Menu:
    def __init__(self):
        self.buttons = []
        self.functions = []
        self.current_option = 0

    def append_option(self, option, callback):
        self.buttons.append(FONT.render(option, True, (255, 255, 255)))
        self.functions.append(callback)

    def switch(self, direction):
        self.current_option = max(0, min(self.current_option + direction, len(self.buttons) - 1))

    def select(self):
        if self.current_option == 1:
            switch_scene(stats)
        if self.current_option == 0:
            switch_scene(scene2)
        self.functions[self.current_option]()

    def draw(self, surf, x, y, option):
        for index, opt in enumerate(self.buttons):
            option_rect = opt.get_rect()
            option_rect.topleft = (x, y + index * option)
            if index == self.current_option:
                draw.rect(surf, pygame.Color('green'), option_rect)
            surf.blit(opt, option_rect)


class Star:
    def __init__(self, app):
        self.screen = app.screen
        self.pos3d = self.get_pos3d()
        self.vel = random.uniform(0.05, 0,25)
        self.color = random.choice(COLORS)
        self.screen_pos = vec2(0, 0)
        self.size = 10
        
    def get_pos3d(self, app):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.randrange(HEIGHT)
        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        return vec3(x, y, Z_DISTANCE)
        
    def update(self):
        self.pos3d.z -= self.vel
        self.pos3d = self.get_pos3d() if self.pos3d.z < 1 else self.pos3d
        
        self.screen_pos = vec2(self.pos3d.x, self.pos3d.y) / self.pos3d.z + CENTER

    def draw(self):
        pg.draw.rect(self.screen, self.color, (*self.screen_pos, self.size, self.size))


class Starfild:
    def __init__(self, app):
        self.stars = [Star(app) for i in range(NUM_STARS)]

    def run(self):
        [star.update() for star in self.stars]
        [star.draw() for star in self.stars]


class Wallpaper:
    def __init__(self):
        # self.screen = pygame.display.set_mode(RES)
        self.clock = pygame.time.Clock()
        self.starfild = Starfild(self)

    def run(self, screen):
        screen.fill((0, 0, 0))
        self.starfild.run()
        self.clock.tick()
    

class Game:
    def __init__(self, board, size):
        self.board = Board(board, size)
        self.size = board
        self.screenSize = (800, 800)
        self.pieceSize = (self.screenSize[0] / self.size[1], self.screenSize[1] / self.size[0])
        self.loadImages()
        self.solver = Solver(self.board)

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.screenSize)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN and not(self.board.get_win() or self.board.get_lost()):
                    self.Click(pygame.mouse.get_pos(), pygame.mouse.get_pressed()[2])
                if event.type == pygame.KEYDOWN:
                    self.solver.move()
                self.screen.fill((0, 0 ,0))
                self.draw()
                pygame.display.flip()
                if self.board.get_win():
                    running = False
                    # Over()
        pygame.quit()

    def draw(self):
        point = (0, 0)
        for row in self.board.getBoard():
            for column in row:
                cell = pygame.Rect(point, self.pieceSize)
                image = self.images[self.getImage(column)]
                self.screen.blit(image, point)
                point = point[0] + self.pieceSize[0], point[1]
            point = 0, point[1] + self.pieceSize[0]

    def loadImages(self):
        lst = ['pics/0.png', 'pics/not_e.png', 'pics/bomb.png', 'pics/1.png', 'pics/2.png', 'pics/3.png', 'pics/4.png',
               'pics/5.png', 'pics/6.png', 'pics/7.png', 'pics/8.png']
        lst2 = ['0', 'empty', 'bomb', '1', '2', '3', '4', '5', '6', '7', '8']
        self.images = {}
        for n, pic in enumerate(lst):
            im = pygame.image.load(pic)
            im = pygame.transform.scale(im, (int(self.pieceSize[0]), int(self.pieceSize[1])))
            self.images[lst2[n]] = im

    def getImage(self, cell):
        if cell.click():
            return str(cell.bomb_around()) if not cell.get_bomb() else 'bomb'
        if self.board.get_lost():
            if cell.get_bomb():
                return 'bomb'
            # потом вместо восьмерки флаг должен быть
        return '8' if cell.flag() else 'empty'

    def Click(self, position, flag):
        index = tuple(int(pos // size) for pos, size in zip(position, self.pieceSize))[::-1]
        c = self.board.getCell(index)
        self.board.Click(c, flag)


# создается доска
class Board:
    def __init__(self, size, lot_bombs):
        self.size = size
        self.board = []
        self.win = False
        self.lost = False
        for x in range(size[0]):
            i = []
            for y in range(size[1]):
                bomb = random.random() < lot_bombs
                piece = StateBomb(bomb)
                i.append(piece)
            self.board.append(i)
        self.set_neighbors()
        self.num_around()

    def getCell(self, index):
        return self.board[index[0]][index[1]]

    def getBoard(self):
        return self.board

    def set_neighbors(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                StateBomb = self.board[row][col]
                neighbors = []
                self.add_neighbors(neighbors, row, col)
                StateBomb.set_neighbors(neighbors)

    def add_neighbors(self, neighbors, row, col):
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r == row and c == col:
                    continue
                if r < 0 or r >= self.size[0] or c < 0 or c >= self.size[1]:
                    continue
                neighbors.append(self.board[r][c])

    def Click(self, cell, flag):
        if cell.click() or (not flag and cell.flag()):
            return
        if flag:
            cell.set_flag()
            return
        cell.Click()
        if cell.get_bomb():
            self.lost = True
        else:
            self.win = self.check_win()
        if cell.bomb_around() == 0:
            for n in cell.get_neighbors():
                self.Click(n, False)

    def check_win(self):
        for i in self.board:
            for cell in i:
                if not cell.get_bomb() and not cell.click():
                    return False
        return True

    def get_win(self):
        return self.win

    def get_lost(self):
        return self.lost

    def num_around(self):
        for i in self.board:
            for cell in i:
                cell.num_around()


class StateBomb:
    def __init__(self, bomb):
        self.bomb = bomb
        self.lot_bombs_around = 0
        self.neighbors = []
        self.clicked = False
        self.Flagged = False

    def __str__(self):
        return str(self.bomb)

    def get_bomb(self):
        return self.bomb

    def click(self):
        return self.clicked

    def Click(self):
        self.clicked = True

    def flag(self):
        return self.Flagged

    def bomb_around(self):
        return self.lot_bombs_around

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def get_neighbors(self):
        return self.neighbors

    def num_around(self):
        number = 0
        for neighbor in self.neighbors:
            if neighbor.get_bomb():
                number += 1
        self.lot_bombs_around = number

    def set_flag(self):
        self.Flagged = not self.Flagged


class Solver:
    def __init__(self, board):
        self.board = board

    def move(self):
        for i in self.board.getBoard():
            for cell in i:
                if not cell.click():
                    continue
                around = cell.bomb_around()
                unknown = 0
                flagged = 0
                neighbors = cell.get_neighbors()
                for c in neighbors:
                    if not c.click():
                        unknown += 1
                    if c.flag():
                        flagged += 1
                if around == flagged:
                    self.unflagged(neighbors)
                if around == unknown:
                    self.all_flag(neighbors)

    def unflagged(self, neighbors):
        for cell in neighbors:
            if not cell.flag():
                self.board.Click(cell, False)

    def all_flag(self, neighbors):
        for cell in neighbors:
            if not cell.flag():
                self.board.Click(cell, True)


class Choice(Menu):
    def select(self):
        if self.current_option == 0:
            switch_scene(game((10, 10), 0.1))
        if self.current_option == 1:
            switch_scene(game((15, 15), 0.2))
        if self.current_option == 2:
            switch_scene(game((25, 25), 0.35))
        self.functions[self.current_option]()


class Over(Choice):
    def select(self):
        if self.current_option == 0:
            switch_scene(scene1())
        if self.current_option == 1:
            switch_scene(stats())
        if self.current_option == 2:
            switch_scene(scene2())
        self.functions[self.current_option]()


def switch_scene(scene):
    global current_scene
    current_scene = scene


current_scene = None

menu = Menu()
choice = Choice()
menu.append_option('Новая игра', lambda: print('new game'))
menu.append_option('Статистика игрока', lambda: print('statistic'))
menu.append_option('Выйти', quit)
choice.append_option('Легко', lambda: print('easy'))
choice.append_option('Средне', lambda: print('normal'))
choice.append_option('Сложно', lambda: print('hard'))
# создать бд и читать количесво побед от туда
all_games = FONT.render(f'Всего игр сыграно: {0}', True, (255, 0, 0))
change_str = pygame.font.SysFont('calibry', 30).render(f'клавиши S и W для выбора', True, (255, 255, 255))
cont = pygame.font.SysFont('calibry', 30).render(f'нажмите пробел для выхода', True, (255, 0, 0))
wallpaper = Wallpaper()


def scene1():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption('Сапер')
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                switch_scene(None)
            elif event.type == KEYDOWN:
                if event.key == K_w:
                    menu.switch(-1)
                elif event.key == K_s:
                    menu.switch(1)
                elif event.key == K_SPACE:
                    menu.select()
                    running = False
        wallpaper.run(screen)
        menu.draw(screen, 250, 300, 75)
        screen.blit(change_str, (0, 775))
        pygame.display.flip()
    pygame.quit()


def scene2():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption('Сапер')
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                switch_scene(None)
            elif event.type == KEYDOWN:
                if event.key == K_w:
                    choice.switch(-1)
                elif event.key == K_s:
                    choice.switch(1)
                elif event.key == K_SPACE:
                    choice.select()
                    running = False
        wallpaper.run(screen)
        choice.draw(screen, 250, 300, 75)
        screen.blit(change_str, (0, 775))
        pygame.display.flip()
    pygame.quit()

def stats():
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption('Сапер')
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                switch_scene(None)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
                switch_scene(scene1)
        wallpaper.run(screen)
        draw.rect(screen, (255, 255, 255), (200, 200, 400, 400))
        screen.blit(all_games, (220, 300))
        screen.blit(cont, (220, 350))
        pygame.display.flip()
    pygame.quit()


def game(size, bombs):
    game = Game(size, bombs)
    game.run()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                running = False
                switch_scene(scene1)
    pygame.quit()


switch_scene(scene1)
while current_scene is not None:
    current_scene()
