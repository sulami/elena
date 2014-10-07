from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import DefaultConfig

class Database:
    """Database object to encapsulate all database interactions"""

    Base = declarative_base()

    def __init__(self, uri):
        self.engine = create_engine(uri, convert_unicode=True)
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   expire_on_commit=True,
                                                   bind=self.engine))
        self.Base.query = self.session.query_property()

        import elena.models
        self.Base.metadata.create_all(bind=self.engine)

