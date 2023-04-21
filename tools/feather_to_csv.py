import pandas as pd

inf = pd.read_feather('37647_dataset.checkpoint')
inf.to_csv('games_description_dataset.csv')
