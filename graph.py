#!/usr/bin/env python3
from multiprocessing import Pool
import utils
from sys import argv
import os
import pandas as pd


def print_help(msg = None, code = 0):
    if not msg is None:
        print(msg)
    print("""usage:
          --dir <directory where to find all csvs> REQUIRED
          """)

    exit(code)

def parse_args():
    dir = None

    a = argv[1:]
    while len(a) != 0:
        first = a[0]
        if "=" in first:
            l = first.split("=")
            a = l + a[1:]
            continue

        if first in ["--help", "-h"]:
            print_help(0)

        elif first in ["--dir", "-d"]:
            dir = a[1]
        else:
            print_help(f"unknown command '{first}'", code=1)

        a = a[2:]

    if None in [dir]:
        print_help("required arguments missing", code=1)

    return str(dir)

dir = parse_args()

ftdict = dict()

for ext,name in utils.filetypes:
    ftdict[ext] = name

def get_csv_paths():
    for f in os.listdir(dir):
        if f.endswith(".csv"):
            yield dir + "/" + f

"""
makes all informations inside a linecount-csv relative to it's previous position
"""
def diff_csv_info(df):
    # sort by unixtimestamp of commit date
    df.sort_values("unix")

    rows = list(df.iterrows())
    keys = df.keys()
    ndf = dict()
    for k in keys:
        v = rows[0][k]
        ndf[k] = [v]

    for i in range(1,(len(rows))):
        _,prev = rows[i-1]
        _,row = rows[i]

        for k in df.keys():
            v = row[k]
            p = prev[k]
            if k in ["repo", "commit", "date", "unix"]:
                ndf[k].append(v)
            else:
                diff = v - p
                ndf[k].append(diff)

    return pd.DataFrame.from_dict(ndf)


# create thread pool for
# downloading and organizing repositories.
pool = Pool(32)

dataframes = pool.map(diff_csv_info,
    pool.map(lambda path: pd.read_csv(path, sep=";"),
                          get_csv_paths())
                      )

# next merge all dataframes into one by concatenation

def concat(frames):
    b = dict()
    keys = frames[0].keys()
    for k in keys:
        b[k] = []

    for f in frames:
        for k in keys:
            b[k].append(f[f])

    return pd.DataFrame.from_dict(b)

df = concat(dataframes)
df.sort_values("unix")


# now, undo diffing

def undiff(df):
    b = dict()
    acc = dict()

    keys = df.keys()
    for k in keys:
        b[k] = []
        if k not in ["repo", "commit", "date", "unix"]:
            acc[k] = 0

    rows = df.iterrows()

    for _,row in rows:
        for k in keys:
            if k not in acc:
                b[k].append(row[k])
            else:
                # else sum with acc
                acc[k] += row[k]
                b[k].append(acc[k])

    newdf = pd.DataFrame.from_dict(b)
    newdf.sort_values("unix")
    return newdf

df = undiff(df)
