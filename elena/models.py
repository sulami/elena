from datetime import datetime

from flask import jsonify
from sqlalchemy import ( Column,
                         Integer,
                         String,
                         DateTime,
                         Boolean,
                         Interval,
                         ForeignKey,
                         desc )
from sqlalchemy.orm import relationship
from elena.database import Database

class Status(Database.Base):
    """Base status class"""

    __tablename__ = 'stati'
    name = Column(String(50), primary_key=True)
    history = Column(Boolean)
    data_points = relationship('DataPoint', order_by=desc('update_time'),
                               lazy='dynamic')
    pull = Column(Boolean)
    pull_url = Column(String(200))
    pull_time = Column(Interval)

    def __init__(self, name, status):
        self.name = name
        self.update(status)

    def __repr__(self):
        return self.data_points.first().__repr__()

    def set_pull(self, url, time):
        self.pull = True
        self.pull_url = url
        self.pull_time = time

    def set_push(self):
        self.pull = False
        self.pull_url = None
        self.pull_time = None

    def update(self, status):
        # TODO history management
        self.data_points.append(DataPoint(self, status))

    def get(self):
        if self.pull and datetime.now() - self.update_time > self.pull_time:
            # TODO pull status
            pass
        status = self.data_points.first()
        return jsonify(name=self.name, status=status.status,
                       update_time=status.update_time)

    def get_history(self):
        # TODO return history if needed
        pass

class DataPoint(Database.Base):
    """datapoint for history creation"""

    __tablename__ = 'hist'
    id = Column(Integer, primary_key=True)
    status_name = Column(String(50), ForeignKey('stati.name'))
    status = Column(String(12))
    update_time = Column(DateTime)

    def __init__(self, status, value):
        self.status_id = status.name
        self.status = value
        self.update_time = datetime.now()

    def __repr__(self):
        return '[{}] {}: {}'.format(
                                self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                                self.status_name, self.status)

