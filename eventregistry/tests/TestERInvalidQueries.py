import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestInvalidQueries(DataValidator):
    """
    validate that valid complex queries execute without an error and that
    malformed complex queries are rejected by the API with an "error" property
    """

    def execQueryString(self, qStr):
        q = QueryArticles()
        q._setVal("query", qStr)
        return self.er.execQuery(q)


    def ensureQueryFails(self, qStr, testName):
        res = self.execQueryString(qStr)
        self.assertTrue("error" in res, "Query in test '%s' should have been rejected with an error, but got: %s" % (testName, list(res.keys())))


    def testValidComplexQuery(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        merkelUri = self.er.getConceptUri("merkel")
        businessUri = self.er.getCategoryUri("business")

        qStr = """
        {
            "$query": {
                "$or": [
                    { "dateStart": "2017-02-05", "dateEnd": "2017-02-05" },
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" },
                    {
                        "$and": [
                            { "conceptUri": "%s" },
                            { "categoryUri": "%s" }
                        ]
                    }
                ],
                "$not": {
                    "$or": [
                        { "dateStart": "2017-02-04", "dateEnd": "2017-02-04" },
                        { "conceptUri": "%s" }
                    ]
                }
            }
        }
            """ % (trumpUri, politicsUri, merkelUri, businessUri, obamaUri)
        q = QueryArticles.initWithComplexQuery(qStr)
        res = self.er.execQuery(q)
        self.assertTrue("error" not in res, "A valid complex query should not return an error, but got: %s" % (res.get("error", "")))
        self.assertIsNotNone(res.get("articles"), "Expected to get 'articles'")


    def testNotWithEmptyOr(self):
        trumpUri = self.er.getConceptUri("Trump")
        politicsUri = self.er.getCategoryUri("politics")
        qStr = """
        {
            "$query": {
                "$or": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                    "$or": [
                    ]
                }
            }
        }
            """ % (trumpUri, politicsUri)
        self.ensureQueryFails(qStr, "notWithEmptyOr")


    def testEmptyNot(self):
        trumpUri = self.er.getConceptUri("Trump")
        politicsUri = self.er.getCategoryUri("politics")
        qStr = """
        {
            "$query": {
                "$or": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                }
            }
        }
            """ % (trumpUri, politicsUri)
        self.ensureQueryFails(qStr, "emptyNot")


    def testUnknownOperator(self):
        trumpUri = self.er.getConceptUri("Trump")
        politicsUri = self.er.getCategoryUri("politics")
        qStr = """
        {
            "$query": {
                "$aaaaor": [
                    { "conceptUri": "%s" },
                    { "categoryUri": "%s" }
                ],
                "$not": {
                }
            }
        }
            """ % (trumpUri, politicsUri)
        self.ensureQueryFails(qStr, "unknownOperator")


    def testEmptyAndWithEmptyNot(self):
        qStr = """
        {
            "$query": {
                "$and": [
                ],
                "$not": {
                }
            }
        }"""
        self.ensureQueryFails(qStr, "emptyAndWithEmptyNot")


    def testEmptyAnd(self):
        qStr = """
        {
            "$query": {
                "$and": [
                ]
            }
        }"""
        self.ensureQueryFails(qStr, "emptyAnd")


    def testAndWithDictValue(self):
        # the value of the $and operator has to be an array, not an object
        qStr = """
        {
            "$query": {
                "$and": {}
            }
        }"""
        self.ensureQueryFails(qStr, "andWithDictValue")


    def testEmptyQuery(self):
        qStr = """
        {
            "$query": {
            }
        }"""
        self.ensureQueryFails(qStr, "emptyQuery")


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestInvalidQueries)
    unittest.TextTestRunner(verbosity=3).run(suite)
