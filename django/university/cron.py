from stats import cache_stats
import json

def stats_caching_job():
    #cache_stats()
    with open("statistics_cache.json", 'w') as f:
            json.dump({"teste" : "dois"}, f)
    