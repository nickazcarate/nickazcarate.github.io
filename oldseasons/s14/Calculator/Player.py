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

    def get_history(self, include_questions_without_answers):
        if include_questions_without_answers == True:
            return self.history
        else:
            # history_minus_empty_answers = self.history[self.history[(isinstance(self.history['answer'], list)) & (len(self.history['answer']) == 0)]]
            # return history_minus_empty_answers
            return self.history[self.history['answer'].str.len() != 0]
