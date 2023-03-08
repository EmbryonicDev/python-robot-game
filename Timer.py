import random


class Timer:
    def __init__(self):
        self.frame_counter = 0
        self.seconds = 55

    def clear_timer(self):
        self.seconds = random.randint(25, 55)
        self.frame_counter = 0

    def add_counter(self):
        self.frame_counter += 1
        if self.return_on_frame(60):
            self.update_seconds()

    def update_seconds(self):
        self.seconds += 1
        if self.seconds == 73:
            self.clear_timer()

    def return_on_frame(self, divisor):
        if self.frame_counter % divisor == 0:
            return True
