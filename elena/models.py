from sqlalchemy import Column, Integer, String, Boolean, Float

from elena.database import Database

class Status(Database.Base):
    """Base status class to inherit from"""

    __tablename__ = 'stati'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    def __init__(self, name, status):
        self.name = name
        self.set_status(status)

    def __repr__(self):
        return '{}: {}'.format(self.name, self.get_status())

class BooleanStatus(Status):
    """Expresses a boolean status, e.g. up or down"""

    bstatus = Column(Boolean)

    def get_status(self):
        return self.bstatus

    def set_status(self, status):
        self.bstatus = status

class NumberStatus(Status):
    """Expresses a whole number status, e.g. number of pageviews"""

    nstatus = Column(Integer)

    def get_status(self):
        return self.nstatus

    def set_status(self, status):
        self.nstatus = status

class FloatStatus(Status):
    """Expresses a floating point status, e.g. a response time"""

    fstatus = Column(Float)

    def get_status(self):
        return self.fstatus

    def set_status(self, status):
        self.fstatus = status

class StringStatus(Status):
    """Expresses a string status, which can be anything"""

    sstatus = Column(String(100))

    def get_status(self):
        return self.sstatus

    def set_status(self, status):
        self.sstatus = status

