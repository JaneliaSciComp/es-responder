from es_responder import app
import unittest
import time

NOW = int(time.time())

class TestDiagnostics(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

# ******************************************************************************
# * Doc/diagnostic endpoints                                                   *
# ******************************************************************************
    def test_blank(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_spec(self):
        response = self.app.get('/spec')
        self.assertEqual(response.status_code, 200)

    def test_doc(self):
        response = self.app.get('/doc')
        self.assertEqual(response.status_code, 200)

    def test_stats(self):
        response = self.app.get('/stats')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json['stats']['requests'], 0)

class TestContent(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

# ******************************************************************************
# * DVID endpoints                                                             *
# ******************************************************************************
    def test_dvid_hitcount_minute(self):
        response = self.app.get('/dvid_hitcount')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result'], 1)

    def test_dvid_hitcount(self):
        response = self.app.get('/dvid_hitcount/1d')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result'], 1000)
        response = self.app.get('/dvid_hitcount/1x')
        self.assertEqual(response.status_code, 400)

# ******************************************************************************
# * General endpoints                                                          *
# ******************************************************************************
    def test_query(self):
        response = self.app.get('/query/dvid_combined_minute_summary')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 1)
        response = self.app.get('/query/no_such_config')
        self.assertEqual(response.status_code, 404)

    def test_hitcount(self):
        response = self.app.get('/hitcount/*/1m')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result'], 100)
        response = self.app.get('/hitcount/no_such_index')
        self.assertEqual(response.status_code, 400)

    def test_hitcount_minute(self):
        response = self.app.get('/hitcount/*')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result'], 100)
        response = self.app.get('/hitcount/no_such_index')
        self.assertEqual(response.status_code, 400)

    def test_hits(self):
        response = self.app.get('/hits/*')
        self.assertEqual(response.status_code, 400)
        response = self.app.get('/hits/*?start=' + str(NOW-60) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 10)
        response = self.app.get('/hits/*?method=get&start=' + str(NOW-60) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 1)
        response = self.app.get('/hits/*?method=ook&start=' + str(NOW-60) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['result']['hits']['total'], 0)

# ******************************************************************************

if __name__ == '__main__':
    unittest.main()
