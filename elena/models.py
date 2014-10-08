from datetime import datetime, timedelta

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
                               lazy='dynamic',
                               cascade='all, delete, delete-orphan')
    pull = Column(Boolean)
    pull_url = Column(String(200))
    pull_time = Column(Interval)

    def __init__(self, name, status):
        self.name = name
        self.update(status)

    def __repr__(self):
        return self.__get__().__repr__()

    def __get__(self):
        return self.data_points.first()

    def __pull__(self):
        # TODO actually pull the status
        pass

    def update(self, status):
        if not self.history:
            d = self.__get__()
            if d:
                d.update(status)
                return
        self.data_points.append(DataPoint(self, status))

    def get(self):
        if self.pull and (datetime.now() - self.__get__().update_time
                          > self.pull_time):
            self.__pull__()
        return self.__get__().get()

    def get_history(self):
        if self.history:
            return jsonify(history=[d.serialize() for d
                                    in self.data_points.all()])
        return self.get()

    def set_pull(self, url, time):
        self.pull = True
        self.pull_url = url
        self.pull_time = timedelta(time)

    def set_push(self):
        self.pull = False
        self.pull_url = None
        self.pull_time = None

class DataPoint(Database.Base):
    """Datapoint for history creation"""

    __tablename__ = 'hist'
    id = Column(Integer, primary_key=True)
    status_name = Column(String(50), ForeignKey('stati.name'))
    status = Column(String(12))
    update_time = Column(DateTime)

    def __init__(self, status, value):
        self.status_id = status.name
        self.update(value)

    def __repr__(self):
        return '[{}] {}: {}'.format(
                                self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                                self.status_name, self.status)

    def update(self, value):
        self.status = value
        self.update_time = datetime.now()

    def get(self):
        return jsonify(name=self.status_name, status=self.status,
                       update_time=self.update_time)

    def serialize(self):
        return { 'status': self.status, 'update_time': self.update_time }

