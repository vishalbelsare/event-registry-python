"""
examples showing how to obtain information how frequently a particular concept is mentioined in
the news articles, or an article is about a particular category
"""


from eventregistry import *

er = EventRegistry()

obamaUri = er.getConceptUri("Trump")
ebolaUri = er.getConceptUri("ebola")

q = GetCounts([obamaUri, ebolaUri])
ret = er.execQuery(q)
print(er.format(ret))
# example of the returned output (shortened) - for each provided uri you get the number of mentioning
# articles per day. Note that days that are older than the date range covered by your subscription plan
# will be reported with a count of 0
# {
#     "http://en.wikipedia.org/wiki/Donald_Trump": [
#         {"date": "2026-07-31", "count": 26598},
#         {"date": "2026-08-01", "count": 17940},
#         ...
#         {"date": "2026-09-01", "count": 8825}
#     ],
#     "http://en.wikipedia.org/wiki/Ebola": [
#         {"date": "2026-07-31", "count": 343},
#         {"date": "2026-08-01", "count": 486},
#         ...
#         {"date": "2026-09-01", "count": 65}
#     ]
# }

q = GetCountsEx([er.getCategoryUri("business")], type="category")
ret = er.execQuery(q)
print(er.format(ret))
# example of the returned output (shortened) - the details of the provided uris are listed in
# "categoryInfo" and each item in "counts" contains the number of matching articles per day for each uri
# {
#     "categoryInfo": [
#         {"uri": "dmoz/Business", "label": "dmoz/Business"}
#     ],
#     "counts": [
#         {"date": "2026-07-31", "dmoz/Business": 1564},
#         {"date": "2026-08-01", "dmoz/Business": 626},
#         ...
#     ]
# }
