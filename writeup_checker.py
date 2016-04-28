#-*- coding: utf-8 -*-
from writeup import WriteUp
import feedparser


class WriteUpChecker:

    def __init__(self):
        print "Wait data"
        self.writeUpsList = self._getWriteUpsList()
        print "All data has been received"

    def _getWriteUpsList(self):
        result = []
        feed = feedparser.parse("https://ctftime.org/writeups/rss/")
        print "Feed received"
        print len(feed)
        for writeup_entry in feed.entries:
            result.append(WriteUp(writeup_entry))
        print "List was collected"
        return result

    def getWriteUpsByTaskName(self, taskName):
        result = []
        for writeup in self.writeUpsList:
            if writeup.task == taskName:
                result.append(writeup)
        return result

    def getWriteUpsByGameName(self, gameName):
        result = []
        for writeup in self.writeUpsList:
            if writeup.event == gameName:
                result.append(writeup)
        return result

    def getWriteUpsByTags(self, tagsList, allTags=True):
        result = []
        for writeup in self.writeUpsList:
            if allTags:
                if self._isAllItemsAreEqual([(tag in writeup.tags) for tag in tagsList]):
                    result.append(writeup)
            else:
                if self._isAnyItemsAreEqual([(tag in writeup.tags) for tag in tagsList]):
                    result.append(writeup)
        return result

    def getWriteUpsByAuthor(self, author):
        result = []
        for writeup in self.writeUpsList:
            if writeup.authorTeam == author:
                result.append(writeup)
        return result

    def _isAllItemsAreEqual(self, collection):
        return all(True == item for item in collection)

    def _isAnyItemsAreEqual(self, collection):
        return any(True == item for item in collection)

if __name__ == "__main__":
    print "Start"
    w = WriteUpChecker()
    print len(w.getWriteUpsByTags(["reverse"]))
    print len(w.getWriteUpsByTags(["binary", "exploitation"], False))
    print len(w.getWriteUpsByTags(["crypto", "forensics"], False))
