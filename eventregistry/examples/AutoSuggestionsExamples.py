"""
examples showing how to use the autosuggest functionalities for concepts, sources, categories, locations, ....
"""

from eventregistry import *

er = EventRegistry()

# get concept uris for concepts based on the concept labels:
conceptUrisMatchingObama = er.suggestConcepts("Obama", lang = "eng", conceptLang = ["eng", "deu"])
print(conceptUrisMatchingObama)
# example of the returned output (shortened):
# [
#     {"uri": "http://en.wikipedia.org/wiki/Barack_Obama", "type": "person", "score": 7697113, "label": {"eng": "Barack Obama", "deu": "Barack Obama"}},
#     {"uri": "http://en.wikipedia.org/wiki/Presidency_of_Barack_Obama", "type": "org", "score": 1480934, "label": {"eng": "Presidency of Barack Obama", "deu": "Kabinett Obama"}},
#     ...
# ]

# get only the top concept that best matches the prefix
conceptUriForBarackObama = er.getConceptUri("Obama")
# "http://en.wikipedia.org/wiki/Barack_Obama"
print("A URI of the top concept that contains the term 'Obama': " + conceptUriForBarackObama)


# return a list of categories that contain text "Business"
businessRelated = er.suggestCategories("Business")
print(businessRelated)
# example of the returned output (shortened):
# [
#     {"uri": "dmoz/Business", "label": "dmoz/Business", "parentUri": "dmoz"},
#     {"uri": "iptc/economy,_business_and_finance", "label": "iptc/economy, business and finance", "parentUri": "iptc"},
#     ...
# ]

# return the top category that contains text "Business"
businessCategoryUri = er.getCategoryUri("Business")
# "dmoz/Business"
print("A URI of the top category that contains the term 'Business': " + businessCategoryUri)


# get a list of locations that best match the prefix "Lond"
locations = er.suggestLocations("Lond")
print(locations)
# example of the returned output (shortened):
# [
#     {"type": "place", "wikiUri": "http://en.wikipedia.org/wiki/City_of_London", "label": {"eng": "City of London"}, "lat": 51.51, "long": -0.09, "country": {"type": "country", "wikiUri": "http://en.wikipedia.org/wiki/United_Kingdom", "label": {"eng": "United Kingdom"}, "lat": 54.76, "long": -2.7}, "score": 7556900},
#     {"type": "place", "wikiUri": "http://en.wikipedia.org/wiki/London", "label": {"eng": "London"}, "lat": 51.51, "long": -0.13, "country": {...}, "score": 7556900},
#     ...
# ]

# get a top location that best matches the prefix "Lond"
londonUri = er.getLocationUri("Lond")
# "http://en.wikipedia.org/wiki/City_of_London"
print("A top location that contains text 'Lond': " + londonUri)


usUri = er.getLocationUri("united states", sources = "country")
# "http://en.wikipedia.org/wiki/United_States"
print(usUri)

# get a top location for "lond" that is located in USA
londonUsUri = er.getLocationUri("Lond", countryUri = usUri)
# "http://en.wikipedia.org/wiki/New_London_County,_Connecticut"
print("A top US location that contains text 'Lond': " + londonUsUri)
