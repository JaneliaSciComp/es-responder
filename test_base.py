from es_responder import app
import unittest
import time

NOW = int(time.time()) - 60

class TestDiagnostics(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

# ******************************************************************************
# * Doc/diagnostic endpoints                                                   *
# ******************************************************************************
    def test_blank(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.app.options('/')
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
# * General endpoints                                                          *
# ******************************************************************************
    def test_query(self):
        response = self.app.get('/query/dvid_combined_minute_summary')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 1)
        response = self.app.get('/query/no_such_config')
        self.assertEqual(response.status_code, 404)

    def test_metrics(self):
        response = self.app.get('/metrics/*')
        self.assertIn(response.status_code, [301, 308])
        response = self.app.get('/metrics/*/1h')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['count'], 100)
        response = self.app.get('/metrics/ook/1h')
        self.assertEqual(response.status_code, 404)

    def test_hits(self):
        response = self.app.get('/hits/*')
        self.assertEqual(response.status_code, 400)
        response = self.app.get('/hits/*?start=' + str(NOW-180) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 10)
        response = self.app.get('/hits/*?method=get&start=' + str(NOW-180) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(response.json['result']['hits']['total'], 1)
        response = self.app.get('/hits/*?method=ook&start=' + str(NOW-180) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['result']['hits']['total'], 0)
        response = self.app.get('/hits/no_such_index?start=' + str(NOW-60) + '&end=' + str(NOW))
        self.assertEqual(response.status_code, 404)

    def test_lasthits(self):
        response = self.app.get('/lasthits/*/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json['result']['hits']['hits']), 1)
        response = self.app.get('/lasthits/no_such_index/1')
        self.assertEqual(response.status_code, 404)

# ******************************************************************************

if __name__ == '__main__':
    unittest.main()
