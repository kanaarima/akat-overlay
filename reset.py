import json

with open("cache.json") as f:
    cache = json.load(f)

with open("cache.json", "w") as f:
    json.dump([cache[-1]], f)
