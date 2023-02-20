import json
import matplotlib.pyplot as plt

def line_chart(keys, values):
    plt.plot(keys, values)
    plt.title("Analysis Tool Usage - Line Chart")
    plt.xlabel("Courses")
    plt.ylabel("Frequency")
    plt.show()

def bar_chart(keys, values):
    plt.bar(keys, values)
    plt.title("Analysis Tool Usage - Bar Chart")
    plt.xlabel("Courses")
    plt.ylabel("Frequency")
    plt.show()

def pie_chart(keys, values):
    plt.pie(values, labels=keys, autopct='%1.1f%%')
    plt.title("Analysis Tool Usage - Pie Chart")
    plt.show()

with open('./cache/statistics_cache.json') as file:
    stats = json.load(file)

stats = {k: v for k, v in stats.items() if v > 0}

keys = list(stats.keys())
values = list(stats.values())

# Show Graphs
line_chart(keys, values)
bar_chart(keys, values)
pie_chart(keys, values)


