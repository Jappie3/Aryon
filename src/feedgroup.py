class FeedGroup:
    def __init__(self, title, feeds):
        self.title = title
        self.feeds = feeds

    def update(self):
        for feed in self.feeds:
            feed.update()
