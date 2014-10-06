class Status:
    """Base status class to inherit from"""
    def __init__(self, status):
        self.status = status

class BooleanStatus(Status):
    """Expresses a boolean status, e.g. up or down"""
    pass

class NumberStatus(Status):
    """Expresses a whole number status, e.g. number of pageviews"""
    pass

class FloatStatus(Status):
    """Expresses a floating point status, e.g. a response time"""
    pass

class StringStatus(Status):
    """Expresses a string status, which can be anything"""
    pass

