# -*- coding: utf-8 -*-
import requests
import winsound
import lxml.html as lh
import cPickle
import ctypes


def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text.encode('cp1251', 'ignore'), title.encode('cp1251', 'ignore'), style)

r = requests.get('https://ctftime.org/')
html = lh.document_fromstring(r.text)
table = html.get_element_by_id('upcoming_events')

new = {}
for i in (table[1], table[2], table[3]):
    name = i[1][0].text.encode('cp1251', 'ignore')
    date = i[2].text.encode('cp1251', 'ignore')
    teams = i[2][0].text.encode('cp1251', 'ignore')
    duration = i[3].text.encode('cp1251', 'ignore')
    new[name] = [date, teams, duration]
#new = dict([i[1][0].text, [i[2].text, i[2][0].text, i[3].text]] for i in (table[1], table[2], table[3])) #same thing
flag_new_game = False
flag_new_time = False
flag_new_team = False
new_games = []
change_time = []
old = cPickle.loads(open('upcoming_ctf.txt','r').read())
for i in new.keys():
    if i in old.keys():
        if old[i][0] != new[i][0]:
            flag_new_time = True
            change_time.append(i)
        if old[i][1] != new[i][1]:
            flag_new_team = True
    else:
        flag_new_game = True
        new_games.append(i)

open('upcoming_ctf.txt','w').write(cPickle.dumps(new))
if flag_new_game:
    teams = "\n".join(i for i in new_games)
    sound = winsound.PlaySound('wav_phrases\\new_game_phrase.wav', winsound.SND_FILENAME)
    Mbox(u"Внимание", u"Новые игры:\n" + teams, 0)
if flag_new_time:
    teams = "\n".join(i for i in change_time)
    sound = winsound.PlaySound('wav_phrases\\new_time_phrase.wav', winsound.SND_FILENAME)
    Mbox(u"Внимание", u"Измененилось время:\n" + teams, 0)
if flag_new_team:
    sound = winsound.PlaySound('wav_phrases\\new_teams_phrase.wav', winsound.SND_FILENAME)
    #Mbox(u"Внимание", u"Новые команды подтвердили участие", 0)
