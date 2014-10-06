import unittest

import run

class BasicTestCase(unittest.TestCase):
    """Unify setup and teardown, verify server starts up"""

    def setUp(self):
        run.debug = True
        self.client = run.app.test_client()

    def tearDown(self):
        pass

    def test_server_up(self):
        return self.client.get('/')

class StatusTestCase(BasicTestCase):
    """Test basic status operations"""

    def test_status_creation(self):
        return self.client.post('/new/', data=dict(name="up", type="bool"))

if __name__ == "__main__":
    unittest.main()

