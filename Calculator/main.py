from Calculator import *
import numpy as np
import jinja2
from IPython.display import display

# TODO: sorting ignoring string case: https://stackoverflow.com/questions/10269701/case-insensitive-list-sorting-without-lowercasing-the-result

import pickle
pd.set_option("display.max_rows", None, "display.max_columns", None)

calculateScores(1)
# printScoreboard()

calculateScores(2)
# printScoreboard()

for p in range(0, len(player_list)):
    print("<h2 id=\"" + player_list[p].get_username() + "\" class=\"player-name\">" + player_list[p].get_username() + "</h2>")
    df = player_list[p].get_history(False).reset_index()
    df_styled = df.style
    df_styled = df_styled.hide_index().hide_columns('index').hide_columns('question_type')  # remove index columns
    print(df_styled.hide_index().render())
    print('\n\n')

scoreboard = getScoreboard()

# for player in sorted(list(scoreboard['username']), key=str.casefold):
#     print("<a href=\"#" + player + "\">" + player + "</a>")

df = getScoreboard().reset_index()
df_styled = df.style
df_styled = df_styled.hide_index().hide_columns('index')  # remove index columns
# print(df_styled.hide_index().render())

# @ nick a, look at this for styling ideas. Look at maybe text gradient or highlighting based on the score value?
#  https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.html



# np.random.seed(24)
# df = pd.DataFrame({'A': np.linspace(1, 10, 10)})
# df = pd.concat([df, pd.DataFrame(np.random.randn(10, 4), columns=list('BCDE'))],
#                axis=1)
# df.iloc[0, 2] = np.nan
#
# s = df.style
# print(s.render())

# calculateScores(3)
# printScores()