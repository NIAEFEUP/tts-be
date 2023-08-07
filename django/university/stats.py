import json
import os
from time import sleep

"""
    This singleton class is used to store the statistics of the requests made to the server.
    It is used to store the number of requests made to the server for each course.
"""
class statistics:
    CACHE_DIR = "./university/cache/"
    REQ_CACHE_FILE = "statistics_cache.json"
    REQ_CACH_PATH = CACHE_DIR + REQ_CACHE_FILE

    __instance = None
    
    def __init__(self, courses, year):
        if statistics.__instance == None:
            self.year = year
            self.requests_stats = dict() # key: id value: number of requests
            if self.load_cache():
                print("Loaded cache")
            else:
                print("Cache not found, initializing statistics to 0")
                for course in courses:
                    self.requests_stats[course["sigarra_id"]] = 0

            statistics.__instance = self



    @staticmethod
    def get_instance():
        return statistics.__instance
    
    def get_year(self):
        return self.year

    def get_request_stats(self):
        return self.requests_stats


    def get_specific_stat(self, id):
        return self.requests_stats[id]

    
    def increment_requests_stats(self, id):
        self.requests_stats[id] += 1

    
    def import_request_stats(self, filepath):
        with open(filepath, 'r') as f:
            self.requests_stats = json.load(f)


    def cache_stats(self, filepath: str):
        if not os.path.isdir(self.CACHE_DIR):
            os.makedirs(self.CACHE_DIR)
        with open(filepath, 'w') as f:
            json.dump(self.requests_stats, f)

    def load_cache(self) -> bool: 
        if os.path.exists(self.REQ_CACH_PATH):
            with open(self.REQ_CACH_PATH, 'r') as f:
                cached_json_stats = json.load(f)

            for id in cached_json_stats:
                self.requests_stats[int(id)] = cached_json_stats[id]

            return True
        
        return False

        
        

    def export_request_stats(self, courses):
        requests_stats_to_export = {}
        for course in courses:
            if course["sigarra_id"] in self.requests_stats:
                requests_stats_to_export[course["name"]] = self.requests_stats[course["sigarra_id"]]

        return json.dumps(requests_stats_to_export, ensure_ascii=False)


def cache_statistics():
    stats = statistics.get_instance()
    if stats != None:
        stats.cache_stats(stats.REQ_CACH_PATH)