from createPlayers import *
from Calculator import *

def generate_history_html_file():
    with open('history_html.txt', 'w') as f:
        for p in range(0, len(player_list)):
            f.write("<h2 id=\"" + player_list[p].get_username() + "\" class=\"player-name\">" + player_list[p].get_username() + "</h2>")
            f.write('\n')
            df = player_list[p].get_history(False).reset_index()

            # rename cols
            df = df.rename(columns={'episode_number': 'Episode #', 'question_proper': 'Question',
                                    'response': 'Your Response', 'answer': 'Answer', 'point_value': 'Point Value',
                                    'points_awarded': 'Points Awarded'})

            df_styled = df.style
            # df_styled = df_styled.hide_index().hide_columns('index')  # remove index columns
            df_styled = df_styled.hide_index().hide_columns(['index', 'question_type'])
            f.write(df_styled.hide_index().render())
            f.write('\n')

def generate_scoreboard_html_file():
    with open('scoreboard_html.txt', 'w') as f:
        scoreboard = getScoreboard()

        # rename columns
        scoreboard = scoreboard.rename(columns={'username': 'Username', 'score': 'Score'})

        df = scoreboard.reset_index()
        df_styled = df.style
        df_styled = df_styled.hide_index().hide_columns('index')  # remove index columns
        f.write(df_styled.hide_index().render())