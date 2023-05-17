from flask import Flask, render_template, jsonify, request
from urllib.parse import unquote
from feed import Feed
from feedgroup import FeedGroup
from feedindex import FeedIndex
import feedparser

app = Flask(__name__, static_folder="templates/static")


feeds = [
    Feed("https://news.ycombinator.com/rss", "HackerNews"),
    FeedGroup(
        "News",
        [
            Feed("https://www.vrt.be/vrtnws/en.rss.articles.xml", "VRT NWS"),
            Feed("https://feeds.feedburner.com/tweakers/mixed", "Tweakers"),
        ],
    ),
    FeedGroup(
        "Tech", [Feed("https://theorangeone.net/posts/feed/", "TheOrangeOne")]
    ),
    Feed("https://news.ycombinator.com/rss", "HackerNews"),
]


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


if __name__ == "__main__":
    app.run(debug=True)
