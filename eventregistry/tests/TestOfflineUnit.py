"""
Offline unit tests for the eventregistry package.
These tests do NOT make any network requests - the EventRegistry HTTP layer is mocked
where needed. They can therefore run without an API key and without internet access.

Run with:
    python -m unittest eventregistry.tests.TestOfflineUnit -v
"""
import datetime
import json
import os
import tempfile
import unittest
from unittest import mock

from eventregistry import *


class FakeResponse:
    """minimal stand-in for requests.Response"""
    def __init__(self, status_code = 200, data = None, headers = None, text = ""):
        self.status_code = status_code
        self._data = data if data is not None else {}
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._data


def makeER(**kwargs):
    """create an EventRegistry instance that never sleeps and never retries forever"""
    kwargs.setdefault("apiKey", "TESTKEY")
    kwargs.setdefault("minDelayBetweenRequests", 0)
    kwargs.setdefault("repeatFailedRequestCount", 0)
    # point to a settings file that does not exist so that the local settings.json is not picked up
    kwargs.setdefault("settingsFName", os.path.join(tempfile.gettempdir(), "er-no-such-settings.json"))
    return EventRegistry(**kwargs)


class TestBaseHelpers(unittest.TestCase):

    def testRemoveInvalidChars(self):
        self.assertEqual(removeInvalidChars("abc"), "abc")
        self.assertEqual(removeInvalidChars("a\x00b\x08c\x0bd\x1fe"), "abcde")
        # tab, newline and carriage return are valid and must be kept
        self.assertEqual(removeInvalidChars("a\tb\nc\rd"), "a\tb\nc\rd")

    def testTryParseInt(self):
        self.assertEqual(tryParseInt("42"), 42)
        self.assertEqual(tryParseInt("notanumber", val = -1), -1)
        self.assertEqual(tryParseInt("", val = -1), -1)

    def testStruct(self):
        s = createStructFromDict({"a": 1, "b": {"c": [1, 2, {"d": "x"}]}})
        self.assertEqual(s.a, 1)
        self.assertEqual(s.b.c[0], 1)
        self.assertEqual(s.b.c[2].d, "x")
        self.assertTrue(s.has("a"))
        self.assertFalse(s.has("nope"))
        lst = createStructFromDict([{"a": 1}, {"a": 2}])
        self.assertEqual([item.a for item in lst], [1, 2])

    def testQueryItems(self):
        andItems = QueryItems.AND(["a", "b"])
        self.assertEqual(andItems.getOper(), "$and")
        self.assertEqual(andItems.getItems(), ["a", "b"])
        orItems = QueryItems.OR(["c"])
        self.assertEqual(orItems.getOper(), "$or")

    def testEncodeDateInvalidValues(self):
        self.assertRaises(ValueError, QueryParamsBase.encodeDate, "01-01-2015")
        self.assertRaises(TypeError, QueryParamsBase.encodeDate, 20150101)
        self.assertRaises(ValueError, QueryParamsBase.encodeDateTime, "2015-01-01")

    def testEncodeDateTimeWithTimezone(self):
        # timezone-aware datetimes must be converted to UTC
        dt = datetime.datetime(2020, 6, 1, 14, 30, 0, tzinfo = datetime.timezone(datetime.timedelta(hours = 2)))
        self.assertTrue(QueryParamsBase.encodeDateTime(dt).startswith("2020-06-01T12:30:00"))


class TestQueryParamAssembly(unittest.TestCase):

    def testSetQueryArrValWithString(self):
        q = QueryParamsBase()
        q._setQueryArrVal("obama", "keyword", "keywordOper", "and")
        self.assertEqual(q.queryParams["keyword"], "obama")
        self.assertNotIn("keywordOper", q.queryParams)

    def testSetQueryArrValWithQueryItems(self):
        q = QueryParamsBase()
        q._setQueryArrVal(QueryItems.OR(["a", "b"]), "conceptUri", "conceptOper", "and")
        self.assertEqual(q.queryParams["conceptUri"], ["a", "b"])
        self.assertEqual(q.queryParams["conceptOper"], "or")

    def testSetQueryArrValWithList(self):
        q = QueryParamsBase()
        q._setQueryArrVal(["a", "b"], "conceptUri", "conceptOper", "and")
        self.assertEqual(q.queryParams["conceptUri"], ["a", "b"])
        self.assertEqual(q.queryParams["conceptOper"], "and")

    def testSetQueryArrValInvalidOperatorDoesNotMutate(self):
        q = QueryParamsBase()
        # "and" operator is invalid when only "or" is allowed (propOperName is None)
        self.assertRaises(ValueError, q._setQueryArrVal, QueryItems.AND(["a", "b"]), "sourceUri", None, "or")
        self.assertNotIn("sourceUri", q.queryParams)

    def testSetQueryArrValNoneAndEmptyIgnored(self):
        q = QueryParamsBase()
        q._setQueryArrVal(None, "keyword", None, "or")
        q._setQueryArrVal("", "keyword", None, "or")
        self.assertEqual(q.queryParams, {})

    def testCopyDoesNotShareState(self):
        q = QueryParamsBase()
        q._setVal("a", 1)
        q2 = QueryParamsBase.copy(q)
        q2._setVal("a", 2)
        self.assertEqual(q.queryParams["a"], 1)

    def testQueryRequiresResultType(self):
        q = Query()
        self.assertRaises(ValueError, q._getQueryParams)


class TestQueryArticlesConstruction(unittest.TestCase):

    def testBasicParams(self):
        q = QueryArticles(keywords = "obama", lang = "eng", dateStart = "2020-01-01", dateEnd = datetime.date(2020, 1, 31))
        params = q._getQueryParams()
        self.assertEqual(params["action"], "getArticles")
        self.assertEqual(params["keyword"], "obama")
        self.assertEqual(params["lang"], "eng")
        self.assertEqual(params["dateStart"], "2020-01-01")
        self.assertEqual(params["dateEnd"], "2020-01-31")
        self.assertEqual(params["resultType"], ["articles"])

    def testDefaultsAreNotSent(self):
        params = QueryArticles(keywords = "x")._getQueryParams()
        for prop in ["isDuplicateFilter", "hasDuplicateFilter", "eventFilter", "startSourceRankPercentile",
                     "endSourceRankPercentile", "minSentiment", "maxSentiment", "dataType", "keywordLoc"]:
            self.assertNotIn(prop, params, "property '%s' should not be included when default" % prop)

    def testNonDefaultsAreSent(self):
        q = QueryArticles(keywords = "x", isDuplicateFilter = "skipDuplicates", minSentiment = -0.5, maxSentiment = 0.5,
                          startSourceRankPercentile = 20, endSourceRankPercentile = 80, dataType = ["news", "pr"])
        params = q._getQueryParams()
        self.assertEqual(params["isDuplicateFilter"], "skipDuplicates")
        self.assertEqual(params["minSentiment"], -0.5)
        self.assertEqual(params["maxSentiment"], 0.5)
        self.assertEqual(params["startSourceRankPercentile"], 20)
        self.assertEqual(params["endSourceRankPercentile"], 80)
        self.assertEqual(params["dataType"], ["news", "pr"])

    def testInvalidPercentilesRejected(self):
        self.assertRaises(ValueError, QueryArticles, startSourceRankPercentile = 15)
        self.assertRaises(ValueError, QueryArticles, startSourceRankPercentile = 50, endSourceRankPercentile = 40)

    def testInitWithArticleUriList(self):
        q = QueryArticles.initWithArticleUriList(["uri1", "uri2"])
        self.assertEqual(q.queryParams["articleUri"], ["uri1", "uri2"])
        self.assertEqual(q.queryParams["dataType"], ["news", "blog", "pr"])
        self.assertRaises(TypeError, QueryArticles.initWithArticleUriList, 123)

    def testInitWithArticleUriWgtList(self):
        q = QueryArticles.initWithArticleUriWgtList(["u1:10", "u2:20"])
        self.assertEqual(q.queryParams["articleUriWgtList"], "u1:10,u2:20")
        self.assertEqual(q.queryParams["dataType"], ["news", "blog", "pr"])
        q = QueryArticles.initWithArticleUriWgtList("u1:10,u2:20")
        self.assertEqual(q.queryParams["articleUriWgtList"], "u1:10,u2:20")

    def testInitWithComplexQuery(self):
        cq = ComplexArticleQuery(BaseQuery(keyword = "abc"))
        q = QueryArticles.initWithComplexQuery(cq)
        self.assertEqual(json.loads(q.queryParams["query"]), {"$query": {"keyword": "abc"}})
        # a valid json string is accepted
        q = QueryArticles.initWithComplexQuery('{"$query": {"keyword": "abc"}}')
        self.assertIn("query", q.queryParams)
        # a dict is accepted
        q = QueryArticles.initWithComplexQuery({"$query": {"keyword": "abc"}})
        self.assertIn("query", q.queryParams)
        # invalid json must raise ValueError
        self.assertRaises(ValueError, QueryArticles.initWithComplexQuery, "{not valid json")
        self.assertRaises(ValueError, QueryArticlesIter.initWithComplexQuery, "{not valid json")


class TestQueryEventsConstruction(unittest.TestCase):

    def testInitWithEventUriList(self):
        q = QueryEvents.initWithEventUriList(["eng-1", "eng-2"])
        self.assertEqual(q.queryParams["eventUriList"], "eng-1,eng-2")
        # a single string uri must NOT be split into characters
        q = QueryEvents.initWithEventUriList("eng-123")
        self.assertEqual(q.queryParams["eventUriList"], "eng-123")

    def testInitWithComplexQueryInvalidJson(self):
        self.assertRaises(ValueError, QueryEvents.initWithComplexQuery, "{bad json")
        self.assertRaises(ValueError, QueryEventsIter.initWithComplexQuery, "{bad json")

    def testRequestEventsInfoBounds(self):
        self.assertRaises(ValueError, RequestEventsInfo, page = 0)
        self.assertRaises(ValueError, RequestEventsInfo, count = 51)


class TestQueryMentionsConstruction(unittest.TestCase):

    def testBasicParams(self):
        q = QueryMentions(keywords = "acquisition", eventTypeUri = "et/business/acquisitions-mergers")
        params = q._getQueryParams()
        self.assertEqual(params["action"], "getMentions")
        self.assertEqual(params["keyword"], "acquisition")
        self.assertEqual(params["eventTypeUri"], "et/business/acquisitions-mergers")

    def testInitWithComplexQueryInvalidJson(self):
        self.assertRaises(ValueError, QueryMentions.initWithComplexQuery, "{bad json")
        self.assertRaises(ValueError, QueryMentionsIter.initWithComplexQuery, "{bad json")

    def testRequestMentionsInfoBounds(self):
        self.assertRaises(ValueError, RequestMentionsInfo, count = 101)


class TestComplexQueryConstruction(unittest.TestCase):

    def testBaseQuery(self):
        q = BaseQuery(keyword = QueryItems.AND(["a", "b"]), lang = "eng", dateStart = "2020-01-01",
                      exclude = BaseQuery(keyword = "spam"))
        obj = q.getQuery()
        self.assertEqual(obj["keyword"], {"$and": ["a", "b"]})
        self.assertEqual(obj["lang"], "eng")
        self.assertEqual(obj["dateStart"], "2020-01-01")
        self.assertEqual(obj["$not"], {"keyword": "spam"})

    def testCombinedQuery(self):
        q = CombinedQuery.OR([BaseQuery(keyword = "a"), BaseQuery(keyword = "b")], exclude = BaseQuery(lang = "deu"))
        obj = q.getQuery()
        self.assertEqual(obj["$or"], [{"keyword": "a"}, {"keyword": "b"}])
        self.assertEqual(obj["$not"], {"lang": "deu"})
        self.assertRaises(ValueError, CombinedQuery.AND, [])
        self.assertRaises(TypeError, CombinedQuery.AND, ["notaquery"])

    def testComplexArticleQueryFilters(self):
        cq = ComplexArticleQuery(BaseQuery(keyword = "x"), minSentiment = -0.4, isDuplicateFilter = "skipDuplicates",
                                 dataType = ["news", "blog"])
        obj = cq.getQuery()
        self.assertEqual(obj["$filter"], {"dataType": ["news", "blog"], "minSentiment": -0.4, "isDuplicate": "skipDuplicates"})
        # no filter key when everything is default
        self.assertNotIn("$filter", ComplexArticleQuery(BaseQuery(keyword = "x")).getQuery())


class TestReturnInfoFlags(unittest.TestCase):

    def testDefaultFlagsAreEmpty(self):
        # when all defaults are used, no flags need to be sent to the API
        self.assertEqual(ReturnInfo().getParams(), {})

    def testNonDefaultFlags(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 200, concepts = True, image = False))
        params = ri.getParams()
        self.assertEqual(params["articleBodyLen"], 200)
        self.assertEqual(params["includeArticleConcepts"], True)
        self.assertEqual(params["includeArticleImage"], False)

    def testValsPrefixing(self):
        # without a prefix the first letter is lowercased, with a prefix it is uppercased and prepended
        flags = ArticleInfoFlags(bodyLen = 200)
        self.assertEqual(flags._getVals(), {"articleBodyLen": 200})
        self.assertEqual(flags._getVals("articles"), {"articlesArticleBodyLen": 200})

    def testInstancesDoNotShareState(self):
        r1 = ReturnInfo()
        r2 = ReturnInfo()
        self.assertIsNot(r1.articleInfo, r2.articleInfo)
        r1.articleInfo._setFlag("includeArticleConcepts", True, False)
        self.assertNotIn("includeArticleConcepts", r2.articleInfo._getFlags())

    def testKwdArgs(self):
        flags = ArticleInfoFlags(someCustomFlag = True, someCustomVal = 7)
        self.assertEqual(flags._getFlags().get("someCustomFlag"), True)
        self.assertEqual(flags._getVals().get("someCustomVal"), 7)

    def testGetConfUsesCorrectFlagObjects(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True),
                        conceptFolderInfo = ConceptFolderInfoFlags(definition = True))
        conf = ri.getConf()
        self.assertIn("includeConceptFolderDefinition", conf["conceptFolderInfo"])
        self.assertNotIn("includeArticleConcepts", conf["conceptFolderInfo"])

    def testSaveAndLoadRoundTrip(self):
        ri = ReturnInfo(articleInfo = ArticleInfoFlags(bodyLen = 100, concepts = True),
                        conceptInfo = ConceptInfoFlags(lang = "spa"))
        fd, fname = tempfile.mkstemp(suffix = ".json")
        os.close(fd)
        try:
            with open(fname, "w", encoding = "utf-8") as f:
                json.dump(ri.getConf(), f)
            loaded = ReturnInfo.loadFromFile(fname)
            self.assertEqual(loaded.getParams(), ri.getParams())
        finally:
            os.remove(fname)


class TestEventRegistryRequests(unittest.TestCase):

    def testCallerParamsNotMutated(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {"ok": True}))
        params = {"q": "test"}
        ret = er.jsonRequest("/api/v1/test", params)
        self.assertEqual(ret, {"ok": True})
        self.assertEqual(params, {"q": "test"}, "the caller's parameter dict must not be modified")
        # but the api key must be included in the actual request
        sentJson = er._reqSession.post.call_args.kwargs["json"]
        self.assertEqual(sentJson["apiKey"], "TESTKEY")

    def testAnalyticsCallerParamsNotMutated(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {"ok": True}))
        params = {"text": "hello"}
        er.jsonRequestAnalytics("/api/v1/annotate", params)
        self.assertEqual(params, {"text": "hello"})

    def testArchiveFlag(self):
        er = makeER(allowUseOfArchive = False)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["forceMaxDataTimeWindow"], 31)
        # per-request override wins
        er.jsonRequest("/api/v1/test", {}, allowUseOfArchive = True)
        self.assertNotIn("forceMaxDataTimeWindow", er._reqSession.post.call_args.kwargs["json"])

    def testFailedRequestRaisesAndReleasesLock(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 400, text = "bad request"))
        self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
        # the lock must be free again after the failure
        self.assertTrue(er._lock.acquire(timeout = 1), "lock was not released after a failed request")
        er._lock.release()

    def testStopStatusCodesDoNotRetry(self):
        er = makeER(repeatFailedRequestCount = 5)
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 401, text = "limit"))
        self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_count, 1, "401 responses must not be retried")

    def testAllStopStatusCodesDoNotRetry(self):
        for code in [204, 400, 401, 403]:
            er = makeER(repeatFailedRequestCount = 5)
            er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = code, text = "err"))
            with mock.patch("eventregistry.EventRegistry.time.sleep"):
                self.assertRaises(Exception, er.jsonRequest, "/api/v1/test", {})
            self.assertEqual(er._reqSession.post.call_count, 1, "%d responses must not be retried" % code)

    def testTemporaryStatusCodesAreRetried(self):
        for code in [429, 500, 503]:
            er = makeER(repeatFailedRequestCount = 3)
            er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = code, text = "err"), FakeResponse(data = {"ok": 1})])
            with mock.patch("eventregistry.EventRegistry.time.sleep") as sleep:
                self.assertEqual(er.jsonRequest("/api/v1/test", {}), {"ok": 1})
            self.assertEqual(er._reqSession.post.call_count, 2, "%d responses should be retried" % code)
            self.assertTrue(sleep.called, "the request should be repeated only after a delay")

    def testAnalyticsTemporaryStatusCodeIsRetried(self):
        er = makeER(repeatFailedRequestCount = 3)
        er._reqSession.post = mock.Mock(side_effect = [FakeResponse(status_code = 503, text = "down"), FakeResponse(data = {"ok": 1})])
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            self.assertEqual(er.jsonRequestAnalytics("/api/v1/test", {}), {"ok": 1})
        self.assertEqual(er._reqSession.post.call_count, 2)

    def testErrorMessageContainsStatusCodeAndMeaning(self):
        er = makeER()
        er._reqSession.post = mock.Mock(return_value = FakeResponse(status_code = 429, text = "slow down"))
        with mock.patch("eventregistry.EventRegistry.time.sleep"):
            with self.assertRaises(Exception) as ctx:
                er.jsonRequest("/api/v1/test", {})
        msg = str(ctx.exception)
        self.assertIn("429", msg)
        self.assertIn("Too many requests", msg)
        self.assertIn("slow down", msg)

    def testRateLimitHeadersParsed(self):
        er = makeER()
        headers = {"x-ratelimit-limit": "5000", "x-ratelimit-remaining": "1234"}
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}, headers = headers))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er.getDailyAvailableRequests(), 5000)
        self.assertEqual(er.getRemainingAvailableRequests(), 1234)
        self.assertEqual(er.getLastHeader("x-ratelimit-limit"), "5000")

    def testExtraParams(self):
        er = makeER()
        er.setExtraParams({"custom": "val"})
        er._reqSession.post = mock.Mock(return_value = FakeResponse(data = {}))
        er.jsonRequest("/api/v1/test", {})
        self.assertEqual(er._reqSession.post.call_args.kwargs["json"]["custom"], "val")

    def testGetUrl(self):
        er = makeER()
        url = er.getUrl(QueryArticles(keywords = "obama"))
        self.assertTrue(url.startswith("https://eventregistry.org/api/v1/article?"))
        self.assertIn("keyword=obama", url)

    def testGetUriFromUriWgt(self):
        self.assertEqual(EventRegistry.getUriFromUriWgt(["uri1:100", "uri2:50"]), ["uri1", "uri2"])
        self.assertRaises(TypeError, EventRegistry.getUriFromUriWgt, "uri1:100")

    def testRequestLogDefaultsToUserFolder(self):
        er = makeER()
        self.assertEqual(er._requestLogFName, os.path.join(os.path.expanduser("~"), ".eventregistry", "requests_log.txt"))

    def testExecQueryRequiresQueryObject(self):
        er = makeER()
        self.assertRaises(TypeError, er.execQuery, {"not": "a query"})

    def testGetArticleUrisAcceptsOnlySingleUrl(self):
        er = makeER()
        er.jsonRequest = mock.Mock(return_value = {"http://x.com/1": "uri-1"})
        self.assertEqual(er.getArticleUris("http://x.com/1"), {"http://x.com/1": "uri-1"})
        er.jsonRequest.assert_called_once_with("/api/v1/articleMapper", {"articleUrl": "http://x.com/1"})
        self.assertRaises(TypeError, er.getArticleUris, ["http://x.com/1", "http://x.com/2"])

    def testArticleMapperCachesResults(self):
        er = makeER()
        er.getArticleUris = mock.Mock(return_value = {"http://x.com/1": "uri-1"})
        mapper = ArticleMapper(er)
        self.assertEqual(mapper.getArticleUri("http://x.com/1"), "uri-1")
        self.assertEqual(mapper.getArticleUri("http://x.com/1"), "uri-1")
        self.assertEqual(er.getArticleUris.call_count, 1, "repeated lookups should be served from the cache")


class TestIterators(unittest.TestCase):

    def _makeArticlePage(self, uris, pages):
        return {"articles": {"results": [{"uri": u} for u in uris], "pages": pages, "totalResults": len(uris)}}

    def testArticleIteratorPagesThroughResults(self):
        er = makeER()
        responses = [self._makeArticlePage(["a1", "a2"], 2), self._makeArticlePage(["a3"], 2)]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryArticlesIter(keywords = "x").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2", "a3"])
        self.assertEqual(er.execQuery.call_count, 2)

    def testArticleIteratorMaxItems(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = self._makeArticlePage(["a1", "a2", "a3"], 1))
        it = QueryArticlesIter(keywords = "x").execQuery(er, maxItems = 2)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"])

    def testArticleIteratorErrorResponse(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"error": "something went wrong"})
        it = QueryArticlesIter(keywords = "x").execQuery(er)
        self.assertEqual(list(it), [])

    def testArticleIteratorCount(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"articles": {"results": [], "pages": 1, "totalResults": 512}})
        self.assertEqual(QueryArticlesIter(keywords = "x").count(er), 512)

    def testArticleIteratorCountKeepsRequestedResult(self):
        er = makeER()
        er.execQuery = mock.Mock(return_value = {"articles": {"results": [], "pages": 1, "totalResults": 5}})
        q = QueryArticlesIter(keywords = "x")
        q.setRequestedResult(RequestArticlesConceptAggr())
        q.count(er)
        self.assertIsInstance(q.resultTypeList[0], RequestArticlesConceptAggr, "count() should not overwrite the requested result type")

    def testArticleIteratorCanBeIteratedTwice(self):
        er = makeER()
        responses = [self._makeArticlePage(["a1", "a2"], 1), self._makeArticlePage(["a1", "a2"], 1)]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryArticlesIter(keywords = "x").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"])
        self.assertEqual([a["uri"] for a in it], ["a1", "a2"], "a second iteration should re-execute the query and return the results again")

    def testArticleIteratorRequiresExecQuery(self):
        self.assertRaises(RuntimeError, iter, QueryArticlesIter(keywords = "x"))

    def testEventIteratorPagesThroughResults(self):
        er = makeER()
        responses = [
            {"events": {"results": [{"uri": "e1"}], "pages": 2, "totalResults": 2}},
            {"events": {"results": [{"uri": "e2"}], "pages": 2, "totalResults": 2}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryEventsIter(keywords = "x").execQuery(er)
        self.assertEqual([e["uri"] for e in it], ["e1", "e2"])

    def testMentionsIteratorPagesThroughResults(self):
        er = makeER()
        responses = [
            {"mentions": {"results": [{"uri": "m1"}, {"uri": "m2"}], "pages": 1, "totalResults": 2}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryMentionsIter(keywords = "x").execQuery(er)
        self.assertEqual([m["uri"] for m in it], ["m1", "m2"])

    def testEventArticlesIterator(self):
        er = makeER()
        responses = [
            {"eng-1": {"articles": {"results": [{"uri": "a1"}], "pages": 1, "totalResults": 1}}},
        ]
        er.execQuery = mock.Mock(side_effect = responses)
        it = QueryEventArticlesIter("eng-1").execQuery(er)
        self.assertEqual([a["uri"] for a in it], ["a1"])


class TestTopicPageDefinition(unittest.TestCase):

    def setUp(self):
        self.tp = TopicPage(eventRegistry = None)

    def testArticleIsDuplicateFilterUsesCorrectKey(self):
        self.tp.setArticleIsDuplicateFilter("keepAll")
        self.assertEqual(self.tp.topicPage["articleIsDuplicate"], "keepAll")
        self.assertNotIn("isDuplicateFilter", self.tp.topicPage)
        self.assertRaises(ValueError, self.tp.setArticleIsDuplicateFilter, "bogusValue")

    def testAddConcept(self):
        self.tp.addConcept("http://en.wikipedia.org/wiki/Apple_Inc.", 30, label = "Apple", required = True)
        concept = self.tp.topicPage["concepts"][0]
        self.assertEqual(concept["uri"], "http://en.wikipedia.org/wiki/Apple_Inc.")
        self.assertEqual(concept["wgt"], 30)
        self.assertEqual(concept["label"], "Apple")
        self.assertTrue(concept["required"])
        # required and excluded cannot both be set
        self.assertRaises(ValueError, self.tp.addConcept, "uri", 10, required = True, excluded = True)

    def testAddKeywordAndCategory(self):
        self.tp.addKeyword("iphone", 20)
        self.assertEqual(self.tp.topicPage["keywords"][0]["keyword"], "iphone")
        self.tp.addCategory("dmoz/Business", 15, excluded = True)
        self.assertTrue(self.tp.topicPage["categories"][0]["excluded"])
        self.assertRaises(ValueError, self.tp.addKeyword, "", 10)

    def testLanguageValidation(self):
        self.tp.setLanguages("eng")
        self.assertEqual(self.tp.topicPage["langs"], ["eng"])
        self.tp.setLanguages(["eng", "deu"])
        self.assertEqual(self.tp.topicPage["langs"], ["eng", "deu"])
        self.assertRaises(ValueError, self.tp.setLanguages, "english")

    def testSourceRankPercentileValidation(self):
        self.tp.setSourceRankPercentile(10, 60)
        self.assertEqual(self.tp.topicPage["startSourceRankPercentile"], 10)
        self.assertEqual(self.tp.topicPage["endSourceRankPercentile"], 60)
        self.assertRaises(ValueError, self.tp.setSourceRankPercentile, 15, 60)
        self.assertRaises(ValueError, self.tp.setSourceRankPercentile, 60, 40)

    def testSaveAndLoadDefinitionRoundTrip(self):
        self.tp.addKeyword("solar", 25)
        self.tp.setMaxDaysBack(14)
        fd, fname = tempfile.mkstemp(suffix = ".json")
        os.close(fd)
        try:
            self.tp.saveTopicPageDefinitionToFile(fname)
            tp2 = TopicPage(eventRegistry = None)
            tp2.loadTopicPageFromFile(fname)
            self.assertEqual(tp2.topicPage, self.tp.topicPage)
        finally:
            os.remove(fname)


class TestRequestClasses(unittest.TestCase):

    def testRequestArticlesInfoBounds(self):
        self.assertRaises(ValueError, RequestArticlesInfo, page = 0)
        self.assertRaises(ValueError, RequestArticlesInfo, count = 101)
        req = RequestArticlesInfo(page = 2, count = 50, sortBy = "date")
        self.assertEqual(req.resultType, "articles")
        self.assertEqual(req.articlesPage, 2)
        self.assertEqual(req.articlesCount, 50)
        req.setPage(5)
        self.assertEqual(req.articlesPage, 5)

    def testRequestArticlesReturnInfoFlagsApplied(self):
        req = RequestArticlesInfo(returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True)))
        self.assertTrue(getattr(req, "includeArticleConcepts"))

    def testRequestArticlesRecentActivityExclusiveParams(self):
        self.assertRaises(ValueError, RequestArticlesRecentActivity,
                          updatesAfterTm = "2020-01-01T00:00:00", updatesAfterMinsAgo = 10)
        req = RequestArticlesRecentActivity(updatesAfterMinsAgo = 10)
        self.assertEqual(req.recentActivityArticlesUpdatesAfterMinsAgo, 10)

    def testRequestEventArticlesForwardsFilters(self):
        req = RequestEventArticles(keywords = "tesla", lang = "eng")
        self.assertEqual(req.resultType, "articles")
        self.assertEqual(req.keyword, "tesla")
        self.assertEqual(req.lang, "eng")
        # queryParams must have been merged into the object and removed
        self.assertFalse(hasattr(req, "queryParams"))

    def testResultTypesAreSet(self):
        self.assertEqual(RequestArticlesUriWgtList().resultType, "uriWgtList")
        self.assertEqual(RequestArticlesTimeAggr().resultType, "timeAggr")
        self.assertEqual(RequestArticlesConceptAggr().resultType, "conceptAggr")
        self.assertEqual(RequestEventsUriWgtList().resultType, "uriWgtList")
        self.assertEqual(RequestEventsConceptAggr().resultType, "conceptAggr")
        self.assertEqual(RequestEventInfo().resultType, "info")
        self.assertEqual(RequestMentionsInfo().resultType, "mentions")
        self.assertEqual(RequestStoryInfo().resultType, "info")
        self.assertEqual(RequestArticleInfo().resultType, "info")


class TestAnalyticsParamAssembly(unittest.TestCase):

    def _makeAnalytics(self):
        er = makeER()
        er.jsonRequestAnalytics = mock.Mock(return_value = {})
        return er, Analytics(er)

    def testAnnotate(self):
        er, an = self._makeAnalytics()
        an.annotate("some text", lang = "eng", customParams = {"extra": 1})
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(url, "/api/v1/annotate")
        self.assertEqual(params["text"], "some text")
        self.assertEqual(params["lang"], "eng")
        self.assertEqual(params["extra"], 1)

    def testSentimentValidatesMethod(self):
        er, an = self._makeAnalytics()
        self.assertRaises(ValueError, an.sentiment, "text", method = "bogus")
        an.sentiment("text", method = "rnn")
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(params["method"], "rnn")

    def testExtractArticleInfoSerializesHeadersAndCookies(self):
        er, an = self._makeAnalytics()
        an.extractArticleInfo("http://x.com", headers = {"User-Agent": "test"}, cookies = {"a": "b"})
        url, params = er.jsonRequestAnalytics.call_args.args
        self.assertEqual(json.loads(params["headers"]), {"User-Agent": "test"})
        self.assertEqual(json.loads(params["cookies"]), {"a": "b"})


if __name__ == "__main__":
    unittest.main(verbosity = 2)
