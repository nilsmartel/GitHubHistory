#!/usr/bin/env python3
from multiprocessing import Pool
import utils
from sys import argv
import os
import numpy as np
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
def diff_csv_info(path):
    df = pd.read_csv(path, sep=";")
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




# create thread pool for
# downloading and organizing repositories.
pool = Pool(32)
