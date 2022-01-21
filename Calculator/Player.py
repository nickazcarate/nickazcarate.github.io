import pandas as pd

class Player:
    def __init__(self, real_name, username, part_of_prizes):
        self.real_name = real_name
        self.username  = username
        self.part_of_prizes = part_of_prizes

        self.points = 0
        self.history = pd.DataFrame()
        # cols (episode #, question, their guess, correct answer, points awarded)

    def get_points(self):
        return self.points

    def get_username(self):
        return self.username

    def add_points(self, points_to_add):
        self.points = self.points + points_to_add

    def append_history(self, history_to_add):
        self.history = self.history.append(history_to_add)

    def get_history(self, include_bonus):
        if include_bonus == True:
            return self.history
        else:
            return self.history[self.history['question_type'] != 'bonus']
