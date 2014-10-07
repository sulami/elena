import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import run
from config import TestConfig
from elena.database import Database

class BasicTestCase(unittest.TestCase):
    """Unify setup and teardown, verify server starts up"""

    def setUp(self):
        run.app.config.from_object('config.TestConfig')
        run.init_db()
        self.client = run.app.test_client()

    def tearDown(self):
        run.app.db.session.remove()

    def test_server_up(self):
        return self.client.get('/')

class StatusTestCase(BasicTestCase):
    """Test basic status operations"""

    def test_status_creation(self):
        return self.client.post('/set/up/', data=dict(value="True"))

    def test_status_existence(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.get('/get/up/')
        assert "True" == rv.data

    def test_status_nonexistence(self):
        rv = self.client.get('/get/notup/')
        assert 404 == rv.status_code

    def test_status_update(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.get('/get/up/')
        assert "True" == rv.data
        self.client.post('/set/up/', data=dict(value="False"))
        rv = self.client.get('/get/up/')
        assert "False" == rv.data

if __name__ == "__main__":
    unittest.main()

