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
        assert 201 == rv.status_code

    def test_status_existence(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == rv.data
        assert 200 == rv.status_code

    def test_status_nonexistence(self):
        rv = self.client.get('/get/notup/')
        assert 404 == rv.status_code

    def test_status_update(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == rv.data
        assert 200 == rv.status_code

        rv = self.client.post('/set/up/', data=dict(value="False"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "False" == rv.data
        assert 200 == rv.status_code

    def test_status_deletion(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == rv.data
        assert 200 == rv.status_code

        rv = self.client.get('/del/up/')
        assert 204 == rv.status_code

        rv = self.client.get('/get/up/')
        assert 404 == rv.status_code

        rv = self.client.get('/del/up/')
        assert 404 == rv.status_code

class MetaTestCase(BasicTestCase):
    """Test general function"""

    def test_status_page(self):
        rv = self.client.get('/status/')
        assert "0" in rv.data

        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.get('/status/')
        assert "1" in rv.data

        self.client.post('/set/down/', data=dict(value="False"))
        rv = self.client.get('/status/')
        assert "2" in rv.data

        self.client.post('/set/down/', data=dict(value="True"))
        rv = self.client.get('/status/')
        assert "2" in rv.data

        self.client.get('/del/down/')
        rv = self.client.get('/status/')
        assert "1" in rv.data

if __name__ == "__main__":
    unittest.main()

