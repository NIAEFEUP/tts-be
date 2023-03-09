import json
import matplotlib.pyplot as plt
import requests

FILE_PATH = './cache/stats_ttsbe_31-01-23.json'
URL = "https://ni.fe.up.pt/tts/api/statistics/?name=tts_be&password=batata_frita_123"


def line_chart(keys, values):
    fig = plt.figure(figsize=(10,5))
    plt.plot(keys, values)
    plt.title("Analysis Tool Usage - Line Chart")
    plt.xlabel("Courses")
    plt.ylabel("Frequency")
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    plt.subplots_adjust(bottom=0.5)
    plt.xticks(rotation=50, ha='right')
    plt.savefig('./stats_graphs/stats_line_chart.png')

def bar_chart(keys, values):
    fig = plt.figure(figsize=(10,5))
    plt.bar(keys, values)
    plt.title("Analysis Tool Usage - Bar Chart")
    plt.xlabel("Courses")
    plt.ylabel("Frequency")
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(fontsize=8)
    plt.subplots_adjust(bottom=0.5)
    plt.xticks(rotation=55, ha='right') 
    plt.savefig('./stats_graphs/stats_bar_chart.png')

def pie_chart(keys, values):
    fig = plt.figure(figsize=(10, 5))
    plt.pie(values, labels=keys, autopct='%1.1f%%')
    plt.title("Analysis Tool Usage - Pie Chart")
    plt.savefig('./stats_graphs/stats_pie_chart.png')

"""
response = requests.get(URL)

if response.status_code == 200:
    stats = response.json()
    stats = eval(stats)
else:
    print("Error: Request failed with status code: ", response.status_code)
"""


with open(FILE_PATH) as file:
    stats = json.load(file)
    stats = eval(stats)

stats = {k: v for k, v in stats.items() if v > 2}

keys = list(stats.keys())
values = list(stats.values())

# Show Graphs
pie_chart(keys, values)
bar_chart(keys, values)
line_chart(keys, values)
plt.show()


