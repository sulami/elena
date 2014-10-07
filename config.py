class DefaultConfig():
    DEBUG = True
    TESTING = False

    DB_URI = 'sqlite:////home/sulami/build/elena/db.sqlite'

class TestConfig(DefaultConfig):
    DEBUG = False
    TESTING = True

    DB_URI = 'sqlite:///:memory:'

class ProductionConfig(DefaultConfig):
    DEBUG = False

