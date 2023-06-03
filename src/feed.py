import requests
import feedparser


class Feed:
    def __init__(self, url, title):
        self.url = url
        self.title = title

    def update(self):
        feed = feedparser.parse(self.url)
        articles = feed.entries
        return articles


#    def fetch_data(self):
#        # fetch raw xml data
#        # return requests.get(self.url).content
#        return feedparser.parse(self.url)


#    def parse_data(self, data):
#        # extract necessary information
#        return feedparser.parse()
#        pass
