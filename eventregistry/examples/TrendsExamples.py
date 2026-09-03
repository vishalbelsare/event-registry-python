"""
examples that illustrate how to obtain the currently top trending concepts or categories
The trends can be computed based on the number of mentions in the news or based on the shares on social media
"""
from eventregistry import *

er = EventRegistry()

#
# top 10 top trending concepts in the news
#
q = GetTrendingConcepts(source = "news", count = 10,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(includeConceptTrendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))
# example of the returned output (shortened). "trendingHistory.news" contains the number of mentions
# of the concept in the news for each of the last days
# [
#     {
#         "uri": "http://en.wikipedia.org/wiki/Grand_Canyon_Village,_Arizona",
#         "type": "loc",
#         "label": {"eng": "Grand Canyon Village, Arizona"},
#         "trendingScore": {"news": {"score": 446.65, "testPopFq": 552, "nullPopFq": 14}},
#         "trendingHistory": {"latestArticleTimestamp": "2026-09-01T08:35:46", "news": [2, 1, ...]},
#         "location": {"type": "place", "label": {"eng": "Grand Canyon Village, Arizona"}, "country": {"type": "country", "label": {"eng": "United States"}}}
#     },
#     {
#         "uri": "http://en.wikipedia.org/wiki/Paul_Goldstein_(tennis)",
#         "type": "person",
#         "label": {"eng": "Paul Goldstein (tennis)"},
#         "trendingScore": {"news": {"score": 403.12, "testPopFq": 266, "nullPopFq": 4}},
#         "trendingHistory": {"latestArticleTimestamp": "2026-09-01T08:35:46", "news": [1, 0, ...]}
#     },
#     ...
# ]

#
# get 20 most trending concept for each entity type
#
q = GetTrendingConceptGroups(source = "news")
# get top trends for individual concept groups - people, locations and organizations
q.getConceptTypeGroups()
ret = er.execQuery(q)
print(er.format(ret))
# example of the returned output (shortened) - a dict with one key per entity type:
# {
#     "person": {
#         "label": "Person",
#         "type": "person",
#         "trendingConcepts": [
#             {"uri": "http://en.wikipedia.org/wiki/Paul_Goldstein_(tennis)", "type": "person", "label": {"eng": "Paul Goldstein (tennis)"}, "trendingScore": {"news": {"score": 404.13, "testPopFq": 265, "nullPopFq": 4}}},
#             ...
#         ]
#     },
#     "org": {
#         "label": "Organization",
#         "type": "org",
#         "trendingConcepts": [
#             {"uri": "http://en.wikipedia.org/wiki/Invest_in_Canada", "type": "org", "label": {"eng": "Invest in Canada"}, "trendingScore": {"news": {"score": 152.91, "testPopFq": 71, "nullPopFq": 2}}},
#             ...
#         ]
#     },
#     "loc": {
#         "label": "Location",
#         "type": "loc",
#         "trendingConcepts": [
#             {"uri": "http://en.wikipedia.org/wiki/Grand_Canyon_Village,_Arizona", "type": "loc", "label": {"eng": "Grand Canyon Village, Arizona"}, "trendingScore": {"news": {"score": 448.66, "testPopFq": 551, "nullPopFq": 14}}, "location": {...}},
#             ...
#         ]
#     }
# }

#
# top 20 trending concepts in the social media
#
q = GetTrendingConcepts(source = "social", count = 20,
    returnInfo = ReturnInfo(
        conceptInfo = ConceptInfoFlags(trendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))
# NOTE: social media trends are currently not computed, so the call returns an error:
# {
#     "error": "Trends with the given parameters were not computed."
# }
# when available, the structure of the results is the same as for the "news" source above


#
# top 10 trending categories in the news
#
q = GetTrendingCategories(source = "news", count = 10,
    returnInfo = ReturnInfo(
        categoryInfo = CategoryInfoFlags(parentUri = True, childrenUris = True, trendingHistory = True)))
ret = er.execQuery(q)
print(er.format(ret))
# example of the returned output (shortened):
# [
#     {"uri": "dmoz/Sports/Soccer/CONMEBOL", "label": "dmoz/Sports/Soccer/CONMEBOL", "trendingScore": {"news": {"score": 112.81, "testPopFq": 595, "nullPopFq": 238}}},
#     {"uri": "dmoz/Arts/Graphic_Design/Graphic_Designers", "label": "dmoz/Arts/Graphic Design/Graphic Designers", "trendingScore": {"news": {"score": 76.7, "testPopFq": 355, "nullPopFq": 179}}},
#     ...
# ]