from Calculator import *
from websiteCode import *

pd.set_option("display.max_rows", None, "display.max_columns", None)

calculateScores(1)
calculateScores(2)
calculateScores(3)
calculateScores(4)
# printScoreboard()

generate_history_html_file()
generate_scoreboard_html_file()

# @ nick a, look at this for styling ideas. Look at maybe text gradient or highlighting based on the score value?
#  https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.html