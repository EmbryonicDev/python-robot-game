import random
import pygame


class ScreenObject:
    def __init__(self, screen_dimensions: list, image: str):
        self.image = self.get_image(image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.screen_width = screen_dimensions[0]
        self.screen_height = screen_dimensions[1]
        self.x = random.randint(self.width, self.screen_width - self.width)
        self.y = random.randint(
            self.height, self.screen_height - (100+self.height))
        self.footprint = self.image.get_rect(x=self.x, y=self.y)

    def toggle_visibility(self):
        self.x *= -1
        self.y *= -1

    # release objects on opposite side of bot on contact
    def get_coords(self, bot_y: str):
        self.x = random.randint(self.width, self.screen_width-self.width)
        self.y = (random.randint(self.height, self.screen_height*0.25)
                  if bot_y > self.screen_height / 2
                  else random.randint(self.screen_height*0.75,
                                      self.screen_height-self.height))
        self.update_footprint()

    def update_footprint(self):
        self.footprint = self.image.get_rect(x=self.x, y=self.y)

    def get_image(self, image: str):
        return pygame.image.load(image+'.png')


class SaveIcon(ScreenObject):
    def __init__(self, screen_dimensions: list, image: str):
        ScreenObject.__init__(self, screen_dimensions, image)

    def update_coords(self, x, y):
        self.x, self.y = x, y
        self.update_footprint()

    def is_clicked(self, x, y):
        return self.footprint.collidepoint(x, y)


class MovingObject(ScreenObject):
    def __init__(self, screen_dimensions: list, image: str):
        ScreenObject.__init__(self, screen_dimensions, image)
        self.choices = [-7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7]
        self.x_speed = random.choice(self.choices)
        self.y_speed = random.choice(self.choices)

    def move_object(self):
        if self.x <= 0 or self.x + self.width >= self.screen_width:
            self.x_speed *= -1
        if self.y <= 0 or self.y + self.height >= self.screen_height:
            self.y_speed *= -1

        self.x += self.x_speed
        self.y += self.y_speed

        self.update_footprint()

    def hit_robot(self, bot_footprint):
        return self.footprint.colliderect(bot_footprint)

    def freeze(self):
        self.x_speed, self.y_speed = 0, 0

    def unfreeze(self):
        self.x_speed, self.y_speed = random.choice(
            self.choices), random.choice(self.choices)


class MovingMonster(MovingObject):
    def __init__(self, screen_dimensions: list, image: str):
        MovingObject.__init__(self, screen_dimensions, image)

    def speed_up(self):
        self.x_speed = 14 if self.x_speed > 0 else -14
        self.y_speed = 14 if self.y_speed > 0 else -14

    def toggle_cupcake(self, cupcake: bool):
        self.image = self.get_image('cupcake' if cupcake else 'monster')


class MovingCoin(MovingObject):
    def __init__(self, screen_dimensions, image):
        MovingObject.__init__(self, screen_dimensions, image)
        self.caught = False

    def catch_coin(self):
        self.caught = True


class BonusCoin(MovingCoin):
    def __init__(self, screen_dimensions: list, image: str):
        MovingCoin.__init__(self, screen_dimensions, image)

        self.freeze()
        self.toggle_visibility()
        self.dict = random.choice([
            {'power': 'freeze', 'user_prompt': 'Ghosts are Frozen',
                'color': (255, 0, 0), 'luck': 'good'},
            {'power': 'speed up',
                'user_prompt': 'Super Fast Ghosts! Be Careful!', 'color': (0, 255, 0), 'luck': 'bad'},
            {'power': 'cupcake', 'user_prompt': 'Eat the Cupcakes!',
                'color': (255, 0, 0), 'luck': 'good'},
            {'power': 'add monsters',
                'user_prompt': 'Adding 5 Monsters', 'color': (0, 255, 0), 'luck': 'bad'},
            {'power': 'add health', 'user_prompt': 'Adding 10 Health Points',
                'color': (255, 0, 0), 'luck': 'good'},
            {'power': 'take health',
                'user_prompt': 'Taking 10 Health Points', 'color': (0, 255, 0), 'luck': 'bad'},
        ])
        self.power = self.dict['power']
        self.user_prompt = self.dict['user_prompt']


class Robot(ScreenObject):
    def __init__(self, screen_dimensions, image):
        ScreenObject.__init__(self, screen_dimensions, image)
        self.health = 100
        self.speed = 8
        self.points = 0
        self.to_left = False
        self.to_right = False
        self.to_up = False
        self.to_down = False
        self.reset_pos()

    def reset_pos(self):
        self.x = 0
        self.y = self.screen_height - self.height

    def add_point(self):
        self.points += 1

    def take_health(self):
        self.health -= 1

    def add_health(self):
        self.health += 2

    def toggle_left(self):
        self.to_left = False if self.to_left else True

    def toggle_right(self):
        self.to_right = False if self.to_right else True

    def toggle_up(self):
        self.to_up = False if self.to_up else True

    def toggle_down(self):
        self.to_down = False if self.to_down else True

    def move_bot(self):
        if self.to_right and self.x <= self.screen_width - self.width:
            self.x += self.speed
        if self.to_left and self.x >= 0:
            self.x -= self.speed
        if self.to_down and self.y <= self.screen_height - self.height:
            self.y += self.speed
        if self.to_up and self.y >= 0:
            self.y -= self.speed

        self.update_footprint()

    def hit_door(self, door_footprint):
        return self.footprint.colliderect(door_footprint)
