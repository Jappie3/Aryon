from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.db import Model
from util.config import config


class DatabaseSession:
    """
    DatabaseSession is a singleton class that creates a database session
    """
    _instance = None

    def __init__(self):
        drop_database = config["DEBUG_DROP_DATABASE_ON_RESTART"]
        engine = create_engine(config["DATABASE_URL"])
        # drop database if DEBUG_DROP_DATABASE_ON_RESTART is set to True
        if drop_database:
            # todo test behaviour with persistent database
            Model.metadata.drop_all(engine)
        # create all tables in the database
        Model.metadata.create_all(engine)
        self.Session = sessionmaker(engine)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseSession, cls).__new__(cls, *args, **kwargs)
        return cls._instance


# create an instance of DatabaseSession
db_session = DatabaseSession().Session
