from datetime import datetime, timedelta
from urllib2 import urlopen, Request

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
                               lazy='dynamic', backref='status',
                               cascade='all, delete, delete-orphan')
    pull = Column(Boolean)
    pull_url = Column(String(200))
    pull_time = Column(Interval)

    def __init__(self, name, value):
        self.name = name
        self.update(value)

    def __repr__(self):
        return self.__get__().__repr__()

    def __get__(self):
        return self.data_points.first()

    def update(self, value):
        if not self.history:
            d = self.__get__()
            if d:
                d.update(value)
                return
        self.data_points.append(DataPoint(self, value))

    def get(self):
        return self.__get__().get()

    def get_history(self):
        if self.history:
            return jsonify(history=[d.serialize() for d
                                    in self.data_points.all()])
        return self.get()

    def pull_update(self):
        try:
            self.update(urlopen(Request(self.pull_url), timeout=2).readline())
        except:
            self.update("Error pulling status update from {}"
                        .format(self.pull_url))

class DataPoint(Database.Base):
    """Datapoint for history creation"""

    __tablename__ = 'hist'
    id = Column(Integer, primary_key=True)
    status_name = Column(String(50), ForeignKey('stati.name'))
    value = Column(String(12))
    update_time = Column(DateTime)

    def __init__(self, status, value):
        self.status_name = status.name
        self.update(value)

    def __repr__(self):
        return '[{}] {}: {}'.format(
                                self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                                self.status_name, self.value)

    def update(self, value):
        self.value = value
        self.update_time = datetime.now()

    def get(self):
        return jsonify(name=self.status_name, status=self.value,
                       update_time=self.update_time)

    def serialize(self):
        return { 'status': self.value, 'update_time': self.update_time }

