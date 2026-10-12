import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from backend.domain import normalize_plate, barrier_transition
from backend.store import Store, Conflict
from backend.server import make_server


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "test.sqlite3"
        self.store = Store(self.path)
    def tearDown(self):
        self.tmp.cleanup()
    def scan(self, **updates):
        data = dict(request_id="test-1", plate="34 DMO 01", confidence=.96, fault="none")
        data.update(updates)
        return self.store.scan(data)
    def test_allowed_opens(self):
        r = self.scan()
        self.assertEqual((r['decision'], r['barrier_action']), ('allow', 'open'))
    def test_denied_stays_closed(self):
        r = self.scan(plate='35 ABC 999')
        self.assertEqual((r['decision'],r['barrier']),('deny','closed'))
    def test_low_confidence(self):
        self.assertEqual(self.scan(confidence=.4)['decision'],'unreadable')
    def test_threshold_boundary(self):
        self.assertEqual(self.scan(confidence=.85)['decision'],'allow')
    def test_bad_format(self):
        self.assertEqual(self.scan(plate='82 ABC 01')['decision'],'unreadable')
    def test_no_fuzzy_match(self):
        self.assertEqual(self.scan(plate='34 DM0 01')['decision'],'deny')
    def test_faults_never_open(self):
        for i,fault in enumerate(['ocr_error','network_timeout']):
            r=self.scan(request_id=f'fault-{i}',fault=fault)
            self.assertEqual((r['decision'],r['barrier_action']),('error','none'))
    def test_repeat_after_close_never_reopens(self):
        self.scan(); self.store.clear()
        r=self.scan()
        self.assertTrue(r['duplicate'])
        self.assertEqual((r['barrier_action'],r['barrier']),('none','closed'))
        self.assertEqual(len(self.store.snapshot()['events']),1)
    def test_conflicting_id(self):
        self.scan()
        with self.assertRaises(Conflict): self.scan(plate='35 ABC 999')
    def test_deny_does_not_close_occupied_barrier(self):
        self.scan()
        r=self.scan(request_id='denied',plate='35 ABC 999')
        self.assertEqual(r['barrier'],'open_waiting_clear')
    def test_concurrent_duplicates_open_once(self):
        with ThreadPoolExecutor(max_workers=6) as pool:
            results=list(pool.map(lambda _: self.scan(),range(12)))
        self.assertEqual(sum(r['barrier_action']=='open' for r in results),1)
        self.assertEqual(len(self.store.snapshot()['events']),1)
    def test_persistence_and_no_reseed(self):
        self.store.change_plate('34 DMO 01',False)
        self.scan()
        reloaded=Store(self.path)
        self.assertNotIn('34DMO01',reloaded.snapshot()['allowed_plates'])
        self.assertEqual(len(reloaded.snapshot()['events']),1)
    def test_invalid_numbers(self):
        for value in [True, float('nan'), float('inf'), -1, 2, '0.9']:
            with self.assertRaises(ValueError): self.scan(confidence=value)
    def test_input_validation(self):
        for body in [[],{},dict(request_id='x',plate=1,confidence=.9)]:
            with self.assertRaises(ValueError): self.store.scan(body)
    def test_normalization_and_clear(self):
        self.assertEqual(normalize_plate('34 dmo 01'),'34DMO01')
        self.assertEqual(barrier_transition('closed','clear'),('closed','none'))


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.server=make_server(Path(cls.tmp.name)/'http.sqlite3',0)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.tmp.cleanup()
    def request(self,path,body=None,headers=None):
        req=Request(self.base+path,data=None if body is None else json.dumps(body).encode(),headers=headers or {'Content-Type':'application/json'})
        return urlopen(req,timeout=3)
    def test_health_and_web(self):
        with self.request('/api/health') as r:self.assertEqual(json.load(r)['mode'],'simulation')
        with self.request('/') as r:self.assertIn('SİMÜLASYON'.encode(),r.read())
    def test_http_roundtrip(self):
        with self.request('/api/demo/scan',{'request_id':'http-1','plate':'06 TST 02','confidence':.99}) as r:
            self.assertEqual(json.load(r)['decision'],'allow')
        with self.request('/api/demo/clear',{}) as r:self.assertEqual(json.load(r)['barrier'],'closed')
    def test_foreign_origin_blocked(self):
        with self.assertRaises(HTTPError) as ctx:self.request('/api/demo/clear',{}, {'Content-Type':'application/json','Origin':'https://example.invalid'})
        self.assertEqual(ctx.exception.code,403)
    def test_unsupported_media(self):
        with self.assertRaises(HTTPError) as ctx:self.request('/api/demo/clear',{}, {'Content-Type':'text/plain'})
        self.assertEqual(ctx.exception.code,415)
    def test_path_and_bad_json_object(self):
        with self.assertRaises(HTTPError) as ctx:self.request('/../../backend/store.py')
        self.assertEqual(ctx.exception.code,404)
        with self.assertRaises(HTTPError) as ctx:self.request('/api/demo/scan',[])
        self.assertEqual(ctx.exception.code,400)


if __name__ == '__main__': unittest.main()
