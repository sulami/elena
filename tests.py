import sys
import time
import unittest
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

from flask.json import loads
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from elena.database import Database
from run import app, init_db

class BasicTestCase(unittest.TestCase):
    """Unify setup and teardown, verify server starts up"""

    longMessage = True

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
        rv = self.client.post('/set/up/', data=dict(value="True"))
        self.assertEqual(201, rv.status_code)

    def test_status_existence(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual("True", loads(rv.data)['status'])

    def test_status_nonexistence(self):
        rv = self.client.get('/get/notup/')
        self.assertEqual(404, rv.status_code)

    def test_status_update(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual("True", loads(rv.data)['status'])

        rv = self.client.post('/set/up/', data=dict(value="False"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual("False", loads(rv.data)['status'])

    def test_status_deletion(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual("True", loads(rv.data)['status'])

        rv = self.client.get('/del/up/')
        self.assertEqual(204, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(404, rv.status_code)

        rv = self.client.get('/del/up/')
        self.assertEqual(404, rv.status_code)

    def test_status_timestamp(self):
        self.client.post('/set/up/', data=dict(value="True"))
        old = loads(self.client.get('/get/up/').data)['update_time']

        time.sleep(1) # Ensure we get a different timestamp

        self.client.post('/set/up/', data=dict(value="True"))
        new = loads(self.client.get('/get/up/').data)['update_time']

        self.assertNotEqual(old, new)

class MetaTestCase(BasicTestCase):
    """Test general function"""

    def test_status_page(self):
        rv = self.client.get('/status/')
        self.assertIn("0", rv.data)

        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.get('/status/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("1", rv.data)

        self.client.post('/set/down/', data=dict(value="False"))
        rv = self.client.get('/status/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("2", rv.data)

        self.client.post('/set/down/', data=dict(value="True"))
        rv = self.client.get('/status/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("2", rv.data)

        self.client.get('/del/down/')
        rv = self.client.get('/status/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("1", rv.data)

class HistoryTestCase(BasicTestCase):
    """Test the status history functionality"""

    def test_history_disabled(self):
        rv = self.client.post('/set/up/', data=dict(value="True"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual("True", loads(rv.data)['status'])
        self.assertEqual(200, rv.status_code)

        rv = self.client.post('/set/up/', data=dict(value="False"))
        self.assertEqual(201, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual("False", loads(rv.data)['status'])
        self.assertEqual(200, rv.status_code)
        self.assertNotIn("history", rv.data)
        self.assertNotIn("True", rv.data)
        self.assertEqual("False",loads(rv.data)['status'])

    def test_check_history(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(history="True"))
        self.assertEqual(200, rv.status_code)

        self.client.post('/set/up/', data=dict(value="False"))
        rv = self.client.get('/his/up/')
        self.assertEqual(200, rv.status_code)
        self.assertIn("True", rv.data)
        self.assertIn("False", rv.data)

    def test_delete_history(self):
        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(history="True"))
        self.assertEqual(200, rv.status_code)

        self.client.post('/set/up/', data=dict(value="False"))
        rv = self.client.get('/his/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual(2, len(loads(rv.data)['history']))
        self.assertEqual("True", loads(rv.data)['history'][1]['status'])
        self.assertEqual("False", loads(rv.data)['history'][0]['status'])

        rv = self.client.post('/atr/up/', data=dict(history="False"))
        self.assertEqual(200, rv.status_code)
        rv = self.client.get('/his/up/')
        self.assertNotIn("history", rv.data)
        self.assertNotIn("True", rv.data)
        self.assertEqual("False", loads(rv.data)['status'])

        rv = self.client.post('/atr/up/', data=dict(history="True"))
        self.assertEqual(200, rv.status_code)
        rv = self.client.get('/his/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual(1, len(loads(rv.data)['history']))
        self.assertEqual("False", loads(rv.data)['history'][0]['status'])

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

    def server_wait(self):
        server = HTTPServer(('', 5001), self.pullHandler)
        server.handle_request()
        server.socket.close()

    def test_pull(self):
        server_thread = Thread(target=self.server_wait)
        server_thread.start()

        self.client.post('/set/up/', data=dict(value="True"))
        rv = self.client.post('/atr/up/', data=dict(pull="True",
                                            pull_url='http://localhost:5001',
                                            pull_time="0"))
        self.assertEqual(200, rv.status_code)

        rv = self.client.get('/get/up/')
        self.assertEqual(200, rv.status_code)
        self.assertEqual("Toast", loads(rv.data)['status'])

class PerformanceTestCase(BasicTestCase):
    """Various performance tests"""

    @unittest.skipUnless('PerformanceTestCase' in sys.argv,
                         "We do not need this test by default")
    def test_lots_of_updates(self):
        for i in xrange(1000):
            self.client.post('/set/' + str(i) + '/', data=dict(value=i))
        for i in xrange(1000):
            rv = self.client.get('/get/' + str(i) + '/')

if __name__ == "__main__":
    unittest.main()

