from db.models import RssFeed, FeedArticle, User
from util.db_session import db_session


def get_feeds(user_sub):
    """
    Get all feeds from the database for a given user
    :param user_sub: ID of the user to get feeds for, defaults to 0
    """
    with db_session() as dbsession:
        return dbsession.query(RssFeed).filter(RssFeed.user_sub == user_sub).all()


def get_articles(feed_id):
    """
    Get all articles for a given feed
    :param feed_id: ID of the feed to get articles for
    """
    with db_session() as dbsession:
        return dbsession.query(FeedArticle).filter(FeedArticle.feed_id == feed_id).all()


def get_users():
    """
    Get all users from the database
    """
    with db_session() as dbsession:
        return dbsession.query(User).all()
