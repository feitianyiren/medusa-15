from datetime import date
from statistics import mean, median

from libsyntyche.common import read_json, local_path


def generate_intervals(stats):
    def getdate(s):
        return date(*map(int, s.split('-')))
    datelist = [getdate(x) for x in stats]
    intervallist = []
    for n, d in enumerate(datelist):
        if n == len(datelist)-1:
            intervallist.append((date.today()-d).days)
        else:
            intervallist.append((datelist[n+1]-d).days)
    return intervallist


def parse_data(data):
    maxnamewidth = 0
    entries = []
    for name, datadict in sorted(data.items()):
        maxnamewidth = max(len(name), maxnamewidth)
        i = generate_intervals(datadict['stats'])
        entry = [name, i[-1], round(mean(i)), round(median(i)), max(i), min(i)]
        entries.append(entry)
    return entries, maxnamewidth

def print_stats(entries, maxnamewidth):
    header = ['name', 'current', 'mean', 'median', 'max', 'min']
    formstr = '{{:{}}}  {{:>8}}  {{:>5}}  {{:>7}}  {{:>4}}  {{:>4}}'.format(maxnamewidth)
    headerstr = formstr.format(*header)
    print(formstr.format(*header))
    print('-'*len(headerstr))
    for entry in entries:
        print(formstr.format(*entry))

def main():
    data = read_json(local_path('medusadata.json'))
    entries, maxnamewidth = parse_data(data)
    print_stats(entries, maxnamewidth)


if __name__ == '__main__':
    main()

