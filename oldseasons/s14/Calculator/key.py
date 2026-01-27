import pandas as pd
import numpy as np

questions_answers_df = pd.DataFrame(np.array([
    ## EPISODE 1
    # zeroed out points for episode 1 weekly Qs due to split premiere
    [1, 'weekly', 'Winner of the Week (5 Points)', 'episode_winner', 'Episode Winner', 0, ['Kornbread Jete']],
    [1, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 0, ['Bosco', 'Kornbread Jete', 'Willow Pill']],
    [1, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 0, ['Alyssa Hunter', 'June Jambalaya', 'Orion Story']],
    [1, 'weekly', 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'episode_eliminated', 'Eliminated Queen', 0, ['Orion Story']],
    [1, 'bonus',  'America\'s Next Drag Superstar (winner of the season) (50 Points)', 'season_winner', 'Season Winner', 50, ['Willow Pill']],
    [1, 'bonus',  'season_top3', 'season_top3', 'Season Top 3', 10, ['Lady Camden', 'Willow Pill']],
    [1, 'bonus',  'Lip Sync Assassin (who will be in the most lip syncs) (15 points)', 'lipsync_assasin', 'Lipsync Assasin', 15, ['Jorgeous']],
    [1, 'bonus',  'Guess a celebrity portrayed in Snatch Game (Guess #1) (10 Points)', 'snatch_game_celebrities', 'Snatch Game Celebrities', 10, []],

    ## EPISODE 2
    [2, 'weekly', 'Winner of the Week (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Angeria Paris VanMichaels']],
    # [2, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Angeria Paris VanMichaels', 'Jorgeous', 'Lady Camden']],
    [2, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Daya Betty', 'Deja Skye', 'Maddy Morphosis']],
    [2, 'weekly', 'Eliminated Queen of the Week (of the bottom 3) (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Daya Betty']],
    [2, 'bonus',  'lipsync_songs', 'lipsync_songs', 'Lipsync Songs', 5, ['My Head & My Heart - Ava Max', 'good 4 u - Olivia Rodrigo']],

    ## EPISODE 3
    [3, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Willow Pill']],
    [3, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Angeria Paris VanMichaels', 'Jorgeous']],
    [3, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['June Jambalaya', 'Orion Story', 'Maddy Morphosis']],
    [3, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['June Jambalaya']],
    [3, 'bonus',  'Who will be picked as Miss Congeniality? (20 points)', 'miss_congeniality', 'Miss Congeniality', 20, ['Kornbread Jete']],
    [3, 'bonus',  'Winner of Snatch Game (10 points)', 'snatch_game_winner', 'Snatch Game Winner', 10, ['Deja Skye']],
    [3, 'bonus',  'Do you think the first two eliminated queens will be brought back? (5 points)', 'first_two_elim_return', 'First Two Eliminations Return', 5, ['Yes']],

    ## EPISODE 4
    [4, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Angeria Paris VanMichaels']],
    [4, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Angeria Paris VanMichaels', 'Deja Skye']],
    [4, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Kornbread Jete', 'Alyssa Hunter', 'Kerri Colby']],
    [4, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Alyssa Hunter']],
    [4, 'bonus',  'Who will be saved by the chocolate bar? (10 points)', 'saved_by_chocolate_bar', 'Saved by the bar', 10, ['Bosco']],
    [4, 'bonus',  'Who will earn the most money throughout the season? (20 points)', 'most_money_earned', 'Most $$$ earned during season', 20, ['Bosco']],

    ## EPISODE 5
    [5, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Bosco']],
    [5, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Bosco', 'Angeria Paris VanMichaels', 'Lady Camden']],
    [5, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Jasmine Kennedie', 'Orion Story', 'Jorgeous']],
    [5, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Orion Story']],
    [5, 'bonus', 'Who will be the first queen to cry this episode? (3 Points)', 'first_to_cry', 'First Queen to Cry', 3, ['Willow Pill']],

    ## EPISODE 6
    [6, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Jorgeous']],
    [6, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Jorgeous', 'Angeria Paris VanMichaels', 'Lady Camden']],
    [6, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Jasmine Kennedie', 'Deja Skye', 'Maddy Morphosis']],
    [6, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Maddy Morphosis']],
    [6, 'bonus',  'season_top3_reask', 'season_top3_reask', 'Season Top 3 (Re-Ask)', 5, ['Lady Camden', 'Willow Pill']],
    [6, 'bonus',  'Of the season top 3, who will be America\'s Next Drag Superstar (winner of the season) (25 Points).', 'season_winner_reask', 'Season Winner', 25, ['Willow Pill']],
    [6, 'bonus',  'Who will be picked as Miss Congeniality? (10 points).', 'miss_congeniality_reask', 'Miss Congeniality (Re-Ask)', 10, ['Kornbread Jete']],

    ## EPISODE 7
    [7, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Lady Camden']],
    [7, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Jorgeous', 'Willow Pill', 'Jasmine Kennedie', 'Bosco', 'Daya Betty', 'Lady Camden']],
    [7, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['No bottoms (tragic)']],
    [7, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['No elimination']],

    ## EPISODE 8
    [8, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Bosco']],
    [8, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Angeria Paris VanMichaels', 'Deja Skye', 'Bosco']],
    [8, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Jasmine Kennedie', 'Lady Camden', 'Kerri Colby']],
    [8, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Kerri Colby']],

    ## EPISODE 9
    [9, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Bosco']],
    [9, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Bosco', 'Deja Skye']],
    [9, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Jasmine Kennedie', 'Jorgeous', 'Daya Betty']],
    [9, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['No elimination']],
    [9, 'bonus', 'What will be the most common color worn on this weeks runway? (3 Points)', 'most_common_color', 'Most Common Runway Color', 3, ['Black']],

    ## EPISODE 10
    [10, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Deja Skye']],
    [10, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Deja Skye']],
    [10, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Jasmine Kennedie', 'Jorgeous', 'Willow Pill', 'Lady Camden', 'Daya Betty', 'Bosco', 'Angeria Paris VanMichaels']],
    [10, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['No elimination']],

    ## EPISODE 11
    [11, 'weekly', 'episode_elim3', 'episode_elim3', 'Eliminated Queen', 5, ['Jasmine Kennedie']],
    [11, 'bonus', 'lipsync_songs', 'lipsync_songs', 'Lipsync Songs', 2, ['Respect - Aretha Franklin', 'Never Too Much - Luther Vandross', 'Radio - Beyonce', 'Don\'t Let Go (Love) - En Vogue', 'Love Don\'t Cost a Thing - Jennifer Lopez']],
    [11, 'bonus', 'Will a gold bar be used this episode? (2 Points)', 'chocolate', 'Was the Chocolate Bar Used?', 5, ['No']],

    ## EPISODE 12
    [12, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Lady Camden']],
    [12, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Willow Pill', 'Daya Betty', 'Lady Camden']],
    [12, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Bosco', 'Jorgeous', 'Deja Skye']],
    [12, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['No elimination']],
    [12, 'bonus', '(Bonus) How many more episodes will be there?(including episode 12) (3 points)', 'more_eps', 'How many more episodes will there be? (including ep 12)', 3, ['5']],

    ## EPISODE 13
    [13, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Bosco']],
    [13, 'weekly', 'episode_top3', 'episode_top3', 'Episode Top 3', 2, ['Bosco', 'Willow Pill', 'Lady Camden']],
    [13, 'weekly', 'episode_bottom3', 'episode_bottom3', 'Episode Bottom 3', 2, ['Daya Betty', 'Jorgeous', 'Deja Skye']],
    [13, 'weekly', 'Of the bottom 3, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['Deja Skye', 'Jorgeous']],
    [13, 'bonus', 'Who will make the first snarky comment about the no elimination? (3 Points)', 'snarky', 'Who will make the first snarky comment about no elimination?', 3, ['Deja Skye']],

    ## EPISODE 14
    [14, 'weekly', 'Of the top 3, who\'s the winner of the week? (5 Points)', 'episode_winner', 'Episode Winner', 5, ['Lady Camden']],
    [14, 'weekly', 'episode_bottom2', 'episode_bottom2', 'Episode Bottom 2', 2, ['Angeria Paris VanMichaels', 'Willow Pill']],
    [14, 'weekly', 'Of the bottom 2, who is the eliminated queen of the week? (5 Points)', 'episode_eliminated', 'Eliminated Queen', 5, ['No elimination']]

]),
    columns = ['episode_number', 'question_type', 'question_raw', 'question_abbreviated', 'question_proper', 'point_value', 'answer'])