import unittest
import eventregistry as ER
from eventregistry.tests.DataValidator import DataValidator


class TestAnalytics(DataValidator):

    def testConcepts(self):
        analytics = ER.Analytics(self.er)
        annInfo = analytics.annotate("Microsoft released a new version of Windows OS.")
        self.assertTrue("annotations" in annInfo, "Annotations were not provided for the given text")
        anns = annInfo["annotations"]
        self.assertTrue(len(anns) >= 1, "Expected at least one annotation in the given text")
        for ann in anns:
            self.assertTrue("url" in ann)
            self.assertTrue("title" in ann)
            self.assertTrue("lang" in ann)
            self.assertTrue("secLang" in ann)
            self.assertTrue("secUrl" in ann)
            self.assertTrue("secTitle" in ann)
            self.assertTrue("wikiDataItemId" in ann)
        annotatedUrls = [ann["url"] for ann in anns]
        self.assertTrue("http://en.wikipedia.org/wiki/Microsoft" in annotatedUrls, "Expected Microsoft to be one of the annotations")
        self.assertTrue("ranges" in annInfo)
        self.assertTrue("language" in annInfo)


    def testCategories(self):
        analytics = ER.Analytics(self.er)
        res = analytics.categorize("Microsoft released a new version of Windows OS.")
        self.assertTrue("categories" in res)
        for catInfo in res["categories"]:
            self.assertTrue("label" in catInfo)
            self.assertTrue("score" in catInfo)


    def testSentiment(self):
        analytics = ER.Analytics(self.er)
        res = analytics.sentiment("""Residents and tourists enjoy holiday weekend even as waves start to pound; beaches remain closed due to dangerous rip currents.
            Despite a state of emergency declared by the governor and warnings about dangerous surf and the possibility of significant coastal flooding, residents and visitors to the Jersey Shore spent Saturday making the most of the calm before the storm.
            Cloudy skies in the morning gave way to sunshine in the afternoon, and despite winds that already were kicking up sand and carving the beach, people flocked to the boardwalk in both Seaside Heights and Point Pleasant Beach, where children rode amusement rides and teens enjoyed ice cream cones. """)
        self.assertTrue("avgSent" in res)
        self.assertTrue("sentimentPerSent" in res)


    def testLanguage(self):
        analytics = ER.Analytics(self.er)
        langInfo = analytics.detectLanguage("Microsoft released a new version of Windows OS.")
        # the endpoint returns a list of detected language candidates, sorted by their score
        self.assertTrue(isinstance(langInfo, list) and len(langInfo) > 0, "Expected a non-empty list of detected languages")
        self.assertEqual(langInfo[0].get("code"), "en")
        self.assertTrue("name" in langInfo[0])
        self.assertTrue("percent" in langInfo[0])


    def testSemanticSimilarity(self):
        doc1 = "The editor, Carrie Gracie, who joined the network 30 years ago, said she quit her position as China editor last week to protest pay inequality within the company. In the letter posted on her website, she said that she and other women had long suspected their male counterparts drew larger salaries and that BBC management had refused to acknowledge the problem."
        doc2 = "Paukenschlag bei der britischen BBC: Die China-Expertin Carrie Gracie hat aus Protest gegen die illegale Gehaltskultur und damit verbundene Heimlichtuerei ihren Job bei dem öffentlich-rechtlichen Sender hingeworfen. Zwei ihrer männlichen Kollegen in vergleichbaren Positionen würden nachweislich wesentlich besser bezahlt."
        analytics = ER.Analytics(self.er)
        ret = analytics.semanticSimilarity(doc1, doc2)
        self.assertTrue("similarity" in ret)


    def testExtractArticleInfo(self):
        analytics = ER.Analytics(self.er)
        info = analytics.extractArticleInfo("https://www.theguardian.com/world/2018/jan/31/this-is-over-puigdemonts-catalan-independence-doubts-caught-on-camera")
        self.assertTrue("title" in info)
        self.assertTrue("body" in info)
        self.assertTrue("date" in info)
        self.assertTrue("datetime" in info)
        self.assertTrue("image" in info)
        # there can be other additional properties available, depending on what is available in the article


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalytics)
    unittest.TextTestRunner(verbosity=2).run(suite)
