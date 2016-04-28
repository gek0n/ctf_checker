# -*- coding: utf-8 -*-
import winsound
import cPickle
import ctypes
import datetime as dt
import checkerGUI
from game import Game
import os
import feedparser
import logging

SHOW_ALL_GAMES = False
SHOW_NEW_STYLE = True
BE_QUIET = False

QUIET_HOURS = {"from": dt.datetime.strptime("21:00", "%H:%M").time(),
               "to": dt.datetime.strptime("9:00", "%H:%M").time()}
WORKING_DIR = os.path.dirname(os.path.abspath("__file__"))

logging.basicConfig(format=u'%(filename)-10s[LINE:%(lineno)d] <%(funcName)-15s> # %(levelname)-8s [%(asctime)s]  %(message)s'.encode('cp1251', 'ignore'), level=logging.DEBUG, filename='ctf_checker_log.log')
logging.log(100, '='*120)


def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text.encode('cp1251', 'ignore'), title.encode('cp1251', 'ignore'), style)


def showGames(title, listOfGames):
    if SHOW_NEW_STYLE:
        logging.debug("Показываем в новом стиле")
        app = checkerGUI.Application(WORKING_DIR)
        app.master.title(title)
        app.initialize(listOfGames)
        app.center()
        logging.debug("Пытаемся запустить окно")
        app.mainloop()
        logging.debug("Окно отработало")
        for gameName, isHide in checkerGUI.gamesHiddenFlags.items():
            loadedFromSiteGames[gameName].isHidden = isHide.get()
    else:
        logging.debug("Показываем в старом стиле")
        games = "\n".join(i for i in listOfGames)
        Mbox(u"Внимание", u"Измененилось время:\n" + games.name, 0)


def notifyAboutGames(state):
    if state["state"]:
        logging.debug(state["debugMessage"])
        if not BE_QUIET and len(state["soundName"]):
            logging.debug("Попытка проиграть звук")
            sound = winsound.PlaySound(os.path.join(WORKING_DIR, "wav_phrases", state["soundName"]), winsound.SND_FILENAME)
            logging.debug("Звук успешно проигран %s" % str(sound))
        logging.debug("%s %s" % (state["title"], state["isHideWidgets"]))
        if not state["isHideWidgets"]:
            showGames(state["title"], state["games"])


def serializeAllGames():
    for game_entry in feed.entries:
        g = Game(game_entry.summary)
        logging.debug(u'Сериализация игры %s' % g.name)
        loadedFromSiteGames[g.name] = g

logging.info('Парсинг RSS новостей с сайта ctftime.org')
feed = feedparser.parse("https://ctftime.org/event/list/upcoming/rss/")
loadedFromSiteGames = {}
serializeAllGames()

if SHOW_ALL_GAMES:
    showGames("Ближайшие игры", loadedFromSiteGames.values())

states = {"isNewGame": {"state": False,
                        "games": [],
                        "title": "Новые игры",
                        "soundName": "new_game_phrase.wav",
                        "debugMessage": "Есть новые игры",
                        "isHideWidgets": False
                        },

          "isNewTime": {"state": False,
                        "games": [],
                        "title": "Изменилось время",
                        "soundName": "new_time_phrase.wav",
                        "debugMessage": "Есть игры с изменившимся временем",
                        "isHideWidgets": False
                        },

          "isNewTeams": {"state": False,
                         "games": [],
                         "title": "Новые команды",
                         "soundName": "new_teams_phrase.wav",
                         "debugMessage": "Есть игры с изменившимся числом команд",
                         "isHideWidgets": True
                         },

          "isGameStart": {"state": False,
                          "games": [],
                          "title": "Стартовали игры",
                          "soundName": "",
                          "debugMessage": "Есть начавшиеся игры",
                          "isHideWidgets": False
                          },

          "isGameWillStartInHour": {"state": False,
                                    "games": [],
                                    "title": "Начнутся через час",
                                    "soundName": "",
                                    "debugMessage": "Есть игры которые начнутся через час",
                                    "isHideWidgets": False
                                    },

          "isGameWillStartInDay": {"state": False,
                                   "games": [],
                                   "title": "Начнутся через день",
                                   "soundName": "",
                                   "debugMessage": "Есть игры которые начнутся через день",
                                   "isHideWidgets": False
                                   }
          }
# loadedFromSiteGames = {}

now_time = dt.datetime.now()
if QUIET_HOURS["from"] < now_time.time() or now_time.time() < QUIET_HOURS["to"]:
    logging.debug('Включен режим тишины')
    BE_QUIET = True

try:
    loadedFromFileGames = cPickle.loads(open(os.path.join(WORKING_DIR, 'upcoming_ctf.txt'), 'r').read())
except IOError:
    logging.exception("Ошибка загрузки старых игр")
    open(os.path.join(WORKING_DIR, 'upcoming_ctf.txt'), 'w').write(cPickle.dumps(loadedFromSiteGames))
    exit()
# loadedFromSiteGames = loadedFromFileGames.copy()
# loadedFromSiteGames["AltayCTF"].teams += 10
logging.debug('Начинаем перебор новых игр')
for gameName, gameFromSite in loadedFromSiteGames.items():
    if gameFromSite.isHidden:
        logging.debug("game %s is hidden" % gameName)
        continue
    daysHours = gameFromSite.GetDaysHoursBeforeGame()

    if((daysHours['days'] == 1) and (daysHours['hours'] == 0)):
        logging.debug(u"Игра %s начнется через 1 день" % gameName.decode("utf8"))
        states["isGameWillStartInDay"]["state"] = True
        states["isGameWillStartInDay"]["games"].append(gameFromSite)

    if((daysHours['days'] == 0) and (daysHours['hours'] == 1)):
        logging.debug(u"Игра %s начнется через 1 час" % gameName.decode("utf8"))
        states["isGameWillStartInHour"]["state"] = True
        states["isGameWillStartInHour"]["games"].append(gameFromSite)

    if (gameFromSite.date['start'] < now_time < gameFromSite.date['end']):
        logging.debug(u"Сейчас идет игра %s" % gameName.decode("utf8"))
        states["isGameStart"]["state"] = True
        states["isGameStart"]["games"].append(gameFromSite)

    if gameName in loadedFromFileGames.keys():
        if loadedFromFileGames[gameName].date != gameFromSite.date:
            logging.debug(u"Изменили время игры %s" % gameName.decode("utf8"))
            states["isNewTime"]["state"] = True
            states["isNewTime"]["games"].append(gameFromSite)

        if loadedFromFileGames[gameName].teams == gameFromSite.teams:
            logging.debug(u"Изменили количество команд %s" % gameName.decode("utf8"))
            states["isNewTeams"]["state"] = True
            states["isNewTeams"]["games"].append(gameFromSite)
    else:
        logging.debug(u"%s нету среди %s, значит она новая" % (gameName, str(loadedFromFileGames.keys())))
        states["isNewGame"]["state"] = True
        states["isNewGame"]["games"].append(gameFromSite)

for state in states.values():
    notifyAboutGames(state)

logging.debug("Заносим все новые игры в файл")
if loadedFromSiteGames.keys():
    open(os.path.join(WORKING_DIR, 'upcoming_ctf.txt'), 'w').write(cPickle.dumps(loadedFromSiteGames))
