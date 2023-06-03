from flask import Flask, render_template, jsonify, request
from urllib.parse import unquote
from dotenv import load_dotenv
from feed import Feed
from feedgroup import FeedGroup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from util.db import Model
from util.models import RssFeed, FeedArticle
import feedparser
import os


def db_init():
    load_dotenv()
    print(f"Database URL: {os.getenv('DATABASE_URL')}")
    engine = create_engine(os.getenv("DATABASE_URL"))
    global Session
    Session = sessionmaker(engine)
    Model.metadata.drop_all(engine)
    Model.metadata.create_all(engine)
    # todo don't make this hardcoded
    theorangeone = RssFeed(title="TheOrangeOne", url="https://theorangeone.net/posts/feed")
    vrtnws = RssFeed(title="VRT NWS", url="https://www.vrt.be/vrtnws/en.rss.articles.xml")
    hackernews = RssFeed(title="HackerNews", url="https://news.ycombinator.com/rss")
    feeds = [theorangeone, vrtnws, hackernews]
    with Session() as session:
        try:
            session.add_all(feeds)
            session.commit()
        except:
            session.rollback()
            raise
        print(f"Added {len(feeds)} feeds to database")
    # populate the database with articles for all the feeds
    for feed in get_feeds():
        feed_articles = feedparser.parse(feed.url).entries
        articles = []
        for feed_article in feed_articles:
            articles.append(FeedArticle(feed_id=feed.id, title=feed_article.title, url=feed_article.link, summary=feed_article.summary))
        with Session() as session:
            try:
                session.add_all(articles)
                session.commit()
            except:
                session.rollback()
                raise
            print(f"Added {len(articles)} articles to database")

def get_feeds():
    """
    Get all feeds from the database
    """
    feeds = []
    with Session() as session:
        feeds = session.query(RssFeed).all()
    # for feed in feeds:
    #     print(f"Loaded feed: {feed.title} {feed.url}")
    return feeds


def get_articles(feed_id):
    """
    Get all articles for a given feed
    """
    articles = []
    with Session() as session:
        articles = session.query(FeedArticle).filter(FeedArticle.feed_id == feed_id).all()
    for article in articles:
        print(f"Loaded article: {article.title} {article.url}")
    return articles


# use the get_feeds and get_articles methods to create feed objects


def db_test():
    theorangeone = RssFeed(title="TheOrangeOne", url="https://theorangeone.net")
    feed_articles = feedparser.parse("https://theorangeone.net/posts/feed/").entries
    articles = []
    for feed_article in feed_articles:
        articles.append(FeedArticle(feed_id=theorangeone.id, title=feed_article.title, url=feed_article.link, summary=feed_article.summary))#, date=feed_article.published))

    with Session() as session:
        try:
            session.add(theorangeone)
            session.commit()
        except:
            session.rollback()
            raise
        print(f"Added {theorangeone} to database")

    with Session() as session:
        try:
            session.add_all(articles)
            session.commit()
        except:
            session.rollback()
            raise
        print(f"Added {len(articles)} articles to database")


app = Flask(__name__, static_folder="templates/static")

# feeds = [
#     Feed("https://news.ycombinator.com/rss", "HackerNews"),
#     FeedGroup(
#         "News",
#         [
#             Feed("https://www.vrt.be/vrtnws/en.rss.articles.xml", "VRT NWS"),
#             Feed("https://feeds.feedburner.com/tweakers/mixed", "Tweakers"),
#         ],
#     ),
#     FeedGroup(
#         "Tech", [Feed("https://theorangeone.net/posts/feed/", "TheOrangeOne")]
#     ),
# ]


@app.route("/")
def index():
    return render_template("index.html", feeds=feeds)


@app.route('/api/feedgroup')
def api_feedgroup():
    feed_url = unquote(request.args.get('url'))
    # feedgroup = FeedGroup.query.get(id)
    # return jsonify(feedgroup.to_dict())


@app.route('/api/feed')
def api_feed():
    feed_url = unquote(request.args.get('url'))
    feed_articles = feedparser.parse(feed_url).entries
    return feed_articles
    # feed = Feed.query.get(id)
    # return jsonify(feed.to_dict())


def main():
    db_init()
    feeds = get_feeds()
    for feed in feeds:
        get_articles(feed.id)
    # db_test()
    # app.run(debug=True)


if __name__ == "__main__":
    main()
