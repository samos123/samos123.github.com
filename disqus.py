import re
import csv
import sys
import requests

"""
Small python script to rewrite urls from disqus
export file.
"""


def format_urls(filename):
    lines = []
    with open(filename, "r") as f:
        lines = f.readlines()

    results = []

    for line in lines:
        new = line.replace("samos-it.com/", "samos-it.com/posts/")\
                .strip()[:-1] + ".html"
        resp = requests.get(new)
        if resp.status_code != 200:
            new += "\t(URL NOT WORKING)"
        results.append( (line, new) )
    return results


def write_to_csv_file(results):
    with open('samos-it-disqus.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(results)


if __name__ == "__main__":
    filename = sys.argv[1]
    results = format_urls(filename)
    print(results)
    write_to_csv_file(results)
