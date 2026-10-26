import json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
class SiteTests(unittest.TestCase):
 def test_app_files(self):
  for path in ('index.html','assets/styles.css','assets/app.js','scripts/build.py','.github/workflows/pages.yml'):
   self.assertTrue((P/path).is_file(),path)
 def test_source_inclusion(self):
  d=P/'data/course.json'
  if not d.exists():self.skipTest('No source bundle generated yet; run python scripts/build.py --sync')
  doc=json.loads(d.read_text())
  self.assertEqual(len(doc['lessons']),5)
  self.assertEqual([x['id'] for x in doc['lessons']],[f'day-{i}' for i in range(1,6)])
  for lesson in doc['lessons']:
   self.assertTrue(lesson['html']);self.assertTrue((P/lesson['source']).exists())
   self.assertNotIn('<script',lesson['html'].lower())
 def test_no_faked_stats(self):
  js=(P/'assets/app.js').read_text();self.assertIn('validDone()',js);self.assertIn('localStorage',js)
if __name__=='__main__':unittest.main()
