import pandas as pd
from Player import *
from createPlayers import *
from key import questions_answers_df
pd.set_option('precision', 0)

import pickle

# def savePlayerList(player_list, episode_number):
#     pickle.dump(player_list, 'rpdr_s14e' + str(episode_number) + 'player_list.pkl')


def calculateScores(episode_number):
    if episode_number >= 1 and episode_number <= 9:
        episode_number_str = '0' + str(episode_number)
    else:
        episode_number_str = str(episode_number)

    responses_raw = pd.read_csv('rpdr_s14e' + episode_number_str + '_responses.csv')

    if episode_number == 1:
        responses_raw['season_top3'] = responses_raw[['Top 3 of the Season (Guess #1) (10 Points)',
                                                      'Top 3 of the Season (Guess #2) (10 Points)',
                                                      'Top 3 of the Season (Guess #3) (10 Points)']].values.tolist()
    if episode_number == 6:
        responses_raw['season_top3_reask'] = responses_raw[['Top 3 of the Season (Guess #1) (5 Points).',
                                                            'Top 3 of the Season (Guess #2) (5 Points).',
                                                            'Top 3 of the Season (Guess #3) (5 Points).']].values.tolist()

    # CONVERT top 3 into list
    if episode_number == 11:
        responses_raw['episode_elim3'] = responses_raw[['Elimination Guess #1 (5 Points)',
                                                        'Elimination Guess #2 (5 Points)',
                                                        'Elimination Guess #3 (5 Points)']].values.tolist()
        responses_raw['lipsync_songs'] = responses_raw[['Guess a lip-sync song #1 (2 Points)',
                                                        'Guess a lip-sync song #2 (2 Points)',
                                                        'Guess a lip-sync song #3 (2 Points)']].values.tolist()
    elif episode_number != 2 and episode_number != 14:
        responses_raw['episode_top3'] = responses_raw[['Top 3 of the Week (Pick #1) (2 Points)',
                                                       'Top 3 of the Week (Pick #2) (2 Points)',
                                                       'Top 3 of the Week (Pick #3) (2 Points)']].values.tolist()

    if episode_number == 2:
        responses_raw['lipsync_songs'] = responses_raw[['Guess a Lip-sync Song performed this season (Guess #1) (5 Points)',
                                                       'Guess a Lip-sync Song performed this season (Guess #2) (5 Points)',
                                                       'Guess a Lip-sync Song performed this season (Guess #3) (5 Points)']].values.tolist()

    if episode_number != 11 and episode_number != 14:
        # CONVERT bottom 3 into list
        responses_raw['episode_bottom3'] = responses_raw[['Bottom 3 of the Week (Pick #1) (2 Points)',
                                                          'Bottom 3 of the Week (Pick #2) (2 Points)',
                                                          'Bottom 3 of the Week (Pick #3) (2 Points)']].values.tolist()

    if episode_number == 14:
        # CONVERT bottom 2 into list
        responses_raw['episode_bottom2'] = responses_raw[['Bottom 2 of the Week (Pick #1) (2 Points)',
                                                          'Bottom 2 of the Week (Pick #2) (2 Points)']].values.tolist()


    for p in range(0, len(player_list)):
        ## get that person's username
        temp_player_username = player_list[p].get_username().strip()

        ## get that person's responses for that episode
        player_responses = responses_raw[responses_raw['Username'] == temp_player_username]

        ## filter answers to relevant episode
        episode_answers = questions_answers_df[questions_answers_df['episode_number'] == episode_number]

        ## IF player did not make any resposes that episode
        if len(player_responses) == 0:
            # add responses col to episode answers that is blank since they did not add anything
            episode_answers['response'] = 'No response'
            episode_answers['points_awarded'] = 0
            player_list[p].append_history(
                episode_answers[['episode_number', 'question_proper', 'question_type',
                                 'response', 'answer', 'point_value', 'points_awarded']])
        elif len(player_responses) > 1:
            raise Exception (temp_player_username + " has more than one bracket submission")
        else:
            player_responses_t = player_responses.transpose()
            player_responses_t.columns = ["response"]
            player_responses_t['questions'] = player_responses_t.index

            ## MERGE user's responses to that episode's answers
            temp_merge = pd.merge(player_responses_t, episode_answers, how='inner', left_on=['questions'],
                                  right_on=['question_raw'])

            # iterate through the joined responses to answers
            for r in range(0, len(temp_merge)):

                # Replace answers that are unneccesary lists into strings
                if (isinstance(temp_merge.iloc[r]['answer'], list)) and (len(temp_merge.iloc[r]['answer']) == 1):
                    temp_merge.loc[r, 'answer'] = temp_merge.loc[r, 'answer'][0]

                    # check if player is correct
                    if temp_merge.loc[r, 'answer'] in temp_merge.loc[r, 'response']:
                        temp_merge.loc[r, 'points_awarded'] = temp_merge.loc[r, 'point_value']
                        player_list[p].add_points(temp_merge.loc[r, 'point_value'])
                    else:
                        temp_merge.loc[r, 'points_awarded'] = 0

                # check if player is correct
                else:
                    if type(temp_merge.loc[r, 'response']) == str:
                        list_overlap = list(set(temp_merge.loc[r, 'answer']) & set([temp_merge.loc[r, 'response']]))
                    else:
                        list_overlap = list(set(temp_merge.loc[r, 'answer']) & set(temp_merge.loc[r, 'response']))
                    num_correct = len(list_overlap)
                    points_to_be_awarded = int(temp_merge.loc[r, 'point_value'] * num_correct)
                    temp_merge.loc[r, 'points_awarded'] = points_to_be_awarded
                    player_list[p].add_points(points_to_be_awarded)

            player_list[p].append_history(temp_merge[
                                              ['episode_number', 'question_proper', 'question_type',
                                               'response', 'answer', 'point_value', 'points_awarded']])
    return player_list
    # savePlayerList(player_list, episode_number)

def getScoreboard():
    scoreboard = pd.DataFrame(columns=['username', 'score'])
    for p in range(0, len(player_list)):
        scoreboard = scoreboard.append([{'username': player_list[p].get_username(), 'score': player_list[p].get_points()}])
    scoreboard = scoreboard.sort_values(['score'], ascending=False)
    return scoreboard

def printScoreboard():
    print(getScoreboard())
