import pandas as pd
import numpy as np

questions_answers_df = pd.DataFrame(np.array([
    ## EPISODE 1
    # zeroed out points for episode 1 weekly Qs due to split premiere
    [1, 'Winner of the Week (5 Points)', 'weekly', 'episode_winner', 0, ['Kornbread Jete']],
    [1, 'Top 3 of the Week (Pick #1) (2 Points)', 'weekly', 'episode_top3', 0, ['Bosco', 'Kornbread Jete', 'Willow Pill']],
    [1, 'episode_bottom3', 'weekly', 'episode_bottom3', 0, ['Alyssa Hunter', 'June Jambalaya', 'Orion Story']],
    [1, 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'weekly', 'episode_eliminated', 0, ['Orion Story']],
    [1, 'America''s Next Drag Superstar (winner of the season) (50 Points)', 'bonus', 'season_winner', 50, []],
    [1, 'Top 3 of the Season (Guess #1) (10 Points)', 'bonus', 'season_top3', 10, []],
    [1, 'Lip Sync Assassin (who will be in the most lip syncs) (15 points)', 'bonus', 'lipsync_assasin', 15, []],
    [1, 'Guess a celebrity portrayed in Snatch Game (Guess #1) (10 Points)', 'bonus', 'snatch_game_celebrities', 10, []],

    ## EPISODE 2
    [2, 'Winner of the Week (5 Points)', 'weekly', 'episode_winner', 5, ['Angeria Paris VanMichaels']],
    # [2, 'episode_top3', 'weekly', 'episode_top3', 2, ['Angeria Paris VanMichaels', 'Jorgeous', 'Lady Camden']],
    [2, 'episode_bottom3', 'weekly', 'episode_bottom3', 2, ['Daya Betty', 'Deja Skye', 'Maddy Morphosis']],
    [2, 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'weekly', 'episode_eliminated', 5, ['Daya Betty']],
    [2, 'Guess a Lip-sync Song performed this season (Guess #1) (5 Points)', 'bonus', 'lipsync_songs', 5, []]

    ## EPISODE 3
    # [3, 'Winner of the Week (5 Points)', 'weekly', 'epsiode_winner', 5, ['rgergrg']],
    # [3, 'Top 3 of the Week (Pick #1) (2 Points)', 'weekly', 'episode_top3', 2, ['Angeria Paris VanMichaels', 'Jorgeous', 'Lady Camden']],
    # [3, 'Bottom 3 of the Week (Pick #1) (2 Points)', 'weekly', 'episode_bottom3', 2, ['Daya Betty', 'Deja Skye', 'Maddy Morphosis']],
    # [3, 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'weekly', 'episode_eliminated', 5, ['Daya Betty']],
    # [3, 'Guess a Lip-sync Song performed this season (Guess #1) (5 Points)', 'bonus', 'lipsync_songs', 5, []]
                                    ]),
    columns = ['episode_number', 'question_raw', 'question_type', 'question_abbreviated', 'point_value', 'answer'])