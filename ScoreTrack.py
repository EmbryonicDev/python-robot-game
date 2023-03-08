class Player:
    def __init__(self):
        self.name = ""
        self.points = 0
        self.level = 0
        self.inputting_name = False
        self.bonus_record = {'freeze': 0, 'speed up': 0, 'cupcake': 0,
                             'add monsters': 0, 'add health': 0, 'take health': 0}
        self.luck_count = {'good': 0, 'bad': 0, 'total count': 0,
                           'good percentage': 0, 'bad percentage': 0,
                           'word': 'Lucky', 'luck': 0}

    def update_player(self, points, level, luck):
        self.points, self.level, self.luck_count['luck'] = int(
            points), int(level), luck

    def set_name(self, name):
        self.name = name

    def update_name(self, char):
        if len(self.name) < 12:
            self.name += char

    def pop_name(self):
        if len(self.name) > 0:
            self.name = self.name[:-1]

    def update_luck(self, type_of_luck):
        self.luck_count['luck']: self.luck_count['good percentage']
        self.luck_count[type_of_luck] += 1
        self.luck_count['total count'] += 1

        # update luck percentages
        if self.luck_count['total count'] > 0:
            self.luck_count['good percentage'] = int((
                self.luck_count['good']/self.luck_count['total count'])*100)
            self.luck_count['bad percentage'] = int(100 -
                                                    self.luck_count['good percentage'])

            if self.luck_count['bad'] > self.luck_count['good']:
                self.luck_count['word'] = 'Unlucky'
                self.luck_count['luck'] = self.luck_count['bad percentage']
            else:
                self.luck_count['word'] = 'Lucky'
                self.luck_count['luck'] = self.luck_count['good percentage']

    def update_bonus_record(self, power):
        self.bonus_record[power] += 1

    def __repr__(self):
        return f"{'{:15}'.format(self.name)}{'{:<8}'.format(self.level)}{'{:<8}'.format(self.points)}{'{:<1}'.format(self.luck_count['luck'])}%"


class HighScores:
    def __init__(self):
        self.top_ten_scores = []
        self.show_high_scores = False

    def get_list_length(self):
        return len(self.top_ten_scores)

    def if_high_score(self, points):
        if ((self.get_list_length() < 10 or
                points > min(int(i.points) for i in self.top_ten_scores))):
            return True
        return False

    def get_new_game_scores(self):
        if self.file_exists():
            self.text_to_list()
        if self.get_list_length() > 1:
            self.sort_scores()
            self.list_to_text()

    def print_players(self):
        titles = f"{'{:<15}'.format('Name')}{'{:<8}'.format('Points')}{'{:<8}'.format('Level')}{'{:<8}'.format('Luck')}"
        print(f"\n{titles}")
        print("-"*len(titles))
        for player in self.top_ten_scores:
            print(player)
        print()

    def update_scores(self, player):
        if self.if_high_score(player.points):
            self.top_ten_scores.append(player)

        self.sort_scores()

        if self.get_list_length() > 10:
            self.top_ten_scores = self.top_ten_scores[0:10]

        self.list_to_text()

        print('update_scores() - executed like <<<< - Ted Bundy - >>>>')
        # For testing
        self.print_players

    def text_to_list(self):
        with open('scores.txt', 'r') as file:
            for line in file:
                if len(line) > 3:
                    line = line.replace('\n', '')
                    parts = line.split(';')
                    player = Player()
                    player.set_name(parts[0])
                    player.update_player(parts[1], parts[2], parts[3])
                    self.top_ten_scores.append(player)

    def sort_scores(self):
        self.top_ten_scores.sort(key=lambda x: x.points, reverse=True)
        self.print_players()

    def file_exists(self):
        file = 'scores.txt'
        try:
            f = open(file, 'r')
            print("File Exists")
            return True
        except IOError:
            f = open(file, 'w+')
            print("File Created")
            return True

    def list_to_text(self):
        with open('scores.txt', 'w') as file:
            for player in self.top_ten_scores:
                if player.name != "":
                    file.write(
                        f"{player.name};{player.points};{player.level};{player.luck_count['luck']}\n")
