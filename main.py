import pygame
import random
import re
import math
from Timer import Timer
from ScreenObjects import ScreenObject, MovingObject, MovingMonster, MovingCoin, BonusCoin, Robot, SaveIcon
from ScoreTrack import Player, HighScores


class GetCoin:
    def __init__(self):
        pygame.init()

        # Window
        self.width = 1000
        self.height = 600
        self.info_board = self.height * 0.14
        self.bonus_board = self.height * 0.14
        self.luck_board = self.height * 0.12
        self.total_height = self.height+self.info_board+self.bonus_board+self.luck_board
        self.window_dimensions = (self.width, self.height)
        self.window = pygame.display.set_mode(
            (self.width, self.total_height))

        # fonts
        self.game_font = pygame.font.SysFont(
            'Arial', math.floor(self.height*0.045))
        self.heading_font = pygame.font.SysFont(
            'Arial', math.floor(self.height*0.085))

        # screen objects / images
        self.door = ScreenObject(self.window_dimensions, 'door')
        self.save_icon = SaveIcon(self.window_dimensions, 'save')
        self.save_icon.update_coords(self.width/2-self.save_icon.width /
                                     2, self.height*.45)

        pygame.display.set_caption('Coin Chaser')
        self.clock = pygame.time.Clock()
        self.new_game()
        self.main_loop()

    def new_game(self):
        self.timer = Timer()
        self.random_color = (random.randint(
            0, 255), random.randint(0, 255), random.randint(0, 255))
        self.game_over = False
        self.game_paused = False
        self.safe_mode = True
        self.level = 1
        self.monster_count = 1
        self.monsters = []
        self.bonus_coin = self.get_bonus_coin()
        self.bot = Robot(self.window_dimensions, 'robot')
        self.player = Player()
        self.high_scores = HighScores()
        self.high_scores.get_new_game_scores()
        self.high_scores.show_high_scores = False
        self.release_coins()
        self.release_monsters()

    def main_loop(self):
        while True:
            self.check_events()
            self.draw_window()
            if not self.game_over and not self.game_paused:
                self.timer.add_counter()
                self.move_coin()
                self.move_bonus_coin()
                self.move_bot()
                self.move_monster()

    def check_events(self):
        key_dict = {
            pygame.K_LEFT: self.bot.toggle_left,
            pygame.K_RIGHT:  self.bot.toggle_right,
            pygame.K_UP:  self.bot.toggle_up,
            pygame.K_DOWN:  self.bot.toggle_down,
            pygame.K_F2:  self.new_game,
            pygame.K_SPACE:  self.toggle_game_over,
            pygame.K_ESCAPE:  exit
        }

        for event in pygame.event.get():
            # handle normal game play & shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key in key_dict:
                    key_dict[event.key]()

            # handle normal game play & shortcuts
            if event.type == pygame.KEYUP:
                if (event.key in key_dict and
                        event.key != pygame.K_SPACE):
                    key_dict[event.key]()

            def submit_score():
                # Remove double spaces, and pre / post white spaces
                self.player.name = re.sub(' +', ' ', self.player.name.strip())
                # only submit name longer than 2 characters
                if len(self.player.name) > 1:
                    self.update_scores(self.player.name)
                    self.high_scores.show_high_scores = True
                    self.player.inputting_name = False

            # handle user input for high score
            if (self.game_over
                    and self.safe_mode
                    and self.high_scores.if_high_score(self.bot.points)
                    ):
                self.player.inputting_name = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if self.save_icon.is_clicked(x, y):
                        submit_score()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.player.pop_name()
                    elif event.key == pygame.K_RETURN:
                        submit_score()

                    else:
                        # append name with user input
                        self.player.update_name(event.dict['unicode'])

            if event.type == pygame.QUIT:
                exit()

    def draw_window(self):
        black = (0, 0, 0)
        white = (255, 255, 255)
        dark_grey = (64, 64, 64)
        red = (255, 0, 0)
        green = (0, 255, 0)
        blue = (0, 0, 255)
        yellow = (255, 255, 0)
        orange = (255, 153, 51)

        # helper functions
        # standard text render
        def get_plain_text(font, text, color):
            return font.render(text, True, color)

        # text render with variable
        def get_text_with_variable(font, text, variable, color: tuple):
            return font.render(
                f"{text}: {variable}", True, color)

        def handle_window_text():
            high_score_color = black
            high_score_bgc = (56, 189, 248)

            def show_scores():
                bold_text = pygame.font.SysFont(
                    'Arial', math.floor(self.height*0.045), bold=True)
                high_score_titles = f"{'{:<20}'.format('Name')}{'{:<9}'.format('Points')}{'{:<8}'.format('Level')}{'{:<9}'.format('Luck')}"
                titles = get_plain_text(
                    bold_text, high_score_titles, high_score_color)
                # text background - high scores
                pygame.draw.rect(self.window, high_score_bgc,
                                 (self.width/2-titles.get_width() / 2-16, self.height*0.2, titles.get_width()+8, self.height*0.75))
                # high score heading
                high_score_heading = get_plain_text(
                    self.heading_font, "High Scores", high_score_color)
                self.window.blit(high_score_heading, (self.width/2-high_score_heading.get_width() /
                                                      2-8, self.height*.2))
                # Line under heading
                pygame.draw.line(self.window, black,
                                 (self.width/2-titles.get_width() /
                                     2-16, self.height*.3+titles.get_height()), (self.width/2-titles.get_width() /
                                                                                 2-16+titles.get_width()+8, self.height*.3+titles.get_height()), 4)
                # high score titles
                self.window.blit(titles, (self.width/2-titles.get_width() /
                                          2, self.height*.3))

                game_text_height_with_padding = self.height*0.3+titles.get_height()+4
                for player in self.high_scores.top_ten_scores:
                    # name
                    game_text = get_plain_text(
                        self.game_font,
                        player.name,
                        high_score_color)
                    self.window.blit(
                        game_text, (self.width/2-titles.get_width() / 2-8, game_text_height_with_padding))
                    # points
                    game_text = get_plain_text(
                        self.game_font,
                        "| "+str(player.points),
                        high_score_color)
                    self.window.blit(
                        game_text, (self.width/2-titles.get_width() / 2-8 + self.width*0.2, game_text_height_with_padding))
                    # level
                    game_text = get_plain_text(
                        self.game_font,
                        "| "+str(player.level),
                        high_score_color)
                    self.window.blit(
                        game_text, (self.width/2-titles.get_width() / 2-8 + self.width*0.3, game_text_height_with_padding))
                    # luck
                    game_text = get_plain_text(
                        self.game_font,
                        "| "+str(player.luck_count['luck'])+'%',
                        high_score_color)
                    self.window.blit(
                        game_text, (self.width/2-titles.get_width() / 2-8 + self.width*0.4, game_text_height_with_padding))
                    game_text_height_with_padding += game_text.get_height() + 4

            # get game over / paused text
            if self.game_over:
                game_text = get_plain_text(
                    self.heading_font, 'Game Over...', white)
            if self.game_paused:
                game_text = get_plain_text(
                    self.heading_font, 'Game Paused...', white)

            if self.game_paused or self.game_over:
                if not self.player.inputting_name:
                    show_scores()
                # text background - game paused / over
                pygame.draw.rect(self.window, dark_grey,
                                 (self.width/2-game_text.get_width() / 2-8, self.height*0.05, game_text.get_width()+8, game_text.get_height()+8))
                # paused / game over text
                self.window.blit(game_text, (self.width/2-game_text.get_width() /
                                             2, self.height*0.05))

            # handle high score user prompt / input
            if (
                self.game_over
                and self.safe_mode
                and self.high_scores.if_high_score(self.bot.points)
            ):
                # high score user prompt text
                game_text = get_plain_text(
                    self.game_font, "High Score! Enter your Name with at least 2 Letters: ", high_score_color)
                game_text2 = get_plain_text(
                    self.heading_font, self.player.name, high_score_color)
                # text background - high score
                pygame.draw.rect(self.window, high_score_bgc,
                                 (self.width/2-game_text.get_width() / 2-8, self.height*0.25, game_text.get_width()+8, (game_text2.get_height()*2)+8))
                # high score user prompt
                self.window.blit(game_text, (self.width/2-game_text.get_width() /
                                             2, self.height*.25))
                # user input
                self.window.blit(game_text2, (self.width/2-game_text2.get_width() /
                                              2, self.height*.25+game_text.get_height()+6))
                # save icon
                self.window.blit(self.save_icon.image,
                                 self.save_icon.footprint)

        def get_dividing_lines():
            # 1st dividing line
            pygame.draw.line(self.window, yellow,
                             (0, self.height), (self.width, self.height), 4)
            # 2nd dividing line
            pygame.draw.line(self.window, yellow,
                             (0, self.height+self.info_board/2), (self.width, self.height+self.info_board/2), 4)
            # 3rd dividing line
            pygame.draw.line(self.window, yellow,
                             (0, self.height+self.bonus_board), (self.width, self.height+self.bonus_board), 4)
            # 4th dividing line
            pygame.draw.line(self.window, yellow,
                             (0, self.total_height-self.luck_board), (self.width, self.total_height-self.luck_board), 4)

        def get_shortcuts():
            # Info board orange rectangle
            pygame.draw.rect(self.window, orange,
                             (0, self.height+3, self.width, self.info_board/2-3))
            # new game
            game_text = get_plain_text(self.game_font, 'New Game', blue)
            self.window.blit(game_text, (25, self.height + 10))
            # pause game
            game_text = get_plain_text(self.game_font, 'Pause - Space', blue)
            self.window.blit(game_text, (self.width*.5-(game_text.get_width()/2),
                                         self.height + 10))
            # quit game
            game_text = get_plain_text(self.game_font, 'Quit - Esc', blue)
            self.window.blit(game_text, (self.width-(game_text.get_width()+25),
                                         self.height + 10))

        def get_bot_info():
            # Info board red rectangle
            pygame.draw.rect(self.window, red,
                             (0, self.height+self.info_board/2+3, self.width, self.info_board/2-3))
            # points
            game_text = get_text_with_variable(self.game_font, 'Points',
                                               self.bot.points, green)
            self.window.blit(
                game_text, (25, self.height + (self.info_board*0.6)))
            # level
            game_text = get_text_with_variable(self.game_font, 'Level',
                                               self.level, green)
            self.window.blit(game_text, (self.width*.5-(game_text.get_width()/2),
                                         self.height + (self.info_board*0.6)))
            # health
            game_text = get_text_with_variable(self.game_font, 'Health',
                                               self.bot.health, green)
            self.window.blit(game_text, (self.width-(game_text.get_width()+25),
                                         self.height + (self.info_board*0.6)))

        def handle_bonus_text():
            # helper function
            def get_color():
                colors = [dark_grey, dark_grey]
                if self.bonus_coin.x > 0 and not self.bonus_coin.caught:
                    colors = [(random.randint(
                        0, 255), random.randint(0, 255), random.randint(0, 255)), black]

                if self.bonus_coin.caught:
                    if self.bonus_coin.power in ['cupcake', 'add health', 'freeze']:
                        colors = [green, blue]
                    else:
                        colors = [red, orange]

                if self.timer.return_on_frame(30):
                    if self.timer.seconds % 2 == 0:
                        self.random_color = colors[0]
                    else:
                        self.random_color = colors[1]

                # make sure rectangle is dark grey before & after bonus
                if (self.game_over or
                    self.timer.seconds <= 60 or
                        self.timer.seconds in [66, 72]):
                    self.random_color = dark_grey

            # bonus board text if ball / bonus state is active
            def blit_text():
                return self.window.blit(game_text, (self.width*.5-(game_text.get_width()/2),
                                                    self.total_height-self.luck_board-self.bonus_board*0.5-game_text.get_height()/2))

            # background rectangle behind bonus board text with padding
            def blit_text_bg():
                return pygame.draw.rect(self.window, black,
                                        (self.width/2-game_text.get_width()/2-8,
                                         self.total_height-self.luck_board-self.bonus_board*0.5-game_text.get_height() /
                                         2-8,
                                         game_text.get_width()+16,
                                         game_text.get_height()+8))

            get_color()
            # Info board rectangle
            pygame.draw.rect(self.window, (self.random_color),
                             (0, self.height+self.info_board+3, self.width, self.bonus_board-3))

            # bonus record text
            line_one_height = self.total_height - self.bonus_board-self.luck_board + 10
            line_two_height = line_one_height+40
            # text when no ball / no active bonus
            if ((self.bonus_coin.x < 0 and
                not self.bonus_coin.caught) or
                    self.game_over):
                # freeze count
                game_text = get_text_with_variable(
                    self.game_font, 'Freeze', self.player.bonus_record['freeze'], (0, 255, 0))
                self.window.blit(
                    game_text, (25, line_one_height))
                # cupcake count
                game_text = get_text_with_variable(
                    self.game_font, 'Cupcakes', self.player.bonus_record['cupcake'], (0, 255, 0))
                self.window.blit(
                    game_text, (self.width*.5-(game_text.get_width()/2), line_one_height))
                # add health count
                game_text = get_text_with_variable(
                    self.game_font, '+ Health', self.player.bonus_record['add health'], (0, 255, 0))
                self.window.blit(
                    game_text, (self.width-(game_text.get_width()+25),
                                line_one_height))
                # speed count
                game_text = get_text_with_variable(
                    self.game_font, 'Fast', self.player.bonus_record['speed up'], red)
                self.window.blit(
                    game_text, (25, line_two_height))
                # add monsters count
                game_text = get_text_with_variable(
                    self.game_font, '+ Monsters', self.player.bonus_record['add monsters'], red)
                self.window.blit(
                    game_text, (self.width*.5-(game_text.get_width()/2), line_two_height))
                # take health count
                game_text = get_text_with_variable(
                    self.game_font, '- Health', self.player.bonus_record['take health'], red)
                self.window.blit(
                    game_text, (self.width-(game_text.get_width()+25),
                                line_two_height))

            # text when ball is on screen
            game_text = get_plain_text(
                self.heading_font, 'Trick or Treat???', white)

            # if bonus ball is on screen, prompt user to catch it
            if self.bonus_coin.x > -1:
                if not self.game_over:
                    # rectangle behind bonus text
                    blit_text_bg()
                    # game text to window
                    blit_text()

            # display user prompt based on bonus_coin.power
            if self.bonus_coin.caught:
                game_text = get_plain_text(
                    self.heading_font, self.bonus_coin.user_prompt, white)
                if not self.game_over:
                    blit_text_bg()
                    blit_text()

        def handle_luck_board():
            # luck board dark grey rectangle
            pygame.draw.rect(self.window, dark_grey,
                             (0, self.total_height-self.luck_board, self.width, self.luck_board))

            if self.player.luck_count['total count'] > 0:
                # green rect for good luck
                pygame.draw.rect(self.window, green,
                                 (0, self.total_height-self.luck_board+2, self.width*self.player.luck_count['good percentage']/100, self.luck_board+2))
                # red rect for bad luck
                pygame.draw.rect(self.window, red,
                                 (self.width*self.player.luck_count['good percentage']/100, self.total_height-self.luck_board+2, self.width, self.luck_board))

                # luck board text - You are xx% [lucky / unlucky]
                game_text = self.game_font.render(
                    f"You are {int(self.player.luck_count['luck'])}% {self.player.luck_count['word']}!!", True, white)

                # text background with padding
                pygame.draw.rect(self.window, dark_grey,
                                 (self.width/2-game_text.get_width() / 2-8,
                                  self.total_height-self.luck_board*.5 -
                                  game_text.get_height()/2-8,
                                  game_text.get_width()+8,
                                  game_text.get_height()+16))
                # text
                self.window.blit(game_text, (self.width/2-game_text.get_width() /
                                             2, self.total_height-self.luck_board*.5-game_text.get_height()/2))

        def handle_door():
            if all(i.caught == True for i in self.coins):
                if self.door.x < 0:
                    self.door.toggle_visibility()
                    self.door.get_coords(self.bot.y)
            else:
                if self.door.x >= 0:
                    self.door.toggle_visibility()
            self.window.blit(self.door.image, (self.door.x, self.door.y))

        def handle_bonus_ball():
            # helper functions
            def add_health():
                if self.timer.return_on_frame(70):
                    self.bot.add_health()

            def speed_up_monsters():
                for monster in self.monsters:
                    monster.speed_up()

            def toggle_cupcake(cupcake=True):
                for monster in self.monsters:
                    monster.toggle_cupcake(cupcake)

            def add_extra_monsters():
                if self.timer.return_on_frame(70):
                    self.monster_count += 1
                    self.release_monsters()

            def update_luck(type_of_luck: str):
                self.player.update_luck(type_of_luck)

            # bonus coin to screen
            if self.timer.seconds == 60:
                self.bonus_coin.toggle_visibility()
                self.bonus_coin.get_coords(self.bot.y)
                self.bonus_coin.unfreeze()
                self.timer.update_seconds()

            # bonus coin with no contact
            if (self.timer.seconds == 66 and
                    not self.bonus_coin.caught):
                self.timer.update_seconds()
                self.bonus_coin = self.get_bonus_coin()

            # bonus coin caught by Robot
            if self.bonus_coin.hit_robot(self.bot.footprint):
                update_luck(self.bonus_coin.dict['luck'])
                # Hide coin when caught
                self.bonus_coin.catch_coin()
                self.bonus_coin.toggle_visibility()
                self.player.update_bonus_record(
                    self.bonus_coin.power)
                self.timer.seconds = 66

            # if coin is caught
            if self.bonus_coin.caught:
                power_dict = {
                    'freeze': self.freeze_monsters,
                    'speed up': speed_up_monsters,
                    'cupcake': toggle_cupcake,
                    'add monsters': add_extra_monsters,
                    'add health': add_health,
                    'take health': self.take_health,
                }
                # activate bonus ball power
                if self.bonus_coin.power in power_dict:
                    power_dict[self.bonus_coin.power]()

                # end bonus round
                if self.timer.seconds == 72:
                    self.timer.clear_timer()
                    self.unfreeze_monsters()
                    toggle_cupcake(False)
                    self.bonus_coin = self.get_bonus_coin()

            # bonus coin to window
            self.window.blit(self.bonus_coin.image,
                             (self.bonus_coin.x, self.bonus_coin.y))

        # game window will be red to warn that bonus mode will end
        window_color = (self.bonus_coin.dict['color'] if self.bonus_coin.caught
                        and self.timer.seconds == 71
                        else (204, 255, 255))

        self.window.fill(window_color)
        handle_luck_board()

        # Info board text
        get_shortcuts()
        get_bot_info()

        # bonus mode info board
        handle_bonus_text()

        # print door
        handle_door()

        # coins
        for coin in self.coins:
            self.window.blit(coin.image, (coin.x, coin.y))

        # bonus coin
        handle_bonus_ball()

        # dividing lines
        get_dividing_lines()

        # monsters
        for monster in self.monsters:
            self.window.blit(monster.image, (monster.x, monster.y))

        # bot
        self.window.blit(self.bot.image, (self.bot.x, self.bot.y))

        # main window text
        handle_window_text()

        pygame.display.flip()
        self.clock.tick(60)

    def move_bot(self):
        # End game when score hits 0
        if self.bot.health < 1:
            self.bot.health = 0
            self.game_over = True

        self.bot.move_bot()

        if (self.bot.hit_door(self.door.footprint) and
            all(i.caught == True for i in self.coins)
            ):
            self.level += 1
            self.monster_count += 1
            self.release_coins()
            self.door.get_coords(self.bot.y)
            self.bot.reset_pos()
            self.release_monsters()

    def move_coin(self):
        for coin in self.coins:
            coin.move_object()
            # Coin hits robot & adds point
            if coin.hit_robot(self.bot.footprint):
                self.bot.add_point()
                coin.catch_coin()
                coin.toggle_visibility()

    def move_monster(self):
        for monster in self.monsters:
            monster.move_object()

            if monster.hit_robot(self.bot.footprint):
                # if cupcake BonusCoin was caught, make them edible
                if self.bonus_coin.caught and self.bonus_coin.power == 'cupcake':
                    monster.toggle_visibility()
                    monster.freeze()
                    self.monster_count -= 1
                else:
                    self.bot.take_health()
                    self.release_monsters()

    def take_health(self):
        if self.timer.return_on_frame(70):
            for i in range(2):
                self.bot.take_health()

    def freeze_monsters(self):
        for monster in self.monsters:
            monster.freeze()

    def unfreeze_monsters(self):
        for monster in self.monsters:
            monster.unfreeze()

    def move_bonus_coin(self):
        self.bonus_coin.move_object()

    def get_bonus_coin(self):
        return BonusCoin(
            self.window_dimensions, 'bonus_coin')

    def toggle_game_over(self):
        if not self.game_over:
            self.game_paused = False if self.game_paused else True

    def release_coins(self):
        self.coins = []
        for i in range(6):
            new_coin = MovingCoin(self.window_dimensions, 'coin')
            new_coin.get_coords(self.height)
            self.coins.append(new_coin)

    def release_monsters(self):
        self.monsters = []
        bot_y = self.bot.y
        for i in range(self.monster_count):
            monster = MovingMonster(self.window_dimensions, 'monster')
            monster.get_coords(bot_y)
            self.monsters.append(monster)

        # release frozen monsters if bonus_coin was caught
        if (self.bonus_coin.caught and
                self.bonus_coin.power == 'freeze'):
            self.freeze_monsters()

    def update_scores(self, player_name):
        self.player.update_player(
            self.bot.points, self.level, self.player.luck_count['good percentage'])
        self.high_scores.update_scores(self.player)
        self.safe_mode = False
        self.high_scores.show_high_scores = True


if __name__ == '__main__':
    GetCoin()
