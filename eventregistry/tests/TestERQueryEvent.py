import unittest, sys
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryEvent(DataValidator):

    def getValidEvent(self):
        q = QueryEvents(lang = "eng", conceptUri = self.er.getConceptUri("Google"))
        q.setRequestedResult(RequestEventsUriWgtList(count = 1, sortBy="size"))
        res = self.er.execQuery(q)
        return EventRegistry.getUriFromUriWgt(res["uriWgtList"]["results"])[0]


    def testEventArticleFiltering(self):
        # use a live event instead of a hardcoded uri so that the test also works without access to the archive
        eventUri = self.getValidEvent()

        # read the event details so that we can filter by a language and a concept that actually appear in the event
        q = QueryEvent(eventUri)
        q.setRequestedResult(RequestEventInfo())
        info = self.er.execQuery(q)[eventUri]["info"]
        lang = sorted(info.get("articleCounts", {"eng": 0}).keys())[0]
        concepts = info.get("concepts", [])
        self.assertTrue(len(concepts) > 0, "Expected the event to have some concepts")
        conceptUri = concepts[0]["uri"]

        totalCount = QueryEventArticlesIter(eventUri).count(self.er)
        self.assertTrue(totalCount > 0, "Expected the event to have some articles")

        countsLang = QueryEventArticlesIter(eventUri, lang = lang).count(self.er)
        self.assertTrue(0 < countsLang <= totalCount, "The language filtered count should be between 0 and the total count")
        countsConcept = QueryEventArticlesIter(eventUri, conceptUri = conceptUri).count(self.er)
        self.assertTrue(0 < countsConcept <= totalCount, "The concept filtered count should be between 0 and the total count")
        countsBoth = QueryEventArticlesIter(eventUri, lang = lang, conceptUri = conceptUri).count(self.er)
        self.assertTrue(countsBoth <= countsLang and countsBoth <= countsConcept, "Combining the filters should not increase the count")

        arts = [art for art in QueryEventArticlesIter(eventUri).execQuery(self.er)]
        self.assertTrue(totalCount == len(arts), "The iterator should return exactly the number of articles reported by count()")

        # the same filters used through QueryEvent + RequestEventArticles should report the same number of matches
        q = QueryEvent(eventUri)
        q.setRequestedResult(RequestEventArticles(lang = lang, conceptUri = conceptUri))
        res = self.er.execQuery(q)
        self.assertTrue(countsBoth == res[eventUri]["articles"]["totalResults"])



    def testArticleSorting(self):
        q = QueryEventArticlesIter(self.getValidEvent())

        # try ascending order
        wgt = None
        for art in q.execQuery(self.er, sortBy="date", sortByAsc=True):
            if wgt is None:
                wgt = art["wgt"]
            self.assertTrue(art["wgt"] >= wgt)
            wgt = art["wgt"]

        # try descending order
        wgt = None
        for art in q.execQuery(self.er, sortBy="date", sortByAsc=False):
            if wgt is None:
                wgt = art["wgt"]
            self.assertTrue(art["wgt"] <= wgt)
            wgt = art["wgt"]


    def testArticleList(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventArticles(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            for article in event.get("articles").get("results"):
                self.ensureValidArticle(article, "testArticleList")


    def testArticleCount(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventArticleUriWgts())
        res = self.er.execQuery(q)

        for (uri, event) in res.items():
            if "newEventUri" in event:
                continue
            iter = QueryEventArticlesIter(uri)
            count = iter.count(self.er)
            uriList = event.get("uriWgtList").get("results")
            if count != len(uriList):
                self.fail("Event did not have expected uri wgt list: expected %d, got %d" % (count, len(uriList)))


    def testArticleUris(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventArticleUriWgts())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertTrue("uriWgtList" in event, "Expected to see 'uriWgtList'")


    def testKeywords(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventKeywordAggr())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("keywordAggr"), "Expected to see 'keywordAggr'")
            if isinstance(event.get("keywordAggr"), dict) and "error" in event.get("keywordAggr"):
                print("Got error: " + event.get("keywordAggr").get("error"))
                continue
            for kw in event.get("keywordAggr").get("results"):
                self.assertIsNotNone(kw.get("keyword"), "Keyword expected")
                self.assertIsNotNone(kw.get("weight"), "Weight expected")

    def testSourceAggr(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventSourceAggr())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("sourceExAggr"), "Expected to see 'sourceExAggr'")


    def testArticleTrend(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventArticleTrend())
        res = self.er.execQuery(q)

        for event in list(res.values()):
            if "newEventUri" in event:
                continue
            self.assertIsNotNone(event.get("articleTrend"), "Expected to see 'articleTrend'")


    def testSimilarEvents(self):
        q = QueryEvent(self.getValidEvent())
        q.setRequestedResult(RequestEventSimilarEvents(
            [{ "uri": "http://en.wikipedia.org/wiki/Barack_Obama", "wgt": 100 }, { "uri": "http://en.wikipedia.org/wiki/Donald_Trump", "wgt": 80 }],
            addArticleTrendInfo = True, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        for simEvent in res.get("events", {}).get("results", []):
            if "newEventUri" in simEvent:
                continue
            self.ensureValidEvent(simEvent, "testSimilarEvents")


    def testEventArticlesIterator(self):
        # check that the iterator really downloads all articles in the event
        iter = QueryEventArticlesIter(self.getValidEvent())
        articleCount = iter.count(self.er)
        articles = [art for art in iter.execQuery(self.er)]
        if articleCount != len(articles):
            self.fail("Event article iterator did not generate the full list of event articles")



if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEvent)
    unittest.TextTestRunner(verbosity=3).run(suite)
