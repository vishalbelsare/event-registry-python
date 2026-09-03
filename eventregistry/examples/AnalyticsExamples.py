"""
Examples of usage of the analytics endpoints
"""

from eventregistry import EventRegistry, Analytics

er = EventRegistry()
analytics = Analytics(er)

res = analytics.sentiment("""
    Residents and tourists enjoy holiday weekend even as waves start to pound; beaches remain closed due to dangerous rip currents.
    Despite a state of emergency declared by the governor and warnings about dangerous surf and the possibility of significant coastal flooding, residents and visitors to the Jersey Shore spent Saturday making the most of the calm before the storm.
    Cloudy skies in the morning gave way to sunshine in the afternoon, and despite winds that already were kicking up sand and carving the beach, people flocked to the boardwalk in both Seaside Heights and Point Pleasant Beach, where children rode amusement rides and teens enjoyed ice cream cones.
""")

print(f"Average sentiment: {res['avgSent']}")
for text, sent in zip(res["sentences"], res["sentimentPerSent"]):
    print(f"Sentence: '{text}' has sentiment {sent}")



