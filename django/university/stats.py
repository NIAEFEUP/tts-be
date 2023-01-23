import json
from celery import shared_task

"""
    This singleton class is used to store the statistics of the requests made to the server.
    It is used to store the number of requests made to the server for each course.
"""
class statistics:

    __instance = None
    
    def __init__(self, courses, year):
        if statistics.__instance == None:
            self.year = year
            self.requests_stats = dict() # key: id value: number of requests
            # print(courses)
            for course in courses:
                self.requests_stats[course["id"]] = 0

            print("requests_stats:", self.requests_stats)
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

    
    def import_request_stats(self, filepath, courses):
        with open(filepath, 'r') as f:
            self.requests_stats = json.load(f)


    def cache_stats(self, filepath):
        with open(filepath, 'w') as f:
            json.dump(self.requests_stats, f)


    def export_request_stats(self, courses):
        requests_stats_to_export = {}
        for course in courses:
            if course["id"] in self.requests_stats:
                requests_stats_to_export[course["name"]] = self.requests_stats[course["id"]]

        return json.dumps(requests_stats_to_export, ensure_ascii=False)


@shared_task
def cache_statistics():
    stats = statistics.get_instance()
    if stats != None:
        stats.cache_stats("requests_stats.json")