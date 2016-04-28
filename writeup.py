# -*- coding: utf-8 -*-
import re
import requests
import lxml.html as lh


class WriteUp:

    def __init__(self, entry):
        self.CTFTimeLink = self._getCTFTimeLink(entry)
        self.__WriteUpPage = self._getHTMLpage(self.CTFTimeLink)
        self.writeUpLink = self._getWriteUpLink(self.__WriteUpPage)
        self.raiting = self._getRaiting(self.__WriteUpPage)
        self.task = self._getTask(self.__WriteUpPage)

        self.__WriteUpsPage = self._getHTMLpage(u"https://ctftime.org/writeups")
        self.taskLink = self._getTaskLink(self.__WriteUpsPage)
        self.event = self._getEvent(self.__WriteUpsPage)
        self.tags = self._getTag(self.__WriteUpsPage)
        self.authorTeam = self._getAuthorTeam(self.__WriteUpsPage)

        self.__TaskPage = self._getHTMLpage(self.taskLink)
        self.points = self._getPoints(self.__TaskPage)
        self.description = self._getDescription(self.__TaskPage)

    def _getCTFTimeLink(self, entry):
        return entry.link

    def _getHTMLpage(self, link):
        try:
            r = requests.get(link, verify=False)
            return lh.document_fromstring(r.text.encode('utf-8'))
        except:
            return None

    def _getWriteUpLink(self, html):
        try:
            tags = html.xpath("//div[@class='well']")
            return tags[-1][0].get("href")
        except:
            return ""

    def _getRaiting(self, html):
        try:
            tags = html.xpath("//span[@id='user_rating']")
            if len(tags) == 1:
                return float(tags[0].text_content())
        except:
            pass
        return 0.0

    def _getTask(self, html):
        try:
            tags = html.xpath("//div[@class='page-header']/h2")
            return tags[0].text_content()
        except:
            return ""

    def _getTaskLink(self, html):
        try:
            tags = html.xpath(u"""//tr[td/a/text()="{0}"]""".format(self.task))
            return u"https://ctftime.org{0}".format(tags[0][1][0].get("href"))
        except:
            return ""

    def _getEvent(self, html):
        try:
            tags = html.xpath(u"""//tr[td/a/text()="{0}"]""".format(self.task))
            return tags[0][0][0].text_content()
        except:
            return [""]

    def _getTag(self, html):
        try:
            tags = html.xpath(u"""//tr[td/a/text()="{0}"]""".format(self.task))
            return tags[0][2].text_content().split(", ")
        except:
            return ""

    def _getAuthorTeam(self, html):
        try:
            tags = html.xpath(u"""//tr[td/a/text()="{0}"]""".format(self.task))
            return tags[0][3][0].text_content()
        except:
            return ""

    def _getDescription(self, html):
        try:
            tags = html.find_class('well')
            return tags[0][0].text_content()
        except:
            return ""

    def _getPoints(self, html):
        try:
            tags = html.xpath("//div[@class=container]/p/text()")
            for tag in tags:
                result = re.search("Points\: (\d+)", tag).group(1)
                if len(result):
                    return int(result, 10)
            return 0
        except:
            return 0

    def __str__(self):
        s = u"Событие: {0}\n\
Таск: {1}\n\
Тэг: {2}\n\
Автор: {3}\n\
Рейтинг: {4}\n\
Очки: {5}\n\
Описание: {6}\n\
Ссылка на ctftime: {7}\n\
Ссылка на райтап: {8}\n\
Ссылка на таск: {9}\n".format(self.event, self.task, self.tags, self.authorTeam, self.raiting, self.points, self.description, self.CTFTimeLink, self.writeUpLink, self.taskLink)
        return s.encode("utf8")

if __name__ == "__main__":
    import feedparser
    feed = feedparser.parse("https://ctftime.org/writeups/rss/")
    for writeup_entry in feed.entries:
        w = WriteUp(writeup_entry)
        print str(w).decode("utf8")
        print '-'*60
