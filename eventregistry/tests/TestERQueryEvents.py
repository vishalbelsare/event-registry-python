import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryEvents(DataValidator):
    def validateGeneralEventList(self, res):
        self.assertIsNotNone(res.get("events"), "Expected to get 'events'")

        totalResults = res.get("events").get("totalResults", 0)
        events = res.get("events").get("results")
        # a page contains 10 events, unless the query matches fewer results overall
        self.assertEqual(len(events), min(10, totalResults), "Expected to get %d events but got %d" % (min(10, totalResults), len(events)))
        for event in events:
            self.ensureValidEvent(event, "eventList")


    def createQuery(self):
        q = QueryEvents(conceptUri = self.er.getConceptUri("Obama"))
        return q


    def testEventList(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

    #
    # test different search query params
    #

    def testEventListWithKeywordSearch(self):
        q = QueryEvents(keywords="germany", dateStart=self.daysAgo(20), dateEnd=self.daysAgo(2))
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

        q2 = QueryEvents.initWithComplexQuery(ComplexEventQuery(
            BaseQuery(keyword = "germany", dateStart = self.daysAgo(20), dateEnd = self.daysAgo(2))))
        q2.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralEventList(res2)

        self.ensureSameResults(res, res2, '[events][].totalResults')


    def testEventListWithSourceSearch(self):
        q = QueryEvents(sourceUri = self.er.getNewsSourceUri("bbc"), dateStart=self.daysAgo(20), dateEnd=self.daysAgo(2))
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

        q2 = QueryEvents.initWithComplexQuery(ComplexEventQuery(
            BaseQuery(sourceUri = self.er.getNewsSourceUri("bbc"), dateStart = self.daysAgo(20), dateEnd = self.daysAgo(2))))
        q2.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralEventList(res2)

        self.ensureSameResults(res, res2, '[events][].totalResults')


    def testEventListWithCategorySearch(self):
        q = QueryEvents(categoryUri = self.er.getCategoryUri("disa"))
        res = self.er.execQuery(q)

        q2 = QueryEvents.initWithComplexQuery(ComplexEventQuery(
            BaseQuery(categoryUri = self.er.getCategoryUri("disa"))))
        res2 = self.er.execQuery(q2)

        self.ensureSameResults(res, res2, '[events][].totalResults')


    def testEventListWithAuthorSearch(self):
        authorUri = self.er.getAuthorUri("associated")
        q = QueryEvents(authorUri = authorUri)
        res = self.er.execQuery(q)

        q2 = QueryEvents.initWithComplexQuery(ComplexEventQuery(
            BaseQuery(authorUri = authorUri)))
        res2 = self.er.execQuery(q2)

        self.ensureSameResults(res, res2, '[events][].totalResults')


    def testEventListWithLanguageSearch(self):
        q = QueryEvents(lang = "spa")
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        if "error" in res:
            return
        self.validateGeneralEventList(res)


    def testEventListWithMinArtsSearch(self):
        q = QueryEvents(minArticlesInEvent = 100)
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)


    def testSearchByKeyword(self):
        q = QueryEvents(keywords = "car")  # get events containing word car
        q.setRequestedResult(RequestEventsInfo(page = 1, count = 50, sortBy = "date", sortByAsc = False,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = "org"),
                eventInfo = EventInfoFlags(concepts = False, articleCounts = False, title = False, summary = False, categories = False, location = False, stories = False, imageCount = 0)
                )))
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "events"), "Results should contain events")

        lastEventDate = obj.events.results[0].eventDate if len(obj.events.results) > 0 else ""
        for event in obj.events.results:
            self.assertTrue(event.eventDate <= lastEventDate, "Events are not sorted by date")
            lastEventDate = event.eventDate
            self.assertFalse(hasattr(event, "articleCounts"), "Event should not contain articleCounts")
            self.assertFalse(hasattr(event, "categories"), "Event should not contain categories")
            self.assertFalse(hasattr(event, "concepts"), "Event should not contain concepts")
            self.assertFalse(hasattr(event, "location"), "Event should not contain location")
            self.assertFalse(hasattr(event, "stories"), "Event should not contain stories")
            self.assertFalse(hasattr(event, "images"), "Event should not contain images")
            self.assertFalse(hasattr(event, "title"), "Event should not contain title")
            self.assertFalse(hasattr(event, "summary"), "Event should not contain summary")



    def testSearchByKeywordRev(self):
        q = QueryEvents(keywords = "car")  # get events containing word car
        q.setRequestedResult(RequestEventsInfo(page = 1, count = 50, sortBy = "date", sortByAsc = True,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = "org"),
                eventInfo = EventInfoFlags(concepts = False, articleCounts = False, title = False, summary = False, categories = False, location = False, stories = False, imageCount = 0)
                )))
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "events"), "Results should contain events")

        lastEventDate = obj.events.results[0].eventDate if len(obj.events.results) > 0 else ""
        for event in obj.events.results:
            self.assertTrue(event.eventDate >= lastEventDate, "Events are not sorted by date")
            lastEventDate = event.eventDate
            self.assertFalse(hasattr(event, "articleCounts"), "Event should not contain articleCounts")
            self.assertFalse(hasattr(event, "categories"), "Event should not contain categories")
            self.assertFalse(hasattr(event, "concepts"), "Event should not contain concepts")
            self.assertFalse(hasattr(event, "location"), "Event should not contain location")
            self.assertFalse(hasattr(event, "stories"), "Event should not contain stories")
            self.assertFalse(hasattr(event, "images"), "Event should not contain images")
            self.assertFalse(hasattr(event, "title"), "Event should not contain title")
            self.assertFalse(hasattr(event, "summary"), "Event should not contain summary")


    def testSearchByKeyword2(self):
        q = QueryEvents(keywords = "car")  # get events containing word car
        q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 5,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(type = ["org", "loc"], lang = "spa"))))
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "conceptTrends"), "Results should contain conceptTrends")

        for concept in obj.conceptTrends.conceptInfo:
            self.assertTrue(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")
            self.assertTrue(hasattr(concept.label, "spa"), "Concept did not contain label in expected langage")


    def testSearchByLocation(self):
        q = QueryEvents(locationUri = self.er.getLocationUri("Germany"))
        q.setRequestedResult(RequestEventsInfo(sortBy="size", sortByAsc=False))
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        lastSize = obj.events.results[0].totalArticleCount if len(obj.events.results) > 0 else 0
        for event in obj.events.results:
            self.assertTrue(event.totalArticleCount <= lastSize)
            lastSize = event.totalArticleCount


    def testEventListWithCombinedSearch1(self):
        q = QueryEvents(keywords="germany", lang = ["eng", "deu"], conceptUri = [self.er.getConceptUri("Merkel")], categoryUri = [self.er.getCategoryUri("Business")])
        q.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)
        self.validateGeneralEventList(res)

        q2 = QueryEvents(
            keywords="germany",
            lang = ["eng", "deu"],
            conceptUri = self.er.getConceptUri("Merkel"),
            categoryUri = self.er.getCategoryUri("Business"))
        q2.setRequestedResult(RequestEventsInfo(count = 10, returnInfo = self.returnInfo))
        res2 = self.er.execQuery(q2)
        self.validateGeneralEventList(res2)

        self.ensureSameResults(res, res2, '[events][].totalResults')


    #
    # test different return types
    #

    def testConceptTrends(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsConceptTrends(conceptCount = 5, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptTrends"), "Expected to get 'conceptTrends'")
        self.assertIsNotNone(res.get("conceptTrends").get("trends"), "Expected to get 'trends' property in conceptTrends")
        self.assertIsNotNone(res.get("conceptTrends").get("conceptInfo"), "Expected to get 'conceptInfo' property in conceptTrends")
        self.assertTrue(len(res["conceptTrends"]["conceptInfo"]) <= 5, "Expected to get 5 concepts in concept trends")
        trends = res["conceptTrends"]["trends"]
        self.assertTrue(len(trends) > 0, "Expected to get trends for some days")
        for trend in trends:
            self.assertTrue("date" in trend, "A trend should have a date")
            self.assertTrue("conceptFreq" in trend, "A trend should have a conceptFreq")
            self.assertTrue("totArts" in trend, "A trend should have a totArts property")
            # the api can pad the conceptFreq array to the requested concept count, so it can be longer than conceptInfo
            self.assertTrue(len(trend.get("conceptFreq")) >= len(res["conceptTrends"]["conceptInfo"]), "Concept frequencies should contain an entry for each returned concept")
        for concept in res.get("conceptTrends").get("conceptInfo"):
            self.ensureValidConcept(concept, "conceptTrends")


    def testConceptAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 100, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptAggr"), "Expected to get 'conceptAggr'")
        concepts = res.get("conceptAggr", {}).get("results", [])
        self.assertEqual(len(concepts), 100, "Expected a different number of concept in conceptAggr")
        for concept in concepts:
            self.ensureValidConcept(concept, "conceptAggr")


    def testKeywordAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsKeywordAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("keywordAggr"), "Expected to get 'keywordAggr'")
        keywords = res.get("keywordAggr", {}).get("results")
        self.assertTrue(len(keywords) > 0, "Expected to get some keywords")
        for kw in keywords:
            self.assertTrue("keyword" in kw, "Expected a keyword property")
            self.assertTrue("weight" in kw, "Expected a weight property")


    def testCategoryAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsCategoryAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("categoryAggr"), "Expected to get 'categoryAggr'")
        categories = res.get("categoryAggr", {}).get("results")
        self.assertTrue(len(categories) > 0, "Expected to get a non empty category aggr")
        for cat in categories:
            self.ensureValidCategory(cat, "categoryAggr")


    def testConceptMatrix(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsConceptMatrix(conceptCount = 20, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("conceptMatrix"), "Expected to get 'conceptMatrix'")
        matrix = res.get("conceptMatrix")
        self.assertTrue("scoreMatrix" in matrix, "Expecting 'scoreMatrix' property in conceptMatrix")
        self.assertTrue("freqMatrix" in matrix, "Expecting 'freqMatrix' property in conceptMatrix")
        self.assertTrue("concepts" in matrix, "Expecting 'concepts' property in conceptMatrix")
        self.assertEqual(len(matrix.get("concepts")), 20, "Expected 20 concepts")
        for concept in matrix.get("concepts"):
            self.ensureValidConcept(concept, "conceptMatrix")


    def testSourceAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsSourceAggr(sourceCount = 15, returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("sourceAggr"), "Expected to get 'sourceAggr'")
        sources = res.get("sourceAggr",{}).get("countsPerSource")
        self.assertEqual(len(sources), 15, "Expected 15 sources")
        for sourceInfo in sources:
            self.ensureValidSource(sourceInfo.get("source"), "sourceAggr")
            self.assertTrue(sourceInfo.get("counts"), "Source info should contain counts object")
            self.assertIsNotNone(sourceInfo.get("counts").get("frequency"), "Counts should contain a frequency")
            self.assertIsNotNone(sourceInfo.get("counts").get("total"), "Counts should contain total")

        countries = res.get("sourceAggr", {}).get("countsPerCountry")
        for country in countries:
            # sources with an unknown location are reported in a single item with an empty uri - skip it
            if not country.get("uri"):
                continue
            self.assertTrue(country.get("type") == "loc", "Country should be a location")
            self.assertTrue(country.get("frequency") > 0)


    def testTimeAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsTimeAggr())
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("timeAggr"), "Expected to get 'timeAggr'")
        results = res.get("timeAggr").get("results")
        self.assertTrue(len(results) > 0, "Expected a non-empty time distribution")
        for item in results:
            self.assertTrue("date" in item, "Each time aggregate item should have a date")
            self.assertTrue("count" in item, "Each time aggregate item should have a count")


    def testLocAggr(self):
        q = self.createQuery()
        q.setRequestedResult(RequestEventsLocAggr(returnInfo = self.returnInfo))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("locAggr"), "Expected to get 'locAggr'")
        results = res.get("locAggr").get("results")
        self.assertTrue(len(results) > 0, "Expected a non-empty location aggregate")
        for item in results:
            self.assertTrue("concept" in item, "Each location aggregate item should have a concept")
            self.assertTrue("count" in item, "Each location aggregate item should have a count")
            self.assertEqual(item["concept"].get("type"), "loc", "The location aggregate should contain location concepts")


    def testBreakingEvents(self):
        q = QueryEvents(categoryUri = "news/Business", lang = "eng")
        q.setRequestedResult(RequestEventsBreakingEvents(count = 20))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("breakingEvents"), "Expected to get 'breakingEvents'")
        events = res.get("breakingEvents").get("results")
        self.assertTrue(len(events) > 0, "Expected to get some breaking events")
        for event in events:
            self.assertTrue("uri" in event, "A breaking event should have an uri")
            self.assertTrue("breakingScore" in event, "A breaking event should have a breakingScore")


    def testRecentActivity(self):
        q = QueryEvents(conceptUri = self.er.getConceptUri("Trump"))
        q.setRequestedResult(RequestEventsRecentActivity(maxEventCount = 20, mandatoryLocation = False))
        res = self.er.execQuery(q)

        activity = res.get("recentActivityEvents")
        self.assertIsNotNone(activity, "Expected to get 'recentActivityEvents'")
        self.assertTrue("newestUpdate" in activity, "Expected a 'newestUpdate' property")
        uris = activity.get("activity", [])
        self.assertTrue(len(uris) > 0, "Expected some recently updated events")
        eventInfo = activity.get("eventInfo", {})
        for uri in uris:
            self.assertTrue(uri in eventInfo, "Each activity uri should have a matching entry in eventInfo")


    def testSearchBySource(self):
        q = QueryEvents(sourceUri = self.er.getNewsSourceUri("bbc"))             # and have been reported by BBC
        q.setRequestedResult(RequestEventsUriWgtList())            # return uris of all events
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)
        self.assertTrue(hasattr(obj, "uriWgtList"), "Results should contain uriWgtList")


    def testSearchBySource2(self):
        q = QueryEvents(sourceUri = self.er.getNewsSourceUri("bbc"))             # and have been reported by BBC
        q.setRequestedResult(RequestEventsInfo(page = 1, count = 50, sortBy = "size", sortByAsc = True,
            returnInfo = ReturnInfo(
                conceptInfo = ConceptInfoFlags(lang = "deu", type = "wiki"),
                eventInfo = EventInfoFlags(concepts = True, articleCounts = True, title = True, summary = True, categories = True, location = True, stories = True, imageCount = 1)
                )))   # return event details for first 50 events
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "events"), "Results should contain events")

        lastArtCount = 0
        self.assertTrue(len(obj.events.results) <= 50, "Returned list of events was too long")

        for event in obj.events.results:
            self.assertTrue(hasattr(event, "articleCounts"), "Event should contain articleCounts")
            self.assertTrue(hasattr(event, "categories"), "Event should contain categories")
            self.assertTrue(hasattr(event, "concepts"), "Event should contain concepts")
            self.assertTrue(hasattr(event, "stories"), "Event should contain stories")
            self.assertTrue(hasattr(event, "title"), "Event should contain title")
            self.assertTrue(hasattr(event, "summary"), "Event should contain summary")
            self.assertTrue(hasattr(event, "images"), "Event should contain images")
            self.assertTrue(hasattr(event, "location"), "Event should contain location")

            self.assertTrue(event.totalArticleCount >= lastArtCount, "Events were not sorted by increasing size")
            lastArtCount = event.totalArticleCount
            for concept in event.concepts:
                self.assertTrue(hasattr(concept.label, "deu"), "Concept should contain label in german language")
                self.assertTrue(concept.type == "wiki", "Got concept of invalid type")


    def testSearchBySource3(self):
        q = QueryEvents(sourceUri = self.er.getNewsSourceUri("bbc"))             # and have been reported by BBC
        q.setRequestedResult(RequestEventsConceptAggr(conceptCount = 5,
            returnInfo = ReturnInfo(conceptInfo = ConceptInfoFlags(type = ["org", "loc"]))))        # compute concept aggregate on the events
        res = self.er.execQuery(q)
        obj = createStructFromDict(res)

        self.assertTrue(hasattr(obj, "conceptAggr"), "Results should contain conceptAggr")

        concepts = obj.conceptAggr.results
        self.assertTrue(len(concepts) <= 10, "Received a list of concepts that is too long")
        for concept in concepts:
            self.assertTrue(concept.type == "loc" or concept.type == "org", "Got concept of invalid type")

    #
    # tests for iterators
    #

    def testQueryEventsIterator(self):
        # check that the iterator really downloads all events
        obamaUri = self.er.getConceptUri("Obama")
        iter = QueryEventsIter(keywords = "germany", conceptUri = obamaUri)
        eventCount = iter.count(self.er)
        events = list(iter.execQuery(self.er, returnInfo = self.returnInfo))
        # the count and the iterated results come from separate requests and the (non-archive) data is continuously updated
        self.assertCountsClose(eventCount, len(events), "Event iterator did not generate the full list of events")


    def testQuery1(self):
        """
        find events about Obama that also mention keyword "germany"
        """
        obamaUri = self.er.getConceptUri("Obama")
        iter = QueryEventsIter(keywords = "germany", conceptUri = obamaUri)
        for event in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 10):
            self.ensureEventHasConcept(event, obamaUri)
            articleIter = QueryEventArticlesIter(event["uri"], lang = allLangs)
            articles = list(articleIter.execQuery(self.er, returnInfo = self.returnInfo))
            self.ensureArticlesContainText(articles, "germany")


    def testQuery2(self):
        """
        search for events covered by a given news source, about a category and mentioning two keywords
        """
        sourceUri = self.er.getNewsSourceUri("los angeles")
        businessCat = self.er.getCategoryUri("business")
        iter = QueryEventsIter(keywords = "obama trump", sourceUri = sourceUri, categoryUri = businessCat)
        for event in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 10):
            self.ensureEventHasCategory(event, businessCat)

            articleIter = QueryEventArticlesIter(event["uri"], lang = allLangs)
            articles = list(articleIter.execQuery(self.er, returnInfo = self.returnInfo))
            self.ensureArticlesContainText(articles, "obama")
            self.ensureArticlesContainText(articles, "trump")

            hasArticleFromLAT = [article["source"]["uri"] == sourceUri for article in articles]
            self.assertTrue(True in hasArticleFromLAT, "event did not have any articles from source los angeles times")


    def testQuery3(self):
        """
        query with some positive but several negative conditions
        """
        obamaUri = self.er.getConceptUri("Obama")
        politicsUri = self.er.getConceptUri("politics")
        chinaUri = self.er.getConceptUri("china")
        unitedStatesUri = self.er.getConceptUri("united states")

        srcDailyCallerUri = self.er.getNewsSourceUri("daily caller")
        srcAawsatUri = self.er.getNewsSourceUri("aawsat")
        srcSvodkaUri = self.er.getNewsSourceUri("svodka")

        catBusinessUri = self.er.getCategoryUri("business")
        catPoliticsUri = self.er.getCategoryUri("politics")
        iter = QueryEventsIter(conceptUri = obamaUri,
                               ignoreConceptUri = [politicsUri, chinaUri, unitedStatesUri],
                               ignoreKeywords=["trump", "politics", "michelle"],
                               ignoreSourceUri = [srcDailyCallerUri, srcAawsatUri, srcSvodkaUri],
                               ignoreCategoryUri = [catBusinessUri, catPoliticsUri],
                               ignoreLang = "zho")
        for event in iter.execQuery(self.er, returnInfo = self.returnInfo, maxItems = 20):
            self.ensureEventHasConcept(event, obamaUri)
            self.ensureEventHasNotConcept(event, politicsUri)
            self.ensureEventHasNotConcept(event, chinaUri)
            self.ensureEventHasNotConcept(event, unitedStatesUri)

            artIter = QueryEventArticlesIter(event["uri"], lang = allLangs)
            articles = list(artIter.execQuery(self.er))
            self.ensureArticlesDoNotContainText(articles, "trump")
            self.ensureArticlesDoNotContainText(articles, "politics")
            self.ensureArticlesDoNotContainText(articles, "michelle")

            self.ensureArticlesNotFromSource(articles, srcDailyCallerUri)
            self.ensureArticlesNotFromSource(articles, srcAawsatUri)
            self.ensureArticlesNotFromSource(articles, srcSvodkaUri)

            self.ensureEventHasNotCategory(event, catBusinessUri)
            self.ensureEventHasNotCategory(event, catPoliticsUri)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryEvents)
    unittest.TextTestRunner(verbosity=3).run(suite)
