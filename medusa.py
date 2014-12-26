#!/usr/bin/env python3
from datetime import date
from statistics import mean, median

from libsyntyche.common import read_json, local_path

def generate_intervals(stats):
    """
    Return all intervals between updates including the current time elapsed
    since the last update for one entry.
    """
    def getdate(s):
        return date(*map(int, s.split('-')))
    datelist = list(map(getdate, stats)) + [date.today()]
    for n, d in enumerate(datelist[:-1]):
        yield (datelist[n+1]-d).days

def generate_entries(data):
    """
    Return name, latest interval and mean, median, max and minimum intervals
    for each entry.
    """
    for name, datadict in sorted(data.items()):
        i = list(generate_intervals(datadict['stats']))
        yield (name, i[-1], round(mean(i)), round(median(i)), max(i), min(i))

def get_max_name_width(entries):
    """
    Return max width of the name in the entries.
    The names are in the first column in the entry list.
    """
    return max(map(len, next(zip(*entries))))

def format_stats(entries, maxnamewidth):
    """
    Return the data in a formatted table as an iterator of strings, including
    a header.
    """
    header = ['name', 'current', 'mean', 'median', 'max', 'min']
    f = '{{:{}}}  {{:>8}}  {{:>5}}  {{:>7}}  {{:>4}}  {{:>4}}'.format(maxnamewidth).format
    yield f(*header)
    yield '-'*len(f(*header))
    for entry in entries:
        yield f(*entry)

def show_stats():
    data = read_json(local_path('medusadata.json'))
    entries = list(generate_entries(data))
    maxnamewidth = get_max_name_width(entries)
    print('\n'.join(format_stats(entries, maxnamewidth)))

def main():
    show_stats()

if __name__ == '__main__':
    main()
