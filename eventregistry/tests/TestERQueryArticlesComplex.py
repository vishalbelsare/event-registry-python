import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryArticlesComplex(DataValidator):

    def getQueryUriListForComplexQuery(self, cq):
        q = QueryArticles.initWithComplexQuery(cq)
        return self.getQueryUriListForQueryArticles(q)


    def getQueryUriListForQueryArticles(self, q):
        q.setRequestedResult(RequestArticlesUriWgtList(count = 50000))
        res = self.er.execQuery(q)
        assert "error" not in res, "Results included error: " + res.get("error", "")
        return res["uriWgtList"]


    def testKw1(self):
        # limit the search to English articles - the keyword matching is language aware, so a non-English
        # article can match "obama" with the name written in a different script
        cq1 = ComplexArticleQuery(BaseQuery(keyword = "obama", keywordLoc = "title", lang = "eng"))
        artIter = QueryArticlesIter.initWithComplexQuery(cq1)
        checked, misses = 0, 0
        for art in artIter.execQuery(self.er, maxItems = 2000):
            checked += 1
            if self.removeAccents(art["title"]).lower().find("obama") < 0:
                misses += 1
        # a tiny number of mismatches can appear due to noise in the article data
        self.assertTrue(misses <= max(2, checked * 0.01), "Too many articles (%d of %d) did not contain the keyword in the title" % (misses, checked))


    def testKw2(self):
        qStr = """
        {
            "$query": {
                "keyword": "obama", "keywordLoc": "title", "lang": "eng"
            }
        }
        """
        qiter = QueryArticlesIter.initWithComplexQuery(qStr)
        checked, misses = 0, 0
        for art in qiter.execQuery(self.er, maxItems = 2000):
            checked += 1
            if self.removeAccents(art["title"]).lower().find("obama") < 0:
                misses += 1
        self.assertTrue(misses <= max(2, checked * 0.01), "Too many articles (%d of %d) did not contain the keyword in the title" % (misses, checked))


    def testKw3(self):
        cq1 = ComplexArticleQuery(BaseQuery(keyword = "home", keywordLoc = "body", lang = "eng"))
        artIter = QueryArticlesIter.initWithComplexQuery(cq1)
        checked, misses = 0, 0
        for art in artIter.execQuery(self.er, maxItems = 2000):
            checked += 1
            if self.removeAccents(art["body"]).lower().find("home") < 0:
                misses += 1
        self.assertTrue(misses <= max(2, checked * 0.01), "Too many articles (%d of %d) did not contain the keyword in the body" % (misses, checked))


    def testCompareSameResultsKw1(self):
        cq1 = ComplexArticleQuery(
            BaseQuery(keyword =  QueryItems.AND(["obama", "trump"]),
                dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(keyword = "obama"),
                BaseQuery(keyword = "trump"),
                BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)) ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryArticles(keywords = QueryItems.AND(["obama", "trump"]), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults1(self):
        cq1 = ComplexArticleQuery(
            BaseQuery(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]),
                dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12),
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(conceptUri = self.er.getConceptUri("obama")),
                BaseQuery(conceptUri = self.er.getConceptUri("trump")),
                BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)) ],
                exclude = BaseQuery(lang = QueryItems.OR(["eng", "deu"]))))

        q = QueryArticles(conceptUri = QueryItems.AND([self.er.getConceptUri("obama"), self.er.getConceptUri("trump")]), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12), ignoreLang = ["eng", "deu"])

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults2(self):
        cq1 = ComplexArticleQuery(
            query = BaseQuery(sourceUri = QueryItems.OR([self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")]),
                dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12),
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.OR([
                BaseQuery(sourceUri = self.er.getNewsSourceUri("bbc"), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)),
                BaseQuery(sourceUri = self.er.getNewsSourceUri("associated press"), dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12))],
                exclude = BaseQuery(conceptUri = QueryItems.OR([self.er.getConceptUri("obama")]))))

        q = QueryArticles(sourceUri = [self.er.getNewsSourceUri("bbc"), self.er.getNewsSourceUri("associated press")], dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12), ignoreConceptUri = self.er.getConceptUri("obama"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults3(self):
        cq1 = ComplexArticleQuery(
            query = BaseQuery(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13),
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(dateStart = self.daysAgo(15)),
                BaseQuery(dateEnd = self.daysAgo(13))],
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        q = QueryArticles(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13), ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])


    def testCompareSameResults4(self):
        businessUri = categoryUri = self.er.getCategoryUri("Business")
        q1 = QueryArticles.initWithComplexQuery("""
        {
            "$query": {
                "dateStart": "%s", "dateEnd": "%s",
                "$not": {
                    "categoryUri": "%s"
                }
            }
        }
        """ % (self.daysAgo(15), self.daysAgo(13), businessUri))

        q = QueryArticles(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13), ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        # compare with old approach
        listRes2 = self.getQueryUriListForQueryArticles(q)
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
        q1 = QueryArticles.initWithComplexQuery(qStr)

        cq2 = ComplexArticleQuery(
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

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])


    def testCompareSameResults6(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        merkelUri = self.er.getConceptUri("merkel")
        businessUri = self.er.getCategoryUri("business")

        # the date range is ANDed with the other conditions and the excluded date is a single day inside that range
        qStr = """
        {
            "$query": {
                "$and": [
                    { "dateStart": "%s", "dateEnd": "%s" },
                    {
                        "$or": [
                            { "conceptUri": "%s" },
                            { "categoryUri": "%s" },
                            {
                                "$and": [
                                    { "conceptUri": "%s" },
                                    { "categoryUri": "%s" }
                                ]
                            }
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
        """ % (self.daysAgo(16), self.daysAgo(12), trumpUri, politicsUri, merkelUri, businessUri, self.daysAgo(14), self.daysAgo(14), obamaUri)
        q1 = QueryArticles.initWithComplexQuery(qStr)

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                    BaseQuery(dateStart = self.daysAgo(16), dateEnd = self.daysAgo(12)),
                    CombinedQuery.OR([
                        BaseQuery(conceptUri = trumpUri),
                        BaseQuery(categoryUri = politicsUri),
                        CombinedQuery.AND([
                            BaseQuery(conceptUri = merkelUri),
                            BaseQuery(categoryUri = businessUri)
                        ])
                    ])
                ],
                exclude = CombinedQuery.OR([
                    BaseQuery(dateStart = self.daysAgo(14), dateEnd = self.daysAgo(14)),
                    BaseQuery(conceptUri = obamaUri)]
                )))

        listRes1 = self.getQueryUriListForQueryArticles(q1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])


    def testCompareSameResults7(self):
        cq1 = ComplexArticleQuery(
            query = BaseQuery(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13),
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        cq2 = ComplexArticleQuery(
            query = CombinedQuery.AND([
                BaseQuery(dateStart=self.daysAgo(20), dateEnd=self.daysAgo(5)),
                BaseQuery(dateStart=self.daysAgo(15)),
                BaseQuery(dateStart=self.daysAgo(18)),
                BaseQuery(dateEnd = self.daysAgo(10)),
                BaseQuery(dateEnd = self.daysAgo(13))],
                exclude = BaseQuery(categoryUri = self.er.getCategoryUri("Business"))))

        q = QueryArticles(dateStart = self.daysAgo(15), dateEnd = self.daysAgo(13), ignoreCategoryUri = self.er.getCategoryUri("business"))

        listRes1 = self.getQueryUriListForComplexQuery(cq1)
        listRes2 = self.getQueryUriListForComplexQuery(cq2)
        # compare with old approach
        listRes3 = self.getQueryUriListForQueryArticles(q)
        self.assertCountsClose(listRes1["totalResults"], listRes2["totalResults"])
        self.assertCountsClose(listRes1["totalResults"], listRes3["totalResults"])



    def _testGetValidContent(self):
        trumpUri = self.er.getConceptUri("Trump")
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getCategoryUri("politics")
        cq = ComplexArticleQuery(
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

        retInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True))

        iter = QueryArticlesIter.initWithComplexQuery(cq)
        for art in iter.execQuery(self.er, returnInfo =  retInfo):
            foundTrump = False
            foundCategory = False
            for c in art.get("concepts", []):
                if c["uri"] == trumpUri: foundTrump = True
            for c in art.get("categories", []):
                if c["uri"].find(politicsUri) == 0: foundCategory = True
            self.assertTrue(foundTrump or foundCategory, "invalid article that should not be in the results")

            date = art["date"]
            if date:
                self.assertTrue(self.daysAgo(16) <= date <= self.daysAgo(12), "article date %s is outside of the queried date range" % date)
                self.assertTrue(date != self.daysAgo(14), "article contained the excluded date")
            for c in art.get("concepts", []):
                self.assertTrue(c["uri"] != obamaUri, "article contained obama")




if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryArticlesComplex)
    # suite = unittest.TestLoader().suiteClass(map(TestQueryArticlesComplex, ["testCompareSameResults5"]))
    unittest.TextTestRunner(verbosity=3).run(suite)
