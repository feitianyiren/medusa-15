#!/usr/bin/env python3
from datetime import date
from math import ceil
from operator import itemgetter
from statistics import mean, median

from libsyntyche.common import read_json, local_path, write_json

# ====================== Stats mode =====================================

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

def format_stats(entries, maxnamewidth, sortby, reverse):
    """
    Return the data in a formatted table as an iterator of strings, including
    a header.
    """
    header = ['name', 'current', 'mean', 'median', 'max', 'min']
    f = '{{:{}}}  {{:>8}}  {{:>5}}  {{:>7}}  {{:>4}}  {{:>4}}'.format(maxnamewidth).format
    yield f(*header)
    yield '\u2500'*len(f(*header))
    for entry in sorted(entries, key=itemgetter(sortby), reverse=reverse):
        yield f(*entry)

def show_stats(data, sortby, reverse):
    entries = list(generate_stats_entries(data))
    maxnamewidth = max(map(len, next(zip(*entries))))
    print('\n'.join(format_stats(entries, maxnamewidth, sortby, reverse)))

# ======================== TODO mode ==================================

def generate_todo_entries(data):
    """
    Return all entries that aren't complete or in hiatus with their name,
    the next update's number and time since last update.
    """
    for name, datadict in data.items():
        if datadict['complete'] or datadict['hiatus']:
            continue
        i = list(generate_intervals(datadict['stats']))[-1]
        maxi = '/' + datadict['total parts'] if 'total parts' in datadict else ''
        yield (name, len(datadict['stats'])+1, i, maxi)

def format_todo(entries):
    """
    Return the data formatted in a table sorted falling after time since
    last update.
    """
    for n, entry in enumerate(sorted(entries, key=itemgetter(2), reverse=True), 1):
        yield ('>> ' if n == 1 else '   ') + '{0}. (+{3}) {1} (upd. {2}{4})'.format(n, *entry)

def show_todo(data):
    entry_strings = list(format_todo(generate_todo_entries(data)))
    maxwidth = max(map(len, entry_strings))-6
    print('\u2550'*(maxwidth//2) + ' TODO ' + '\u2550'*ceil(maxwidth/2))
    print('\n'.join(entry_strings))

# ===================== Update mode ====================================

def get_entry_name(names, namearg):
    """
    Return the entry with the namearg as name or as a part of its name.
    If there are more than one that fit, print the possibilities and quit.
    If no entries match, quit.
    """
    if namearg in names:
        return namearg
    partialnames = []
    for name in names:
        if namearg in name:
            partialnames.append(name)
    if not partialnames:
        raise KeyError
    if len(partialnames) == 1:
        return partialnames[0]
    else:
        print('Ambiguous name, can mean these entries:')
        for p in partialnames:
            print('*', p)
        raise KeyError

def run_update(data, name):
    try:
        entryname = get_entry_name(data.keys(), name)
    except KeyError:
        print('Error: Can\'t find entry')
    else:
        today = date.today().strftime('%Y-%m-%d')
        data[entryname]['stats'].append(today)
        write_json(local_path('medusadata.json'), data)
        print('Updated today: {}'.format(entryname))


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['stats', 'todo', 'update'])
    parser.add_argument('entryname', nargs='?',
                        help='part of the name of the fic to update')
    sortalt = ['name', 'cur', 'mean', 'med', 'max', 'min']
    parser.add_argument('-s', '--sort-stats', choices=sortalt, default=sortalt[0])
    parser.add_argument('-r', '--reverse', action='store_true')
    args = parser.parse_args()
    data = read_json(local_path('medusadata.json'))
    if args.mode == 'stats':
        show_stats(data, sortalt.index(args.sort_stats) if args.sort_stats else None,
                   args.reverse)
    elif args.mode == 'todo':
        show_todo(data)
    elif args.mode == 'update':
        if not args.entryname or not args.entryname.strip():
            print('Error: No entry name specified')
            return
        run_update(data, args.entryname)

if __name__ == '__main__':
    main()
