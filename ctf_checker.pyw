# -*- coding: utf-8 -*-
import requests
import winsound
import lxml.html as lh
import cPickle
import ctypes
import re
import datetime as dt
from checkerGUI import Application

SHOW_ALL_GAMES = False
SHOW_NEW_STYLE = True

def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text.encode('cp1251', 'ignore'), title.encode('cp1251', 'ignore'), style)

class Game:

    def __init__(self, game_row):
        self.name = self.GetName(game_row)
        self.type = self.GetType(game_row)
        self.state = self.GetState(game_row)
        self.local_page = self.GetLocalPage(game_row)
        self.date = self.GetDate(game_row)
        self.teams = self.GetTeams(game_row)
        self.duration = self.GetDuration(game_row)

        r = requests.get('https://ctftime.org' + self.local_page)
        html = lh.document_fromstring(r.text)
        table = html.find_class('span10')[0]

        self.place_type = self.GetPlaceType(table)
        self.site = self.GetSite(table)
        self.rank = self.GetRank(table)

    def __str__(self):
        return "Игра: %s\nТип: %s\nСостояние: %s\nСсылка: %s\nДата проведения: с %s по %s\nКоличество команд: %s\nПродолжительность: %d дней %d часов\nМесто проведения: %s\nСайт игры: %s\nРанг: %s\n"\
                 %(self.name, self.type, self.state, self.local_page, self.date['start'].strftime("%d %B %Y года в %H:%M"), self.date['end'].strftime("%d %B %Y года в %H:%M"), self.teams, self.duration['days'], self.duration['hours'], self.place_type, self.site, self.rank)

    def GetType(self, game_row):
        return game_row[0][0].attrib['alt'].encode('utf-8', 'ignore') #Получаем тип игры (Jeopardy или Classic)

    def GetLocalPage(self, game_row):
        return game_row[1][0].attrib['href'] #Получаем ссылку на страницу игры на сайте ctftime.org

    def GetState(self, game_row):
        try:
            result = game_row[1][1].attrib['id'].encode('utf-8', 'ignore') #Идет игра или нет
        except KeyError:
            result = 'upcoming'
        return result

    def GetName(self, game_row):
        return game_row[1][0].text.encode('utf-8', 'ignore')

    def GetDate(self, game_row):
        string = game_row[2].text.encode('utf-8', 'ignore')
        date = {'start':0, 'stop':0}
        start, end = string.split(" — ")
        end = end.strip(" UTC ")
        date['start'] = dt.datetime.strptime(start, "%B %d, %Y %H:%M")
        date['start'] = date['start'] + dt.timedelta(hours=3)
        date['end'] = dt.datetime.strptime(end, "%B %d, %H:%M")
        date['end'] = date['end'].replace(year=date['start'].year)
        date['end'] = date['end'] + dt.timedelta(hours=3)
        return date

    def GetTeams(self, game_row):
        return int(re
            .search("\d+", game_row[2][0]
                .text
                .encode('utf-8', 'ignore'))
            .group(0))

    def GetDuration(self, game_row):
        string = game_row[3].text.encode('utf-8', 'ignore')
        time = {'days':0, "hours":0}
        try:
            buf = re.search("\d+d \d+h", string).group(0)
            time["days"] = int(buf.split(" ")[0].strip("d"))
            time["hours"] = int(buf.split(" ")[1].strip("h"))
        except AttributeError:
            buf = re.search("\d+h", string).group(0)
            time["hours"] = int(buf.strip("h"))
        return time


    def GetPlaceType(self, game_row):
        return game_row[1].text_content().encode('utf-8', 'ignore')

    def GetSite(self, game_row):
        return game_row[5][0].text.encode('utf-8', 'ignore')

    def GetRank(self, game_row):
        return float(re
            .search("\d+.\d+", game_row[6]
                .text
                .encode('utf-8', 'ignore'))
            .group(0))


r = requests.get('https://ctftime.org')
html = lh.document_fromstring(r.text)
table = html.get_element_by_id('upcoming_events')
newGames = {}
if SHOW_ALL_GAMES:
    app = Application()
    app.master.title('Ближайшие игры')
for game_row in (table[1], table[2], table[3]):
    g = Game(game_row)
    newGames[g.name] = g
    if SHOW_ALL_GAMES: app.createWidgets(newGames[g.name].__dict__)
if SHOW_ALL_GAMES: app.mainloop()

isNewGame = False
isNewTime = False
isNewTeams = False
showGames = []
changedTimes = []
try:
    oldGames = cPickle.loads(open('upcoming_ctf.txt','r').read())
except IOError:
    open('upcoming_ctf.txt','w').write(cPickle.dumps(newGames))
    exit()
for gameName in newGames.keys():
    if gameName in oldGames.keys():
        if oldGames[gameName].date != newGames[gameName].date:
            isNewTime = True
            changedTimes.append(gameName)
        if oldGames[gameName].teams != newGames[gameName].teams:
            isNewTeams = True
    else:
        isNewGame = True
        showGames.append(gameName)

open('upcoming_ctf.txt','w').write(cPickle.dumps(newGames))
if isNewGame:
    sound = winsound.PlaySound('C:\\ctf_checker\\wav_phrases\\new_game_phrase.wav', winsound.SND_FILENAME)
    if SHOW_NEW_STYLE:
        app = Application()
        app.master.title('Новые игры')
        for name in showGames:
            app.createWidgets(newGames[name].__dict__)
        app.center()
        app.mainloop()
    else:
        teams = "\n".join(i for i in showGames)
        Mbox(u"Внимание", u"Новые игры:\n" + teams, 0)
if isNewTime:
    sound = winsound.PlaySound('C:\\ctf_checker\\wav_phrases\\new_time_phrase.wav', winsound.SND_FILENAME)
    if SHOW_NEW_STYLE:
        app = Application()
        app.master.title('Изменилось время')
        for name in changedTimes:
            app.createWidgets(newGames[name].__dict__)
        app.center()
        app.mainloop()
    else:
        teams = "\n".join(i for i in changedTimes)
        Mbox(u"Внимание", u"Измененилось время:\n" + teams, 0)
if isNewTeams:
    sound = winsound.PlaySound('C:\\ctf_checker\\wav_phrases\\new_teams_phrase.wav', winsound.SND_FILENAME)
    #Mbox(u"Внимание", u"Новые команды подтвердили участие", 0)
