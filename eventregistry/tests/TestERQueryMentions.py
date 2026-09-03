import unittest
from eventregistry import *
from eventregistry.tests.DataValidator import DataValidator


class TestQueryMentions(DataValidator):

    def testMentionsList(self):
        etUri = self.er.getEventTypeUri("acquisition")
        self.assertIsNotNone(etUri, "Expected to find an event type uri for 'acquisition'")
        q = QueryMentions(eventTypeUri = etUri, lang = "eng")
        q.setRequestedResult(RequestMentionsInfo(count = 50))
        res = self.er.execQuery(q)

        self.assertIsNotNone(res.get("mentions"), "Expected to get 'mentions'")
        self.assertTrue(res["mentions"]["totalResults"] > 0, "Expected a non-zero number of matching mentions")
        mentions = res["mentions"]["results"]
        self.assertEqual(len(mentions), 50, "Expected to get 50 mentions")
        for mention in mentions:
            for prop in ["uri", "lang", "date", "articleUri", "articleUrl", "sentence", "eventType"]:
                self.assertTrue(prop in mention, "Property '%s' was expected in a mention" % (prop))
            self.assertEqual(mention["lang"], "eng", "Mention is not in the requested language")
            self.assertTrue(mention["eventType"].get("uri", "").startswith(etUri),
                "Mention event type '%s' does not match the requested event type '%s'" % (mention["eventType"].get("uri"), etUri))


    def testMentionsIterator(self):
        etUri = self.er.getEventTypeUri("acquisition")
        self.assertIsNotNone(etUri)
        iter = QueryMentionsIter(eventTypeUri = etUri, lang = "eng")
        totalCount = iter.count(self.er)
        self.assertTrue(totalCount > 0, "Expected a non-zero number of matching mentions")

        maxItems = min(totalCount, 300)
        mentions = list(iter.execQuery(self.er, maxItems = maxItems))
        self.assertEqual(len(mentions), maxItems, "Mentions iterator did not return the expected number of items")
        uris = [mention["uri"] for mention in mentions]
        self.assertEqual(len(set(uris)), len(uris), "Mentions iterator returned duplicated items")


    def testMentionsComplexQuery(self):
        etUri = self.er.getEventTypeUri("acquisition")
        self.assertIsNotNone(etUri)
        # use a fixed date window that ends in the past - new mentions are constantly being added,
        # so comparing the total counts of two unbounded queries would be flaky
        dateEnd = datetime.date.today() - datetime.timedelta(days = 2)
        dateStart = dateEnd - datetime.timedelta(days = 6)
        q1 = QueryMentions(eventTypeUri = etUri, lang = "eng", dateStart = dateStart, dateEnd = dateEnd)
        q1.setRequestedResult(RequestMentionsInfo(count = 20))
        res1 = self.er.execQuery(q1)

        q2 = QueryMentions.initWithComplexQuery({
            "$query": {
                "$and": [
                    { "eventTypeUri": etUri },
                    { "lang": "eng" },
                    { "dateStart": QueryParamsBase.encodeDate(dateStart), "dateEnd": QueryParamsBase.encodeDate(dateEnd) }
                ]
            }
        })
        q2.setRequestedResult(RequestMentionsInfo(count = 20))
        res2 = self.er.execQuery(q2)

        self.ensureSameResults(res1, res2, '[mentions][].totalResults')


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQueryMentions)
    unittest.TextTestRunner(verbosity=3).run(suite)
