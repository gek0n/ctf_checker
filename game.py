# -*- coding: utf-8 -*-
import re
import requests
import lxml.html as lh
import datetime as dt
import logging


class Game:

    def __init__(self, game_row):
        self.reg_name = re.compile("Name: ([\w\s]+)")
        self.name = self.GetName(game_row)
        self.type = self.GetType(game_row)
        self.local_page = self.GetLocalPage(game_row)
        self.date = self.GetDate(game_row)
        self.duration = self.GetDuration(game_row)

        r = requests.get(self.local_page, verify=False)
        html = lh.document_fromstring(r.text)
        table = html.find_class('span10')[0]

        self.teams = self.GetTeams(html)
        self.state = self.GetState(html)
        self.place_type = self.GetPlaceType(table)
        self.site = self.GetSite(table)
        self.isHidden = False
        self.rank = self.GetRank(table)

    def __str__(self):
        s = u"Игра: %s\nТип: %s\nСостояние: %s\nСсылка: %s\nДата проведения: с %s по %s\nКоличество команд: %d\nПродолжительность: %d дней %d часов\nМесто проведения: %s\nСайт игры: %s\nРанг: %.2f\n" \
            % (self.name, self.type, self.state.decode("utf8"), self.local_page, self.date['start'].strftime("%d %B %Y года в %H:%M").decode("utf8"), self.date['end'].strftime("%d %B %Y года в %H:%M").decode("utf8"), self.teams, self.duration['days'], self.duration['hours'], self.place_type.decode("utf8"), self.site.decode("utf8"), self.rank)
        return s.encode("utf8")

    def GetName(self, game_row):
        return re.search("Name: ([\w\s]+)", game_row.split('\n')[0]).group(1)

    def GetType(self, game_row):  # Получаем тип игры (Jeopardy или Classic)
        return re.search("Format: ([\w\s]+)", game_row).group(1)

    def GetState(self, game_row):
        if len(game_row.find_class('page-header')[0][0]):
            return 'running'
        else:
            return 'upcoming'

    def GetLocalPage(self, game_row):  # Получаем ссылку на страницу игры на сайте ctftime.org
        return re.search("https\:\/\/ctftime\.org\/event\/\d+", game_row).group(0)

    def GetDate(self, game_row):
        dates = re.search("Date: ([\w\s/:/.,]+) &mdash; ([\w\s/:/.,]+)", game_row)
        date = {'start': dt.timedelta.min, 'end': dt.timedelta.min}
        start, end = dates.group(1), dates.group(2)
        start = start.replace("Sept", "Sep").replace("midnight", "12 AM").replace("March", "Mar.").replace("April", "Apr.").replace("May", "May.").replace("June", "Jun.").replace("Jule", "Jul.")
        start = start.replace("p.m.", "PM").replace("a.m.", "AM").replace("noon", "12 PM")
        end = end.replace("Sept", "Sep").replace("March", "Mar.").replace("April", "Apr.").replace("May", "May.").replace("June", "Jun.").replace("Jule", "Jul.")
        end = end.strip(" UTC ")
        try:
            date['start'] = dt.datetime.strptime(start, "%b. %d, %Y, %I:%M %p")
        except ValueError:
            logging.exception(u"Ошибка перевода даты начала игры")
            date['start'] = dt.datetime.strptime(start, "%b. %d, %Y, %I %p")
        date['start'] = date['start'] + dt.timedelta(hours=3)
        try:
            date['end'] = dt.datetime.strptime(end, "%d %b. %Y, %H:%M")
        except ValueError:
            logging.exception(u"Ошибка перевода даты завершения игры")
            date['end'] = dt.datetime.strptime(end, "%d %b. %Y, %H")
        date['end'] = date['end'] + dt.timedelta(hours=3)
        return date

    def GetTeams(self, game_row):
        teams = game_row.xpath('.//p[contains(text(),"teams total")]')
        if len(teams):
            return int(teams[0].text.split(' ')[0])
        else:
            return 0

    def GetDuration(self, game_row):
        dur = self.date['end'] - self.date['start']
        time = {'days': 0, "hours": 0}
        time['days'] = dur.days
        time['hours'] = dur.seconds // 3600
        return time

    def GetPlaceType(self, game_row):
        try:
            result = game_row[1].text_content().encode('utf-8', 'ignore')
        except:
            logging.exception(u"Ошибка распознавания места игры")
            result = ""
        return result

    def GetSite(self, game_row):
        try:
            result = game_row[5][0].text.encode('utf-8', 'ignore')
        except:
            logging.exception(u"Ошибка распознавания сайта игры")
            result = ""
        return result

    def GetRank(self, game_row):
        try:
            result = float(re.search("\d+.\d+", game_row[6].text.encode('utf-8', 'ignore')).group(0))
        except:
            logging.exception(u"Ошибка распознавания рейтинга игры")
            result = 0
        return result

    def GetDaysHoursBeforeGame(self):
        now_time = dt.datetime.now()
        result = self.date['start'] - now_time
        return {'days': result.days, 'hours': result.seconds // 3600}
