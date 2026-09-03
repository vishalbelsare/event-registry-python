import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestAutoSuggest(DataValidator):

    def testConcepts(self):
        self.assertTrue(self.er.getConceptUri("Obama") == "http://en.wikipedia.org/wiki/Barack_Obama", "No suggestions are provided for name Obama")


    def testCategories(self):
        self.assertTrue(self.er.getCategoryUri("business") == "dmoz/Business")
        self.assertTrue(self.er.getCategoryUri("birding") == "dmoz/Recreation/Birding")


    def testSource(self):
        self.assertTrue(self.er.getNewsSourceUri("nytimes") == "nytimes.com")
        self.assertIn(self.er.getNewsSourceUri("bbc"), ("bbc.co.uk", "bbc.com"))

        # test PR sources
        self.assertTrue(self.er.getNewsSourceUri("Business Wire") == "businesswire.com")
        self.assertTrue(self.er.getNewsSourceUri("dailypolitical.com") == "dailypolitical.com")

        # test blogs
        # self.assertTrue(self.er.getNewsSourceUri("slideshare.net") == "slideshare.net")
        # self.assertTrue(self.er.getNewsSourceUri("topix.com") == "topix.com")

        srcList = self.er.suggestSourcesAtPlace(self.er.getConceptUri("New York City"))
        self.assertTrue(len(srcList) > 0)


    def testLocations(self):
        self.assertTrue(self.er.suggestLocations("Washington")[0].get("wikiUri") == "http://en.wikipedia.org/wiki/Washington_(state)")
        # "London" also matches City of London and other places, so just check that London is among the top suggestions
        londonUris = [loc.get("wikiUri") for loc in self.er.suggestLocations("London")[:3]]
        self.assertTrue("http://en.wikipedia.org/wiki/London" in londonUris)
        self.assertTrue(len(self.er.suggestLocationsAtCoordinate(38.893352, -77.093779, 300, limitToCities=True)) > 0)


    def testAuthors(self):
        authors = self.er.suggestAuthors("associated")
        self.assertTrue(len(authors) > 0, "Expected to get some author suggestions")
        for author in authors:
            self.assertTrue("uri" in author, "Author should have an uri")
            self.assertTrue("name" in author, "Author should have a name")
        self.assertEqual(self.er.getAuthorUri("associated"), authors[0].get("uri"))


    def testEventTypes(self):
        eventTypes = self.er.suggestEventTypes("acquisition")
        self.assertTrue(len(eventTypes) > 0, "Expected to get some event type suggestions")
        for eventType in eventTypes:
            self.assertTrue("uri" in eventType, "Event type should have an uri")
            self.assertTrue(eventType["uri"].startswith("et/"), "Event type uris should start with 'et/'")
        self.assertEqual(self.er.getEventTypeUri("acquisition"), eventTypes[0].get("uri"))


    def testSdgAndSasbUris(self):
        sdg = self.er.getSdgUris()
        self.assertTrue(len(sdg.get("results", [])) > 0, "Expected a non-empty list of SDG uris")
        for item in sdg["results"]:
            self.assertTrue(item.get("uri", "").startswith("sdg/"), "SDG uris should start with 'sdg/'")
        sasb = self.er.getSasbUris()
        self.assertTrue(len(sasb.get("results", [])) > 0, "Expected a non-empty list of SASB uris")
        for item in sasb["results"]:
            self.assertTrue(item.get("uri", "").startswith("sasb/"), "SASB uris should start with 'sasb/'")






if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAutoSuggest)
    unittest.TextTestRunner(verbosity=2).run(suite)
