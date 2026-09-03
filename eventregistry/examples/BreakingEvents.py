from eventregistry import *

er = EventRegistry()

# get the list of all breaking events
params = {
    "includeEventSocialScore": True,
    "includeEventLocation": True,
    "includeLocationGeoLocation": True
}

res = er.jsonRequest("/api-c/v1/event/getBreakingEvents", paramDict=params)
print(res)
# example of the returned output (shortened):
# {
#     "breakingEvents": {
#         "results": [
#             {
#                 "uri": "eng-11966764",
#                 "eventDate": "2026-08-31",
#                 "totalArticleCount": 314,
#                 "articleCounts": {"eng": 314},
#                 "title": {"eng": "At the Tupac Trial, Old Rumors Still Trail Sean Combs"},
#                 "summary": {"eng": "Duane Davis, who is charged in the murder of the rapper Tupac Shakur, repeatedly accused ..."},
#                 "concepts": [
#                     {"uri": "http://en.wikipedia.org/wiki/Tupac_Shakur", "type": "person", "score": 100, "label": {"eng": "Tupac Shakur"}},
#                     {"uri": "http://en.wikipedia.org/wiki/Murder", "type": "wiki", "score": 88, "label": {"eng": "Murder"}},
#                     ...
#                 ],
#                 "categories": [
#                     {"uri": "dmoz/Society/Crime/Murder", "label": "dmoz/Society/Crime/Murder", "wgt": 25},
#                     ...
#                 ],
#                 "location": {"type": "place", "label": {"eng": "Las Vegas"}, "lat": 36.17, "long": -115.14, "country": {"type": "country", "label": {"eng": "United States"}, "lat": 39.76, "long": -98.5}},
#                 "socialScore": 0,
#                 "sentiment": -0.4,
#                 "breakingScore": 2.29
#             },
#             ...
#         ]
#     }
# }


q = QueryEvents(
    categoryUri="news/Business",
    lang="eng")
q.setRequestedResult(RequestEventsBreakingEvents())

res = er.execQuery(q)
print(res)
# the returned events have the same structure as in the example above, this time under the "breakingEvents" key
# of the standard execQuery result. Example (shortened):
# {
#     "breakingEvents": {
#         "results": [
#             {
#                 "uri": "eng-11970620",
#                 "eventDate": "2026-09-01",
#                 "totalArticleCount": 20,
#                 "articleCounts": {"eng": 20},
#                 "title": {"eng": "Investors gear up for new GoG 4-year bond"},
#                 "summary": {"eng": "Ghana's financial portfolio investment community - and their counterparts abroad ..."},
#                 "concepts": [{"uri": "http://en.wikipedia.org/wiki/Stock", "type": "wiki", "score": 100, "label": {"eng": "Stock"}}, ...],
#                 "categories": [{"uri": "dmoz/Business/Investing/Stocks_and_Bonds", "label": "dmoz/Business/Investing/Stocks and Bonds", "wgt": 19}, ...],
#                 "location": {"type": "place", "label": {"eng": "Seoul"}, "country": {"type": "country", "label": {"eng": "South Korea"}}},
#                 "sentiment": 0.06,
#                 "breakingScore": 1.09
#             },
#             ...
#         ]
#     }
# }
