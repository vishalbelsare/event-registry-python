import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryEventsComplex(DataValidator):

    def getQueryUriListForComplexQuery(self, cq):
        q = QueryEvents.initWithComplexQuery(cq)
        return self.getQueryUriListForQueryEvents(q)


    def getQueryUriListForQueryEvents(self, q):
        q.setRequestedResult(RequestEventsUriWgtList(count = 50000))
        res = self.er.execQuery(q)
        assert "error" not in res, "Results included error: " + res.get("error", "")
        return res["uriWgtList"]


    def testCompareSameResults1(self):
        cq1 = ComplexEventQuery(
            BaseQuery(
                conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]),
                dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))
            ))

        cq2 = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(conceptUri = self.er.getConceptUri("obama")),
                    BaseQuery(conceptUri = self.er.getConceptUri("trump")),
                    BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12))
                ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryEvents(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults2(self):
        cq1 = ComplexEventQuery(
            BaseQuery(
                sourceUri = QueryItems.OR([self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")]),
                dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12),
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        cq2 = ComplexEventQuery(
            CombinedQuery.OR([
                    BaseQuery(sourceUri = self.er.getNewsSourceUri("bbc"), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)),
                    BaseQuery(sourceUri = self.er.getNewsSourceUri("associated press"), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12))
                ],
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        q = QueryEvents(sourceUri = [self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")], dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12), ignoreConceptUri = self.er.getConceptUri("obama"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults3(self):
        cq1 = ComplexEventQuery(
            BaseQuery(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13),
                      exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        cq2 = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(dateStart = self.daysAgo(15)),
                    BaseQuery(dateEnd = self.daysAgo(13))
                ],
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        q = QueryEvents(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13), ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryEvents(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults4(self):
        businessUri = categoryUri = self.er.getCategoryUri("Business")
        q1 = QueryEvents.initWithComplexQuery("""
        {
            "$query": {
                "dateStart": "%s", "dateEnd": "%s",
                "$not": {
                    "categoryUri": "%s"
                }
            }
        }
        """ % (self.daysAgo(15), self.daysAgo(13), businessUri))

        q = QueryEvents(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13), ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForQueryEvents(q1)
        # compare with old approach
        listRes2 = self.getQueryUriListForQueryEvents(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])


    def testCompareSameResults5(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        # the date range is ANDed with the other conditions and the excluded date is a single day inside that range
        qStr = """
        {
            "$query": {
                "$and": [
                    { "dateStart": "%s", "dateEnd": "%s" },
                    {
                        "$or": [
                            { "conceptUri": "%s" },
                            { "categoryUri": "%s" }
                        ]
                    }
                ],
                "$not": {
                    "$or": [
                        { "dateStart": "%s", "dateEnd": "%s" },
                        { "conceptUri": "%s" }
                    ]
                }
            }
        }
        """ % (self.daysAgo(16), self.daysAgo(12), trumpUri, politicsUri, self.daysAgo(14), self.daysAgo(14), obamaUri)
        q1 = QueryEvents.initWithComplexQuery(qStr)

        cq2 = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)),
                    CombinedQuery.OR([
                        BaseQuery(conceptUri = trumpUri),
                        BaseQuery(categoryUri = politicsUri)
                    ])
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = self.daysAgo(14), dateEnd = self.daysAgo(14)),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        listRes1 = self.getQueryUriListForQueryEvents(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])


    def testGetValidContent(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        cq = ComplexEventQuery(
            query = CombinedQuery.AND([
                    BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)),
                    CombinedQuery.OR([
                        BaseQuery(conceptUri = trumpUri),
                        BaseQuery(categoryUri = politicsUri)
                    ])
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = self.daysAgo(14), dateEnd = self.daysAgo(14)),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        retInfo = ReturnInfo(
            eventInfo = EventInfoFlags(concepts=True, categories=True, stories=True),
            conceptInfo = ConceptInfoFlags(maxConceptsPerType = 100))

        iter = QueryEventsIter.initWithComplexQuery(cq)
        for event in iter.execQuery(self.er, returnInfo =  retInfo, maxItems = 2000):
            foundTrump = False
            foundCategory = False
            for c in event.get("concepts", []):
                if c["uri"] == trumpUri: foundTrump = True
            for c in event.get("categories", []):
                if c["uri"].find(politicsUri) == 0: foundCategory = True
            self.assertTrue(foundTrump or foundCategory, "invalid event that should not be in the results")

            date = event.get("eventDate", "")
            if date:
                self.assertTrue(self.daysAgo(16) <= date <= self.daysAgo(12), "event date %s is outside of the queried date range" % date)
                self.assertTrue(date != self.daysAgo(14), "event contained the excluded date")
            for c in event.get("concepts", []):
                self.assertTrue(c["uri"] != obamaUri, "event contained obama")




if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEventsComplex)
    unittest.TextTestRunner(verbosity=3).run(suite)
