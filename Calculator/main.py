from Calculator import *
import numpy as np
import jinja2
from IPython.display import display

import pickle
pd.set_option("display.max_rows", None, "display.max_columns", None)

calculateScores(1)
# printScoreboard()

calculateScores(2)
# printScoreboard()

df = player_list[1].get_history(False).reset_index()

# df = getScoreboard().reset_index()
df_styled = df.style
print(df_styled.render())



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