import json
import matplotlib.pyplot as plt


with open('./cache/statistics_cache.json') as file:
    stats = json.load(file)

stats = {k: v for k, v in stats.items() if v > 0}

keys = list(stats.keys())
values = list(stats.values())

# Show Graphs
line_chart(keys, values)
bar_chart(keys, values)
pie_chart(keys, values)

