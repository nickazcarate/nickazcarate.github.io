import pandas as pd
from Player import Player

e01_responses_raw = pd.read_csv('rpdr_s14e01_responses.csv')

# Create players that are a part of episode 1, i.e.:
# The Scorpio ♏️, Miguelol, Poinhub, MattMatt, Derek Berry, Jojo, Ball Enchilada
# edwin, Rawhul, Logie, azkratie, Jorge, Eric seeeeee, Damian, thatonebitch aka t1b
# ChitoMaciel, Thots Anna Prayers, Faguette

player_list = []
for p in range(0, len(e01_responses_raw)):
    ## get that p row
    ## use 3 values to create obj
    player = Player(e01_responses_raw.iloc[p]['Real Name'],
                    e01_responses_raw.iloc[p]['Username'],
                    e01_responses_raw.iloc[p]['Do you want to be a part of the prizes component?'])

    ## add player to player list
    player_list.append(player)

