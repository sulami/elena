from sqlalchemy import Column, String, DateTime

from elena.database import Database

class Status(Database.Base):
    """Base status class"""

    __tablename__ = 'stati'
    name = Column(String(50), primary_key=True)
    status = Column(String(12))
    update_time = Column(DateTime)

    def __init__(self, name, status):
        self.name = name
        self.update(status)

    def __repr__(self):
        return '[{}] {}: {}'.format(
                                self.update_time.strftime('%Y-%m%d %H:%M:%S'),
                                self.name, self.status)

    def update(self, status):
        self.status = status
        update_time = Column(DateTime)

