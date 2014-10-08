import time
import unittest
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from flask.json import loads
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from elena.database import Database
from run import app, init_db

class BasicTestCase(unittest.TestCase):
    """Unify setup and teardown, verify server starts up"""

    def setUp(self):
        app.config.from_object('config.TestConfig')
        init_db()
        self.client = app.test_client()

    def tearDown(self):
        app.db.session.remove()

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
        assert "True" == loads(rv.data)['status']
        assert 200 == rv.status_code

    def test_status_nonexistence(self):
        rv = self.client.get('/get/notup/')
        assert 404 == rv.status_code

    def test_status_update(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == loads(rv.data)['status']
        assert 200 == rv.status_code

        rv = self.client.post('/set/up/', data=dict(value="False"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "False" == loads(rv.data)['status']
        assert 200 == rv.status_code

    def test_status_deletion(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == loads(rv.data)['status']
        assert 200 == rv.status_code

        rv = self.client.get('/del/up/')
        assert 204 == rv.status_code

        rv = self.client.get('/get/up/')
        assert 404 == rv.status_code

        rv = self.client.get('/del/up/')
        assert 404 == rv.status_code

    def test_status_timestamp(self):
        self.client.post('/set/up/', data=dict(value="True"))
        old = loads(self.client.get('/get/up/').data)['update_time']

        time.sleep(1) # Ensure we get a different timestamp

        self.client.post('/set/up/', data=dict(value="True"))
        new = loads(self.client.get('/get/up/').data)['update_time']

        assert old != new

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

class HistoryTestCase(BasicTestCase):
    """Test the status history functionality"""

    def test_history_disabled(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "True" == loads(rv.data)['status']
        assert 200 == rv.status_code

        rv = self.client.post('/set/up/', data=dict(value="False"))
        assert 201 == rv.status_code

        rv = self.client.get('/get/up/')
        assert "False" == loads(rv.data)['status']
        assert 200 == rv.status_code
        assert "history" not in rv.data
        assert "True" not in rv.data
        assert "False" == loads(rv.data)['status']

    def test_check_history(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(history="True"))
        assert 200 == rv.status_code

        self.client.post('/set/up/', data=dict(value="False"))
        rv = self.client.get('/his/up/')
        assert 200 == rv.status_code
        assert "True" in rv.data
        assert "False" in rv.data

    def test_delete_history(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(history="True"))
        assert 200 == rv.status_code

        self.client.post('/set/up/', data=dict(value="False"))
        rv = self.client.get('/his/up/')
        assert 200 == rv.status_code
        assert 2 == len(loads(rv.data)['history'])
        assert "True" == loads(rv.data)['history'][1]['status']
        assert "False" == loads(rv.data)['history'][0]['status']

        rv = self.client.post('/atr/up/', data=dict(history="False"))
        assert 200 == rv.status_code
        rv = self.client.get('/his/up/')
        assert "history" not in rv.data
        assert "True" not in rv.data
        assert "False" == loads(rv.data)['status']

class PullTestCase(BasicTestCase):
    """Test the status pull functionality"""

    class pullHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Toast")
            return

        def log_message(self, format, *args):
            # silence the server by overriding the logger
            pass

    def test_pull(self):
        server = HTTPServer(('', 5001), self.pullHandler)
        server.handle_request()

        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(pull="True",
                                                    pull_url="localhost:5001",
                                                    pull_time="0"))
        assert 200 == rv.status_code

        rv = self.client.get('/get/up/')
        assert 200 == rv.status_code

        server.socket.close()

if __name__ == "__main__":
    unittest.main()

