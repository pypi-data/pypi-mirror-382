I’m looking to build a relatively simple (to begin with) service which provides the ability to take an object as a payload (eg. A simple string to begin with, but likely evolving to be a more complex object with multiple attributes).

It would then identify if this was already a known entity via heuristics, hybrid vector search with both dense, sparse, and reranking models, perform entity recognition and resolution, and then suggest back a recommended match (or create a new one if unknown).

The ultimate aim of this service is to serve as a canonical source of truth for uniquely identifying (and therefore providing back a “guid”) an entity for a given domain. This would then act as a critical cornerstone for masterdata management in a platform. Assume I prefer self-hosted and opensource solutions. Do not recommend anything that I can’t run myself using docker and/or python.

I’m looking for something that’s ideally general purpose, can be used across arbitrary domains, extensible, and zero/few-shot, with the ability to train over time.

Thoughts are that it should:

- allows me to configure an arbitrary data model (e.g. an Organisation)
- provide basic CRUD services as a RESTful API
- provide MERGE and UPSERT services as a RESTful API
- provide MATCH capabilities as a RESTful API with gracefully degrading Exact Match -> Business Logic -> Fuzzy Match -> Vector Match -> Graph Boosting etc. etc.
- perform Named Entity Recognition and Entity Resolution
- wraps all of the above with FastMCP so that we can expose to LLMs over HTTP remotely
- leverage LLMs (or Small Language Models) as part of the pipeline to identify the domain, provide few shot prompts, identify and propose new candidates for relationships and entities

Points to note:

- Assume this could be **any** domain. But start initially with the obvious ones.
- The domains could vary from Corporate (ie. business logic) through to Consumer (e.g. pop culture) and include things such as Companies through to characters from Cartoons or tagging for Stable Diffusion.
- Start with simple strings but we will expand this over time. An example might be that I want to manage a list of available “Products” but the string itself might be an email or line from an invoice. So we would need to extract and identify from there.
- I’m fine with higher latency to begin with as my expectation is both that accuracy is more important and that we can improve this over time.
- No constraints as such but I’d like to see an assessment of options. Postgres17+ with extensions such as PGVector and AGE could be a good fit.
