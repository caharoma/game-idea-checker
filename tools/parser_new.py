from bs4 import BeautifulSoup
import requests
import json 
import pandas as pd
import numpy as np
from threading import Thread

IDIS = pd.read_csv('steamcmd_appid.csv')
IDIS = IDIS[IDIS.columns[0]].values
OFFSET = 0
DESCRIPTION_CLASS = 'game_area_description'
REVIEWS_CLASS = 'user_reviews'
DATA_NAME = 'games_description_dataset'
LINK = 'https://store.steampowered.com/app/'
DATA = pd.DataFrame(columns=['appid', 'description', 'purchases', 'score'])
BANNED_SYMBOLS = ['About This Game', '\n', '\r', '\t', '\s', '\x93', '\x94']


def cfg_load():
    global OFFSET, PREFIX
    try:
        with open('parser.cfg') as f:
            _data = json.load(f)
            OFFSET = _data['OFFSET']
    except:
        _data = {'OFFSET':OFFSET, 'PREFIX':PREFIX}
        OFFSET = _data['OFFSET']
        PREFIX = _data['PREFIX']

def cfg_save():
    global OFFSET, PREFIX
    _data = {'OFFSET':OFFSET, 'PREFIX':PREFIX}
    with open('parser.cfg', 'w+') as f:
        f.write(json.dumps(_data))

def checkpoint():
    global PREFIX
    print('checkpoint '+str(PREFIX))
    DATA.to_feather(str(PREFIX) + '_dataset.checkpoint')
    PREFIX = PREFIX + 1

def parse_link():
    global OFFSET, IDIS, DESCRIPTION_CLASS, REVIEWS_CLASS, LINK, DATA, BANNED_SYMBOLS, OFFSET_MAX

    while OFFSET < OFFSET_MAX:
        _offset = OFFSET
        OFFSET = OFFSET + 1
        try:
            print('parsing app id ' + str(IDIS[_offset]))
            print(str(_offset)+'/'+str(OFFSET_MAX))
        except:
            continue
        try:
            _data = {}
            req = requests.get(LINK + str(IDIS[_offset]))
            html = BeautifulSoup(req.text, features='html.parser')
            valid = html.find('div',{'class':DESCRIPTION_CLASS})
            if valid == None:
                cfg_save()
                continue
            else:
                try:
                    _data.update({'appid':IDIS[_offset]})
                    x = valid.get_text()
                    for i in BANNED_SYMBOLS:
                        x = x.replace(i,'')
                    if len(x) < 350:
                        continue
                    _data.update({'description':x})
                    _buyers = html.find('div',{'itemprop':'aggregateRating'})
                    _score = _buyers.find('span', {'class':'game_review_summary'})
                    _buyers = _buyers.find('span',{'class':'responsive_hidden'})

                    _buyers = _buyers.get_text().replace('(','').replace(')','').replace(',','')
                    _buyers = int(_buyers)
                    _buyers = round(_buyers / 2 * 100)
                    _data.update({'purchases': _buyers})

                    _score = _score.get_text()
                    match _score:
                        case 'Overwhelmingly Negative':
                            _score = 0
                        case 'Very Negative':
                            _score = 0
                        case 'Negative':
                            _score = 0
                        case 'Mostly Negative':
                            _score = 0
                        case 'Mixed':
                            _score = 1
                        case 'Mostly Positive':
                            _score = 2
                        case 'Positive':
                            _score = 2
                        case 'Very Positive':
                            _score = 3
                        case 'Overwhelmingly Positive':
                            _score = 3

                    _data.update({'score':_score})
                    print(_data)
                    DATA = DATA._append(_data, ignore_index=True)
                    if DO_CHECKPOINTS == True:
                        checkpoint()
                    continue
                except:
                    continue
        except:
            continue



THREADS = 50
OFFSET_MAX = 160340
PREFIX = 0
DO_CHECKPOINTS = True

threads = []

cfg_load()

for i in range(0,THREADS):
    th = Thread(target=parse_link)
    threads.append(th)

for i in threads:
    i.start()
for i in threads:
    i.join()

print('saving')
print(DATA)
DATA.to_feather(DATA_NAME)
cfg_save()
