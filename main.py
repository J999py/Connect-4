# Imports

import sys
import pygame
import numpy as np
# from pygame import mixer

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, button_img):
        super().__init__()
        button_img = pygame.image.load(button_img).convert_alpha()
        self.image = button_img
        self.rect = self.image.get_rect(topleft=(x, y))

    def player_input(self):
        mouse_point = pygame.mouse.get_pos()
        button_click = pygame.mouse.get_pressed()[0]
        global game_active
        global game_active_but_completed
        if pygame.Rect.collidepoint(self.rect, mouse_point) and button_click:
            pygame.time.wait(200)
            game_active = True

    def update(self):
        self.player_input()

class Board:
    def __init__(self):
        self.chip_pos = np.zeros((6, 7), dtype=np.int8)
        self.turn = 1
        self.turn_count = 0
        self.x = 0
        self.y = 0

    def game_turn(self, x, y, color):
        self.x = x
        self.y = y
        self.chip_pos[y, x] = color

        if self.turn == 1:
            self.turn = 2
            global blue_chip_group
            blue_chip_group.add(Chips(-100, -100, board_coord, 2))

        elif self.turn == 2:
            self.turn = 1
            global red_chip_group
            red_chip_group.add(Chips(-100, -100, board_coord, 1))

    def clear(self):
        self.chip_pos = np.zeros((6, 7), dtype=np.int8)


class Chips(pygame.sprite.Sprite):
    def __init__(self, x, y, board, color):
        super().__init__()
        self.color = color
        if self.color == 1:
            self.image = pygame.image.load('Red Chip.png')
        else:
            self.image = pygame.image.load('Blue Chip.png')

        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y
        self.board = board
        self.coin_placed = False

    def chip_hover(self):
        if not check_win()[0]:
            self.x = pygame.mouse.get_pos()[0]
            if self.x <= 226 + 35:
                self.x = 226 + 35
            elif self.x >= 765:
                self.x = 765
            self.y = 40
            self.rect.center = self.x, self.y

    def chip_drop(self):
        if pygame.mouse.get_pressed()[0] and not self.coin_placed and not check_win()[0]:
            # Loop to iterate through all the possible valid clicks
            for i in range(7):
                global game_board
                global chip_centre_positions
                x_left = 226 + 70 * i + i * 14
                x_right = 226 + 70 * (i + 1) + i * 14
                if x_left <= pygame.mouse.get_pos()[0] <= x_right:
                    self.x = x_left + 35

                    # Checks if there are any chips already placed and decides index and y position based on that
                    chips = game_board.chip_pos.transpose()
                    flipped_column = np.flip(chips[i])
                    for j in range(6):
                        if flipped_column[j] == 0:
                            y_index = 5 - j
                            self.y = 35 + 81 + 7 + 70 * (5 - j) + (5 - j) * 14
                            break

                    # This is if the column is full
                    if 0 not in flipped_column:
                        break
                    x_index = i
                    game_board.game_turn(x_index, y_index, self.color)
                    self.coin_placed = True
                    self.rect.center = self.x, self.y
                    pygame.time.wait(200)

        if self.coin_placed or check_win()[0]:
            self.rect.center = self.x, self.y

    def update(self):
        if not self.coin_placed:
            self.chip_hover()
        self.chip_drop()

def draw_circles_on_board():
    chip_positions = []
    for r in range(7):
        chip_positions.append([])
        for c in range(6):
            chip_positions[r].append([])

    for i in range(7):
        x = 226 + 35 + 70 * i + i * 14
        for j in range(6):
            y = 35 + 81 + 7 + 70 * j + j * 14
            pygame.draw.circle(screen, (0, 0, 0), (x, y), 35)
            chip_positions[i][j].append(x)
            chip_positions[i][j].append(y)
    return chip_positions

def list_win_check(win_list):
    """ Takes a list of length greater than equal to 4 and
    checks if there are 4 1's or 2's in a row and returns a bool"""
    if len(win_list) >= 4:
        bool_list = []
        for i in range(len(win_list) - 3):
            check_list = []
            for j in range(4):
                check_list.append(win_list[j + i])
            if check_list == [1, 1, 1, 1] or check_list == [2, 2, 2, 2]:
                bool_list.append(True)
            else:
                bool_list.append(False)

        return True in bool_list

    else:
        return False

def check_win():
    global game_board
    chips_grid = game_board.chip_pos

    # Vertical test
    flipped_grid = chips_grid.transpose()
    win_check_y = list_win_check(flipped_grid[game_board.x])

    # Horizontal test
    win_check_x = list_win_check(chips_grid[game_board.y])

    # Diagonal test (Bottom Left to Top Right)
    [x, y] = [game_board.x, game_board.y]
    while x > 0 and y < 5:
        [x, y] = [x - 1, y + 1]
    diagonal_list = [chips_grid[y][x]]
    while x < 6 and y > 0:
        [x, y] = [x + 1, y - 1]
        diagonal_list.append(chips_grid[y][x])

    win_check_dg1 = list_win_check(diagonal_list)

    # Diagonal test (Top Left to Bottom Right)
    [x, y] = [game_board.x, game_board.y]
    while x < 6 and y < 5:
        [x, y] = [x + 1, y + 1]
    diagonal_list = [chips_grid[y][x]]
    while x > 0 and y > 0:
        [x, y] = [x - 1, y - 1]
        diagonal_list.append(chips_grid[y][x])

    win_check_dg2 = list_win_check(diagonal_list)

    draw_checklist = []
    for i in range(6):
        draw_checklist.append(0 not in chips_grid[i])
    draw = False not in draw_checklist

    return [win_check_x or win_check_y or win_check_dg1 or win_check_dg2 or draw, x, y, draw]

def title_screen():
    screen.blit(background, (0, 0))

def exit_button():
    pygame.draw.rect(screen, (255, 0, 0), return_rect, 0, 5)
    screen.blit(return_text, return_rect)
    return pygame.Rect.collidepoint(return_rect, pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]


# Configuration
pygame.init()
fps = 144
fpsClock = pygame.time.Clock()
width, height = 1040, 585

# Start Screen Setup
screen = pygame.display.set_mode((width, height))
background = pygame.image.load('connect4_bg.png')

# Caption
pygame.display.set_caption("Connect 4")
icon = pygame.image.load('connect4_icon.png')
pygame.display.set_icon(icon)

# Setting the game state
game_state = True
game_active = False
game_active_but_completed = False

# Button on intro page and return to menu page
font = pygame.font.Font('freesansbold.ttf', 32)

play_button = pygame.sprite.GroupSingle()
play_button.add(Button(758, 292, 'Play_button.png'))

return_text = font.render('Return to Main Menu', True, (255, 255, 255))
return_rect = return_text.get_rect()

# Blue won
text_blue = font.render('GAME OVER BLUE WON', True, (0, 255, 0))
rect_blue = text_blue.get_rect()
rect_blue.center = (520, 50)

# Red won
text_red = font.render('GAME OVER RED WON', True, (0, 255, 0))
rect_red = text_blue.get_rect()
rect_red.center = (520, 50)

# Draw
text_draw = font.render("It's a draw!", True, (0, 255, 0))
rect_draw = text_blue.get_rect()
rect_draw.center = (620, 50)

# Initialising the Board and the Chips
chip_centre_positions = draw_circles_on_board()
game_board = Board()
board_coord = game_board.chip_pos
red_chip_group = pygame.sprite.Group()
blue_chip_group = pygame.sprite.Group()

red_chip_group.add(Chips(-100, -100, board_coord, 1))

while game_state:
    fpsClock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state = False

    if game_active:
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, '#e7d66e', ((219, 81), (585, 504)))
        draw_circles_on_board()

        if game_board.turn == 1:
            red_chip_group.draw(screen)
            blue_chip_group.draw(screen)
            red_chip_group.update()

        elif game_board.turn == 2:
            blue_chip_group.draw(screen)
            red_chip_group.draw(screen)
            blue_chip_group.update()

        if check_win()[0]:
            if game_active_but_completed:
                game_board.clear()
                red_chip_group.empty()
                blue_chip_group.empty()
                game_active = False

                chip_centre_positions = draw_circles_on_board()
                game_board = Board()
                board_coord = game_board.chip_pos
                red_chip_group = pygame.sprite.Group()
                blue_chip_group = pygame.sprite.Group()
                red_chip_group.add(Chips(-100, -100, board_coord, 1))

            draw = check_win()[3]
            if draw:
                screen.blit(text_draw, rect_draw)
            if game_board.turn == 1 and not draw:
                screen.blit(text_blue, rect_blue)
            elif game_board.turn == 2 and not draw:
                screen.blit(text_red, rect_red)

                game_active_but_completed = exit_button()

    else:
        title_screen()
        play_button.draw(screen)
        play_button.update()

    pygame.display.update()
    pygame.display.flip()
