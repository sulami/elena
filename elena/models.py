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
        self.set(value)

    def get_recent(self):
        return self.data_points.first()

    def set(self, value):
        if not self.history:
            d = self.get_recent()
            if d:
                d.set(value)
                return
        self.data_points.append(DataPoint(self, value))

    def get(self):
        return self.get_recent().get()

    def get_history(self):
        if self.history:
            return jsonify(history=[d.serialize() for d
                                    in self.data_points.all()])
        return self.get()

    def pull_update(self):
        try:
            self.set(urlopen(Request(self.pull_url), timeout=2).readline())
        except:
            self.set("Error pulling status update from {}"
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
        self.set(value)

    def set(self, value):
        self.value = value
        self.update_time = datetime.now()

    def get(self):
        return jsonify(name=self.status_name, status=self.value,
                       update_time=self.update_time)

    def serialize(self):
        return { 'status': self.value, 'update_time': self.update_time }

