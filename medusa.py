#!/usr/bin/env python3
from datetime import date
from math import ceil
from operator import itemgetter
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

def generate_stats_entries(data):
    """
    Return name, latest interval and mean, median, max and minimum intervals
    for each entry.
    """
    for name, datadict in sorted(data.items()):
        i = list(generate_intervals(datadict['stats']))
        yield (name, i[-1], round(mean(i)), round(median(i)), max(i), min(i))

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

def generate_todo_entries(data):
    """
    Return all entries that aren't complete or in hiatus with their name,
    the next update's number and time since last update.
    """
    for name, datadict in data.items():
        if datadict['complete'] or datadict['hiatus']:
            continue
        i = list(generate_intervals(datadict['stats']))[-1]
        yield (name, len(datadict['stats'])+1, i)

def format_todo(entries):
    """
    Return the data formatted in a table sorted falling after time since
    last update.
    """
    for n, entry in enumerate(sorted(entries, key=itemgetter(2), reverse=True), 1):
        yield ('>> ' if n == 1 else '   ') + '{0}. (+{3}) {1} (upd. {2})'.format(n, *entry)

def show_stats(data):
    entries = list(generate_stats_entries(data))
    maxnamewidth = max(map(len, next(zip(*entries))))
    print('\n'.join(format_stats(entries, maxnamewidth)))

def show_todo(data):
    entry_strings = list(format_todo(generate_todo_entries(data)))
    maxwidth = max(map(len, entry_strings))-6
    print('='*(maxwidth//2) + ' TODO ' + '='*ceil(maxwidth/2))
    print('\n'.join(entry_strings))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['stats', 'todo'])
    args = parser.parse_args()
    modes = {'stats': show_stats, 'todo': show_todo}
    modes[args.mode](read_json(local_path('medusadata.json')))

if __name__ == '__main__':
    main()
