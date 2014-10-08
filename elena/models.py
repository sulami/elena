from datetime import datetime

from flask import jsonify
from sqlalchemy import Column, String, DateTime, Boolean, Interval

from elena.database import Database

class Status(Database.Base):
    """Base status class"""

    __tablename__ = 'stati'
    name = Column(String(50), primary_key=True)
    status = Column(String(12))
    update_time = Column(DateTime)
    pull = Column(Boolean)
    pull_url = Column(String(200))
    pull_time = Column(Interval)

    def __init__(self, name, status):
        self.name = name
        self.update(status)

    def __repr__(self):
        return '[{}] {}: {}'.format(
                                self.update_time.strftime('%Y-%m-%d %H:%M:%S'),
                                self.name, self.status)

    def set_pull(self, url, time):
        self.pull = True
        self.pull_url = url
        self.pull_time = time

    def set_push(self):
        self.pull = False
        self.pull_url = None
        self.pull_time = None

    def update(self, status):
        self.status = status
        self.update_time = datetime.now()

    def get(self):
        if self.pull and datetime.now() - self.update_time > self.pull_time:
            # TODO pull status
            pass
        return jsonify(name=self.name, status=self.status,
                       update_time=self.update_time)

