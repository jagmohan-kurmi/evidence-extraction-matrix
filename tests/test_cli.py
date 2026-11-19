import json,tempfile,unittest
from pathlib import Path
from evidence_extraction_matrix.cli import validate,flatten,main
class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.schema={"fields":[{"name":"design","required":True},{"name":"notes","required":False}]}
        self.good={"study_id":"s1","fields":{"design":{"value":"cohort","page":"2","citation":"Lee 2024","quote":"We followed..."}}}
    def test_required_and_evidence_fields(self):
        self.assertEqual(validate(self.schema,[self.good]),[])
        bad={"study_id":"s2","fields":{"design":{"value":"trial","page":"3"}}}
        issues=validate(self.schema,[bad]); self.assertTrue(any("missing evidence citation" in x for x in issues)); self.assertTrue(any("missing evidence quote" in x for x in issues))
        self.assertTrue(any("missing required field design" in x for x in validate(self.schema,[{"study_id":"s3","fields":{}}])))
    def test_csv_flatten_and_cli_malformed(self):
        self.assertIn("design_quote",flatten(self.schema,[self.good])[0])
        with tempfile.TemporaryDirectory() as td:
            src=Path(td)/"input.json"; src.write_text(json.dumps({"schema":self.schema,"records":[self.good]}),encoding="utf-8"); out=Path(td)/"out.csv"
            self.assertEqual(main([str(src),"--format","csv","--output",str(out)]),0); self.assertIn("Lee 2024",out.read_text(encoding="utf-8"))
            src.write_text("[",encoding="utf-8"); self.assertEqual(main([str(src)]),2)
    def test_duplicate_schema_fields_rejected(self):
        with self.assertRaises(ValueError): validate({"fields":[{"name":"x"},{"name":"x"}]},[])
if __name__=="__main__":unittest.main()
