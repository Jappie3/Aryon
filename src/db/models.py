from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Model


class User(Model):
    """
    User model, represents a user
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # unique subject identifier from the OpenID Connect provider
    # todo consider making this the primary key (make sure to check if it's unique (should be))
    oidc_sub: Mapped[str] = mapped_column(String, unique=True)

    feeds: Mapped[list['RssFeed']] = relationship(
        cascade="all, delete-orphan", back_populates='user'
    )

    def __init__(self, oidc_sub, name=''):  # default to empty string
        self.name = name
        self.oidc_sub = oidc_sub


class RssFeed(Model):
    """
    RSS Feed model, represents an RSS feed
    """
    __tablename__ = 'rss_feeds'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id')
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    # note = Column(String) # todo maybe add the ability to add notes to a feed?
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    feed_articles: Mapped[list['FeedArticle']] = relationship(
        cascade="all, delete-orphan", back_populates='feed'
    )

    user: Mapped['User'] = relationship(
        back_populates='feeds'
    )

    def __init__(self, title, url, user_id=0):  # default to userid 0 -> does not exist (starts an 1)
        self.title = title
        self.url = url
        self.user_id = user_id


class FeedArticle(Model):
    """
    Feed Article model, represents an article from an RSS feed
    """
    # todo boolean to indicate if article has been read
    __tablename__ = 'feed_articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('rss_feeds.id')
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str]
    date = Column(DateTime, default=datetime.utcnow)
    # date: Mapped[datetime] = Column(DateTime, nullable=False)

    feed: Mapped['RssFeed'] = relationship(
        back_populates='feed_articles'
    )

    def __init__(self, feed_id, title, url, summary, date):
        self.title = title
        self.url = url
        self.feed_id = feed_id
        self.summary = summary
        self.date = date
