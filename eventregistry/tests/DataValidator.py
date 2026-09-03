import unittest, jmespath, unicodedata
from eventregistry import *


class DataValidator(unittest.TestCase):
    def removeAccents(self, inputStr):
        nfkdForm = unicodedata.normalize('NFKD', inputStr)
        return "".join([c for c in nfkdForm if not unicodedata.combining(c)])


    def __init__(self, *args, **kwargs):
        super(DataValidator, self).__init__(*args, **kwargs)

        # load settings from the current folder. use different instance than for regular ER requests
        currPath = os.path.split(os.path.realpath(__file__))[0]
        settPath = os.path.join(currPath, "settings-test.json")
        # repeatFailedRequestCount is set so that a failing endpoint makes the test fail instead of retrying indefinitely
        self.er = EventRegistry(verboseOutput = True, settingsFName = settPath, allowUseOfArchive = False, minDelayBetweenRequests=0, repeatFailedRequestCount=1)

        self.articleInfo = ArticleInfoFlags(bodyLen = -1, concepts = True, storyUri = True, originalArticle = True, categories = True,
                links = True, videos = True, image = True, location = True, extractedDates = True, socialScore = True, sentiment = True, includeArticleDuplicateList = True)
        self.sourceInfo = SourceInfoFlags(title = True, description = True, location = True, ranking = True, image = True, socialMedia = True)
        self.conceptInfo = ConceptInfoFlags(type=["entities"], lang = ["eng", "spa"], synonyms = True, image = True, description = True,
                includeConceptConceptClassMembership = True, maxConceptsPerType = 50)
        self.locationInfo = LocationInfoFlags(wikiUri = True, label = True, geoNamesId = True, geoLocation = True, population = True,
                countryArea = True, countryDetails = True, countryContinent = True,
                placeFeatureCode = True, placeCountry = True)
        self.categoryInfo = CategoryInfoFlags(includeCategoryParentUri = True, includeCategoryChildrenUris = True)
        self.eventInfo = EventInfoFlags(commonDates = True, stories = True, socialScore = True, imageCount = 2)
        self.storyInfo = StoryInfoFlags(categories = True, date = True, concepts = True, title = True, summary = True,
                                        medoidArticle = True, commonDates = True, socialScore = True, imageCount = 2)
        self.returnInfo = ReturnInfo(articleInfo = self.articleInfo, conceptInfo = self.conceptInfo, eventInfo = self.eventInfo, storyInfo = self.storyInfo,
            sourceInfo = self.sourceInfo, locationInfo = self.locationInfo, categoryInfo = self.categoryInfo)


    @staticmethod
    def daysAgo(count):
        """date string for the day `count` days ago. The tests run with allowUseOfArchive=False,
        so the query dates have to be within the recent (non-archive) data window.
        The individual backend instances can differ by +-1 day of content at the edges of that window, so the
        tests that compare result counts always AND a date range of about two weeks ago (e.g. daysAgo(16)..daysAgo(12))
        with the other query conditions - never OR a date condition with other conditions"""
        return QueryParamsBase.encodeDate(datetime.date.today() - datetime.timedelta(days = count))


    def assertCountsClose(self, count1, count2, msg = None, tolerance = 0.01):
        """compare two result counts obtained by separate requests. The live data is continuously
        updated (also for past dates), so the counts can legitimately differ by a small amount"""
        allowed = max(10, int(max(count1, count2) * tolerance))
        self.assertTrue(abs(count1 - count2) <= allowed, (msg or "The compared counts differ too much") + ": %d vs %d" % (count1, count2))


    def ensureValidConcept(self, concept, testName):
        for prop in [ "uri", "label", "synonyms", "image"]:
            self.assertTrue(prop in concept, "Property '%s' was expected in concept for test %s" % (prop, testName))
        self.assertTrue(concept.get("type") in ["person", "loc", "org"], "Expected concept to be an entity type, but got %s" % (concept.get("type")))
        if concept.get("location"):
            self.ensureValidLocation(concept.get("location"), testName)


    def ensureValidArticle(self, article, testName):
        for prop in ["url", "uri", "title", "body", "source", "time", "date", "lang", "image", "links", "videos", "categories", "location", "duplicateList", "originalArticle", "extractedDates", "concepts", "shares", "sentiment"]:
            self.assertTrue(prop in article, "Property '%s' was expected in article for test %s" % (prop, testName))
        for concept in article.get("concepts"):
            self.ensureValidConcept(concept, testName)
        self.assertTrue(article.get("isDuplicate") or "eventUri" in article, "Nonduplicates should have event uris")


    def ensureValidSource(self, source, testName):
        for prop in ["uri", "title", "description", "image", "thumbImage", "favicon", "location", "ranking", "socialMedia"]:
            self.assertTrue(prop in source, "Property '%s' was expected in source for test %s" % (prop, testName))


    def ensureValidCategory(self, category, testName):
        for prop in ["uri", "parentUri"]:
            self.assertTrue(prop in category, "Property '%s' was expected in category for test %s" % (prop, testName))


    def ensureValidLocation(self, location, testName):
        for prop in ["wikiUri", "label", "lat", "long", "geoNamesId", "population"]:
            self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "country":
            for prop in ["area", "code2", "code3", "webExt", "continent"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))
        if location.get("type") == "place":
            for prop in ["featureCode", "country"]:
                self.assertTrue(prop in location, "Property '%s' was expected in a location for test %s" % (prop, testName))


    def ensureValidEvent(self, event, testName):
        for prop in ["uri", "title", "summary", "articleCounts", "concepts", "categories", "location", "eventDate", "commonDates", "stories", "socialScore", "images"]:
            self.assertTrue(prop in event, "Property '%s' was expected in event for test %s" % (prop, testName))
        for concept in event.get("concepts"):
            self.ensureValidConcept(concept, testName)
        for story in event.get("stories"):
            self.ensureValidStory(story, testName)
        for category in event.get("categories"):
            self.ensureValidCategory(category, testName)
        if event.get("location"):
            self.ensureValidLocation(event.get("location"), testName)


    def ensureValidStory(self, story, testName):
        for prop in ["uri", "title", "summary", "concepts", "categories", "location",
                     "storyDate", "averageDate", "commonDates", "socialScore", "images"]:
            self.assertTrue(prop in story, "Property '%s' was expected in story for test %s" % (prop, testName))
        if story.get("location"):
            self.ensureValidLocation(story.get("location"), testName)


    def ensureArticleBodyContainsText(self, article, text):
        self.assertTrue("body" in article, "Article did not contain body")
        if re.search(r"(^|\s|\W)" + text + r"($|'|\s|\W)", article["body"], re.IGNORECASE) is None:
            self.fail("Article body did not contain text '%s'" % (text))


    def ensureArticleBodyDoesNotContainText(self, article, text):
        if "body" in article:
            if re.search(r"(^|\s|\W)" + text + r"($|'|\s|\W)", article["body"], re.IGNORECASE) is not None:
                self.fail("Article body contained text '%s' and it shouldn't" % (text))


    def ensureArticleHasConcept(self, article, conceptUri):
        self.assertTrue("concepts" in article, "Article did not contain concept array")
        for concept in article["concepts"]:
            if conceptUri == concept["uri"]:
                return
        self.fail("Article concepts did not contain concept '%s'" % (conceptUri))


    def ensureArticleHasNotConcept(self, article, conceptUri):
        if "concepts" in article:
            for concept in article["concepts"]:
                if conceptUri == concept["uri"]:
                    self.fail("Article concepts contained concept '%s'" % (conceptUri))


    def ensureArticleHasCategory(self, article, categoryUri):
        """
        ensure that the article has the given category or ANY child category
        """
        self.assertTrue("categories" in article, "Article did not contain category array")
        for category in article["categories"]:
            if category["uri"].find(categoryUri) == 0:
                return
        self.fail("Article categories did not contain category '%s'" % (categoryUri))


    def ensureArticleHasNotCategory(self, article, categoryUri):
        """
        ensure that the article is not annotated directly with the given category.
        Note: ignoreCategoryUri does not exclude the items that are annotated only with a CHILD
        of the ignored category, so child categories are not treated as a failure here
        """
        for category in article.get("categories", []):
            if category["uri"] == categoryUri:
                self.fail("Article categories contained an excluded category '%s'" % (categoryUri))


    def ensureArticleSource(self, article, sourceUri):
        self.assertTrue(article.get("source").get("uri") == sourceUri, "Article source is not '%s'" % sourceUri)


    def ensureArticleNotFromSource(self, article, sourceUri):
        self.assertFalse(article.get("source").get("uri") == sourceUri, "Article should not be from source '%s'" % sourceUri)


    def ensureArticlesContainText(self, articles, keyword):
        """assure that at least one article contains the given keyword"""
        hasKw = [True for art in articles if
            re.search(r"(^|\s|\W)" + keyword + r"($|'|\s|\W)", art["body"], re.IGNORECASE) is not None]
        if len(hasKw) == 0:
            self.fail("None of the articles contained given keyword '%s'" % keyword)


    def ensureArticlesDoNotContainText(self, articles, keyword):
        """assure that none of the articles contain the given keyword"""
        for article in articles:
            self.ensureArticleBodyDoesNotContainText(article, keyword)


    def ensureArticlesNotFromSource(self, articles, sourceUri):
        """assure that none of the articles are from the given source"""
        for article in articles:
            self.ensureArticleNotFromSource(article, sourceUri)


    def ensureEventHasConcept(self, event, conceptUri):
        self.assertTrue("concepts" in event, "Event did not contain concept array")
        for concept in event["concepts"]:
            if conceptUri == concept["uri"]:
                return
        self.fail("Event concepts did not contain concept '%s'" % (conceptUri))


    def ensureEventHasNotConcept(self, event, conceptUri):
        if "concepts" in event:
            for concept in event["concepts"]:
                if conceptUri == concept["uri"]:
                    self.fail("Event concepts contained concept '%s'" % (conceptUri))


    def ensureEventHasCategory(self, event, categoryUri):
        """
        ensure that the event has the given category or ANY child category
        """
        self.assertTrue("categories" in event, "Event did not contain category array")
        for category in event["categories"]:
            if category["uri"].find(categoryUri) == 0:
                return
        self.fail("Event categories did not contain category '%s'" % (categoryUri))


    def ensureEventHasNotCategory(self, event, categoryUri):
        """
        ensure that the event is not annotated directly with the given category.
        Note: ignoreCategoryUri does not exclude the items that are annotated only with a CHILD
        of the ignored category, so child categories are not treated as a failure here
        """
        for category in event.get("categories", []):
            if category["uri"] == categoryUri:
                self.fail("Event categories contained an excluded category '%s'" % (categoryUri))


    def ensureSameResults(self, res1, res2, queryStr):
        arr1 = jmespath.compile(queryStr).search(res1)
        arr2 = jmespath.compile(queryStr).search(res2)
        if not isinstance(arr1, list) or not isinstance(arr2, list):
            return
        if arr1 != [] and arr2 != []:
            if isinstance(arr1[0], (int, float)) and isinstance(arr2[0], (int, float)):
                # counts obtained by two separate requests can differ slightly since the data is continuously updated
                self.assertCountsClose(arr1[0], arr2[0], "Found different results for query %s" % (queryStr))
            elif arr1[0] != arr2[0]:
                self.fail("Found different results for query %s" % (queryStr))
        elif len(arr1) != len(arr2):
            self.fail("Found different number of results for query %s" % (queryStr))

