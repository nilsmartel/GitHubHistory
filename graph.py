#!/usr/bin/env python3
from multiprocessing import Pool
import utils
from sys import argv
import os
import pandas as pd
import config
import matplotlib.pyplot as plt


def print_help(msg = None, code = 0):
    if msg is not None:
        print(msg)
    print("""usage:
          --dir <directory where to find all csvs> REQUIRED
          --graph <filename to save graph as> REQUIRED
          """)

    exit(code)

def parse_args():
    dir = None
    graph = None

    a = argv[1:]
    while len(a) != 0:
        first = a[0]
        if "=" in first:
            both = first.split("=")
            a = both + a[1:]
            continue

        if first in ["--help", "-h"]:
            print_help(0)

        elif first in ["--dir", "-d"]:
            dir = a[1]
        elif first in ["--graph", "-g"]:
            graph = a[1]
        else:
            print_help(f"unknown command '{first}'", code=1)

        a = a[2:]

    if None in [dir, graph]:
        print_help("required arguments missing", code=1)

    graph = str(graph)
    if not graph.endswith(".png"):
        graph += ".png"

    return str(dir), graph

dir, filename = parse_args()

ftdict = dict()

for ext,name in utils.filetypes:
    ftdict[ext] = name

def get_csv_paths():
    for f in os.listdir(dir):
        if f.endswith(".csv"):
            yield dir + "/" + f

def get_rows(df):
    for _,row in df.iterrows():
        yield row

"""
makes all informations inside a linecount-csv relative to it's previous position
"""
def diff_csv_info(df: pd.DataFrame):
    # sort by unixtimestamp of commit date
    df.sort_values("unix", inplace=True)

    rows = list(get_rows(df))
    if len(rows) == 0:
        return df

    keys = df.keys()
    ndf = dict()
    for k in keys:
        v = rows[0][k]
        ndf[k] = [v]

    for i in range(1,(len(rows))):
        prev = rows[i-1]
        row = rows[i]

        for k in df.keys():
            v = row[k]
            p = prev[k]
            if k in ["repo", "commit", "date", "unix"]:
                ndf[k].append(v)
            else:
                diff = v - p
                ndf[k].append(diff)

    return pd.DataFrame.from_dict(ndf)

def read(path):
    return pd.read_csv(path, sep=";")

print("[graph.py] reading and diffing commit information")

# create thread pool for
# downloading and organizing repositories.
pool = Pool(32)

dataframes = pool.map(diff_csv_info, pool.map(read, get_csv_paths()))

# next merge all dataframes into one by concatenation

def concat(frames):
    b = dict()
    keys = frames[0].keys()
    for k in keys:
        b[k] = []

    for f in frames:
        for row in get_rows(f):
            for k in keys:
                b[k].append(row[k])

    return pd.DataFrame.from_dict(b)

print("[graph.py] merging commit information")

df = concat(dataframes)
df.sort_values("unix", inplace=True)


# now, undo diffing

def undiff(df):
    b = dict()
    acc = dict()

    keys = df.keys()
    for k in keys:
        b[k] = []
        if k not in ["repo", "commit", "date", "unix"]:
            acc[k] = 0

    rows = get_rows(df)

    for row in rows:
        for k in keys:
            if k not in acc:
                b[k].append(row[k])
            else:
                # else sum with acc
                acc[k] += row[k]
                b[k].append(acc[k])

    newdf = pd.DataFrame.from_dict(b)
    newdf.sort_values("unix", inplace=True)
    return newdf

d = undiff(df)

print(f"[graph.py] found {d.size} commits")


# now plot the graph

print("[graph.py] configure graph")

fig, ax = plt.subplots(figsize=(15, 15))

def fmt(date):
    return date.split(" ")[0]

colors=[]
xlabels = list(map(fmt, d['date']))
y = []
labels = []

discard = config.languages_to_ignore()
keep = config.languages_to_keep()

if keep is None or len(keep) == 0:
    # set keep to all filetypes
    keep = set(map(lambda x: x[1], utils.filetypes))

for _, kind in utils.filetypes:
    if kind in discard:
        print(f"[graph.py] ignoring   {kind}")
        continue
    if kind not in keep:
        print(f"[graph.py] discarding {kind}")
        continue

    values = d[kind]
    if len(values) == 0:
        continue

    labels.append(kind)
    y.append(values)
    c = utils.langcolors[kind] if kind in utils.langcolors else None
    colors.append(c)

x = d['unix']
ax.stackplot(x, y, labels=labels, colors=colors)
# ax.stackplot(x, y, labels=labels)
ax.legend()
ax.set_ylabel('lines of code')
ax.set_xlabel('time')

def skip(ls, n):
    i = 0
    for elem in ls:
        if i%n == 0:
            yield elem
        i+=1

def skipl(ls, n):
    return list(skip(ls, n))

s = 300
_ = ax.set_xticks(skipl(x, s), skipl(xlabels, s), rotation=45)

fig.tight_layout()


print("[graph.py] saving graph as " + filename)

fig.savefig(filename)
