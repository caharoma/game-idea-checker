import pandas as pd

BANNED_SYMBOLS = ['™','@','®','_','🤖',' 🏆','🔥','*','🌌','🦀','●','■','=','♠','🐤','🤗','🍅','🍔','🧬','🍧','👍','🏛','🐌','🌲', '◆','】','【','＜','＞','⬆','⬇','⬅','➡','🌽','🍖','🍆','🗽','💥','-','❤','▶','⭐️','+']
BANNED_WORDS = ['Reviews','REVIEWS','://store.steampowered.com/app']

df = pd.read_csv('games_description_dataset.csv')

df = df.drop_duplicates(subset=['description'])
df_c = pd.DataFrame(columns=['appid', 'description', 'purchases', 'score'])

for i in df.itertuples():
    dsc = ''
    if BANNED_WORDS[0] in i.description[0:7] or BANNED_WORDS[1] in i.description[0:7]:
        continue
    if BANNED_WORDS[2] in i.description:
        continue
    dsc = i.description
    for l in BANNED_SYMBOLS:
        dsc = dsc.replace(l,'')
    if len(dsc) < 350:
        continue
    x = {'appid':i.appid, 'description':dsc, 'purchases':i.purchases, 'score':i.score}
    df_c = df_c._append(x, ignore_index=True)

df_c.to_csv('cleared_games_descriptions.csv')