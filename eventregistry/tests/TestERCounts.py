import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestCounts(DataValidator):

    def testConceptCounts(self):
        trumpUri = self.er.getConceptUri("Trump")
        ebolaUri = self.er.getConceptUri("Ebola")
        self.assertIsNotNone(trumpUri)
        self.assertIsNotNone(ebolaUri)

        q = GetCounts([trumpUri, ebolaUri])
        res = self.er.execQuery(q)

        for uri in [trumpUri, ebolaUri]:
            self.assertTrue(uri in res, "Expected the counts result to contain the concept '%s'" % (uri))
            counts = res[uri]
            self.assertTrue(isinstance(counts, list) and len(counts) > 0, "Expected a non-empty list of daily counts")
            for item in counts:
                self.assertTrue("date" in item, "Each count item should have a date")
                self.assertTrue("count" in item, "Each count item should have a count")
        # a popular concept should be mentioned on at least one of the days
        self.assertTrue(any(item["count"] > 0 for item in res[trumpUri]), "Expected at least one day with a non-zero count")


    def testCategoryCountsEx(self):
        businessUri = self.er.getCategoryUri("business")
        self.assertIsNotNone(businessUri)

        q = GetCountsEx([businessUri], type = "category")
        res = self.er.execQuery(q)

        self.assertTrue("categoryInfo" in res, "Expected 'categoryInfo' in the results")
        self.assertTrue("counts" in res, "Expected 'counts' in the results")
        self.assertEqual(res["categoryInfo"][0].get("uri"), businessUri)
        self.assertTrue(len(res["counts"]) > 0, "Expected a non-empty list of daily counts")
        for item in res["counts"]:
            self.assertTrue("date" in item, "Each count item should have a date")
            self.assertTrue(businessUri in item, "Each count item should have a count for the requested category")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCounts)
    unittest.TextTestRunner(verbosity=3).run(suite)
