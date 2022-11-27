#!/usr/bin/env python3
from multiprocessing import Pool
import utils
from sys import argv
import os
import pandas as pd


def print_help(msg = None, code = 0):
    if msg is not None:
        print(msg)
    print("""usage:
          --dir <directory where to find all csvs> REQUIRED
          """)

    exit(code)

def parse_args():
    return "/tmp/allrepos"
    dir = None

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

df = undiff(df)
