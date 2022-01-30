import pandas as pd
import numpy as np

questions_answers_df = pd.DataFrame(np.array([
    ## EPISODE 1
    # zeroed out points for episode 1 weekly Qs due to split premiere
    [1, 'weekly', 'Winner of the Week (5 Points)', 'episode_winner', 'Episode Winner', 0, ['Kornbread Jete']],
    [1, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 0, ['Bosco', 'Kornbread Jete', 'Willow Pill']],
    [1, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 0, ['Alyssa Hunter', 'June Jambalaya', 'Orion Story']],
    [1, 'weekly', 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'episode_eliminated', 'Eliminated Queen', 0, ['Orion Story']],
    [1, 'bonus',  'America''s Next Drag Superstar (winner of the season) (50 Points)', 'season_winner', 'Season Winner', 50, []],
    [1, 'bonus',  'Top 3 of the Season (Guess #1) (10 Points)', 'season_top3', 'Season Top 3', 10, []],
    [1, 'bonus',  'Lip Sync Assassin (who will be in the most lip syncs) (15 points)', 'lipsync_assasin', 'Lipsync Assasin', 15, []],
    [1, 'bonus',  'Guess a celebrity portrayed in Snatch Game (Guess #1) (10 Points)', 'snatch_game_celebrities', 'Snatch Game Celebrities', 10, []],

    ## EPISODE 2
    [2, 'weekly', 'Winner of the Week (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Angeria Paris VanMichaels']],
    # [2, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Angeria Paris VanMichaels', 'Jorgeous', 'Lady Camden']],
    [2, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Daya Betty', 'Deja Skye', 'Maddy Morphosis']],
    [2, 'weekly', 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Daya Betty']],
    [2, 'bonus',  'Guess a Lip-sync Song performed this season (Guess #1) (5 Points)', 'lipsync_songs', 'Lipsync Songs', 5, []],

    ## EPISODE 3
    [3, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Willow Pill']],
    [3, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Angeria Paris VanMichaels', 'Jorgeous']],
    [3, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['June Jambalaya', 'Orion Story', 'Maddy Morphosis']],
    [3, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['June Jambalaya']],
    [3, 'bonus',  'Who will be picked as Miss Congeniality? (20 points)', 'miss_congeniality', 'Miss Congeniality', 20, []],
    [3, 'bonus',  'Winner of Snatch Game (10 points)', 'snatch_game_winner', 'Snatch Game Winner', 10, []],
    [3, 'bonus',  'Do you think the first two eliminated queens will be brought back? (5 points)', 'first_two_elim_return', 'First Two Eliminations Return', 5, ['Yes']],

    ## EPISODE 4
    [4, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Angeria Paris VanMichaels']],
    [4, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Angeria Paris VanMichaels', 'Deja Skye']],
    [4, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Kornbread Jete', 'Alyssa Hunter', 'Kerri Colby']],
    [4, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['June Jambalaya']],
    [4, 'bonus',  'Who will be saved by the chocolate bar? (10 points)', 'saved_by_chocolate_bar', 'Saved by the bar', 10, []],
    [4, 'bonus',  'Who will earn the most money throughout the season? (20 points)', 'most_money_earned', 'Most $$$ earned during season', 20, []]




                                    ]),
    columns = ['episode_number', 'question_type', 'question_raw', 'question_fancy', 'question_abbreviated', 'point_value', 'answer'])